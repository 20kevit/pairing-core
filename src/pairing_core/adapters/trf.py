"""TRF interchange at the adapter edge (W2 foundation).

Never imported by core domain code (import-lint enforced): TRF types live
exclusively here and in future engine adapters.

Subset scope (documented deviations from full TRF16/TRF26):
- Player lines: ``001 <id> [sex] [title] <name> <rating> <fed> <fideid>
  <birth> <points> [<rank>] (<opp> <color> <result>)*`` — whitespace
  tokenized (cf. Tornelo TRFx doc, SPP TRF-update deck: real files use
  this shape). sex/title optional on parse; always written (``-`` default).
  rank is written NEVER, parsed leniently (leading token when token count
  demands it). fed/fideid/birth default (XXX/0/0) when unknown.
- Result codes accepted: 1 0 = + - D F H L U W Z (per echecs/trf table,
  secondary source). Anything else is malformed input.
- Header/tags: 012 (name), 062 (player count informational), XXR (total
  rounds, mandatory for engines per JaVaFo AUM), XXZ (absent ids), XXP
  (forbidden pairs). Other tags/XX lines are ignored on parse (documented).
- Pairing-allocated bye in history: ``0000 - F``. ASSUMPTION (UNKNOWN,
  flagged): full-point code carries the win-valued PAB under standard
  scoring so engine score cross-checks (BBP refuses on mismatch) hold.
  MUST be re-verified against live BBP/JaVaFo binaries.
- Engine pairing output (shared BBP/JaVaFo shape per AUM): first line is
  the pair count, then ``<white> <black>`` lines; bye is ``<id> 0``.

Live-binary acceptance of emitted files is PENDING (no binaries in this
environment); round-trip self-consistency + AUM-shaped fixtures are tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from pairing_core.errors import InternalError, InvalidRequestError

RESULT_CODES = ("1", "0", "=", "+", "-", "D", "F", "H", "L", "U", "W", "Z")
COLORS = ("w", "b", "-")
SEX_CODES = ("m", "w", "-")
TITLE_CODES = ("GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM", "-")
DEFAULT_FED = "XXX"


@dataclass(frozen=True)
class TrfRound:
    """One played/unplayed round from the player's perspective."""
    opponent: Optional[int]  # None -> unplayed round (0000)
    color: str  # w/b/-
    result: str  # RESULT_CODES

    def __post_init__(self) -> None:
        if self.opponent is not None and (
                not isinstance(self.opponent, int)
                or isinstance(self.opponent, bool)):
            raise InvalidRequestError("TRF opponent must be int or None.")
        if self.color not in COLORS:
            raise InvalidRequestError(
                f"TRF color must be one of {COLORS}.")
        if self.result not in RESULT_CODES:
            raise InvalidRequestError(
                f"TRF result must be one of {RESULT_CODES}.")


@dataclass(frozen=True)
class TrfPlayer:
    """Adapter-edge player record (NOT a domain object)."""
    pairing_id: int
    name: str = ""
    rating: int = 0
    points: float = 0.0
    rounds: Tuple[TrfRound, ...] = ()
    sex: str = "-"
    title: str = "-"
    federation: str = DEFAULT_FED
    fide_id: str = "0"
    birth_year: str = "0"

    def __post_init__(self) -> None:
        if not isinstance(self.pairing_id, int) or \
                isinstance(self.pairing_id, bool) or self.pairing_id < 1:
            raise InvalidRequestError("TRF pairing id must be int >= 1.")
        if not isinstance(self.name, str) or not self.name:
            raise InvalidRequestError("TRF player name must be non-empty.")
        if any(c.isspace() for c in self.name):
            raise InvalidRequestError("TRF player name must be one token.")
        object.__setattr__(self, "rounds", tuple(self.rounds))


@dataclass(frozen=True)
class TournamentInput:
    """Adapter-edge tournament file content."""
    players: Tuple[TrfPlayer, ...] = ()
    rounds_total: int = 0
    name: str = "pairing-core"
    absent_ids: Tuple[int, ...] = ()
    forbidden_pairs: Tuple[Tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "players", tuple(self.players))
        object.__setattr__(self, "absent_ids", tuple(self.absent_ids))
        object.__setattr__(
            self, "forbidden_pairs",
            tuple(tuple(p) for p in self.forbidden_pairs))


