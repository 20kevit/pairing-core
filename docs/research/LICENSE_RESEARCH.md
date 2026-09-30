# License Research (STAGE 2, §2.13)

Canonical references (provisions as published; SPDX IDs): MIT
(`https://opensource.org/licenses/MIT`), Apache-2.0
(`https://www.apache.org/licenses/LICENSE-2.0`), GPL-3.0/LGPL-3.0/AGPL-3.0
(`https://www.gnu.org/licenses/`), GPL FAQ on process separation
(`https://www.gnu.org/licenses/gpl-faq.html#MereAggregation`). Project-licence
facts PRIMARY (repo files/pages); third-party-licence *implications* are
standard reading, marked ANALYSIS.

## 1. Licence profiles

| Licence | Type | Attribution | Modification | Patent grant | Key condition |
|---|---|---|---|---|---|
| MIT | permissive | preserve notice | allowed, no source duty | none express | keep notice |
| Apache-2.0 | permissive | preserve notice | allowed; NOTICE file | express grant + retaliation | keep notice/NOTICE, state changes |
| GPL-3.0 | strong copyleft | yes | allowed; derivative must stay GPL | express | distribute source of combined work |
| LGPL-3.0 | weak copyleft | yes | library-linking permitted w/ conditions | express | relinkable/proprietary-combination terms |
| AGPL-3.0 | network copyleft | yes | SaaS use = distribution trigger | express | offer source to network users |
| JaVaFo custom | free-of-charge + attribution (PRIMARY: project page) | mention + notify | UNKNOWN (no text retrieved) | none known | UNKNOWN redistribution terms |
| Vega/Swiss-Manager etc. | proprietary/commercial | — | no | — | purchase/terms (PRIMARY vendor: 150€/75€ Swiss-Manager) |

## 2. Implications for pairing-core (ANALYSIS, conservative)

- Python library, MIT (current declaration): maximal compatibility —
  distributable, embeddable (incl. commercial/SaaS), no source duties. Keeping
  MIT is frictionless UNLESS a copyleft engine is linked in-process.
- Apache-2.0 (BBP) content: combinable with MIT output (Apache→MIT one-way
  compatible for combined works with notice preservation); *depending* on BBP
  code (py4swiss-style `cpp/` vendoring) keeps library Apache-compatible but
  adds NOTICE duties. Subprocess use of BBP binary: no licence combination at
  all (separate process) — only redistribution terms of the binary matter.
- GPL-family: in-process dependency would force copyleft onto distributions
  (GPL) or SaaS source duties (AGPL) — AVOID inside the library. Subprocess
  boundary (separate program communicating at arm's length, cf. GPL FAQ
  MereAggregation) is the standard containment. python-chess (GPL-3.0) noted as
  do-not-depend for this reason.
- JaVaFo adapter: subprocess + user-supplied binary + attribution satisfies the
  known terms; BUNDLING/REDISTRIBUTING javafo.jar needs author clearance
  (UNKNOWN → OWNER DECISION REQUIRED; default: never bundle, document
  bring-your-own-binary).
- Patent: Apache-2.0 express grant is a plus for BBP-derived code; MIT has no
  express grant (accepted residual risk, standard for the ecosystem).

## 3. Recommendation input (not decision)

MIT retention is compatible with every strategy except in-process GPL linkage
(which is independently rejected). If BBP code is ever vendored, add NOTICE
handling. Full recommendation in `docs/spec/LICENSE_STRATEGY.md` (Stage 3).
