# FIDE Swiss Systems Overview (STAGE 2 RESEARCH)

Evidence grades: **PRIMARY** (FIDE Handbook / FIDE Council docs / engine's own
docs), **SECONDARY** (reputable explainers, consistent with primary excerpts).
Full citations in `SOURCES.md`. Nothing here is implementation.

## 1. Chapter map of FIDE Handbook section C.04 (rules in force from 1 Feb 2026)

VERIFIED (PRIMARY: FIDE Council doc CM3-202517, approved 28/10/2025, applied
1 Feb 2026; corroborated by FIDE news 2026-02-01 and handbook chapter index):

| Chapter | Content | Status 2026 |
|---|---|---|
| C.04.1 | Basic Rules for Swiss Systems (rematch ban, odd-player bye, color limits) | in force |
| C.04.2 | General Handling Rules for Swiss Tournaments (systems, initial order, acceleration regime, QC authorisation) | in force |
| C.04.3 | FIDE (Dutch) System — baseline, criteria C1–C21 | rewritten 2026 |
| C.04.4.1 | Dubov System | in force |
| C.04.4.2 | Burstein System (recodified, was generic) | in force |
| C.04.4.3 | Lim System (Singapore; new/promoted 2026) | in force |
| C.04.5 | Double Swiss (every pairing = two-game alternating-colour match) | codified 2026 |
| C.04.6 | Swiss Team system (referenced by implementations; text not retrieved — UNVERIFIED detail) | exists |
| C.04.7 | Accelerated Systems: Baku Acceleration (moved from C.04.5) | in force |
| C.04 App. A | Endorsement: FPC (Free Pairings Checker), RTG (Random Tournament Generator) definitions | in force |

