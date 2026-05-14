from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _ui_run_lib import (
    REQUIRED_BRIEF_FIELDS,
    active_subagents,
    audit_passed,
    load_json,
    load_manifest,
    page_artifacts,
    page_brief_ready,
    page_has_required_worker_artifacts,
    page_is_worker_approved,
    refresh_phase_status,
    required_pages,
    resolve_run_path,
    save_manifest,
    structured_doc_ready,
    style_contract_locked,
    write_json,
)


def add(blockers: list[dict[str, Any]], code: str, message: str, page_id: str | None = None) -> None:
    item: dict[str, Any] = {"code": code, "message": message}
    if page_id:
        item["page_id"] = page_id
    blockers.append(item)


def validate_brief(run_dir: Path, page: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    artifacts = page_artifacts(page)
    brief_path = resolve_run_path(run_dir, artifacts.get("brief_path"))
    if not brief_path or not brief_path.exists():
        add(blockers, "PAGE_BRIEF_MISSING", "Required page is missing a page brief.", page.get("page_id"))
        return
    try:
        brief = load_json(brief_path)
    except Exception as exc:
        add(blockers, "PAGE_BRIEF_INVALID_JSON", f"Page brief is not valid JSON: {exc}", page.get("page_id"))
        return
    for field in REQUIRED_BRIEF_FIELDS:
        if field not in brief:
            add(blockers, "PAGE_BRIEF_FIELD_MISSING", f"Page brief missing field: {field}", page.get("page_id"))
    for field in ["prototype_interactions", "route_targets", "state_requirements"]:
        if field in brief and not isinstance(brief[field], list):
            add(blockers, "PAGE_BRIEF_FIELD_INVALID", f"Page brief field must be a list: {field}", page.get("page_id"))


def validate_worker(run_dir: Path, page: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    ok, missing = page_has_required_worker_artifacts(run_dir, page)
    if not ok:
        for key in missing:
            add(blockers, "WORKER_ARTIFACT_MISSING", f"Missing worker artifact: {key}", page.get("page_id"))
    if not page_is_worker_approved(run_dir, page):
        add(blockers, "WORKER_NOT_APPROVED", "Worker result is missing or not approved.", page.get("page_id"))


def extract_js_object_after(text: str, marker: str) -> str | None:
    start_marker = text.find(marker)
    if start_marker < 0:
        return None
    start = text.find("{", start_marker)
    if start < 0:
        return None
    depth = 0
    in_string = False
    escape = False
    quote = ""
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                in_string = False
            continue
        if char in {'"', "'"}:
            in_string = True
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def prototype_routes(run_dir: Path, manifest: dict[str, Any]) -> set[str]:
    artifacts = manifest.get("artifacts") or {}
    path = resolve_run_path(run_dir, artifacts.get("prototype_data"))
    if not path or not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="ignore")
    object_text = extract_js_object_after(text, "window.PROTOTYPE_DATA") or extract_js_object_after(text, "const prototypeData")
    if not object_text:
        return set()
    try:
        data = json.loads(object_text)
    except Exception:
        return set()
    routes = set()
    for page in data.get("pages") or []:
        if isinstance(page, dict):
            value = page.get("id") or page.get("route")
            if value:
                routes.add(str(value).lstrip("#"))
    return routes


def validate(run_dir: Path, phase: str) -> dict[str, Any]:
    manifest = load_manifest(run_dir)
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    pages = required_pages(manifest)

    if not pages:
        add(blockers, "PAGE_INVENTORY_EMPTY", "No non-deferred required pages found in page_inventory.")

    if active_subagents(manifest):
        add(blockers, "ACTIVE_SUBAGENTS_RUNNING", "Style/page/regeneration SubAgents are still active.")

    if not style_contract_locked(run_dir, manifest):
        add(blockers, "STYLE_CONTRACT_NOT_LOCKED", "global_style_contract is missing or not locked.")

    for page in pages:
        validate_brief(run_dir, page, blockers)
        validate_worker(run_dir, page, blockers)

    if not audit_passed(run_dir, manifest):
        add(blockers, "MAIN_AUDIT_NOT_PASSED", "Main-agent audit is missing or not passed.")

    if not structured_doc_ready(run_dir, manifest):
        add(blockers, "STRUCTURED_DESIGN_DOC_MISSING", "Structured design document is missing.")

    phase_status = refresh_phase_status(manifest, run_dir)
    react_allowed = not blockers and phase_status.get("react_allowed", phase_status.get("html_allowed", False))
    html_allowed = react_allowed

    if phase in {"prototype", "final"}:
        routes = prototype_routes(run_dir, manifest)
        required_route_ids = {str(page.get("page_id")) for page in pages}
        missing_routes = sorted(required_route_ids - routes)
        if missing_routes:
            for page_id in missing_routes:
                add(blockers, "PROTOTYPE_ROUTE_MISSING", "Prototype route missing for required page.", page_id)
        if not routes:
            add(blockers, "PROTOTYPE_DATA_MISSING", "prototype-data.js is missing or invalid.")

    if phase == "design-completion" and blockers:
        add(
            blockers,
            "DESIGN_COMPLETION_GATE_FAILED",
            "React/Figma must remain blocked until all design artifacts, main audit, and structured design doc pass.",
        )

    report = {
        "run_dir": str(run_dir),
        "phase": phase,
        "passed": not blockers,
        "react_allowed": react_allowed,
        "html_allowed": html_allowed,
        "page_count": len(pages),
        "phase_status": phase_status,
        "blockers": blockers,
        "warnings": warnings,
    }
    manifest["phase_status"]["react_allowed"] = react_allowed
    manifest["phase_status"]["html_allowed"] = html_allowed
    artifacts = manifest.get("artifacts") or {}
    report_path = resolve_run_path(run_dir, artifacts.get("validation_report")) or (run_dir / "qa" / "validation-report.json")
    write_json(report_path, report)
    save_manifest(run_dir, manifest)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate design-doc-to-ui run gates.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--phase", default="design-completion", choices=["design-completion", "prototype", "final"])
    args = parser.parse_args()

    report = validate(Path(args.run_dir), args.phase)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
