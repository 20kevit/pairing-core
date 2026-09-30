# Engine Strategy Options (STAGE 2, §2.14 — evaluation only, NO decision)

## Options

**A — Native only.** Keep one hand-built Dutch kernel, extend to 2026 + systems.
Correctness: full control, full burden (criteria optimisation is a rewrite-scale
change). Maintenance: all in-house. Portability: pure Python, best. Licensing:
clean MIT. FIDE: longest path to conformance confidence. Testing: needs oracle
harness anyway. Flexibility (custom constraints like XXP/locks): best.

**B — External only.** Library becomes a TRF multiplexer over BBP/JaVaFo
subprocesses. Correctness: inherits reference behaviour. Maintenance: hostage
to upstreams (BBP Burstein flawed; JaVaFo version/build-coupled; JVM/C++
toolchain in deployment). Portability: worst (binaries+JVM). Licensing:
JaVaFo bundling UNKNOWN; user-supplied binaries friction. FIDE: closest to
endorsed behaviour for Dutch-2025. Testing: still needs own harness.
Flexibility: limited to TRF(x)-expressible constraints.

**C — Native + external adapters.** Native default; optional BBP/JaVaFo
subprocess adapters behind one interface. Correctness: native improves while
adapters give reference parity from day one. Maintenance: adapter surface is
small (TRF build/parse + process supervision + error mapping). Portability:
core pure; adapters opt-in with declared requirements. Licensing: clean if
bring-your-own-binary + attribution. FIDE: adapters usable as conformance
oracles immediately. Flexibility: native covers custom constraints; adapters
cover reference fidelity. Cost: TRF layer + failure model required.

**D — Reference engines + conformance harness + selectable engines.** C plus a
standing differential-test harness (seeded corpora à la RTG, golden files,
cross-engine matrix) as a first-class repo asset. Highest assurance, highest
upfront cost (harness + corpus + TRF). This is C with the test strategy made
explicit — the form Stage 3 will likely PROPOSE (not decide here).

## Comparison summary

| Axis | A | B | C | D (=C+harness) |
|---|---|---|---|---|
| correctness confidence | low-med | high (Dutch) | med-high | highest |
| maintenance burden | high (all rules in-house) | low core / high ops | medium | medium+ |
| portability | best | worst | best core, opt-in adapters | same as C |
| licensing risk | none | JaVaFo bundling UNKNOWN | low (BYO binary) | low |
| FIDE proximity | far | nearest | near via adapters | near + provable |
| testing leverage | none external | oracles only | oracles as tests | oracles as CI |
| custom constraints | best | TRF-limited | best of both | best of both |
| dependency risk | none | binaries/JVM/QT? no—JVM+C++ | opt-in only | opt-in only |

## Research lean (explicitly PROPOSED, for owner review in Stage 4)

D, with native Dutch-2026 alignment as the first correctness milestone and BBP
as the first oracle/adapter (Apache-2.0 is the cleanest licence; CLI stable;
TRF-2026 current). JaVaFo second (licence clearance needed for bundling; BYO
binary meanwhile). Cross-engine goldens from day one. No implementation here.