def build_trf(tournament: TournamentInput) -> str:
    """Serialize to TRF(x)-shaped text (subset; see module docstring)."""
    if not isinstance(tournament.rounds_total, int) or \
            isinstance(tournament.rounds_total, bool) or \
            tournament.rounds_total < 0:
        raise InvalidRequestError("rounds_total must be int >= 0.")
    lines = [f"012 {tournament.name}", f"062 {len(tournament.players)}",
             f"XXR {tournament.rounds_total}"]
    for pid in tournament.absent_ids:
        lines.append(f"XXZ {pid}")
    for pair in tournament.forbidden_pairs:
        lines.append(f"XXP {pair[0]} {pair[1]}")
    for p in tournament.players:
        parts = ["001", str(p.pairing_id), p.sex, p.title, p.name,
                 str(p.rating), p.federation, p.fide_id, p.birth_year,
                 _fmt_points(p.points)]
        for r in p.rounds:
            opp = "0000" if r.opponent is None else str(r.opponent)
            parts += [opp, r.color, r.result]
        lines.append(" ".join(parts))
    return "\n".join(lines) + "\n"


def _fmt_points(points: float) -> str:
    if not isinstance(points, (int, float)) or isinstance(points, bool):
        raise InvalidRequestError("TRF points must be numeric.")
    text = str(float(points))
    return text


def parse_trf(text: str) -> TournamentInput:
    """Lenient TRF(x)-subset parser (see module docstring for scope).

    Malformed content -> InvalidRequestError with line context. Unknown
    tags/XX lines are ignored (documented subset behavior).
    """
    players: List[TrfPlayer] = []
    name = "pairing-core"
    rounds_total = 0
    absent: List[int] = []
    forbidden: List[Tuple[int, int]] = []
    seen_ids = set()
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        head, _, rest = line.partition(" ")
        if head == "012":
            name = rest.strip() or name
        elif head == "062":
            pass  # informational only
        elif head == "XXR":
            rounds_total = _parse_int(rest.strip(), lineno, "XXR rounds")
        elif head == "XXZ":
            absent += [_parse_int(t, lineno, "XXZ id")
                       for t in rest.split()]
        elif head == "XXP":
            ids = [_parse_int(t, lineno, "XXP id") for t in rest.split()]
            if len(ids) != 2:
                _fail(lineno, "XXP needs exactly two ids")
            forbidden.append((ids[0], ids[1]))
        elif head == "001":
            player = _parse_player(rest.split(), lineno)
            if player.pairing_id in seen_ids:
                _fail(lineno, f"duplicate pairing id {player.pairing_id}")
            seen_ids.add(player.pairing_id)
            players.append(player)
        # DAT/TRF26 tags/other XX codes: out of subset, ignored.
    players.sort(key=lambda p: p.pairing_id)
    return TournamentInput(players=tuple(players), rounds_total=rounds_total,
                           name=name, absent_ids=tuple(absent),
                           forbidden_pairs=tuple(forbidden))


def _fail(lineno: int, message: str) -> None:
    raise InvalidRequestError(f"TRF line {lineno}: {message}.")


def _parse_int(token: str, lineno: int, what: str) -> int:
    try:
        return int(token)
    except ValueError:
        _fail(lineno, f"bad integer {token!r} ({what})")
        raise AssertionError("unreachable")