Historical note (PRIMARY: 1987 GA regulations + 2024 TEC references): the old
"C.04.2 FIDE Swiss Rules" listed PETUNIA Dutch, GMB Lim, SWISS CHESS Dutch,
SVBOSS Dutch, DUBOV, BURSTEIN (GA '98). Unpublished systems need QC temporary
authorisation + declaration by the arbiter (C.04.2 §1.2–1.3, PRIMARY).

## 2. System-by-system (purpose, mechanics, FIDE status)

### 2.1 Dutch (C.04.3) — baseline, default choice

Score groups processed top-down; S1/S2 halves by pairing number; transpositions
then exchanges; floaters cascade downward. Full spec: `DUTCH_SYSTEM_SPECIFICATION.md`.
FIDE status: THE default; sole system implemented by all currently endorsed
Dutch programs (PRIMARY: endorsed-programs table). Pairing-core's native engine
targets the pre-2026 formulation — see native-vs-FIDE matrix.

### 2.2 Dubov (C.04.4.1) — anti-“Swiss gambit”, rating-aware

Devised by GM Daniil Dubov (SECONDARY: multiple explainers; PRIMARY structure
from 2024 TEC draft + 2025 Council text). Signature mechanics VERIFIED
(PRIMARY excerpts): **there are no downfloaters in the Dubov system** —
brackets pull UPfloaters from lower scoregroups; two-step procedure (first fix
number of pairs/floaters under criteria C1–C5, then choose best pairing);
completion criterion C4 + quality criteria C5 (max pairs), C6 (max incoming
floaters by number then score), C7 (outgoing floaters optimise next bracket).
Adjacent-style pairing inside groups per implementations. Purpose (SECONDARY,
Held 2020 comparison study): reduce rating-spread unfairness of Dutch; at its
best in central scoregroups (~20–30 Elo ARO variability reduction, vanishing at
top). FIDE status: approved alternative; endorsed implementations exist in Vega
(Dubov internal, Turin 2006 — older rules).

### 2.3 Burstein (C.04.4.2) — fairness-by-opposition-strength

Designed to maximise fair treatment: equal scorers should have met equivalent
opposition (PRIMARY: C040402Till2026 excerpt). Mechanics VERIFIED (PRIMARY:
2020 SPP minutes + 2025 Council text): ranking order for pairing = Buchholz
then Sonneborn-Berger; median-scoregroup cracking rules (§2.6.1/2.6.2: crack
neighbour pairing and re-treat players as floaters when floater counts unbalance);
A–E article structure mirroring Dutch; default acceleration semantics that
differ from Dutch (PRIMARY: BBP README — without XXA codes Burstein defaults to
its own acceleration system; Dutch defaults to none). BBP's own Burstein is
self-declared "flawed… not endorsed" (PRIMARY: BBP README + arxiv paper).
FIDE status: approved, recodified 2026.

### 2.4 Lim (C.04.4.3) — colour/float refinement, newest

Origin: Singapore (SECONDARY: playvibechess; Lim named in 1987 list as GMB Lim).
Mechanics PARTIALLY VERIFIED (PRIMARY excerpt: pairing runs top-down to just
before the median scoregroup, then bottom-up — bi-directional; implementations
describe strict colour rules). Purpose (SECONDARY, consistent): better colour
distribution, fewer floaters; bye to lowest-ranked of bottom group. FIDE status:
approved; current text C040403202602 (Feb 2026). Detail level: thinner than
Dutch/Dubov/Burstein in retrieved sources — flagged in SOURCES.md.

### 2.5 Double Swiss (C.04.5) — two-game mini-matches

Every pairing = two consecutive games with alternating colours; match score =
sum (VERIFIED: secondary guide consistent with chapter title; echecs/swiss
implements: bye = 1.5 = win+draw). Purpose: colour fairness by construction.
Relevance: pairing-core would need a match/result model — currently absent.

### 2.6 Team Swiss (C.04.6) + Olympiad pairing rules

Teams paired as units (match points primary in Olympiad context); board colours
and line-ups per Olympiad rules (PRIMARY: Olympiad Pairing Rules chapter
exists; detail not retrieved — UNVERIFIED). Implementations: echecs/swiss
`team` subpath ("teams as players, Type A colour preferences" — SECONDARY).
Vega/Orion and Swiss-Manager handle team Swiss + Olympiad/ECU systems (PRIMARY:
vendor pages). Relevance: needs team/match abstractions pairing-core lacks.

### 2.7 Accelerated systems — Baku (C.04.7)

Top-half virtual win-point early, halved mid-way, removed at end (SECONDARY,
consistent across sources; JaVaFo `-b` flag + XXA codes PRIMARY for mechanism
carriage). Others (e.g. Sevillano/Grant?) not retrieved — UNKNOWN. Relevance:
virtual points interact with float histories (JaVaFo AUM mandates full XXA
history for floater computation) — a future input-model concern.

### 2.8 Historical / national variants (for context, NOT targets)

USCF Swiss (different bye/colour rules), ECF "patent" middle-of-group pairing
(SECONDARY: chess.SE), older Dutch implementations (PETUNIA, SVBOSS,
SWISS CHESS). Recorded to prevent "we invented it" syndrome; no further action.

## 3. Cross-system comparison (ruleset/version/FIDE status)

| System | Chapter | 2026 text | Brackets | Float direction | Colours | Bye | FIDE status |
|---|---|---|---|---|---|---|---|
| Dutch | C.04.3 | rewritten (C1–C21) | score groups, S1/S2 | down (cascade) | abs/strong/mild, topscorer split | lowest score (C5), win-point value | baseline/default |
| Dubov | C.04.4.1 | in force | scoregroups, no downfloaters | up only | same E-rules family | per Basic rules | approved alt |
| Burstein | C.04.4.2 | recodified | Buchholz-ordered groups, median cracking | both, median-centred | E-rules consistent w/ Dutch+Dubov | PAB must allow completion | approved alt |
| Lim | C.04.4.3 | in force (new) | bi-directional around median | both | strict | bottom-group lowest-ranked | approved alt |
| Double | C.04.5 | codified 2026 | as Dutch | as Dutch | alternating by construction | 1.5 pts | approved |
| Team | C.04.6 | exists (detail UNVERIFIED) | teams | teams | board colours | team-level | approved |
| Baku | C.04.7 | renumbered | virtual points | virtual-aware | as host system | as host | approved accel |

## 4. What this means for pairing-core (research conclusion, not decision)

- The native engine implements a pre-2026 Dutch formulation (pairity-driven
  floats, draw-valued bye assumption in docs, no C1–C21 optimisation framing,
  no topscorer split). The 2026 Dutch is a criteria-optimisation system —
  conceptually closer to BBP's weighted matching than to the native search.
- Any "FIDE-correct" claim must name system + ruleset date (e.g. "Dutch,
  C.04.3-till-2026" vs "Dutch, C.04.3-from-2026"). The repo's "effective
  1 July 2025" string matches NEITHER current text (till-2026 vs from-2026
  split) — VERIFIED mismatch, see DUTCH_SYSTEM_SPECIFICATION.md §1.
- Dubov/Burstein/Lim/Double/Team each need distinct bracket/float/result
  models; none fits the native `Bracket` abstraction without extension
  (Stage 3 taxonomy).
