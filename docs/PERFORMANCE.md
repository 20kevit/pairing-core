# Performance characterization (v0.4.0 — measured, not optimized)

Policy: measure-first, optimize only on demonstrated production need. No
hard timing asserts anywhere (machine-dependent); gates assert *outcomes*
(success vs typed bounded failure). Raw records:
`tests/data/benchmarks/` (refresh opt-in: `PAIRING_UPDATE_BASELINES=1`).

## Representative figures (reference machine, 2026-10-03)

Frozen `dutch-till2026-compat` kernel, realistic randomized histories:

| Case | Outcome | Wall time |
|---|---|---|
| n=8, round 1 | success, 4 boards | ~0.00 s |
| n=50, round 4 | success, 25 boards | ~0.01 s |
| n=100, round 5 | success, 50 boards | ~0.01 s |

Reproduce: `python3 -m pytest tests/test_benchmarks.py -q`
(scenarios + printed table with `-s`).

## L1 ceiling — where it appears and how it behaves

Exact search over dense brackets grows factorially. Probe: 20 players,
round 6, near-complete opponent histories (almost every pairing is a
rematch), `wall_clock_seconds=20`:

- Outcome: `EngineTimeoutError` after ~6 s (step budget engages first).
- No hang, no partial pairing escapes (O02: exception, not a result).
- Cancellation of the same input: `CancelledError` in ~0.06 s.
- Budgets are caller-scaled; guidance in
  `docs/audit/SEARCH_CEILING_POLICY.md`.

Reproduce (probes used for this table):

```bash
python3 -m pytest tests/test_benchmarks.py tests/test_benchmarks_2026.py -q
```

Pathological scenarios in those files must end `timeout-bounded`
(typed `EngineTimeoutError`), never hang.

## 2026 family

Per-ruleset benchmark record (`benchmarks_2026.json`): round-1 and
realistic sizes succeed; factorial ceilings (notably Dutch/Burstein big
brackets) terminate typed under budget. No heuristic pruning is applied
anywhere — a ceiling never returns a best-effort pairing.

## External engines

Adapter overhead is one supervised subprocess invocation per call
(TRF write → run with timeout → parse). Live-oracle runs are env-gated
(`BBP_EXE`, `JAVAFO_JAR`) and excluded from timing gates.
