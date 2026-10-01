# Architecture Specification (OWNER DECISION O01/O07 — as built upon in blueprint)

## 1. Adopted structure (FINAL per O01, refined from mission §3.5 hypothesis)

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
- Timeout/cancellation (O10): every execution bounded by wall-clock timeout +
  deterministic step budget; native interruption at bracket-boundary
  checkpoints (step budget primary for reproducibility); external supervision
  with grace-then-terminate; typed timeout errors with diagnostics.
- Explicit engine configuration (O03): default vs explicitly-selected vs
  explicitly-allowed-fallback are distinct request modes; metadata always
  records requested/actual engine + reason + versions; silent substitution is
  architecturally impossible (no code path performs it).
- Conformance harness (permanent asset): goldens, FIDE cases, differential
  cases, seeded corpora, property/regression cases, cross-engine comparison
  with 7-class outcome taxonomy (exact-equivalent / rule-equivalent-reordered
  / valid-alternative / rule-violation / implementation-specific /
  unsupported-feature / oracle-disagreement-needs-investigation).
- tiebreak-core relation (O05/O09): independent future library; pairing-core
  consumes only narrow ranking/index inputs (Burstein); one-way dependency;
  no tournament-core.

## 3. Non-goals enforced by construction

No HTTP, no DB, no UI, no ratings, no general tie-break calculation
(Burstein consumes narrow ranking/index inputs as data — O05), no standings. Dependency rule: core imports
stdlib only; adapters import core; nothing imports adapters except registry
extras. Test rule: every abstraction has an oracle-backed suite before a
second implementor exists.