def _parse_player(tokens: List[str], lineno: int) -> TrfPlayer:
    idx = 0
    try:
        pid = int(tokens[idx])
        idx += 1
    except (ValueError, IndexError):
        _fail(lineno, "bad pairing id")
        raise AssertionError("unreachable")
    sex, title = "-", "-"
    if idx < len(tokens) and tokens[idx] in SEX_CODES:
        sex = tokens[idx]
        idx += 1
    if idx < len(tokens) and tokens[idx] in TITLE_CODES:
        title = tokens[idx]
        idx += 1
    try:
        name = tokens[idx]
        rating = int(tokens[idx + 1])
        fed = tokens[idx + 2]
        fide_id = tokens[idx + 3]
        birth = tokens[idx + 4]
        points = float(tokens[idx + 5])
        rest = tokens[idx + 6:]
    except (IndexError, ValueError):
        _fail(lineno, "truncated 001 header fields")
        raise AssertionError("unreachable")
    triples = _split_rounds(rest, lineno)
    rounds = []
    for opp_tok, color, result in triples:
        try:
            opp = int(opp_tok)
        except ValueError:
            _fail(lineno, f"bad opponent {opp_tok!r}")
            raise AssertionError("unreachable")
        if color not in COLORS:
            _fail(lineno, f"bad color {color!r}")
        if result not in RESULT_CODES:
            _fail(lineno, f"bad result {result!r}")
        rounds.append(TrfRound(opponent=None if opp == 0 else opp,
                               color=color, result=result))
    return TrfPlayer(pairing_id=pid, name=name, rating=rating,
                     points=points, rounds=tuple(rounds), sex=sex,
                     title=title, federation=fed, fide_id=fide_id,
                     birth_year=birth)


def _split_rounds(tokens: List[str], lineno: int) -> List[Tuple[str, str, str]]:
    if not tokens:
        return []
    body = tokens
    if len(tokens) % 3 == 1 and len(tokens) >= 4:
        # Leading rank token (observed real-file shape); drop after sanity.
        try:
            int(tokens[0])
        except ValueError:
            _fail(lineno, "round data not in triples")
            raise AssertionError("unreachable")
        body = tokens[1:]
    if len(body) % 3 != 0:
        _fail(lineno, "round data not in triples")
    return [(body[i], body[i + 1], body[i + 2])
            for i in range(0, len(body), 3)]


def parse_pairing_output(text: str) -> List[Tuple[int, Optional[int]]]:
    """Parse shared BBP/JaVaFo pairing output (AUM §output).

    First non-empty line: pair count; then ``<white> <black>`` lines, bye as
    ``<id> 0``. Count mismatch or malformed lines -> InternalError (engine
    output fault, captured for diagnosis).
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise InternalError("empty engine pairing output.")
    try:
        count = int(lines[0])
    except ValueError:
        raise InternalError(
            f"engine output first line is not a pair count: "
            f"{lines[0]!r}.") from None
    pairs: List[Tuple[int, Optional[int]]] = []
    for raw in lines[1:]:
        parts = raw.split()
        if len(parts) != 2:
            raise InternalError(
                f"malformed engine pairing line: {raw!r}.")
        try:
            white, black = int(parts[0]), int(parts[1])
        except ValueError:
            raise InternalError(
                f"non-integer engine pairing line: {raw!r}.") from None
        pairs.append((white, None if black == 0 else black))
    if len(pairs) != count:
        raise InternalError(
            f"engine pair count {count} != {len(pairs)} lines.")
    return pairs


def from_engine_request(request: object,
                        rounds_by_player: Dict[int, List[TrfRound]],
                        *,
                        name: str = "pairing-core",
                        absent_ids: Tuple[int, ...] = ()) -> TournamentInput:
    """Bridge new-API request + caller-supplied per-round histories to TRF.

    Core PlayerData carries no per-round mapping (by design), so the caller
    (manager/adapter user) supplies it here. Histories must cover played
    rounds; lengths are NOT cross-checked against points here (engines verify
    scores themselves, e.g. BBP refuses on mismatch).
    """
    from pairing_core.api import EngineRequest

    if not isinstance(request, EngineRequest):
        raise InvalidRequestError("EngineRequest required.")
    players = []
    for p in request.players:
        hist = rounds_by_player.get(p.id, [])
        players.append(TrfPlayer(
            pairing_id=p.pairing_no if p.pairing_no else p.id,
            name=f"Player{p.id}", rating=p.rating, points=p.points,
            rounds=tuple(hist)))
    forbidden = []
    if request.constraints is not None:
        forbidden = [tuple(x) for x in
                     request.constraints.forbidden_pairs]
    return TournamentInput(players=tuple(players),
                           rounds_total=request.round_number,
                           name=name, absent_ids=tuple(absent_ids),
                           forbidden_pairs=tuple(forbidden))
