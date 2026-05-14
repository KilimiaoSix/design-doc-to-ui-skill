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


def load_artifact_json(run_dir: Path, manifest: dict[str, Any], key: str) -> tuple[dict[str, Any] | None, str]:
    artifacts = manifest.get("artifacts") or {}
    path = resolve_run_path(run_dir, artifacts.get(key))
    if not path or not path.exists():
        return None, f"Missing artifact: {key}"
    try:
        data = load_json(path)
    except Exception as exc:
        return None, f"Invalid JSON artifact {key}: {exc}"
    if not isinstance(data, dict):
        return None, f"Artifact must be a JSON object: {key}"
    return data, ""


def companion_loaded(manifest: dict[str, Any], key: str) -> bool:
    return bool(((manifest.get("companion_skills") or {}).get(key) or {}).get("loaded"))


def page_scores(data: dict[str, Any]) -> list[dict[str, Any]]:
    scores = data.get("page_scores") or data.get("pages") or []
    return [item for item in scores if isinstance(item, dict)]


def score_value(item: dict[str, Any]) -> float | None:
    value = item.get("visual_similarity_score")
    if value is None:
        value = item.get("score")
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number > 1:
        number = number / 100
    return number


def validate_visual_audit(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    if not companion_loaded(manifest, "visual_audit"):
        add(blockers, "VISUAL_AUDIT_COMPANION_NOT_LOADED", "design-doc-to-ui-visual-audit must be loaded before visual parity audit.")
    data, error = load_artifact_json(run_dir, manifest, "visual_parity_audit")
    if error:
        add(blockers, "VISUAL_PARITY_AUDIT_MISSING", error)
        return
    if not data.get("passed"):
        add(blockers, "VISUAL_PARITY_AUDIT_NOT_PASSED", "visual-parity-audit.json is missing passed=true.")
    hard_failures = data.get("hard_failures") or []
    if hard_failures:
        add(blockers, "VISUAL_PARITY_HARD_FAILURES", "Visual audit contains hard failures.")
    threshold = float((manifest.get("prototype_policy") or {}).get("visual_similarity_threshold", 0.80))
    required_ids = {str(page.get("page_id")) for page in required_pages(manifest)}
    seen_ids: set[str] = set()
    for item in page_scores(data):
        page_id = str(item.get("page_id") or item.get("id") or "")
        if page_id:
            seen_ids.add(page_id)
        score = score_value(item)
        if score is None:
            add(blockers, "VISUAL_SCORE_MISSING", "Page visual_similarity_score is missing.", page_id or None)
        elif score < threshold:
            add(blockers, "VISUAL_SCORE_BELOW_THRESHOLD", f"Page visual_similarity_score {score:.2f} is below {threshold:.2f}.", page_id or None)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, "VISUAL_AUDIT_PAGE_MISSING", "Visual audit missing required page.", missing_page_id)


