# Current Capabilities — pairing-core v0.1.0 (STAGE 1)

Conformance key: SUPPORTED (code + test evidence), PARTIAL (code, gaps noted),
ABSENT (no code). No "planned" column — per instructions, unsupported features
are not marked as planned (the JavaFo/BBP docstring mentions are recorded as
NOT IMPLEMENTED, not roadmap).

| Capability | Current status | Evidence | Notes |
|---|---|---|---|
| Dutch Swiss | PARTIAL | `pairer.py` + `bracket.py` + round-1 goldens pass | Dutch-family search; FIDE-article-level conformance UNVERIFIED; search-completeness suspect (PAIRING_ENGINE.md §5.1) |
| FIDE rules version | UNVERIFIED claim | `__fide_reference__` string only | "C.04.2 + C.04.3 (eff. 1 July 2025)" is asserted, not traced; no handbook in repo |
| Determinism | SUPPORTED | no RNG; `test_repeat_and_reorder` green | Pair-set level; color-orientation reorder stability untested |
| Seeded randomness | ABSENT | no seed param anywhere | By design (fully deterministic) |
| Byes | PARTIAL | `bye.py` + `test_odd_five`, `test_bye_fresh_first` | Bottom-up fresh-first; greedy first-wins choice; repeat path untested |
| Color allocation | PARTIAL | `color.py` + `test_color_absolute` | 4-priority chain; only absolute case tested |
| Color history | SUPPORTED (input) | `color_hist` → `ColorState` | Derivation VERIFIED; garbage chars ignored (no validation) |
| Float handling | PARTIAL | `floats.py` + two-pass search | 3-level model; upfloat-constraint path suspect dead; zero float tests |
| Rematch avoidance | SUPPORTED | bidirectional checks + `test_no_rematch` | Absolute; both maps consulted |
| Constraints (locked/forbidden) | PARTIAL | `locked_pairs` validated preassignments | No generic forbidden-pair API beyond played sets |
| Validation | PARTIAL | `validator.py` 16 checks + smoke test | Legality yes; optimality no; engine never self-validates |
| Error model | PARTIAL | `ValueError`-only, messages w/ bracket summary | No taxonomy; callers can't distinguish categories programmatically |
| Serialization | ABSENT | no json/dict/TRF code | — |
| Engine abstraction | SUPPORTED | `PairingEngine` ABC + `NativeDutchEngine` | One implementor; stability unproven |
| External engines | ABSENT | docstring mentions only | JavaFo/BBP NOT IMPLEMENTED |
| Round Robin | ABSENT | — | No code |
| Team Swiss | ABSENT | — | No code |
| Team Round Robin | ABSENT | — | No code |
| Knockout | ABSENT | — | No code |
| Match play | ABSENT | — | No code |
| Performance testing | ABSENT | no benchmarks | 2M-step cap exists untested |
| Property testing | ABSENT | no hypothesis/fuzz | — |
| Conformance testing | PARTIAL | 15 contract tests, trivial goldens | No external FIDE reference cases |

Additional present-but-ungraded capabilities: legacy donor-object normalization
(`_normalize_input`, `validate_and_fix`, `PlayerSnapshot` alias); board
numbering (normal-first/bye-last); float-tag output (`D`/`U`); bye-selection
warnings (`validate_bye_selection`, untested); human-readable bracket summary
for failure messages.
