# License Strategy (STAGE 3 SPEC — PROPOSED, OWNER DECISION REQUIRED to adopt)

## Recommendation: RETAIN MIT for the library; bring-your-own-binary for
external engines; NOTICE hygiene for any Apache-2.0-derived code.

Rationale (evidence: LICENSE_RESEARCH.md + SOURCES.md): MIT keeps maximal
compatibility (distribution, commercial, SaaS) with zero source duties; BBP
(Apache-2.0) is safely usable via subprocess today and vendored later subject
to NOTICE preservation + change statements; JaVaFo's custom free+attribution
terms permit *use* with attribution but redistribution is UNKNOWN — bundling
is therefore FORBIDDEN by default pending written clearance (owner decision);
no GPL-family code in-process, ever (would force copyleft; python-chess
explicitly excluded as a dependency for this reason among others).

## Actions specified (not taken — Stage 1 rules persist)

1. Add `LICENSE` (MIT text) + SPDX `license-expression` in pyproject; keep
   bare-`text` removal as the same change. 2. Add `NOTICE` file if/when BBP
   code vendored. 3. Adapter docs carry per-engine attribution (JaVaFo page
   mention requirement). 4. CI licence check: no GPL in dependency closure;
   SBOM-friendly zero-runtime-deps posture retained. 5. Revisit only if a
   copyleft oracle must be vendored (rejected by default).
