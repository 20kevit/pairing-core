#!/usr/bin/env python3
"""Build and validate the offline FIDE source/clause evidence views.

The JSON registry under docs/rules/fide/registry/ is authoritative for this
system. This tool uses only the Python standard library; it never fetches
sources. Run `python tools/fide_evidence.py build` after editing the registry,
and `python tools/fide_evidence.py check` in CI.

Documentation links and tests are evidence pointers, not a conformity verdict.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIDE = ROOT / "docs" / "rules" / "fide"
REGISTRY = FIDE / "registry"
SOURCES_PATH = REGISTRY / "sources.json"
SYSTEMS_PATH = REGISTRY / "systems.json"
CLAUSES_PATH = REGISTRY / "clauses.json"

SOURCE_STATUSES = {
    "current", "superseded", "historical", "unknown",
    "historical_snapshot", "current_list_as_retrieved",
}
SOURCE_CLASSES = {"normative", "official_context", "official_list", "normative_boundary", "rights_search_attempt"}
IMPLEMENTATION_STATUSES = {
    "implemented", "partial", "caller_supplied", "out_of_scope",
    "not_implemented", "unmapped", "disputed", "historical_compat",
    "withdrawn",
}
INDEPENDENT_STATUSES = {
    "none", "official_worked_example_only", "external_oracle",
    "independent_property", "not_applicable", "disputed",
}
CLASSIFICATIONS = {
    "normative", "official_example", "official_table", "product_boundary", "boundary",
    "historical", "recommendation", "official_list", "withdrawn_claim",
    "unverified_source_claim",
}


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON registry {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"{path.relative_to(ROOT)}: expected object with schema_version 1")
    if not isinstance(data.get("records"), list):
        raise ValueError(f"{path.relative_to(ROOT)}: records must be a list")
    if not _iso_date(data.get("as_of")) or data.get("as_of") is None:
        raise ValueError(f"{path.relative_to(ROOT)}: as_of must be a real YYYY-MM-DD date")
    if any(not isinstance(record, dict) for record in data["records"]):
        raise ValueError(f"{path.relative_to(ROOT)}: every record must be a JSON object")
    return data


def load_registry() -> tuple[dict, dict, dict]:
    return _read_json(SOURCES_PATH), _read_json(SYSTEMS_PATH), _read_json(CLAUSES_PATH)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iso_date(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _ast_symbols(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise ValueError(f"cannot parse {path.relative_to(ROOT)}: {exc}") from exc
    found: set[str] = set()

    def names(target: ast.AST) -> None:
        if isinstance(target, ast.Name):
            found.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                names(item)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names(target)
        elif isinstance(node, ast.AnnAssign):
            names(node.target)
    return found


def _check_symbol(ref: str, *, test: bool = False) -> str | None:
    if not isinstance(ref, str) or ref.count("::") != 1:
        return f"invalid reference {ref!r}; expected path::symbol"
    rel, symbol = ref.split("::", 1)
    path = (ROOT / rel).resolve()
    if ROOT not in path.parents:
        return f"referenced file escapes repository: {rel}"
    if not path.is_file():
        return f"missing referenced file {rel}"
    if path.suffix != ".py":
        return f"referenced symbol file must be Python source: {rel}"
    if not symbol or "." in symbol:
        return f"invalid symbol in {ref!r}; use a module-level symbol"
    if test:
        if not path.is_relative_to(ROOT / "tests") or not symbol.startswith("test_"):
            return f"test reference must name tests/...::test_*; got {ref}"
    elif not path.is_relative_to(ROOT / "src"):
        return f"implementation reference must name src/...; got {ref}"
    try:
        symbols = _ast_symbols(path)
    except ValueError as exc:
        return str(exc)
    if symbol not in symbols:
        return f"symbol {symbol!r} not found in {rel}"
    return None


def validate_registry(sources: dict, systems: dict, clauses: dict) -> list[str]:
    errors: list[str] = []
    source_records = sources["records"]
    system_records = systems["records"]
    clause_records = clauses["records"]
    source_by_id: dict[str, dict] = {}
    system_by_id: dict[str, dict] = {}
    for records, destination, label in (
        (source_records, source_by_id, "source"),
        (system_records, system_by_id, "system"),
    ):
        for record in records:
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id:
                errors.append(f"{label} record has a missing or non-string ID")
            elif record_id in destination:
                errors.append(f"duplicate {label} ID {record_id}")
            else:
                destination[record_id] = record
    if sources.get("as_of") != systems.get("as_of") or sources.get("as_of") != clauses.get("as_of"):
        errors.append("source, system, and clause registries must share the same as_of date")

    snapshot_date = sources.get("as_of")
    if not _iso_date(snapshot_date) or snapshot_date is None:
        errors.append("source registry as_of must be a real YYYY-MM-DD date")

    for source in source_records:
        sid = source.get("id", "<missing-id>")
        if not re.fullmatch(r"F-[0-9]{4}", str(sid)):
            errors.append(f"{sid}: source ID must use the stable F-0000 form")
        for field in ("title", "authority", "source_class", "status", "status_basis", "rights", "retrievals"):
            if not source.get(field):
                errors.append(f"{sid}: missing required source metadata {field}")
        source_class = source.get("source_class")
        if not isinstance(source_class, str) or source_class not in SOURCE_CLASSES:
            errors.append(f"{sid}: unknown source class {source_class!r}")
        source_status = source.get("status")
        if not isinstance(source_status, str) or source_status not in SOURCE_STATUSES:
            errors.append(f"{sid}: unknown source status {source_status!r}")
        url = source.get("url")
        if url is not None:
            if not isinstance(url, str):
                errors.append(f"{sid}: official URL must be a string or null")
            else:
                parsed_url = urlsplit(url)
                if parsed_url.scheme != "https" or not parsed_url.netloc or parsed_url.username or parsed_url.password:
                    errors.append(f"{sid}: official URL must be a credential-free https URL")
        for date_field in ("approval_date", "effective_from", "effective_to"):
            if not _iso_date(source.get(date_field)):
                errors.append(f"{sid}: {date_field} must be a real YYYY-MM-DD date or null")
        if source.get("status") in ("current", "current_list_as_retrieved") and not url:
            errors.append(f"{sid}: current source must have an official URL")
        if source.get("status") == "superseded" and not source.get("superseded_by"):
            errors.append(f"{sid}: superseded edition must identify its successor")
        effective_to = source.get("effective_to")
        if source.get("status") in ("current", "current_list_as_retrieved") and isinstance(effective_to, str) and snapshot_date and effective_to < snapshot_date:
            errors.append(f"{sid}: current source ended before the registry snapshot date")
        for relation in ("supersedes", "superseded_by"):
            values = source.get(relation)
            if not isinstance(values, list):
                errors.append(f"{sid}: {relation} must be a list")
                continue
            for target in values:
                if not isinstance(target, str):
                    errors.append(f"{sid}: {relation} targets must be source ID strings")
                elif target not in source_by_id:
                    errors.append(f"{sid}: dangling {relation} target {target}")

        rights = source.get("rights")
        if not isinstance(rights, dict):
            errors.append(f"{sid}: rights metadata must be an object")
            rights = {}
        for field in ("rights_holder", "license_status", "redistribution", "note"):
            if not isinstance(rights.get(field), str) or not rights[field].strip():
                errors.append(f"{sid}: rights.{field} must be a non-empty string")
        permission = rights.get("permission_obtained")
        if not isinstance(permission, bool):
            errors.append(f"{sid}: permission_obtained must be an explicit boolean")
        permission_record = rights.get("permission_record")
        if permission is True and (not isinstance(permission_record, str) or not permission_record.strip()):
            errors.append(f"{sid}: recorded redistribution permission requires a permission_record")
        local_original = rights.get("local_original")
        local_digest = rights.get("local_original_sha256")
        if local_original is not None and not isinstance(local_original, str):
            errors.append(f"{sid}: local_original must be a repository-relative path or null")
            local_original = None
        if permission is not True and local_original is not None:
            errors.append(f"{sid}: a local original requires recorded redistribution permission")
        if local_original is None and local_digest is not None:
            errors.append(f"{sid}: local-original SHA-256 is present without a local original")
        if local_original is not None:
            if not isinstance(local_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", local_digest):
                errors.append(f"{sid}: an authorized local original requires a SHA-256 digest")
            else:
                original_path = (ROOT / local_original).resolve()
                if ROOT not in original_path.parents or not original_path.is_file():
                    errors.append(f"{sid}: local original path is absent or escapes repository")
                elif sha256(original_path) != local_digest:
                    errors.append(f"{sid}: local-original SHA-256 mismatch")
        distribution = rights.get("redistribution", "")
        if permission is not True and local_original is None and not str(distribution).startswith("link_only_no_full_source_text_or_original_file_committed"):
            errors.append(f"{sid}: a source without recorded permission must use link-only redistribution policy")

        retrievals = source.get("retrievals")
        if not isinstance(retrievals, list) or not retrievals:
            errors.append(f"{sid}: at least one retrieval record is required")
            continue
        for index, retrieval in enumerate(retrievals, 1):
            label = f"{sid} retrieval {index}"
            if not isinstance(retrieval, dict):
                errors.append(f"{label}: retrieval record must be an object")
                continue
            retrieved_on = retrieval.get("retrieved_on")
            retrieval_day = retrieved_on
            if _iso_date(retrieved_on) and retrieved_on is not None:
                if retrieval.get("retrieval_date_precision") not in (None, "exact"):
                    errors.append(f"{label}: exact date must not carry an approximate precision label")
            elif isinstance(retrieved_on, str):
                match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})_or_earlier_as_recorded", retrieved_on)
                if not match or not _iso_date(match.group(1)) or retrieval.get("retrieval_date_precision") != "on_or_before":
                    errors.append(f"{label}: retrieved_on must be a real date or an explicitly labeled historical bound")
                    retrieval_day = None
                else:
                    retrieval_day = match.group(1)
            else:
                errors.append(f"{label}: retrieved_on must be a real date or an explicitly labeled historical bound")
                retrieval_day = None
            if retrieval_day and snapshot_date and retrieval_day > snapshot_date:
                errors.append(f"{label}: retrieval date is after the registry snapshot")
            if not isinstance(retrieval.get("method"), str) or not retrieval["method"].strip():
                errors.append(f"{label}: retrieval method is required")
            raw_bytes_retained = retrieval.get("raw_bytes_retained")
            if not isinstance(raw_bytes_retained, bool):
                errors.append(f"{label}: raw_bytes_retained must be an explicit boolean")
            digest = retrieval.get("sha256")
            artifact = retrieval.get("artifact_path")
            if digest is None:
                if not isinstance(retrieval.get("sha256_scope"), str) or not retrieval["sha256_scope"].strip():
                    errors.append(f"{label}: missing transparent reason for unavailable checksum")
            elif not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                errors.append(f"{label}: invalid SHA-256 digest")
            elif not artifact and not retrieval.get("sha256_scope"):
                errors.append(f"{label}: a digest without a retained artifact needs explicit historical/reverification scope")
            if raw_bytes_retained and (not artifact or not digest):
                errors.append(f"{label}: retained raw bytes require an artifact path and SHA-256")
            if artifact:
                if not isinstance(artifact, str):
                    errors.append(f"{label}: artifact_path must be a repository-relative path or null")
                    continue
                artifact_path = (ROOT / artifact).resolve()
                if ROOT not in artifact_path.parents or not artifact_path.is_file():
                    errors.append(f"{label}: artifact path is absent or escapes repository")
                elif digest and isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) and sha256(artifact_path) != digest:
                    errors.append(f"{label}: artifact SHA-256 mismatch")

    # Check that source supersession links are reciprocal; dates/status remain separate.
    for source in source_records:
        sid = source.get("id")
        supersedes = source.get("supersedes")
        superseded_by = source.get("superseded_by")
        if isinstance(supersedes, list):
            for target in supersedes:
                if isinstance(target, str) and target in source_by_id:
                    reverse = source_by_id[target].get("superseded_by")
                    if isinstance(reverse, list) and sid not in reverse:
                        errors.append(f"{sid}: supersedes {target}, but the reverse link is missing")
        if isinstance(superseded_by, list):
            for target in superseded_by:
                if isinstance(target, str) and target in source_by_id:
                    reverse = source_by_id[target].get("supersedes")
                    if isinstance(reverse, list) and sid not in reverse:
                        errors.append(f"{sid}: superseded_by {target}, but the reverse link is missing")

    clause_ids: set[str] = set()
    clause_anchors: set[str] = set()
    for rule in clause_records:
        rid = rule.get("id", "<missing-clause-id>")
        if not isinstance(rid, str) or not rid:
            errors.append("clause record has a missing or non-string ID")
            continue
        if rid in clause_ids:
            errors.append(f"duplicate clause ID {rid}")
        clause_ids.add(rid)
        anchor = rule.get("anchor")
        if not isinstance(anchor, str) or not re.fullmatch(r"[a-z0-9-]+", anchor):
            errors.append(f"{rid}: invalid stable anchor {anchor!r}")
        else:
            if anchor in clause_anchors:
                errors.append(f"{rid}: duplicate anchor {anchor}")
            clause_anchors.add(anchor)
        source_id = rule.get("source_id")
        implementation_status = rule.get("implementation_status")
        classification = rule.get("classification")
        verification_status = rule.get("independent_verification_status")
        if not isinstance(source_id, str) or (source_id not in source_by_id and implementation_status != "withdrawn"):
            errors.append(f"{rid}: unknown source ID {source_id!r}")
        if not isinstance(rule.get("section"), str) or not rule["section"] or not isinstance(rule.get("requirement_paraphrase"), str) or not rule["requirement_paraphrase"]:
            errors.append(f"{rid}: exact section and original paraphrase are required")
        if not isinstance(implementation_status, str) or implementation_status not in IMPLEMENTATION_STATUSES:
            errors.append(f"{rid}: invalid implementation status {implementation_status!r}")
        if not isinstance(classification, str) or classification not in CLASSIFICATIONS:
            errors.append(f"{rid}: invalid source/record classification {classification!r}")
        if not isinstance(verification_status, str) or verification_status not in INDEPENDENT_STATUSES:
            errors.append(f"{rid}: invalid independent-verification status {verification_status!r}")
        rule_systems = rule.get("systems", [])
        if not isinstance(rule_systems, list):
            errors.append(f"{rid}: systems must be a list")
            rule_systems = []
        for sid in rule_systems:
            if not isinstance(sid, str) or sid not in system_by_id:
                errors.append(f"{rid}: unknown system ID {sid!r}")
        if not isinstance(rule.get("closure_action"), str) or not rule["closure_action"].strip():
            errors.append(f"{rid}: a closure action is required")
        if isinstance(source_id, str) and not rid.startswith(source_id + ":"):
            errors.append(f"{rid}: stable clause ID must begin with {source_id}:")
        impl_refs = rule.get("implementation_refs", [])
        test_refs = rule.get("test_refs", [])
        if not isinstance(impl_refs, list) or not isinstance(test_refs, list):
            errors.append(f"{rid}: code/test references must be lists")
            continue
        if implementation_status in ("implemented", "partial", "caller_supplied") and not impl_refs:
            errors.append(f"{rid}: mapped implementation status requires an inspected code reference")
        if implementation_status == "unmapped" and (impl_refs or test_refs):
            errors.append(f"{rid}: unmapped clause cannot claim code/test mappings")
        if implementation_status in ("out_of_scope", "withdrawn") and impl_refs:
            errors.append(f"{rid}: out-of-scope/withdrawn clause cannot claim implementation")
        if rule.get("test_evidence_status") != ("linked_repository_tests" if test_refs else "no_named_repository_test"):
            errors.append(f"{rid}: test evidence status disagrees with named test references")
        for ref in impl_refs:
            problem = _check_symbol(ref)
            if problem:
                errors.append(f"{rid}: {problem}")
        for ref in test_refs:
            problem = _check_symbol(ref, test=True)
            if problem:
                errors.append(f"{rid}: {problem}")
        fixture = rule.get("official_example_fixture")
        if verification_status == "official_worked_example_only" and (not fixture or not test_refs):
            errors.append(f"{rid}: official worked-example status needs a fixture and named test")
        if fixture:
            if not isinstance(fixture, str):
                errors.append(f"{rid}: official-example fixture must be a repository-relative path")
                continue
            fixture_path = (ROOT / fixture).resolve()
            if ROOT not in fixture_path.parents or not fixture_path.is_file():
                errors.append(f"{rid}: missing or escaping official-example fixture {fixture}")
            else:
                try:
                    fixture_data = json.loads(fixture_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"{rid}: invalid example fixture JSON: {exc}")
                else:
                    if not isinstance(fixture_data, dict):
                        errors.append(f"{rid}: example fixture root must be a JSON object")
                        continue
                    source_value = fixture_data.get("source")
                    source_rec = source_by_id.get(source_id, {})
                    allowed = {value for value in (source_id, source_rec.get("url")) if isinstance(value, str)}
                    if source_value not in allowed:
                        errors.append(f"{rid}: fixture source {source_value!r} does not match source registry")
                    if fixture_data.get("provenance") not in ("official-example", "official-example-with-derived-truncation"):
                        errors.append(f"{rid}: fixture is not marked as an official worked example")
                    content_type = fixture_data.get("content_type")
                    if not isinstance(content_type, str) or "project_authored" not in content_type:
                        errors.append(f"{rid}: fixture must label transcription/derivation as project-authored")
                    rights_note = fixture_data.get("redistribution_rights")
                    if not isinstance(rights_note, str) or "permission" not in rights_note.lower() or "not established" not in rights_note.lower():
                        errors.append(f"{rid}: fixture must disclose unresolved redistribution rights")

    for system in system_records:
        sid = system.get("id", "<missing-system-id>")
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid):
            errors.append(f"{sid}: invalid stable system ID")
        for field in ("name", "kind", "status", "scope_note"):
            if not isinstance(system.get(field), str) or not system[field].strip():
                errors.append(f"{sid}: system view requires non-empty {field}")
        source_ids = system.get("source_ids", [])
        entry_points = system.get("entry_points", [])
        limitations = system.get("limitations", [])
        if not isinstance(source_ids, list) or not isinstance(entry_points, list) or not isinstance(limitations, list):
            errors.append(f"{sid}: source_ids, entry_points and limitations must be lists")
            continue
        for source_id in source_ids:
            if not isinstance(source_id, str) or source_id not in source_by_id:
                errors.append(f"{sid}: unknown source ID {source_id!r}")
        for ref in entry_points:
            problem = _check_symbol(ref)
            if problem:
                errors.append(f"{sid}: {problem}")
        for limit in limitations:
            if not isinstance(limit, str) or not limit.strip():
                errors.append(f"{sid}: empty or invalid limitation")

    return errors


def _md(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip() if text is not None else "—"


def _link(label: str, target: str) -> str:
    return f"[{label}]({target})"


def _rel(from_rel: str, to_rel: str) -> str:
    return Path(to_rel).as_posix() if from_rel == "" else __import__("posixpath").relpath(to_rel, str(PurePosixPath(from_rel).parent))


@lru_cache(maxsize=None)
def _symbol_lineno(ref: str) -> int | None:
    rel, symbol = ref.split("::", 1)
    path = ROOT / rel
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return None

    def contains_name(target: ast.AST, wanted: str) -> bool:
        if isinstance(target, ast.Name):
            return target.id == wanted
        if isinstance(target, (ast.Tuple, ast.List)):
            return any(contains_name(item, wanted) for item in target.elts)
        return False

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
            return node.lineno
        if isinstance(node, ast.Assign) and any(contains_name(target, symbol) for target in node.targets):
            return node.lineno
        if isinstance(node, ast.AnnAssign) and contains_name(node.target, symbol):
            return node.lineno
    return None


def _reference_links(refs: list[str], from_rel: str) -> str:
    if not refs:
        return "—"
    links = []
    for ref in refs:
        rel, _symbol = ref.split("::", 1)
        line = _symbol_lineno(ref)
        target = f"../../../{rel}" + (f"#L{line}" if line else "")
        links.append(f"[`{ref}`]({_rel(from_rel, target)})")
    return ", ".join(links)


def _source_by_id(sources: dict) -> dict[str, dict]:
    return {item["id"]: item for item in sources["records"]}


def _system_by_id(systems: dict) -> dict[str, dict]:
    return {item["id"]: item for item in systems["records"]}


def _rule_status(rule: dict) -> str:
    return rule["implementation_status"].replace("_", " ")


def _checksum_display(retrieval: dict) -> str:
    digest = retrieval.get("sha256")
    scope = retrieval.get("sha256_scope")
    if digest:
        if not retrieval.get("artifact_path") and scope:
            return f"{digest} — not reverified against a retained artifact: {scope}"
        return digest
    return scope or "Unavailable; no reason recorded"


def _source_page(source: dict, rules: list[dict], source_path: str) -> str:
    rows = ["# " + source["title"], "", f"**Source ID:** `{source['id']}`<br>",
            f"**Authority/class:** {source.get('authority','—')} / `{source.get('source_class','—')}`<br>",
            f"**Approval/effective:** {source.get('approval_date') or 'not stated'} / {source.get('effective_from') or 'not stated'} to {source.get('effective_to') or 'no end date recorded'}<br>",
            f"**Edition status:** `{source['status']}` — {_md(source.get('status_basis'))}<br>",
            f"**Official source:** {_link(source['url'], source['url']) if source.get('url') else 'No stable official URL recorded'}", "",
            *( ["**Source URI gap:** No stable official URL was captured in the prior-wave index. Recover the exact official publication pointer before using this record as normative text; otherwise retain it as historical metadata only.", ""] if not source.get('url') else [] ),
            "## Provenance and rights", "",
            "This page is a project-authored metadata record and clause paraphrase, not an official FIDE reproduction or translation. Public access does not grant redistribution permission. No reuse licence or written permission is recorded; the repository therefore links to the official source and does not store its full text or original file.", "",
            "| Retrieval | Method | Raw source bytes / checksum | Local original |", "|---|---|---|---|"]
    for retrieval in source.get("retrievals", []):
        digest = _checksum_display(retrieval)
        rows.append(f"| {_md(retrieval.get('retrieved_on'))} | {_md(retrieval.get('method'))} | {_md(digest)} | {_md(retrieval.get('artifact_path') or 'None')} |")
    rows.extend(["", f"**Repository rights disposition:** `{source['rights']['redistribution']}`; permission obtained: `{str(source['rights']['permission_obtained']).lower()}`.<br>",
                 f"**Rights note:** {source['rights'].get('note', 'No rights determination recorded.')}", "",
                 f"**Scope note:** {source.get('scope_note','—')}", "",
                 "## Clause records", "",
                 "Implementation status and independent-verification status are separate. A source/test link is not proof of conformity.", ""])
    if not rules:
        rows.extend(["No clause record currently cites this source in the active clause registry.", ""])
    for rule in rules:
        rows.extend([f"<a id=\"{rule['anchor']}\"></a>",
                     f"### {rule['section']} — {rule['title']}", "",
                     f"**Clause ID:** `{rule['id']}`<br>",
                     f"**Classification:** `{rule['classification']}`<br>",
                     f"**Systems:** {', '.join(f'`{s}`' for s in rule['systems']) or '—'}<br>",
                     f"**Project paraphrase:** {rule['requirement_paraphrase']}<br>",
                     f"**Implementation status:** `{_rule_status(rule)}`<br>",
                     f"**Independent verification:** `{rule['independent_verification_status']}` — {_md(rule['independent_verification_note'])}<br>",
                     f"**Code:** {_reference_links(rule['implementation_refs'], source_path) if rule['implementation_refs'] else 'Not mapped'}<br>",
                     f"**Named tests:** {_reference_links(rule['test_refs'], source_path) if rule['test_refs'] else 'None recorded'}<br>",
                     f"**Closure action:** {rule['closure_action']}<br>"])
        if rule.get("official_example_fixture"):
            rows.append(f"**Worked-example fixture:** `{rule['official_example_fixture']}`<br>")
        if rule.get("legacy_rule_ids"):
            rows.append("**Legacy IDs:** " + ", ".join(f"`{x}`" for x in rule["legacy_rule_ids"]) + "<br>")
        rows.append(f"**Index:** {_link('all clauses', _rel(source_path, 'CLAUSE_INDEX.md') )} · {_link('coverage dashboard', _rel(source_path, 'COVERAGE_DASHBOARD.md'))}")
        rows.append("")
    return "\n".join(rows).rstrip() + "\n"


def _system_page(system: dict, rules: list[dict], source_by_id: dict, page_rel: str) -> str:
    rows = [f"# {system['name']}", "", f"**System ID:** `{system['id']}`<br>",
            f"**System status:** `{system['status']}`<br>",
            f"**Sources:** {', '.join(_link(source_id, _rel(page_rel, f'source-pages/{source_id}.md')) for source_id in system['source_ids'])}", "",
            "## Scope and limitations", "", system['scope_note'], ""]
    if system.get("entry_points"):
        rows.extend(["**Inspected entry points:** " + _reference_links(system['entry_points'], page_rel), ""])
    rows.append("Limitations:")
    rows.extend(f"- {item}" for item in system.get("limitations", []))
    rows.extend(["", "## Clause-level view", "",
                 "The rows below state project implementation and independent verification separately. They are not a conformity result.", "",
                 "| Clause ID | Source clause | Project paraphrase | Implementation | Verification | Code/tests | Closure |",
                 "|---|---|---|---|---|---|---|"])
    for rule in rules:
        target = _rel(page_rel, f"source-pages/{rule['source_id']}.md") + "#" + rule["anchor"]
        refs = [*rule["implementation_refs"], *rule["test_refs"]]
        ref_links = _reference_links(refs, page_rel) if refs else "none mapped"
        rows.append(f"| {_link(rule['id'], target)} | {_md(rule['section'])} | {_md(rule['requirement_paraphrase'])} | `{_rule_status(rule)}` | `{rule['independent_verification_status']}` | {ref_links} | {_md(rule['closure_action'])} |")
    rows.extend(["", f"For all systems and aggregate counts, see {_link('coverage dashboard', _rel(page_rel, 'COVERAGE_DASHBOARD.md'))} and {_link('complete clause index', _rel(page_rel, 'CLAUSE_INDEX.md'))}.", ""])
    return "\n".join(rows)


def _render(sources: dict, systems: dict, clauses: dict) -> dict[str, str]:
    source_by_id = _source_by_id(sources)
    system_by_id = _system_by_id(systems)
    source_records = sorted(sources["records"], key=lambda x: x["id"])
    system_records = sorted(systems["records"], key=lambda x: x["id"])
    rules = sorted(clauses["records"], key=lambda x: (x["source_id"], x["section"], x["id"]))
    outputs: dict[str, str] = {}

    # One source page per source and one current view per system.
    for source in source_records:
        source_rules = [r for r in rules if r["source_id"] == source["id"]]
        rel = f"source-pages/{source['id']}.md"
        outputs[rel] = _source_page(source, source_rules, rel)
    for system in system_records:
        system_rules = [r for r in rules if system["id"] in r["systems"]]
        rel = f"system-pages/{system['id']}.md"
        outputs[rel] = _system_page(system, system_rules, source_by_id, rel)

    # Machine-generated source index.
    rows = ["# FIDE source index (generated)", "",
            f"**Registry snapshot:** {sources['as_of']} · **Records:** {len(source_records)}", "",
            "Status describes the cited document edition/list, not implementation or endorsement. Each source page records retrieval provenance, checksum availability, supersession and redistribution posture.", "",
            "| Source ID | Authority / type | Title | Approved / effective | Status | Supersedes / successor | Official URL |", "|---|---|---|---|---|---|---|"]
    for source in source_records:
        rel = f"source-pages/{source['id']}.md"
        target = _rel("SOURCE_INDEX.md", rel)
        successor = ", ".join(source.get("supersedes", [])) + (" / " if source.get("supersedes") and source.get("superseded_by") else "") + ", ".join(source.get("superseded_by", []))
        date = f"{source.get('approval_date') or 'not stated'} / {source.get('effective_from') or 'not stated'}–{source.get('effective_to') or 'open/not recorded'}"
        url = _link("official", source["url"]) if source.get("url") else "not recorded"
        rows.append(f"| {_link(source['id'], target)} | {_md(source.get('authority'))} / `{_md(source.get('source_class'))}` | {_md(source.get('title'))} | {_md(date)} | `{source['status']}` | {_md(successor or '—')} | {url} |")
    rows.extend(["", "### Source scope and historical material", "",
                 "This structured index covers every source ID referenced by the current clause registry, plus the prior FIDE source-index records retained from the earlier research wave. It is not a legal opinion or a statement that every historical source was re-retrieved in this wave.",
                 "", _link("prior source-index snapshot", "history/SOURCE_INDEX_20261027_pre_clause_registry.md"), ""])
    outputs["SOURCE_INDEX.md"] = "\n".join(rows)

    # Retrieval manifest and rights disposition.
    rows = ["# FIDE source manifest (generated)", "",
            f"**As of:** {sources['as_of']} · **Source records:** {len(source_records)}", "",
            "## Redistribution and provenance policy", "",
            "No open reuse licence or written permission to redistribute FIDE material was established in this audit. The FIDE Handbook legal-terms lookup returned 404 (source F-0801); that failed lookup establishes neither permission nor a prohibition. Public download is not redistribution permission. No full FIDE source text, OCR, translation, or original PDF/HTML is committed by this documentation system; generated requirements are project-authored paraphrases with exact source references. Some test fixtures retain project-authored structured transcriptions or derived data from cited numerical examples, including the published Berger schedules for N=3–16. Those fixtures are explicitly labeled; permission for redistribution of source-derived example data is not established and must not be inferred. If written permission is later obtained, retain the permission record, original artifact and verified checksum before changing this policy.", "",
            "The parsed-page retrieval interface used for the 2026-10-27 review did not expose original response bytes. Therefore the current source pages have no source-text SHA-256; this is stated per retrieval rather than replaced with a fabricated digest. Historical temporary-file digests are preserved as historical records and are not presented as verified local artifacts. Prior-wave dates recorded as `2026-10-03_or_earlier_as_recorded` retain `retrieval_date_precision: on_or_before`; they are not normalized to an invented exact date.", "",
            "| Source ID | Retrieved | Method | Raw bytes / SHA-256 | Local original | Rights |", "|---|---|---|---|---|---|"]
    for source in source_records:
        for retrieval in source.get("retrievals", []):
            checksum = _checksum_display(retrieval)
            rows.append(f"| `{source['id']}` | {_md(retrieval.get('retrieved_on'))} | {_md(retrieval.get('method'))} | {_md(checksum)} | {_md(retrieval.get('artifact_path') or 'None')} | `{source['rights']['redistribution']}` |")
    rows.extend(["", "## Evidence limitations", "",
                 "- A source URL, parsed page, metadata date, paraphrase, code reference or regression test does not establish legal redistribution permission or conformity.",
                 "- A checksum is validated only when an artifact is present. A prior-wave hash with no retained file is labeled historical and cannot be rechecked offline.",
                 "- Current and superseded status is bounded to the official pages/records retrieved and cited; absence from a list is not proof that no separate FIDE decision exists.",
                 "", _link("prior retrieval ledger and historical hashes", "history/SOURCE_MANIFEST_20261027_pre_clause_registry.md"), ""])
    outputs["SOURCE_MANIFEST.md"] = "\n".join(rows)

    # Full clause index with stable IDs and explicit anchors.
    rows = ["# Clause index (generated)", "",
            f"**Clause records:** {len(rules)} · **Sources:** {len(source_records)} · **Systems/views:** {len(system_records)}", "",
            "Each clause ID is stable within its cited source edition (`Source-ID:section`). Summaries are project-authored paraphrases, not official quotations. Grouped article ranges and unmapped clauses are shown explicitly; code/test links are not conformity findings.", "",
            _link("registry guide", "README.md") + " · " + _link("coverage dashboard", "COVERAGE_DASHBOARD.md") + " · " + _link("source index", "SOURCE_INDEX.md") + " · " + _link("system views", "SYSTEM_COVERAGE.md"), ""]
    for source in source_records:
        source_rules = [r for r in rules if r["source_id"] == source["id"]]
        if not source_rules:
            continue
        source_heading = _link(source['id'] + ' — ' + source['title'], f"source-pages/{source['id']}.md")
        rows.extend([f"## {source_heading}", "",
                     "| Clause ID | Section | Requirement paraphrase | Systems | Implementation | Independent verification |", "|---|---|---|---|---|---|"])
        for rule in source_rules:
            target = f"source-pages/{source['id']}.md#{rule['anchor']}"
            rows.append(f"| {_link(rule['id'], target)} | {_md(rule['section'])} | {_md(rule['requirement_paraphrase'])} | {_md(', '.join(rule['systems']))} | `{_rule_status(rule)}` | `{rule['independent_verification_status']}` |")
        rows.append("")
    outputs["CLAUSE_INDEX.md"] = "\n".join(rows)

    # Evidence matrix: implementation and verification are independent columns.
    rows = ["# Rule-to-source implementation and test matrix (generated)", "",
            "This matrix is a project-maintained evidence index. It does not establish that an algorithm meets every rule. `Implementation status` and `Independent verification` are deliberately separate; a source/code/test link is not a FIDE conformity result.", "",
            _link("registry guide and classification semantics", "README.md") + " · " + _link("coverage dashboard", "COVERAGE_DASHBOARD.md") + " · " + _link("complete clause index", "CLAUSE_INDEX.md") + " · " + _link("historical matrix snapshot", "history/RULE_SOURCE_MATRIX_20261027_pre_clause_registry.md"), "",
            "| Clause ID | Source | Section | System(s) | Requirement (project paraphrase) | Classification | Implementation status | Code symbols | Named tests | Independent verification | Closure action |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for rule in rules:
        src_link = _link(rule["source_id"], f"source-pages/{rule['source_id']}.md#{rule['anchor']}")
        codes = _reference_links(rule["implementation_refs"], "RULE_SOURCE_MATRIX.md")
        tests = _reference_links(rule["test_refs"], "RULE_SOURCE_MATRIX.md")
        clause_link = _link(rule['id'], f"source-pages/{rule['source_id']}.md#{rule['anchor']}")
        rows.append(f"| {clause_link} | {src_link} | {_md(rule['section'])} | {_md(', '.join(rule['systems']))} | {_md(rule['requirement_paraphrase'])} | `{rule['classification']}` | `{_rule_status(rule)}` | {codes} | {tests} | `{rule['independent_verification_status']}` | {_md(rule['closure_action'])} |")
    outputs["RULE_SOURCE_MATRIX.md"] = "\n".join(rows)

    # Current system catalog and per-system records.
    rows = ["# Current system catalog (generated)", "",
            "The names below identify ruleset paths or product boundaries. They do not imply certification, full-system conformity or FIDE endorsement.", "",
            "| System ID | Type | Current implementation/evidence status | Sources | Scope and salient limitations |", "|---|---|---|---|---|"]
    for system in system_records:
        source_links = ", ".join(_link(x, f"source-pages/{x}.md") for x in system["source_ids"])
        system_link = _link(f"`{system['id']}`", f"system-pages/{system['id']}.md")
        limitations = " ".join(system.get("limitations", []))
        rows.append(f"| {system_link} | `{system['kind']}` | `{system['status']}` | {source_links} | {_md(system['scope_note'] + ' ' + limitations)} |")
    rows.extend(["", f"All system records are generated from `{SYSTEMS_PATH.relative_to(ROOT)}`. See {_link('coverage dashboard', 'COVERAGE_DASHBOARD.md')} for counts, not compliance status.", ""])
    outputs["CURRENT_SYSTEM_CATALOG.md"] = "\n".join(rows)

    rows = ["# System coverage index (generated)", "",
            "This is a navigation and documentation-coverage view, not a compliance badge. Unmapped and disputed records remain visible on their system pages.", "",
            "| System ID | Clause records | Mapped implementation refs | Named tests | No independent verification | Official worked-example only | Unmapped/disputed/out-of-scope | View |", "|---|---:|---:|---:|---:|---:|---:|---|"]
    for system in system_records:
        selected = [r for r in rules if system["id"] in r["systems"]]
        mapped = sum(bool(r["implementation_refs"]) for r in selected)
        named_tests = sum(bool(r["test_refs"]) for r in selected)
        no_independent = sum(r["independent_verification_status"] in ("none", "not_applicable") for r in selected)
        examples = sum(r["independent_verification_status"] == "official_worked_example_only" for r in selected)
        open_items = sum(r["implementation_status"] in ("unmapped", "disputed", "out_of_scope") for r in selected)
        system_view = _link('view', f"system-pages/{system['id']}.md")
        rows.append(f"| `{system['id']}` | {len(selected)} | {mapped} | {named_tests} | {no_independent} | {examples} | {open_items} | {system_view} |")
    rows.extend(["", _link("coverage dashboard", "COVERAGE_DASHBOARD.md"), ""])
    outputs["SYSTEM_COVERAGE.md"] = "\n".join(rows)

    # Dashboard counts only registry/evidence coverage, never conformance.
    from collections import Counter
    impl_counts = Counter(r["implementation_status"] for r in rules)
    verify_counts = Counter(r["independent_verification_status"] for r in rules)
    source_counts = Counter(s["status"] for s in source_records)
    mapped_count = sum(bool(r["implementation_refs"]) for r in rules)
    test_count = sum(bool(r["test_refs"]) for r in rules)
    rows = ["# FIDE documentation and evidence coverage dashboard", "",
            f"**Registry snapshot:** {sources['as_of']} · **Generated from:** `registry/sources.json`, `registry/systems.json`, `registry/clauses.json`", "",
            "> [!WARNING]", "> These counts measure source/rule indexing and project evidence pointers only. They do **not** measure FIDE compliance, approval, certification, independent evaluation, or production readiness.", "",
            "## Source inventory", "",
            f"- Source records: **{len(source_records)}**; all source IDs referenced by the clause registry are validated against this list.",
            "- Status counts: " + "; ".join(f"`{k}` {v}" for k, v in sorted(source_counts.items())),
            "- Current parsed Handbook pages retrieved in this review expose no original bytes; those entries have no claimed raw-source checksum. No local FIDE originals or bulk texts are committed.",
            "- Redistribution permission/open licence: **not established**. No source originals/full texts are committed; a small set of clearly labeled test fixtures contains structured transcriptions or derived values from named official numerical examples, and rights for those example-data transcriptions are also not established.", "",
            "## Clause/evidence inventory", "",
            f"- Clause records: **{len(rules)}** across **{len({r['source_id'] for r in rules})}** cited sources and **{len(system_records)}** system/boundary views.",
            f"- Records with at least one inspected implementation symbol: **{mapped_count}**.",
            f"- Records with at least one named repository test: **{test_count}**.",
            "- Implementation-status counts: " + "; ".join(f"`{k}` {v}" for k, v in sorted(impl_counts.items())),
            "- Independent-verification-status counts: " + "; ".join(f"`{k}` {v}" for k, v in sorted(verify_counts.items())),
            "- External independent oracle/evaluation records in this registry: **0**. Official worked-example regressions are separately identified and do not establish full-system behavior.",
            "- A large unmapped count is intentional: clauses are not marked supported just because a nearby implementation or generic test exists.", "",
            "## Per-system counts", "",
            "| System | Clauses | Impl refs | Test refs | Unmapped/disputed | Out of scope | Independent status |", "|---|---:|---:|---:|---:|---:|---|"]
    for system in system_records:
        selected = [r for r in rules if system["id"] in r["systems"]]
        dist = Counter(r["independent_verification_status"] for r in selected)
        system_link = _link(system['id'], f"system-pages/{system['id']}.md")
        rows.append(f"| {system_link} | {len(selected)} | {sum(bool(r['implementation_refs']) for r in selected)} | {sum(bool(r['test_refs']) for r in selected)} | {sum(r['implementation_status'] in ('unmapped','disputed') for r in selected)} | {sum(r['implementation_status']=='out_of_scope' for r in selected)} | {_md(', '.join(f'{k}: {v}' for k,v in sorted(dist.items())))} |")
    rows.extend(["", "## Known evidence gaps that remain visible", "",
                 "- Superseded source editions are indexed; apart from explicit grouped historical records, they are not exhaustively clause-mapped and do not establish prior-edition coverage.",
                 "- Historical `dutch-till2026-compat` is represented by a grouped behavioral record, not a clause-complete current-rule map.",
                 "- C.04.4.2 Burstein Index calculation remains absent; callers must provide complete values and provenance. C.07 values are not presumed equivalent.",
                 "- Dutch C8 and Double/Team look-ahead are partial implementation strategies; Lim scrutiny/order includes a disputed record.",
                 "- The parent C.05 general-regulations page remains an unresolved source pointer because the fetch exposed no article text; current Annex 2 Varma draw procedures are inventoried as out of scope.",
                 "- Olympiad clauses and independent per-system evidence remain incomplete; event-management rules are caller-owned/out of scope.",
                 "- All unmapped records include a closure action on their source/system view.", "",
                 "## Navigation", "",
                 _link("clause index", "CLAUSE_INDEX.md") + " · " + _link("source index", "SOURCE_INDEX.md") + " · " + _link("rule/source/code/test matrix", "RULE_SOURCE_MATRIX.md") + " · " + _link("system views", "SYSTEM_COVERAGE.md"), "",
                 "Current readiness and audit findings remain authoritative in " + _link("GAP_REGISTER.md", "../../audit/GAP_REGISTER.md") + "; the separate acceptance gates are in " + _link("COMPLETION_STANDARD.md", "../../audit/COMPLETION_STANDARD.md") + ".", ""])
    outputs["COVERAGE_DASHBOARD.md"] = "\n".join(rows)

    build_inputs = {
        "sources_sha256": sha256(SOURCES_PATH),
        "systems_sha256": sha256(SYSTEMS_PATH),
        "clauses_sha256": sha256(CLAUSES_PATH),
    }
    outputs["BUILD_INFO.json"] = json.dumps({
        "schema_version": 1,
        "as_of": sources["as_of"],
        **build_inputs,
        "source_record_count": len(source_records),
        "clause_record_count": len(rules),
        "system_view_count": len(system_records),
        "source_page_count": len(source_records),
        "generated_markdown_count": sum(not k.endswith(".json") for k in outputs),
        "generated_paths_excluding_build_info": sorted(outputs),
    }, indent=2, ensure_ascii=False) + "\n"
    return outputs


def _anchor_set(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    anchors = set(re.findall(r"<a\s+[^>]*id=[\"']([^\"']+)[\"']", text, re.I))
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        slug = heading.lower().strip()
        slug = re.sub(r"<[^>]+>", "", slug)
        slug = re.sub(r"[^\w\- ]", "", slug, flags=re.UNICODE)
        slug = re.sub(r"\s+", "-", slug).strip("-")
        if slug:
            anchors.add(slug)
    return anchors


def validate_links(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    link_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    for source_path in paths:
        text = source_path.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            target = target.strip().split()[0].strip("<>")
            parts = urlsplit(target)
            if parts.scheme or target.startswith("//"):
                continue
            raw_path = unquote(parts.path)
            if raw_path:
                dest = (source_path.parent / raw_path).resolve()
            else:
                dest = source_path.resolve()
            if ROOT not in dest.parents and dest != ROOT:
                errors.append(f"{source_path.relative_to(ROOT)}: link escapes repository: {target}")
                continue
            if not dest.exists():
                errors.append(f"{source_path.relative_to(ROOT)}: broken local link: {target}")
                continue
            if parts.fragment and dest.is_file():
                fragment = unquote(parts.fragment)
                if re.fullmatch(r"L[1-9][0-9]*", fragment) and dest.suffix == ".py":
                    line_number = int(fragment[1:])
                    if line_number <= len(dest.read_text(encoding="utf-8").splitlines()):
                        continue
                elif fragment in _anchor_set(dest):
                    continue
                errors.append(f"{source_path.relative_to(ROOT)}: missing fragment #{fragment} in {dest.relative_to(ROOT)}")
    return errors


def expected_files(sources: dict, systems: dict, clauses: dict) -> dict[str, str]:
    return _render(sources, systems, clauses)


def validate_render_counts(outputs: dict[str, str], sources: dict, systems: dict, clauses: dict) -> list[str]:
    errors: list[str] = []
    rules = clauses["records"]
    source_records = sources["records"]
    system_records = systems["records"]

    def linked_clause_rows(relative: str) -> int:
        return sum(line.startswith("| [F-") for line in outputs[relative].splitlines())

    for relative in ("CLAUSE_INDEX.md", "RULE_SOURCE_MATRIX.md"):
        observed = linked_clause_rows(relative)
        if observed != len(rules):
            errors.append(f"{relative}: generated {observed} clause rows, registry has {len(rules)}")
    source_rows = sum(line.startswith("| [F-") for line in outputs["SOURCE_INDEX.md"].splitlines())
    if source_rows != len(source_records):
        errors.append(f"SOURCE_INDEX.md: generated {source_rows} source rows, registry has {len(source_records)}")
    catalog_rows = sum(line.startswith("| [") for line in outputs["CURRENT_SYSTEM_CATALOG.md"].splitlines())
    if catalog_rows != len(system_records):
        errors.append(f"CURRENT_SYSTEM_CATALOG.md: generated {catalog_rows} system rows, registry has {len(system_records)}")
    coverage_rows = sum(line.startswith("| `") for line in outputs["SYSTEM_COVERAGE.md"].splitlines())
    if coverage_rows != len(system_records):
        errors.append(f"SYSTEM_COVERAGE.md: generated {coverage_rows} system rows, registry has {len(system_records)}")

    for source in source_records:
        relative = f"source-pages/{source['id']}.md"
        expected = sum(rule["source_id"] == source["id"] for rule in rules)
        observed = outputs[relative].count('<a id=')
        if observed != expected:
            errors.append(f"{relative}: generated {observed} clause anchors, registry has {expected}")
    for system in system_records:
        relative = f"system-pages/{system['id']}.md"
        expected = sum(system["id"] in rule["systems"] for rule in rules)
        observed = linked_clause_rows(relative)
        if observed != expected:
            errors.append(f"{relative}: generated {observed} clause rows, registry has {expected}")
    return errors


def run(mode: str) -> int:
    try:
        sources, systems, clauses = load_registry()
    except ValueError as exc:
        print(f"fide_evidence: {exc}", file=sys.stderr)
        return 1
    errors = validate_registry(sources, systems, clauses)
    if errors:
        print(f"fide_evidence {mode}: {len(errors)} registry problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1
    outputs = expected_files(sources, systems, clauses)
    errors.extend(validate_render_counts(outputs, sources, systems, clauses))
    if mode == "build":
        if errors:
            print(f"fide_evidence: refusing to generate; {len(errors)} validation error(s):", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        for relative, content in outputs.items():
            path = FIDE / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        for relative, content in outputs.items():
            path = FIDE / relative
            if not path.is_file():
                errors.append(f"generated file missing: {path.relative_to(ROOT)} (run tools/fide_evidence.py build)")
            elif path.read_text(encoding="utf-8") != content:
                errors.append(f"generated file is stale: {path.relative_to(ROOT)} (run tools/fide_evidence.py build)")
        generated_dirs = (FIDE / "source-pages", FIDE / "system-pages")
        expected_paths = {FIDE / p for p in outputs}
        for directory in generated_dirs:
            for path in directory.glob("*.md"):
                if path not in expected_paths:
                    errors.append(f"unexpected generated page: {path.relative_to(ROOT)}")

    # Independently check declared generated counts/hashes and all relevant local navigation.
    build_info_path = FIDE / "BUILD_INFO.json"
    if mode == "check" and build_info_path.is_file():
        try:
            info = json.loads(build_info_path.read_text(encoding="utf-8"))
            if info.get("source_record_count") != len(sources["records"]):
                errors.append("BUILD_INFO source count does not match registry")
            if info.get("clause_record_count") != len(clauses["records"]):
                errors.append("BUILD_INFO clause count does not match registry")
            if info.get("system_view_count") != len(systems["records"]):
                errors.append("BUILD_INFO system count does not match registry")
            if info.get("source_page_count") != len(sources["records"]):
                errors.append("BUILD_INFO source-page count does not match registry")
            expected_markdown_count = sum(not name.endswith(".json") for name in outputs)
            if info.get("generated_markdown_count") != expected_markdown_count:
                errors.append("BUILD_INFO generated Markdown count does not match generated views")
            if info.get("sources_sha256") != sha256(SOURCES_PATH) or info.get("systems_sha256") != sha256(SYSTEMS_PATH) or info.get("clauses_sha256") != sha256(CLAUSES_PATH):
                errors.append("BUILD_INFO registry digest mismatch")
            if info.get("generated_paths_excluding_build_info") != sorted(k for k in outputs if k != "BUILD_INFO.json"):
                errors.append("BUILD_INFO generated-file list/count is stale")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid BUILD_INFO.json: {exc}")

    nav_paths = {ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "docs" / "INDEX.md"}
    nav_paths.update(path for path in FIDE.rglob("*.md") if path.is_file())
    for path in sorted(nav_paths):
        if path.is_file():
            errors.extend(validate_links([path]))
    if errors:
        print(f"fide_evidence {mode}: {len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"fide_evidence {mode}: OK ({len(sources['records'])} sources, {len(clauses['records'])} clause records, {len(systems['records'])} views, {len(outputs)-1} generated files)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"), nargs="?", default="check")
    args = parser.parse_args()
    return run(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
