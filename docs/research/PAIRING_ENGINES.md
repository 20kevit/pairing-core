# Pairing Engines Research: BBP, JaVaFo, Mature Systems (STAGE 2, §§2.5–2.7)

## 1. BBP Pairings (PRIMARY: repo README + files, retrieved in full)

- Identity: BieremaBoyzProgramming/bbpPairings, C++ engine (NOT a manager),
  112 stars / 48 forks / 128 commits; issues 4, PRs 6 (maturity: maintained,
  small community).
- Version/ruleset: implements **2025 Dutch rules** (effective date delayed to
  2026); Burstein included but self-declared "flawed… not endorsed".
- License: **Apache-2.0** (LICENSE.txt + Apache-2.0.txt in repo — VERIFIED file
  presence; OSI terms per canonical text).
- Interface: JaVaFo-1.4-AUM-compatible CLI (with author's permission):
  `bbpPairings [--dutch|--burstein] input -p [out] [-l [list]]`, `-c`
  (check), `-g [model|cfg] -o trf [-s seed]` (RTG with seed), `-r` (version).
  No `-w`/`-q` (always weighted matching). Input TRF-2026 (+ back-compat
  TRF(bx) with BBW/BBD/BBL/BBZ/BBF/BBU point-system codes); no random initial
  colour (must specify; inference rule documented).
- Algorithm: weighted general-graph (blossom) matching, Galil-Micali-Gabow;
  Dutch O(n³·s²·log n); Burstein O(n³). Deterministic given input (+ explicit
  seed only for RTG).
- Validation/errors: checklist mode (C2 bye-eligibility, C14/C16 float
  columns); error codes 0–5 (0 ok; 1 no-valid-pairing; 2 unexpected; 3 invalid
  request; 4 size/memory; 5 file access) — a ready-made error taxonomy to learn
  from. Validity cross-check of scores vs results (refuses on mismatch).
- Tests/maturity: test/ dir in repo; py4swiss differential-tests against
  bbpPairings.exe; gnutterts/chesspairing includes BBP test cases. Used by
  SwissSys (endorsed Minsk 2018, v9.6).
- Limitations: Dutch-only (mature); Burstein flawed; no Dubov/Lim; C++
  build/packaging burden for a Python library; TRF-only I/O (no library API).
- FIDE relationship: engine inside FIDE-endorsed SwissSys; BBP itself is not
  "endorsed" as a standalone program (endorsement attaches to programs+versions).

## 2. JaVaFo (PRIMARY: AUM + project page, retrieved in full)

- Identity: by IA Roberto Ricca (Secretary, FIDE SPPC); Java .jar; Rel. 2.2
  build 3222; "FIDE reference pairer" (SECONDARY label, consistent with
  endorsement-table role: FPC/RTG flow through JaVaFo for most programs).
- License: **free of charge, attribution required** (mention rrweb.org/javafo
  in commercial products + notify author). NOT an OSI licence; redistribution/
  bundling terms UNKNOWN — no licence text retrieved. OWNER DECISION REQUIRED
  before any bundling/distribution.
- Interface: TRF(x) in (TRF16 + XXR/XXZ/XXC/XXA/XXP/XXS); out: count + `white
  black` lines, bye = `id 0`; `-p/-c [round]/-l/-g/-b/-r`; experimental Java
  API (`main.jar`, `JaVaFoApi.exec`, op codes 1000–1301: pairing, Baku,
  pre/post checklists, tournament/round check, RTG).
- Semantics learned: pairing-id vs positional-id (`XXC rank`); scoring systems
  via XXS with strict Points cross-check; acceleration via XXA history (full
  history needed for floaters); forbidden pairs XXP (arbitrary lists);
  initial colour random-by-default but **seeded by TRF hash (reproducible)**;
  checklist Pref/(-1R)/(-2R)/G-n columns; RTG (Milvang outcome model, 15–415
  players, 5–17 rounds, seed in `012` field, seed re-generates same TRF per build).
- Operational requirements: JVM in target environment; stderr messages
  hard to interpret; "error in pairing engine very unlikely but not impossible".
- FIDE status: reference engine for Dutch certification flows (markjenkins
  front-end calls it "the official FIDE pairing engine for certifying other
  implementations" — SECONDARY characterisation, consistent with FPC role).

## 3. Mature professional systems (§2.7; vendor pages PRIMARY, feature claims as stated)

| Program | Author | Systems | Engine | Licence/cost (as stated) | FIDE endorsement | Interop |
|---|---|---|---|---|---|---|
| Vega (+Orion teams) | Luigi Forlano (ITA) | Dutch, Dubov, Lim, Dutch-variant, Burstein, USCF, RR, Baku accel | JaVaFo (Dutch) + internal (Dubov) | free ≤30 players Win / free Linux (vendor/secondary claims) | Dutch 2012+2017, Dubov 2006 | TRF, FIDE/USCF/ECF/DZW reports |
| Swiss-Manager | Heinz Herzog (AUT) | Swiss to 2000 pl/23 rds, RR, team-Swiss/RR | JaVaFo | commercial 150€/75€ light | Minsk 2018 v13 | chess-results DB (~1M tournaments), HTML/Excel |
| SwissSys | Thad Suits (USA) | Dutch | bbpPairings | commercial (vendor) | Minsk 2018 v9.6 | via BBP |
| SwissMaster | KNSB (NED) | Dutch | JaVaFo (current; internal earlier) | federation program | Minsk 2018 v5.6.9/5.7 | TRF |
| Swiss-Chess/WinSwiss | F.-J. Weber (GER) | Dutch | internal | commercial (vendor) | Minsk 2018 v9.05 (+FPC/RTG console) | console FPC/RTG |
| UTU Swiss | Neil Hayward (UK) | Dutch | JaVaFo | commercial (vendor) | Abu Dhabi 2020 | — |
| ChessManager | T. Żyźniewski (POL) | Dutch (+Olympiad adjustments) | JaVaFo | freemium/web | Abu Dhabi 2020 (interim) | web, TRF20 work |
| STOP | A. Lenhard (GER) | Dutch | JaVaFo | free | Abu Dhabi 2020 | — |
| Tornelo | Tornelo (AUS) | Dutch | ? (UNVERIFIED) | free tier/web | endorsed (VCL round 2019–20) | web |
| JavaPairing | E. Cervesato (ITA) | Dutch + others | internal | open (SourceForge) | Tallinn 2013 v2.7 | jar CLI |

Lesson: endorsement attaches to (program, version, system, engine); managers
standardise on JaVaFo/BBP via TRF(x); nobody exposes a reusable library API —
the gap pairing-core targets.
