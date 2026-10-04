"""TRF interchange at the adapter edge (W2 foundation, W6-verified vs BBP).

Never imported by core domain code (import-lint enforced): TRF types live
exclusively here and in future engine adapters.

Wire format (VERIFIED against BBP's own parser, src/fileformats/trf.cpp —
primary source; BBP 2025-Dutch build, Apache-2.0, used as reference only):
- 001 lines are FIXED-WIDTH: id[4,8), rating[48,52) (blank allowed),
  score[80,84) (tenths, e.g. " 3.5"), round entries from char 91 in steps
  of 10: opponent[0,4) of entry (blank or 0000 = no opponent), color at
  entry+5 (w/b/-/space), result at entry+7. Name/rank/other columns are
  ignored by BBP and carried opaquely here.
- Result semantics (BBP mapping): D = = H draw; + W 1 F U win; - L 0 Z loss.
  Unplayed = blank/0000 opponent. Crucially, **U marks PAB participation**
  (participatedInPairing) AND scores a win: a pairing-allocated bye in
  history is ``0000 - U`` (VERIFIED in BBP source, common.h eligibleForBye:
  past U-win blocks future PAB). F is a requested full-point bye
  (non-participation). The earlier F-for-PAB assumption was WRONG and is
  corrected here.
- Tags: 012 (name), 062 (count, informational), XXR/142 (total rounds,
  REQUIRED > 0), XXP (whitespace id list = mutually forbidden),
  XXC rank/white1/black1 (BBP-verified tokens), 240/162 parsed where seen.
  XXZ (JaVaFo absentees) is WRITTEN for JaVaFo but BBP does not read it
  (BBP absentee mechanism: UNVERIFIED — limitation, see below).
- Parser is dual-mode: fixed-width first (BBP-shaped files, multi-token
  names supported), then whitespace-token fallback (JaVaFo-shaped). Unknown
  tags/XX lines ignored (documented subset). Consequence of ignoring 240:
  future-round bye declarations from third-party files are NOT consumed —
  callers pass current-round absentees explicitly via
  TournamentInput.absent_ids / XXZ.

Known limitations (all explicit): BBP absentee (current-round) mechanism
unverified (XXZ written for JaVaFo only); live-binary acceptance PENDING
for JaVaFo; acceleration (XXA/250) neither written nor parsed; 240 lines
parsed into nothing (see parse_trf docstring).
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
    initial_color: str = ""  # "", "w" (XXC white1) or "b" (XXC black1)

    def __post_init__(self) -> None:
        object.__setattr__(self, "players", tuple(self.players))
        object.__setattr__(self, "absent_ids", tuple(self.absent_ids))
        object.__setattr__(
            self, "forbidden_pairs",
            tuple(tuple(p) for p in self.forbidden_pairs))
        if self.initial_color not in ("", "w", "b"):
            raise InvalidRequestError(
                "initial_color must be '', 'w' or 'b'.")


def _check_range(value: int, low: int, high: int, what: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) \
            or not low <= value <= high:
        raise InvalidRequestError(
            f"TRF {what} must be int in [{low}, {high}], got {value!r}.")


def build_trf(tournament: TournamentInput) -> str:
    """Serialize to BBP-compatible fixed-width TRF(x) (see module docstring).

    Raises InvalidRequestError for values the fixed format cannot carry
    (ids/ratings outside 1..9999/0..9999, scores not in tenths below 100,
    rounds_total < 1, overlong names are truncated).
    """
    if not isinstance(tournament.rounds_total, int) or \
            isinstance(tournament.rounds_total, bool) or \
            tournament.rounds_total < 0:
        raise InvalidRequestError("rounds_total must be int >= 0.")
    lines = [f"012 {tournament.name}", f"062 {len(tournament.players)}"]
    if tournament.rounds_total >= 1:
        # BBP requires XXR > 0 when present; omit when unknown (BBP's own
        # RTG output carries no XXR line and derives rounds from matches).
        lines.append(f"XXR {tournament.rounds_total}")
    if tournament.initial_color == "w":
        lines.append("XXC white1")
    elif tournament.initial_color == "b":
        lines.append("XXC black1")
    for pid in tournament.absent_ids:
        _check_range(pid, 1, 9999, "absent id")
        lines.append(f"XXZ {pid}")
    for pair in tournament.forbidden_pairs:
        lines.append(f"XXP {pair[0]} {pair[1]}")
    for p in tournament.players:
        _check_range(p.pairing_id, 1, 9999, "pairing id")
        _check_range(p.rating, 0, 9999, "rating")
        if not isinstance(p.points, (int, float)) or \
                isinstance(p.points, bool) or \
                not 0 <= p.points < 100 or \
                abs(round(float(p.points) * 10)
                    - float(p.points) * 10) > 1e-9:
            raise InvalidRequestError(
                f"TRF points must be tenths in [0, 100), got {p.points!r}.")
        seen = set()
        head = ("001 " + f"{p.pairing_id:>4d}" + "  "
                + p.name[:38].ljust(38) + f"{p.rating:>4d}"
                + " " * 28 + f"{float(p.points):4.1f}" + " " * 7)
        entries = ""
        for r in p.rounds:
            opp = "0000" if r.opponent is None else f"{r.opponent:>4d}"
            if r.opponent is not None:
                _check_range(r.opponent, 1, 9999, "opponent id")
                if r.opponent in seen:
                    raise InvalidRequestError(
                        f"duplicate opponent {r.opponent} "
                        f"for player {p.pairing_id}.")
                seen.add(r.opponent)
            entries += f"{opp} {r.color} {r.result}  "
        lines.append(head + entries)
    return "\n".join(lines) + "\n"


def parse_trf(text: str) -> TournamentInput:
    """Dual-mode TRF(x)-subset parser (see module docstring for scope).

    Fixed-width mode first (BBP-shaped files; multi-token names OK), then
    whitespace-token fallback (JaVaFo-shaped). Malformed content ->
    InvalidRequestError with line context. Unknown tags/XX lines, 240/162
    lines, and DAT lines are ignored (documented subset behavior).
    """
    players: List[TrfPlayer] = []
    name = "pairing-core"
    rounds_total = 0
    initial_color = ""
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
        elif head in ("XXR", "142"):
            rounds_total = _parse_int(rest.strip(), lineno, "XXR rounds")
        elif head == "XXC":
            for tok in rest.split():
                if tok == "white1":
                    initial_color = "w"
                elif tok == "black1":
                    initial_color = "b"
        elif head == "XXZ":
            absent += [_parse_int(t, lineno, "XXZ id")
                       for t in rest.split()]
        elif head == "XXP":
            ids = [_parse_int(t, lineno, "XXP id") for t in rest.split()]
            if len(ids) != 2:
                _fail(lineno, "XXP needs exactly two ids")
            forbidden.append((ids[0], ids[1]))
        elif head == "001":
            player = _parse_player_fixed(raw, lineno)
            if player is None:
                player = _parse_player_tokens(rest.split(), lineno)
            if player.pairing_id in seen_ids:
                _fail(lineno, f"duplicate pairing id {player.pairing_id}")
            seen_ids.add(player.pairing_id)
            players.append(player)
        # DAT/TRF26 tags/240/162/other XX codes: out of subset, ignored.
    players.sort(key=lambda p: p.pairing_id)
    return TournamentInput(players=tuple(players), rounds_total=rounds_total,
                           name=name, absent_ids=tuple(absent),
                           forbidden_pairs=tuple(forbidden),
                           initial_color=initial_color)


def _parse_player_fixed(raw: str, lineno: int) -> Optional[TrfPlayer]:
    """Fixed-width 001 parse (BBP shape); None if the line is not fixed.

    Columns: id[4,8), name[10,48) opaque, rating[48,52) (blank allowed),
    score[80,84), entries from 91 in steps of 10 (opp[0,4) blank/0000/int,
    color[+5] w/b/-/space, result[+7]). All-blank entries are trailing
    padding and skipped. Rank zone [84,91) ignored.
    """
    line = raw.rstrip("\n")
    if len(line) < 84 or not line.startswith("001"):
        return None
    try:
        pid = int(line[4:8])
    except ValueError:
        return None
    name = line[10:48].strip() if len(line) >= 48 else ""
    name = name or f"Player{pid}"
    rating = 0
    if len(line) >= 52 and line[48:52].strip():
        try:
            rating = int(line[48:52])
        except ValueError:
            return None
    try:
        points = float(line[80:84])
    except ValueError:
        return None
    rounds: List[TrfRound] = []
    pos = 91
    ok_shape = True
    while pos + 8 <= len(line):
        entry = line[pos:pos + 10]
        opp_tok, color, result = entry[0:4], entry[5:6], entry[7:8]
        if entry.strip() == "":
            pos += 10
            continue
        if color not in ("w", "b", "-", " "):
            ok_shape = False
            break
        try:
            opp = None if opp_tok.strip() in ("", "0000") else int(opp_tok)
        except ValueError:
            ok_shape = False
            break
        res = result.upper()
        if res not in RESULT_CODES:
            ok_shape = False
            break
        if color == " ":
            # Padding without opponent: skip (BBP trailing shape).
            pos += 10
            continue
        rounds.append(TrfRound(opponent=opp, color=color, result=res))
        pos += 10
    if not ok_shape:
        return None
    tail = line[pos:]
    if tail.strip() != "":
        return None
    try:
        return TrfPlayer(pairing_id=pid, name=name.replace(" ", "_"),
                         rating=rating, points=points,
                         rounds=tuple(rounds))
    except InvalidRequestError:
        _fail(lineno, "fixed 001 values out of range")
        raise AssertionError("unreachable")


def _fail(lineno: int, message: str) -> None:
    raise InvalidRequestError(f"TRF line {lineno}: {message}.")


def _parse_int(token: str, lineno: int, what: str) -> int:
    try:
        return int(token)
    except ValueError:
        _fail(lineno, f"bad integer {token!r} ({what})")
        raise AssertionError("unreachable")


def _parse_player_tokens(tokens: List[str], lineno: int) -> TrfPlayer:
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


def validate_external_pairs(pairs: List[Tuple[int, Optional[int]]],
                              present_ids: Tuple[int, ...], *,
                              absent_ids: Tuple[int, ...] = (),
                              engine: str = "engine") -> None:
    """Semantic validation of external pairing output against the roster.

    Authoritative adapter-edge check (shared by BBP/JaVaFo): syntactic
    parsing alone never confers trust. Every violation is an engine-output
    fault -> InternalError (never silently accepted, never coerced).

    Enforced: positive-int ids; no self-pair; no duplicate appearance
    (a bye recipient is unpaired, so bye+paired or double-bye fails);
    at most one bye; every appearing id is a rostered player (unknown
    ids fail); every non-absent roster player appears exactly once
    (missing players fail). Absent ids (XXZ) may appear at most once:
    engines that ignore absentees still pair them, engines that honour
    them omit them — both shapes validate.
    """
    roster = set(present_ids)
    absent = set(absent_ids)
    seen: set = set()
    byes = 0
    for white, black in pairs:
        if black is not None and white == black:
            raise InternalError(
                f"{engine} self-paired player {white}.")
        for pid in (white,) if black is None else (white, black):
            if not isinstance(pid, int) or isinstance(pid, bool) or pid < 1:
                raise InternalError(
                    f"{engine} pairing id not a positive int: {pid!r}.")
            if pid not in roster:
                raise InternalError(
                    f"{engine} paired unknown player {pid}.")
            if pid in seen:
                raise InternalError(
                    f"{engine} lists player {pid} twice.")
            seen.add(pid)
        if black is None:
            byes += 1
    if byes > 1:
        raise InternalError(f"{engine} granted {byes} byes (at most one).")
    missing = sorted(set(present_ids) - absent - seen)
    if missing:
        raise InternalError(
            f"{engine} omitted roster players {missing}.")


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
                        absent_ids: Tuple[int, ...] = (),
                        rounds_total: Optional[int] = None,
                        ) -> TournamentInput:
    """Bridge new-API request + caller-supplied per-round histories to TRF.

    Core PlayerData carries no per-round mapping (by design), so the caller
    (manager/adapter user) supplies it here. Histories must cover played
    rounds; lengths are NOT cross-checked against points here (engines verify
    scores themselves, e.g. BBP refuses on mismatch). rounds_total sets XXR
    (total planned rounds; BBP requires it > 0) and defaults to the request
    round number when unknown.
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
                           rounds_total=(request.round_number
                                         if rounds_total is None
                                         else rounds_total),
                           name=name, absent_ids=tuple(absent_ids),
                           forbidden_pairs=tuple(forbidden))
