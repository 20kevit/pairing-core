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
- [Closure and boundary queue](CLAUSE_CLOSURE_QUEUE.md) — every partial,
caller-supplied, out-of-scope, disputed, historical, withdrawn, or unmapped clause
with its source cue, named-test scope, and explicit next action.
- [Rights and fixture inventory](RIGHTS_AND_FIXTURE_INVENTORY.md) — source-copy
and source-derived data dispositions, fixture consumers, unresolved rights, and
the recorded project-owner disposition.
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

The source registry includes the 2026 FIDE Swiss pages (C.04), the Dutch,
Dubov, Burstein, Lim, Double Swiss, Team Swiss and Baku systems, Berger and
Varma annex pages, and dated 2022 Olympiad pairing material, plus sources
relevant to product boundaries and historical context. The correct C.05 parent
page (`C05GeneralRegulations`) and its linked `Competition_Rules.pdf` were
inspected as parsed content. The PDF states approval by the 1986 General
Assembly and amendments through 2018 but gives no effective date; revision,
current applicability, and supersession remain unknown (`F-0502`). Berger is
implemented as a fixed schedule; Annex 2's restricted Varma draw remains
caller/arbiter work. Current C.02.03 Article 7 and C.02.04 THP-list sources
provide program-level evaluation context; they do **not** turn this library into
a Tournament Handler Program.

C.04.4.2 Burstein Index calculations are not implemented here. Pairing-Core
accepts caller-supplied values with provenance requirements; C.07 Buchholz or
Sonneborn-Berger values are not treated as equivalent to C.04 values without
verified semantic evidence. See the
[Burstein integration boundary](../../spec/TIEBREAK_ARCHITECTURE.md#2-current-burstein-input-contract).
The current C.02.04 list retrieved for this audit does not show Pairing-Core;
that statement is bounded to that retrieved list and is not proof that no
separate or later FIDE decision exists.

The `classification` field describes the record/source type; `normative` means
a project paraphrase of a cited provision and does **not** classify its legal
force. Each clause also records short source wording cues and qualifiers,
a `reading_status`, a project note, and—where the source is ambiguous—competing
readings. These are evidence notes, not legal-force categories. Clauses whose
exact wording was not reverified say so; source retrieval failure is not treated
as proof of nonexistence. The Lim Article 4.1 wording/example conflict remains
`disputed` with both readings and a closure action. The Double/Team priority
reading is labeled as the repository's textual reading, not an official
interpretation. No FIDE force category or interpretation is invented.

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

The structured records identify the authority, source title/URL, revision
label, approval/effective dates where stated, identity basis, status basis,
retrieval date/method/content representation, original-byte retention and
checksum status, and supersession basis/relationships. The 2026-10-27 parsed
page interface did not expose original response bytes, so current source-byte
hashes are not claimed. Prior-wave digests are kept in separate historical
checksum fields and explicitly marked not reverified against retained files.
The interim-2025 Dutch PDF (F-0106) is now identified through the correct official
Council-document URL and parsed in full; its approval line is the placeholder
`dd/mm/yyyy`, and its original bytes remain unavailable. The failed Handbook
page fetch and the earlier PDF-path 404 are retained as distinct retrieval
failures, not evidence of nonexistence.

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
2. Write a concise repository-authored paraphrase and a bounded source modality:
   short verbatim cue, qualifiers, reading status, project note, and competing
   readings/resolution basis when applicable. Do not add a legal-force category
   or present repository interpretation as an official one.
3. Inspect every implementation symbol and test named in the record. Use
   `path::module_level_symbol`; the validator checks the file and symbol.
4. Keep implementation and independent-verification statuses separate. Give
   every clause a named-test scope/boundary and an explicit next action; keep
   every non-implemented record in the generated closure queue.
5. Record source identity/revision, retrieval and rights evidence. Never
   fabricate a source checksum or treat parsed HTML/Markdown as original bytes.
6. Regenerate and check the views offline:

   ```bash
   python tools/fide_evidence.py build
   python tools/fide_evidence.py check
   python tools/validate_sources.py
   python -m pytest tests/test_source_registry.py -q
   ```

The validator checks registry IDs/statuses and reciprocal supersession links;
source identity/revision/retrieval/content/checksum metadata; rights policy;
per-clause source-modality alternatives and test scope; code/test/input
references; exact registration of every official-example fixture and its
unresolved-rights label; local paths/anchors; registry hashes; and generated
view counts. It uses no network and creates no conformity verdict. A passing
validator verifies registry structure and navigation, not the factual accuracy
of every paraphrase or source reading.

## Preserved research history

The earlier research wave's source index, source manifest, matrix, system
catalog, and coverage table are retained under [`history/`](history/) without
silently overwriting those findings. Older narrative, extracted, and evidence
notes remain available for audit context; where they are not generated from the
current registry, treat them as dated research snapshots and use the links
above for current source status and clause coverage.
