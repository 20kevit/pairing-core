# Final Capability & Professionalization Report (master wave)

## 1–3. Commits & tree

- Starting commit: `871a0aa`. Final commit: (this wave's last checkpoint;
  see log). Branch `main`, linear history, all pushed to `origin/main`,
  working tree clean, no force-push at any point.
- Wave checkpoints: C9 bye ordering; TRF/oracle/property expansion;
  live-oracle conformance docs; budgets-in-envelope + tiering; JaVaFo live
  verification; forbidden-pair enforcement + budget policy; Berger round
  robin; API audit/docs; capability/research updates; explainability +
  serialization + maturity model (+ this report's commit).

## 4–7. Systems & rulesets

- IMPLEMENTED & tested: Dutch compat kernel (`dutch-till2026-compat`,
  frozen+hardened); Berger round robin single/double (validated vs C.05).
- RESEARCHED+ (nearest candidates): Double Swiss C.04.5 (skeleton:
  TPN/upfloaters/C1/C2/C4/C5/PAB; procedures 3.4–3.6 + colours missing);
  Olympiad team Swiss (median groups, float priority tables, board colours,
  B/C-team odds; articles 3–6 missing).
- BLOCKED with reasons: Dutch-2026 (no PRIMARY C10–C21/P0 text), Dubov
  (no text, no oracle), Burstein (BBP self-declared flawed, no text), Lim
  (thin text, no oracle), C.04.6 TPS (excerpts only), KO/match (no single
  authoritative pairing text, no requesting use case).
- UNSUPPORTED (explicit): Round Robin beyond Berger tables; team play of any
  kind; acceleration; non-standard scoring in core.

## 8. Capability maturity matrix

See `docs/CAPABILITY.md` (product authority): Dutch-compat PRODUCTION_READY
(compat scope); RR VALIDATED; forbidden/C9/budgets/envelopes/adapters/harness/
benchmarks PRODUCTION_READY-or-VALIDATED as listed; 2026/Dubov/Burstein/Lim/
Team/KO BLOCKED/RESEARCHED with reasons. No maturity upgraded without
evidence; none claimed beyond it.

## 9–13. API, constraints, diagnostics, explainability, reproducibility

- API: 47+ exports, all additive; tiers recorded (PUBLIC_API.md §4);
  `explain()` + request serialization added; `SwissEngine` legacy-compat.
- Constraints: forced + forbidden (rematch-equivalent, BBP-XXP-agreeing);
  bye directives explicitly refused; validator FORBID-01.
- Diagnostics: typed taxonomy + bracket summaries + timeout context +
  validator codes + adapter captures; deterministic and serializable.
- Explainability: `explain()` (boards/floats/colours/bye inputs) + to_dict.
- Reproducibility: envelopes (engine/ruleset/versions/digest/budgets/
  warnings) + canonical serialization + replay-equality tests.

## 14–17. External engines, tests, benchmarks, security

- BBP 8f9e3c5 (BYO source build): 42-tournament differential (24 compatible,
  18 native-Impossible/oracle-clean), XXP/C9/PAB-U/score-checks verified,
  version-probed, stub-tested. Nothing vendored (Apache-2.0 respected).
- JaVaFo 2.2 b3223 (BYO JVM+jar, Dutch-2017 vintage): pairing/version/NPE-
  failure/impossible paths verified live; attribution documented.
- Tests: 247 passed, 10 skipped (heavy/oracle env-gates with reasons),
  0 failed; hash-seed sweeps green (241 passed); 30 seeded property tests;
- Benchmarks: realistic 50–1000 + pathological, baselines recorded;
  single-1000 round-1 ≈97s bounded; pathological hangs eliminated (measured).
- Security: subprocess argv-only/no-shell, kill-after-grace, 10MiB caps,
  strict UTF-8, explicit paths, tempdir cleanup, linear parsing, strict
  boundary, import-lint isolation; hostile re-audit clean.

## 18–20. Licensing, compatibility, limitations

- MIT retained; LICENSE file added; no GPL anywhere (dependency-free core);
  BBP use-only; JaVaFo BYO + attribution; no bundling.
- v0.1.0 behavior preserved: 41/41 goldens + 15/15 contract green at every
  checkpoint; kernel outputs byte-identical (one intentional, evidenced,
  unpinned-territory refinement: C9 bye ordering, zero golden impact).
- Known limitations: §10 above + asymmetric-history strictness (manager
  evidence pending) + oracle-mass storage undecided + wall-clock default
  open + TRF acceleration/240-consumption out of scope.

## 21–22. Risks & questions

- High: 1000-player round-1 budget policy unset (measured, ungated).
- Medium: dated-ruleset migration vehicle for E.5/float-bar; tiebreak-core
  still future; live JaVaFo mass smaller than BBP's.
- Open owner items: budget policy adoption; migration scope/timing;
  oracle-mass storage; `SwissEngine` tier detail (minor).

## 23. Next step

Decide the three high/medium items above; then Dutch-2026 criteria engine
(if PRIMARY text obtained) or additional oracle mass; chess-manager
integration preparation only after that. Integration itself NOT performed
(no manager sources present or touched).

## 24. Verdict

CONDITIONAL production gate (unchanged in kind, narrowed in scope since the
last wave): the library is trustworthy within its explicit maturity matrix —
Dutch-compat + RR + constraints + adapters + harness are evidence-backed;
everything else is labeled BLOCKED/RESEARCHED, not shipped. No FIDE
compliance or endorsement claimed anywhere.
