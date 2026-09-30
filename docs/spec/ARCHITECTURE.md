# Architecture Specification (STAGE 3 SPEC — PROPOSED)

## 1. Verdict on the hypothesised structure (mission §3.5)

The hypothesis (Domain → Rules/Constraints → Engine Provider Interface →
Registry → Native/External(BBP, JaVaFo)) is **ADOPTED with modifications**
(PROPOSED): it fits the evidence (JaVaFo/BBP are process-shaped; native is
library-shaped; TRF is the interchange), but (a) Rules/Constraints must be
*data* (RulesetId + ConstraintSet), not a layer; (b) a Validation/Diagnostics
sidecar and a Reproducibility envelope are first-class; (c) I/O (TRF) is an
adapter, never in core.

```
            ┌─────────────────────────┐
            │     Pairing Domain      │  entities, histories, ledgers (pure)
            └────────────┬────────────┘
                         │ RulesetId + ConstraintSet (data)
            ┌────────────▼────────────┐
            │  Engine Provider        │  pair(request) -> RoundPairing
            │  Interface + Registry   │  capabilities(), versions()
            └───┬─────────┬───────────┘
      ┌─────────▼──┐  ┌───▼──────────────┐
      │ Native     │  │ External adapters │  opt-in extras
      │ Dutch…     │  │ BBP │ JaVaFo │…  │  subprocess + TRF
      └─────────┬──┘  └───┬──────────────┘
   ┌────────────▼─────────▼───────────┐
   │ Validation/Diagnostics sidecar   │  legality + criteria-cost report
   │ Reproducibility envelope         │  replay metadata on every output
   └──────────────────────────────────┘
```

## 2. Component responsibilities (proposed)

- Domain: types + derivation helpers (colour/float states) + roll-forward.
- Criteria engine (native): per-system optimisation over dated rulesets
  (Dutch-2026 first); explicit cost model mirroring C1–C21 (replaces
  satisficing search; Stage-1 kernel behaviour preserved under a
  `dutch-pre2026-compat` ruleset ONLY via the v0.1.0 harness).
- Provider interface: identity, versions, capabilities, determinism contract,
  error taxonomy, diagnostics schema — identical for native and external
  (ENGINE_ABSTRACTION.md).
- Registry: named engine lookup + capability query ("which engine pairs
  Dutch-2026 with seeds?") — answers the Stage-4 capability model.
- Adapters: TRF build/parse, process supervision (timeout, crash, malformed
  output mapping to R-EXT-01 errors), BYO-binary resolution, attribution
  notices (JaVaFo).
- Validation sidecar: legality verdict + per-criterion cost + bye/float/colour
  accounting; callable standalone (FPC-analogue over TRF + native objects).

## 3. Non-goals enforced by construction

No HTTP, no DB, no UI, no ratings, no tie-breaks (except Burstein-internal
ranking inputs, passed as data), no standings. Dependency rule: core imports
stdlib only; adapters import core; nothing imports adapters except registry
extras. Test rule: every abstraction has an oracle-backed suite before a
second implementor exists.
