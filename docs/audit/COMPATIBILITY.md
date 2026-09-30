# Backward Compatibility Baseline — v0.1.0 (STAGE 1)

v0.1.0 (SHA `2cb570b`, single-commit repo) is the first and only baseline, so
"compatibility" here means: what a consumer adopting v0.1.0 could already be
depending on, and what must therefore be preserved or deliberately versioned.

## 1. Preliminary compatibility contract (what v0.1.0 guarantees in practice)

**Import paths** (VERIFIED): `pairing_core` top-level names in `__all__`
(`PlayerData`, `PlayerSnapshot`, `PairingCard`, `RoundResult`,
`PairingRequest`, `PairingEngine`, `NativeDutchEngine`, `SwissEngine`,
`pair_round`, `validate_round`, `ValidationReport`, `Finding`,
`__version__`, `__fide_reference__`) + `pairing_core.<module>` deep paths
used by shims (`pairing_core.models.*`, `pairing_core.engine.SwissEngine`,
`pairing_core.validator.validate_and_fix` — the last NOT in `__all__` but
importable and donor-shaped).

**Data structures**: field names/defaults of the four dataclasses
(PUBLIC_API.md §1 + §3 signature table); `FrozenSet` opponents; `Optional`
black/bye conventions; float-tag alphabet `{D,U,""}`; color-hist alphabet
`{w,b,-}`; `round_number` echo.

**Behavioral surface consumers may depend on** (all VERIFIED, all observable):
round-1 S1-vs-S2 shapes (`{(1,5),(2,6),(3,7),(4,8)}` for 8); bye-last board
ordering; `bye_player_id` echo; fresh-before-repeat bye preference; `ValueError`
on illegal locked pairs / impossible pairings; `ValidationReport` severity
split (ERROR vs WARNING vs INFO) and rule-code strings; silent legacy
normalization (donor objects accepted).

**Documented guarantees**: determinism ("same input → same output", README +
`pairer.py` docstring — behaviorally VERIFIED for pair sets); "No Flask, no
SQLAlchemy, no persistence, no network" (VERIFIED true); FIDE reference string
(claim, not guarantee).

**Undocumented-but-observable** (high compat risk): silent `status` filtering;
rating-ignored ordering; garbage-history tolerance; greedy bye/first-local
choices; exact `ValueError` message texts (consumers may substring-match —
fragile); `is_bye`+`black_id=None` encoding; in-place board mutation of
returned cards.

## 2. Gaps that weaken the contract

No `CHANGELOG`, no deprecation policy, no versioning scheme statement, no
stability tiering (experimental vs stable), rule codes without a codebook,
`SwissEngine`-in-`__all__`-but-not-in-docstring ambiguity, `PlayerSnapshot`
alias without documented sunset, `validate_and_fix` legacy surface without
contract. License text missing (MIT claim without file — downstream packaging
risk, not API risk).

## 3. Compatibility hazards for future stages (recorded, not decided)

Any change to: dataclass fields/defaults, `sort_key` ordering, bye ordering,
search order (first-wins choices), float-tag semantics, board-numbering order,
`ValueError`-vs-typed-errors, rule-code strings/severities, or the silent
normalization behaviors would be **observable breaking changes** for a
v0.1.0 consumer. Future work needs explicit contract tiering
(explicit-public vs implicit vs internal per PUBLIC_API.md) before touching
these. No decision made in Stage 1.
