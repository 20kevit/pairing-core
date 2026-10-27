# FIDE source and clause evidence registry

This directory provides a versioned, offline-checkable index of FIDE sources,
project-authored requirement paraphrases, implementation references, tests,
and visible evidence gaps. **It is not a FIDE compliance report or approval.**
Snapshot date: **2026-10-27**. Pairing-Core produces and validates pairings;
tournament management, ratings, standings, tie-break calculations, and FIDE
Tournament Handler Program evaluation are outside its product boundary.

## Start here

- [Coverage dashboard](COVERAGE_DASHBOARD.md) — source, rule, system, and
evidence-pointer counts; counts are not conformance.
- [Clause index](CLAUSE_INDEX.md) — stable source-edition IDs, section anchors,
project paraphrases, implementation status, and separate verification status.
- [Rule/source/code/test matrix](RULE_SOURCE_MATRIX.md) — clause-level links to
inspected symbols and named tests, including unmapped and disputed clauses.
- [System coverage index](SYSTEM_COVERAGE.md) and
[per-system views](system-pages/) — navigable views of pairing systems and
product-boundary topics.
- [Source index](SOURCE_INDEX.md) — authority, edition dates, current/superseded
status, retrievals, and source relationships.
- [Source manifest](SOURCE_MANIFEST.md) — retrieval evidence, checksum
availability, rights posture, and historical retrieval limitations.
- Machine-readable canonical registries:
  [`registry/sources.json`](registry/sources.json),
  [`registry/systems.json`](registry/systems.json), and
  [`registry/clauses.json`](registry/clauses.json).
- [Audit gap register](../../audit/GAP_REGISTER.md) and
  [completion standard](../../audit/COMPLETION_STANDARD.md) remain authoritative
  for readiness and acceptance verdicts.

## Scope and interpretation

The source registry includes current applicable FIDE Swiss rules (C.04), the
Dutch, Dubov, Burstein, Lim, Double Swiss, Team Swiss, Baku, Berger Annexes 1
and 2, and dated Olympiad pairing material, plus sources relevant to product
boundaries and historical context. The current Annex 2 Varma restricted-draw
procedure is caller/arbiter work, not a Berger opponent schedule. The parent
C.05 general-regulations pointer remains unresolved because its current page
fetch returned only generic Handbook navigation (`F-0502`). Current retrieved
C.02.03 Article 7 and C.02.04 THP-list sources are included because they define
program-level evaluation context; they do **not** turn this library into a
Tournament Handler Program.

C.04.4.2 Burstein Index calculations are not implemented here. Pairing-Core
accepts caller-supplied values with provenance requirements; C.07 Buchholz or
Sonneborn-Berger values are not treated as equivalent to C.04 values without
verified semantic evidence. See the
[Burstein integration boundary](../../spec/TIEBREAK_ARCHITECTURE.md#2-current-burstein-input-contract).
The current C.02.04 list retrieved for this audit does not show Pairing-Core;
that statement is bounded to that retrieved list and is not proof that no
separate or later FIDE decision exists.

The `classification` field describes the source statement or boundary. In this
schema, `normative` means “a paraphrase of a cited source provision”; it does
not by itself classify the provision's mandatory force. This first-pass index
does not yet classify the force of every source clause individually; where the
record itself is an official table or list, official example, recommendation,
product boundary, historical item, or withdrawn claim, that is marked separately. No official
interpretation is invented: repository readings are marked disputed, while
implementation strategies, product policy, and unresolved work are stated in
repository status/limitations/closure notes, not passed off as FIDE text. This
force-classification gap remains part of the open clause-inventory work.

Each clause has two independent evidence axes:

- **Implementation status** describes the repository mapping (`implemented`,
  `partial`, `caller_supplied`, `out_of_scope`, `unmapped`, `disputed`,
  `historical_compat`, or `withdrawn`). A code link does not show that every
  required behavior is implemented.
- **Independent-verification status** distinguishes no independent evidence
  from regressions of official worked examples. Repository tests, including
  official-example tests, are not independent evaluation or conformity proof.

`unmapped`, `disputed`, and out-of-scope clauses are intentionally retained and
carry closure actions. Superseded editions are indexed, but historical clause
records are explicitly partial; their presence is not a claim of exhaustive
historical coverage.

## Provenance and redistribution

The structured records identify the source authority, document edition and
effective dates where available, official URL, status basis, retrieval date and
method, source-file checksum status, and supersession relationships. The
2026-10-27 parsed-page retrieval interface did not expose original response
bytes, so no raw-source hashes are claimed for those pages. Two historical
hashes from a prior wave remain labeled not reverified, with no local originals
retained.

No open reuse licence or written permission to redistribute FIDE material
was established in this audit. A lookup of `https://handbook.fide.com/legal`
returned 404; that failed lookup establishes neither permission nor a
prohibition, and is recorded as source `F-0801`. Public availability is not permission. The
registry adds no full FIDE source text, OCR, translation, or original source
file; clause descriptions are project-authored paraphrases. A small set of
tests retains project-authored structured transcriptions or derived values from
cited numerical examples, including the published Berger schedules for N=3–16.
Those fixtures are labeled with their source, content type, and unresolved
redistribution rights; their presence is not a permission finding. The earlier
retrieval ledger is preserved in [`history/`](history/) as historical evidence,
not as a current legal conclusion. Do not add local originals unless the
permission record, lawful scope, and verified checksum are recorded.

## Editing and offline validation

The JSON registries are the maintained source of truth; generated Markdown
views must not be hand-edited. For each rule change:

1. Use a stable `Source-ID:section` clause ID and exact section reference.
2. Write a concise repository-authored paraphrase and use the schema's
   source-record classes (`normative`, `official_example`, `official_table`,
   `recommendation`, `official_list`, boundary, historical, or claim-status labels). `normative`
   alone does not mean “mandatory”: mark force distinctions only when the
   inspected edition supports them, and otherwise leave that classification
   gap explicit. Do not present repository interpretation as an official one.
3. Inspect every implementation symbol and test named in the record. Use
   `path::module_level_symbol`; the validator checks the file and symbol.
4. Keep implementation and independent-verification statuses separate. Add a
   closure action for unmapped, disputed, or out-of-scope items.
5. Record source edition, retrieval and rights information. Never fabricate a
   source checksum or treat parsed HTML/Markdown as the original bytes.
6. Regenerate and check the views offline:

   ```bash
   python tools/fide_evidence.py build
   python tools/fide_evidence.py check
   python tools/validate_sources.py
   python -m pytest tests/test_source_registry.py -q
   ```

The validator checks registry IDs/statuses and supersession links, source
metadata and checksum/artifact consistency, local redistribution policy,
implementation/test references, example-fixture provenance, internal paths and
anchors, registry hashes, and generated-view counts. It performs no network
requests and creates no conformance verdict.

## Preserved research history

The earlier research wave's source index, source manifest, matrix, system
catalog, and coverage table are retained under [`history/`](history/) without
silently overwriting those findings. Older narrative, extracted, and evidence
notes remain available for audit context; where they are not generated from the
current registry, treat them as dated research snapshots and use the links
above for current source status and clause coverage.
