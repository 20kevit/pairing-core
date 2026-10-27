"""Offline negative tests for the FIDE registry validator and navigation."""

from copy import deepcopy

from tools import fide_evidence


def _registries():
    return tuple(deepcopy(registry) for registry in fide_evidence.load_registry())


def _clause(clauses, clause_id):
    return next(record for record in clauses["records"]
                if record["id"] == clause_id)


def test_validator_rejects_disputed_clause_without_competing_readings():
    sources, systems, clauses = _registries()
    rule = _clause(clauses, "F-0112:4.1.1-4.1.2")
    rule["source_modality"]["competing_readings"] = []
    errors = fide_evidence.validate_registry(sources, systems, clauses)
    assert any(rule["id"] in error and "at least two competing" in error
               for error in errors)


def test_validator_rejects_invented_legal_force_category():
    sources, systems, clauses = _registries()
    rule = _clause(clauses, "F-0101:6")
    rule["source_modality"]["force_category"] = "mandatory"
    errors = fide_evidence.validate_registry(sources, systems, clauses)
    assert any(rule["id"] in error and "do not invent a legal force category" in error
               for error in errors)


def test_validator_rejects_verbatim_cue_for_unavailable_source_text():
    sources, systems, clauses = _registries()
    rule = _clause(clauses, "F-0106:interim-PAB")
    rule["source_modality"]["reading_status"] = "source_text_unavailable"
    rule["source_modality"]["verbatim_cue"] = "shall"
    errors = fide_evidence.validate_registry(sources, systems, clauses)
    assert any(rule["id"] in error and "unverified/unavailable source" in error
               for error in errors)


def test_validator_requires_explicit_test_scope_even_without_named_tests():
    sources, systems, clauses = _registries()
    rule = _clause(clauses, "F-0103:1.5")
    rule["test_scope"] = "  "
    errors = fide_evidence.validate_registry(sources, systems, clauses)
    assert any(rule["id"] in error and "explicit test scope/boundary" in error
               for error in errors)


def test_validator_rejects_original_checksum_when_bytes_were_not_retained():
    sources, systems, clauses = _registries()
    retrieval = sources["records"][1]["retrievals"][0]
    retrieval["sha256"] = "a" * 64
    errors = fide_evidence.validate_registry(sources, systems, clauses)
    assert any("original-byte checksum cannot be claimed" in error
               for error in errors)


def test_validator_requires_source_identity_and_revision_evidence():
    sources, systems, clauses = _registries()
    sources["records"][0]["revision"] = "  "
    errors = fide_evidence.validate_registry(sources, systems, clauses)
    assert any("revision must explicitly state evidence or uncertainty" in error
               for error in errors)


def test_nonimplemented_records_are_all_rendered_in_closure_queue():
    sources, systems, clauses = _registries()
    outputs = fide_evidence._render(sources, systems, clauses)
    queue = outputs["CLAUSE_CLOSURE_QUEUE.md"]
    expected = [
        record["id"] for record in clauses["records"]
        if record["implementation_status"] != "implemented"
    ]
    rendered_rows = [line for line in queue.splitlines()
                     if line.startswith("| [F-")]
    assert len(expected) == len(rendered_rows)
    assert all(f"[{clause_id}]" in queue for clause_id in expected)
    assert any(record["implementation_status"] == "caller_supplied"
               for record in clauses["records"])
    assert any(record["implementation_status"] == "out_of_scope"
               for record in clauses["records"])


def test_render_count_validator_rejects_missing_out_of_scope_clause():
    sources, systems, clauses = _registries()
    outputs = fide_evidence._render(sources, systems, clauses)
    target = next(record["id"] for record in clauses["records"]
                  if record["implementation_status"] == "out_of_scope")
    outputs["CLAUSE_CLOSURE_QUEUE.md"] = "\\n".join(
        line for line in outputs["CLAUSE_CLOSURE_QUEUE.md"].splitlines()
        if not (line.startswith("| [F-") and f"[{target}]" in line)
    )
    errors = fide_evidence.validate_render_counts(outputs, sources, systems, clauses)
    assert any("non-implemented records" in error for error in errors)


def test_validator_reports_broken_local_navigation_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(fide_evidence, "ROOT", tmp_path)
    page = tmp_path / "docs" / "rules" / "fide" / "README.md"
    page.parent.mkdir(parents=True)
    page.write_text("[missing](missing-clause.md)\n", encoding="utf-8")
    errors = fide_evidence.validate_links([page])
    assert errors == [
        "docs/rules/fide/README.md: broken local link: missing-clause.md"
    ]
