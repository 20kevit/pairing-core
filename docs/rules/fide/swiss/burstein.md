# Burstein System — Structured Research Note

## Identity
- System: Burstein System, C.04.4.2. Design goal: fairness-by-opposition-strength —
  equal scorers should have met equivalent opposition (NOTE, PRIMARY excerpt
  C040402Till2026).
- Rulesets: till-2026 [F-0111] → 2026 recodified [F-0110] (Council 28/10/2025,
  effective 01/02/2026; "recodified, was generic" per chapter record).

## Authoritative sources
- [F-0110] C040402202602 (CURRENT); [F-0111] C040402Till2026 (SUPERSEDED);
  [F-0201] enacting bundle; 2020 SPP minutes (Burstein rewording — prior wave);
  [F-0101]/[F-0103] common rules.

## Inputs
- Base Swiss inputs + Buchholz / Sonneborn-Berger computed opposition metrics
  (tie-break regs 2026 context; DEFINITIONS).

## Definitions
- Ranking order for pairing = Buchholz then Sonneborn-Berger (MANDATORY RULE,
  PRIMARY: 2020 SPP minutes + 2025 Council text).
- Median-scoregroup cracking §§2.6.1/2.6.2: crack neighbour pairing and re-treat
  players as floaters when floater counts unbalance (ALGORITHM STEP, PRIMARY).
- A–E article structure mirroring Dutch (NOTE).
- Default acceleration semantics differ from Dutch: without XXA codes Burstein
  defaults to its own acceleration system; Dutch defaults to none (MANDATORY RULE
  for engine behavior, PRIMARY: BBP README).

## Pairing process / Ordering
- Buchholz-ordered groups; median-centred float handling (both directions)
  (ALGORITHM STEP, frame).
- Score ordering + colour treatment + opponent selection: full 2026 text pending.

## Colour / Float / Bye / Exchange / Special cases
- Colours: E-rules consistent with Dutch+Dubov (NOTE, frame).
- PAB must allow completion (MANDATORY RULE, frame — C.04.1 art. context).
- Official examples: in full text (G-01).

## Historical implementation differences (NOTE, PRIMARY engine self-report)
- BBP's Burstein is self-declared "flawed… not endorsed" (BBP README + arXiv-adjacent
  paper). It must NEVER serve as a conformance oracle for Burstein.
- Vega implements Burstein internally (Dubov Turin-2006 era rules for its Dubov;
  Burstein vintage TBD — vendor PRIMARY, version UNVERIFIED).

## Ambiguities
- A-B1: full recodified-2026 text (article bodies pending).
- A-B2: median-cracking trigger thresholds (§2.6.1 vs 2.6.2 boundary conditions).

## Implementation assessment
- Needs Buchholz-ordered bracket model + median-cracking; distinct from Dutch engine.
- Status: RESEARCH CONTINUES.