def validate_feishu_delivery(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    if not companion_loaded(manifest, "feishu_doc"):
        add(blockers, "FEISHU_COMPANION_NOT_LOADED", "design-doc-to-ui-feishu-doc must be loaded before Feishu delivery.")
    data, error = load_artifact_json(run_dir, manifest, "feishu_doc_audit")
    if error:
        add(blockers, "FEISHU_DOC_AUDIT_MISSING", error)
        return
    if not data.get("passed"):
        add(blockers, "FEISHU_DOC_AUDIT_NOT_PASSED", "feishu-doc-audit.json is missing passed=true.")
    if int(data.get("whiteboard_count") or 0) < 3:
        add(blockers, "FEISHU_WHITEBOARD_COUNT_LOW", "Feishu rich document must include at least 3 whiteboard/diagram blocks.")
    if int(data.get("table_count") or 0) < 4:
        add(blockers, "FEISHU_TABLE_COUNT_LOW", "Feishu rich document must include at least 4 structured tables.")
    if not data.get("design_narrative_present"):
        add(blockers, "FEISHU_DESIGN_NARRATIVE_MISSING", "Feishu document must include design thinking/narrative.")
    if not data.get("page_linkage_present"):
        add(blockers, "FEISHU_PAGE_LINKAGE_MISSING", "Feishu document must explain page linkage and task flow.")
    if data.get("blockers"):
        add(blockers, "FEISHU_DOC_AUDIT_BLOCKERS", "Feishu document audit contains blockers.")


def validate_figma_delivery(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    if not companion_loaded(manifest, "figma_replica"):
        add(blockers, "FIGMA_COMPANION_NOT_LOADED", "design-doc-to-ui-figma-replica must be loaded before Figma delivery.")
    data, error = load_artifact_json(run_dir, manifest, "figma_replica_audit")
    if error:
        add(blockers, "FIGMA_REPLICA_AUDIT_MISSING", error)
        return
    if not data.get("passed"):
        add(blockers, "FIGMA_REPLICA_AUDIT_NOT_PASSED", "figma-replica-audit.json is missing passed=true.")
    required_count = len(required_pages(manifest))
    if int(data.get("frame_count") or 0) < required_count:
        add(blockers, "FIGMA_FRAME_COUNT_LOW", "Figma frame count is lower than required page count.")
    if data.get("missing_assets"):
        add(blockers, "FIGMA_MISSING_ASSETS", "Figma replica audit lists missing assets.")
    if data.get("repair_required"):
        add(blockers, "FIGMA_REPAIR_REQUIRED", "Figma replica audit requires repairs.")
    threshold = float((manifest.get("prototype_policy") or {}).get("visual_similarity_threshold", 0.80))
    required_ids = {str(page.get("page_id")) for page in required_pages(manifest)}
    seen_ids: set[str] = set()
    for item in page_scores(data):
        page_id = str(item.get("page_id") or item.get("id") or "")
        if page_id:
            seen_ids.add(page_id)
        score = score_value(item)
        if score is None:
            add(blockers, "FIGMA_SCORE_MISSING", "Figma page visual_similarity_score is missing.", page_id or None)
        elif score < threshold:
            add(blockers, "FIGMA_SCORE_BELOW_THRESHOLD", f"Figma page visual_similarity_score {score:.2f} is below {threshold:.2f}.", page_id or None)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, "FIGMA_AUDIT_PAGE_MISSING", "Figma audit missing required page.", missing_page_id)


def validate_delivery(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    validate_visual_audit(run_dir, manifest, blockers)
    channels = manifest.get("delivery_channels") or {}
    if (channels.get("feishu") or {}).get("requested"):
        validate_feishu_delivery(run_dir, manifest, blockers)
    if (channels.get("figma") or {}).get("requested"):
        validate_figma_delivery(run_dir, manifest, blockers)


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

    if phase in {"prototype", "final", "delivery"}:
        routes = prototype_routes(run_dir, manifest)
        required_route_ids = {str(page.get("page_id")) for page in pages}
        missing_routes = sorted(required_route_ids - routes)
        if missing_routes:
            for page_id in missing_routes:
                add(blockers, "PROTOTYPE_ROUTE_MISSING", "Prototype route missing for required page.", page_id)
        if not routes:
            add(blockers, "PROTOTYPE_DATA_MISSING", "prototype-data.js is missing or invalid.")

    delivery_checked = phase == "delivery"
    if delivery_checked:
        validate_delivery(run_dir, manifest, blockers)

    if phase == "design-completion" and blockers:
        add(
            blockers,
            "DESIGN_COMPLETION_GATE_FAILED",
            "React/Figma must remain blocked until all design artifacts, main audit, and structured design doc pass.",
        )

    if delivery_checked:
        visual_blocked = any(str(item.get("code") or "").startswith("VISUAL_") for item in blockers)
        phase_status["visual_parity_passed"] = not visual_blocked
        phase_status["delivery_passed"] = not blockers

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
    manifest["phase_status"]["react_allowed"] = html_allowed
    manifest["phase_status"]["html_allowed"] = html_allowed
    artifacts = manifest.get("artifacts") or {}
    report_path = resolve_run_path(run_dir, artifacts.get("validation_report")) or (run_dir / "qa" / "validation-report.json")
    write_json(report_path, report)
    save_manifest(run_dir, manifest)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate design-doc-to-ui run gates.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--phase", default="design-completion", choices=["design-completion", "prototype", "delivery", "final"])
    args = parser.parse_args()

    report = validate(Path(args.run_dir), args.phase)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
