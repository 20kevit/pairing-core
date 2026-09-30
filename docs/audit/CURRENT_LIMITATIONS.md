# Current Limitations — pairing-core v0.1.0 (STAGE 1)

Categories kept strictly separate per instructions. Every item carries its
evidence pointer; "suspected" items state what would confirm them.

## A. Confirmed limitations (demonstrated by source/tests)

A1. **First-local shortcut: FALSE POSITIVE as completeness bug, confirmed
    doc-overclaim**: `_search_bracket_configurations` (`pairer.py:241-255`)
    consumes only the first local pairing per configuration, contradicting the
    module docstring's "backtracks over all local pairings" claim (wording
    contradiction VERIFIED). Completeness is NOT harmed: downstream depends only
    on the downfloater set, all subsets are explored, and a 4000-case randomized
    differential probe found 0 engine-failure-with-solution instances (method in
    EVIDENCE_INDEX.md). Open instead: docstring accuracy + FIDE first-wins
    fidelity (UNVERIFIED, Stage 2).
A2. **No input validation beyond locked pairs**: duplicate ids, `pairing_no=0`,
    malformed histories, non-numeric fields are silently absorbed (dict
    last-wins, garbage-char ignore, or unhandled `TypeError`). VERIFIED by
    absence of checks in `models.py`/`engine.py`.
A3. **Engine never self-validates**: `engine.py`/`pairer.py` contain no
    `validate_round` call; illegal-output detection depends on caller discipline.
A4. **`rating` is dead input**: required field, zero algorithmic reads
    (VERIFIED grep + probe). Callers supplying rating-but-default-`pairing_no`
    get meaningless ordering.
A5. **Silent `status` filtering**: non-`"active"` legacy objects dropped without
    warning/report (VERIFIED probe: withdrawn player vanished, bye reassigned).
A6. **Id-based equality hazard**: `EnginePlayer.__eq__` on id alone; duplicate
    ids corrupt exchange swaps (`exchange.py:208-209`) and collapse maps.
    No test guards this.
A7. **`validate_and_fix` misnomer**: name promises repair; body only validates
    (`validator.py:85-136`). Legacy trap.
A8. **`is_upfloater` confirmed permanently `False` (dead flag, no behavioral
    impact found)**: the only assignments in the codebase are `= False`
    (`models.py:396` init, `pairer.py:303` restore); nothing ever sets it `True`
    (VERIFIED exhaustive grep + code-path review, Stage 1.6). Upfloat
    enforcement flows exclusively through opponent-down inference
    (`floats.py:240-241`), which covers every actual upfloat (pairs form only
    inside merged brackets, so a floated-against player is always flagged).
    Dead `or`-branches remain as code hygiene debt; FIDE-model fidelity of the
    inference itself is UNVERIFIED (Stage 2, ex-B6).
A9. **Committed `egg-info/`**: regenerable build artifact tracked in git;
    can go stale relative to `pyproject.toml`.
A10. **No serialization / roll-forward helpers**: caller must hand-maintain
    `color_hist`/`float_hist`/`opponents`/`points` between rounds; format errors
    silently absorbed (A2). No multi-round test exists.
A11. **Greedy bye choice**: first bye candidate whose remainder pairs wins
    (`engine.py:267-292`); not proven globally optimal across bye candidates.
A12. **Non-English comment** (`pairer.py:244`, Persian) + Priority-1 docstring
    imprecision (`color.py:50` "3 consecutive" vs 2-history trigger) + `__all__`
    vs module-docstring export inconsistency (`SwissEngine`) — documentation
    hygiene, all VERIFIED.
A13. **No CLI / TRF / FIDE-export I/O**: library-only; external reference
    cross-checking impossible in-repo.
A14. **No benchmarks, no scale tests**: 2M-step cap and caches untested under load.

## B. Suspected limitations (strongly indicated, need Stage 2 verification)

B1. **Upfloat-over-strictness**: `float_pair_legal` (`floats.py:240-241`) treats
    anyone facing a downfloater as an upfloater subject to `can_upfloat`,
    rejecting `last_was_up` players in the strict pass. May reject FIDE-legal
    pairings. Needs FIDE-text comparison + targeted tests.
B2. **Bye-order vs FIDE**: bottom-up `(points, -pno, id)` ordering is the
    engine's interpretation; whether the handbook wants lowest-score-first
    globally (vs within lowest bracket) needs handbook check.
B3. **Exchange-order vs FIDE**: `exchange.py` claims "FIDE convention" without
    article citation; exact order needs handbook verification.
B4. **Absolute-conflict resolution** (both players `must_white`/`must_black`):
    higher-ranked-wins is a code choice (`color.py:93-96`) with no cited rule.
B5. **Exponential worst case despite pruning**: pruning is exact (safe), but no
    measurement proves the 2M cap suffices for realistic large fields; a
    100+ single-bracket pathological state may `ValueError` where FIDE expects
    a pairing. Needs benchmarks.
B6. **Float-tag semantics for locked cards**: locked cards carry `""` floats
    always — suspected inconsistency for history roll-forward, needs donor
    `chess-manager` comparison.

## C. Unknowns (cannot be answered from this repo alone)

C1. Byte-equivalence with donor `chess-manager domain/pairing/` (no donor present).
C2. Which FIDE handbook edition/interpretation decisions the donor made.
C3. Intended support for accelerated pairings, requested byes, withdrawals,
    late entries (shims hint at them; no spec here).
C4. Expected behavior for total-odd fields where all players already had byes
    (code path exists; untested).
C5. Performance envelope at 100/250/500/1000 players (no data).
C6. Thread-safety/reentrancy expectations (no concurrent use evident; shared
    mutation of `EnginePlayer` flags during search makes instances
    single-use — untested).
C7. Whether `SwissEngine` top-level export is intentional public API or
    accidental (docstring omits it).

## D. Missing capabilities (clearly do not exist — VERIFIED absent)

D1. FIDE conformance/reference test corpus; TRF I/O; CLI.
D2. Round-Robin, team events, knockout, match play, accelerated Swiss.
D3. Ratings integration, standings/result management, tournament lifecycle.
D4. JavaFo/BBP adapters (docstring future only).
D5. Seeded randomness; property/fuzz/performance/conformance suites.
D6. Serialization (JSON/dict/TRF), persistence, API server, notifications.
D7. Lint/type/test config beyond bare pytest `testpaths`; CI workflows.
D8. `LICENSE` file, `CHANGELOG`, contributing docs, issue templates.
