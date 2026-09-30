# Reproducibility Specification (STAGE 3 SPEC — PROPOSED)

## 1. Replay envelope (required on every result)

Input digest (canonical serialisation hash) + full input reference; round;
RulesetId (system + effective date + acceleration + point values incl. PAB
value); engine id + version (+ binary build where external); ConstraintSet
digest (forced/forbidden/bye directives); seed (or explicit `none`);
pairing-number assignment fingerprint (order + numbers, since ranking is
caller-owned); software version pins (library, adapter, TRF dialect);
timestamp (informational only, never an input).

## 2. Guarantees

`replay(envelope) == result` byte-identical (C-REP-01). External engines:
replay valid to the extent the engine self-identifies (JaVaFo build-coupled
seeds documented as a caveat). Initial-colour lots: only via declared seed;
hash-seeded defaults (JaVaFo-style) are allowed ONLY if disclosed in the
envelope.

## 3. Retention & audit

Envelopes stored alongside results by the manager; core provides
verify/envelope-diff helpers. Audit trail = envelopes + diagnostics, no
logging framework inside core.
