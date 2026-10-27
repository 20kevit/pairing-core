# Capability and evidence status

**Current source:** `0.4.2.dev0` (unreleased development snapshot). The
published `v0.4.1` tag and artifacts are immutable. This file is a concise
product view; the authoritative audit findings and exact closure evidence are
in [`audit/GAP_REGISTER.md`](audit/GAP_REGISTER.md), and measurable readiness
gates are in [`audit/COMPLETION_STANDARD.md`](audit/COMPLETION_STANDARD.md).
Older conformance matrices and completion reports are historical project
records, not independent FIDE evaluation.

## Product boundary

Pairing-Core is a pairing-only Python library: it accepts caller-owned
pairing-relevant state and produces one-round pairings. It is not a tournament
manager, standings service, rating calculator, or general tie-break library.
It has no runtime dependencies and does not silently select an external
engine. External BBP/JaVaFo adapters remain explicit bring-your-own-binary
integrations.

## Pairing systems

"Implemented" below means source code exists. It does not mean the system
has been fully independently verified, is production-ready for every event,
or has FIDE approval, certification, endorsement, or formal evaluation.

| System | Effective source | Current scope/evidence statement |
|---|---|---|
| `dutch-till2026-compat` | Frozen legacy behavior | Golden-pinned compatibility mode with documented deviations; not the current 2026 Dutch formulation. |
| `dutch-2026` | C.04.3, effective 2026-02-01 | Engine and tests exist. Exact-search ceilings and documented interpretations remain; no external FIDE evaluation. |
| `dubov-2026` | C.04.4.1, effective 2026-02-01 | Engine and tests exist. Required ratings and event histories are caller-owned; no external FIDE evaluation. |
| `burstein-2026` | C.04.4.2, effective 2026-02-01 | Pairing procedures consume a complete external `BursteinIndexSet` after Dutch seeding. Pairing-Core does not calculate or independently verify Buchholz/SB. No suitable C.04 calculator is evidenced in inspected `tiebreak-core` v1.2.0. |
| `lim-2026` | C.04.4.3, effective 2026-02-01 | Engine and tests exist. Documented scrutiny/order approximations and unresolved readings remain. |
| `double-2026` | C.04.5, effective 2026-02-01 | Engine and tests exist. Next-bracket lookahead is a bounded implementation strategy/limitation, not proof of full criterion conformance. |
| `team-2026` | C.04.6, effective 2026-02-01 | Pairing mechanics exist. Team composition, lineups, match results, and score valuation remain caller-owned. |
| `olympiad-2022` | Olympiad Pairing Rules, effective 2022-01-01 | Separate dated team system. Initial team ordering and event facts are caller-owned; evidence posture differs from C.04 Handbook chapters. |
| Baku helper | C.04.7, effective 2026-02-01 | Acceleration helper only; group membership, standings, and use with a pairing engine remain caller responsibilities. |
| Berger round robin | C.05 Annex 1 | Table generation exists. Official-table comparison coverage is documented in the tests; do not infer untested field sizes from algorithmic structure. |

Official source identity and dates, direct text retrieval, interpretations,
implementation strategies, policy choices, and unresolved questions are
recorded separately in the audit register. The texts alone do not prove that
an implementation conforms.

## Cross-cutting engineering surface

| Capability | Current statement |
|---|---|
| 2026 request validation | Value objects reject malformed types/ranges and non-finite numeric inputs; the public dispatcher validates exact roster coverage and core output invariants. These checks do not replace full clause-level conformance testing. |
| Result provenance | 2026 public results carry a dated ruleset, engine/package version, round, normalized input digest, canonical result digest, and any Burstein Index source metadata. The digest provides integrity/replay support, not correctness proof. |
| Determinism | Deterministic ordering and serialization are tested; declared engine budgets can return typed timeout/cancellation errors rather than partial results. Review the current CI evidence for the exact revision. |
| External process handling | POSIX adapters use isolated process groups and terminate descendants on timeout, output overflow, and cleanup. Windows standard-library handling guarantees direct-child cleanup only. |
| Tie-break calculations | Outside Pairing-Core. No dependency on `tiebreak-core`; C.07 outputs are not assumed to be C.04 Burstein values. |
| Berger evidence (`berger-rr`) | Exact official C.05 Annex 1 comparisons cover every published field size 3–16; structural checks outside that table range do not imply additional official examples. The tests do not establish universal C.05 conformance. |
| Packaging | Runtime dependency-free; MIT license text is present. CI is configured for CPython 3.10–3.15; Python 3.10 remains only as a compatibility check despite upstream end-of-life, and exact revision results must be verified. |

## Readiness and FIDE standing

- **Engineering quality:** report against the gates in
  [`audit/COMPLETION_STANDARD.md`](audit/COMPLETION_STANDARD.md) for an exact
  source revision; a green suite alone is not a universal readiness verdict.
- **Production use:** limited to a named engine and operating subset whose
  assumptions, evidence, state roll-forward, and constraints are validated by
  the consuming product. There is no blanket production-ready claim.
- **Formal FIDE evaluation:** Pairing-Core alone is a library, not a complete
  Tournament Handler Program. It has not been formally evaluated.
- **Endorsement:** no endorsement evidence found in the official list
  retrieved for this audit; no endorsement claim is made. See G-12/G-13 in
  the gap register.

No general "FIDE-compliant" or "fully conformant" badge is supported by the
current evidence. Reassess any capability statement when its primary source,
implementation, independent tests, or evaluation status changes.
