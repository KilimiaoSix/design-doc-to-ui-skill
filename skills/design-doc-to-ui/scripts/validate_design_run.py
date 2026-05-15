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
    structured_doc_quality_passed,
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


def validate_structured_doc_audit(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    data, error = load_artifact_json(run_dir, manifest, "structured_design_doc_audit")
    if error:
        add(blockers, "STRUCTURED_DESIGN_DOC_AUDIT_MISSING", error)
        return

    if data.get("passed") is not True:
        add(blockers, "STRUCTURED_DESIGN_DOC_AUDIT_NOT_PASSED", "structured-design-doc-audit.json is missing passed=true.")

    try:
        quality_score = float(data.get("quality_score"))
    except (TypeError, ValueError):
        add(blockers, "STRUCTURED_DESIGN_DOC_SCORE_MISSING", "Structured design document audit quality_score is missing or invalid.")
        quality_score = 0.0
    if quality_score < 0.85:
        add(blockers, "STRUCTURED_DESIGN_DOC_SCORE_LOW", f"Structured design document quality_score {quality_score:.2f} is below 0.85.")

    required_count = len(required_pages(manifest))
    documented_count = data.get("documented_page_spec_count")
    try:
        documented_page_count = int(documented_count)
    except (TypeError, ValueError):
        add(blockers, "DOCUMENTED_PAGE_SPEC_COUNT_MISSING", "documented_page_spec_count is missing or invalid.")
        documented_page_count = 0
    if documented_page_count < required_count:
        add(blockers, "DOCUMENTED_PAGE_SPECS_INCOMPLETE", "Structured design document does not include a detailed spec for every required page.")

    required_flags = [
        "source_traceability_present",
        "design_rationale_present",
        "user_story_acceptance_criteria_present",
        "journey_and_ia_present",
        "page_specs_complete",
        "interaction_state_matrix_present",
        "component_token_system_present",
        "accessibility_review_present",
        "handoff_acceptance_criteria_present",
        "revision_history_present",
    ]
    for key in required_flags:
        if data.get(key) is not True:
            add(blockers, "STRUCTURED_DESIGN_DOC_QUALITY_FIELD_MISSING", f"Structured design document audit missing or failed field: {key}.")

    if data.get("screenshot_catalog_only"):
        add(blockers, "STRUCTURED_DESIGN_DOC_SCREENSHOT_CATALOG_ONLY", "Structured design document is effectively a screenshot/page catalog.")
    if data.get("blockers"):
        add(blockers, "STRUCTURED_DESIGN_DOC_AUDIT_BLOCKERS", "Structured design document audit contains blockers.")


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


def validate_max_active_subagents(data: dict[str, Any], blockers: list[dict[str, Any]], prefix: str) -> None:
    value = data.get("max_active_subagents")
    if value is None:
        add(blockers, f"{prefix}_MAX_ACTIVE_SUBAGENTS_MISSING", "Aggregate worker result must record max_active_subagents.")
        return
    try:
        number = int(value)
    except (TypeError, ValueError):
        add(blockers, f"{prefix}_MAX_ACTIVE_SUBAGENTS_INVALID", "max_active_subagents is invalid.")
        return
    if number > 6:
        add(blockers, f"{prefix}_MAX_ACTIVE_SUBAGENTS_TOO_HIGH", "At most 6 page SubAgents may be active at the same time.")


def validate_referenced_worker_file(
    run_dir: Path,
    path_value: Any,
    blockers: list[dict[str, Any]],
    missing_code: str,
    invalid_code: str,
    page_id: str | None,
) -> dict[str, Any]:
    if not path_value:
        add(blockers, missing_code, "Page worker reference path is missing.", page_id)
        return {}
    path = resolve_run_path(run_dir, str(path_value))
    if not path or not path.exists():
        add(blockers, missing_code, f"Page worker reference file is missing: {path_value}", page_id)
        return {}
    try:
        data = load_json(path)
    except Exception as exc:
        add(blockers, invalid_code, f"Page worker reference file is invalid JSON: {exc}", page_id)
        return {}
    if not isinstance(data, dict):
        add(blockers, invalid_code, "Page worker reference file must be a JSON object.", page_id)
        return {}
    return data


def validate_referenced_file_exists(
    run_dir: Path,
    path_value: Any,
    blockers: list[dict[str, Any]],
    missing_code: str,
    page_id: str | None,
) -> None:
    if not path_value:
        add(blockers, missing_code, "Page worker reference path is missing.", page_id)
        return
    path = resolve_run_path(run_dir, str(path_value))
    if not path or not path.exists():
        add(blockers, missing_code, f"Page worker reference file is missing: {path_value}", page_id)


def validate_page_worker_coverage(
    run_dir: Path,
    data: dict[str, Any],
    required_ids: set[str],
    blockers: list[dict[str, Any]],
    prefix: str,
    path_keys: list[str],
) -> list[dict[str, Any]]:
    results = data.get("page_worker_results")
    if not isinstance(results, list):
        add(blockers, f"{prefix}_PAGE_WORKER_RESULTS_MISSING", "Aggregate worker result must include page_worker_results.")
        return []
    seen_ids: set[str] = set()
    worker_payloads: list[dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            add(blockers, f"{prefix}_PAGE_WORKER_RESULT_INVALID", "page_worker_results entries must be objects.")
            continue
        page_id = str(item.get("page_id") or item.get("id") or "")
        if page_id:
            seen_ids.add(page_id)
        if item.get("passed") is not True:
            add(blockers, f"{prefix}_PAGE_WORKER_NOT_PASSED", "Page worker result is not passed.", page_id or None)
        for key in path_keys:
            payload = validate_referenced_worker_file(
                run_dir,
                item.get(key),
                blockers,
                f"{prefix}_PAGE_WORKER_FILE_MISSING",
                f"{prefix}_PAGE_WORKER_FILE_INVALID",
                page_id or None,
            )
            if payload:
                worker_payloads.append(payload)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, f"{prefix}_PAGE_WORKER_MISSING", "Aggregate worker result missing required page worker.", missing_page_id)
    return worker_payloads


def validate_page_worker_registry(
    run_dir: Path,
    manifest: dict[str, Any],
    key: str,
    required_ids: set[str],
    blockers: list[dict[str, Any]],
    prefix: str,
    path_keys: list[str],
) -> None:
    data, error = load_artifact_json(run_dir, manifest, key)
    if error:
        add(blockers, f"{prefix}_PAGE_WORKER_REGISTRY_MISSING", error)
        return
    if data.get("passed") is not True:
        add(blockers, f"{prefix}_PAGE_WORKER_REGISTRY_NOT_PASSED", "Page worker registry is missing passed=true.")
    validate_max_active_subagents(data, blockers, prefix)
    try:
        registered_count = int(data.get("registered_page_count"))
    except (TypeError, ValueError):
        add(blockers, f"{prefix}_REGISTERED_PAGE_COUNT_MISSING", "registered_page_count is missing or invalid.")
        registered_count = 0
    if registered_count < len(required_ids):
        add(blockers, f"{prefix}_REGISTERED_PAGE_COUNT_LOW", "Page worker registry has fewer pages than required.")
    pages = data.get("pages") or []
    if not isinstance(pages, list):
        add(blockers, f"{prefix}_PAGE_WORKER_REGISTRY_INVALID", "Page worker registry pages must be a list.")
        return
    seen_ids: set[str] = set()
    for item in pages:
        if not isinstance(item, dict):
            add(blockers, f"{prefix}_PAGE_WORKER_REGISTRY_ENTRY_INVALID", "Page worker registry entries must be objects.")
            continue
        page_id = str(item.get("page_id") or item.get("id") or "")
        if page_id:
            seen_ids.add(page_id)
        if item.get("passed") is not True:
            add(blockers, f"{prefix}_PAGE_WORKER_REGISTRY_ENTRY_NOT_PASSED", "Registered page worker is not passed.", page_id or None)
        for path_key in path_keys:
            if path_key == "review":
                validate_referenced_file_exists(
                    run_dir,
                    item.get(path_key),
                    blockers,
                    f"{prefix}_PAGE_WORKER_REGISTRY_FILE_MISSING",
                    page_id or None,
                )
            else:
                validate_referenced_worker_file(
                    run_dir,
                    item.get(path_key),
                    blockers,
                    f"{prefix}_PAGE_WORKER_REGISTRY_FILE_MISSING",
                    f"{prefix}_PAGE_WORKER_REGISTRY_FILE_INVALID",
                    page_id or None,
                )
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, f"{prefix}_PAGE_WORKER_REGISTRY_PAGE_MISSING", "Page worker registry missing required page.", missing_page_id)


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
        if item.get("baseline_replica_passed") is not True:
            add(blockers, "BASELINE_REPLICA_NOT_PASSED", "Page does not pass baseline replication against approved imagegen design.", page_id or None)
        if item.get("interaction_or_prototype_links_passed") is not True:
            add(blockers, "INTERACTION_OR_LINKS_NOT_PASSED", "Page interactions or Figma prototype links are missing, broken, or unverified.", page_id or None)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, "VISUAL_AUDIT_PAGE_MISSING", "Visual audit missing required page.", missing_page_id)


def validate_react_scaffold(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    required_ids = {str(page.get("page_id")) for page in required_pages(manifest)}
    required_count = len(required_ids)
    data, error = load_artifact_json(run_dir, manifest, "react_scaffold_audit")
    if error:
        add(blockers, "REACT_SCAFFOLD_AUDIT_MISSING", error)
        return
    if data.get("passed") is not True:
        add(blockers, "REACT_SCAFFOLD_NOT_PASSED", "react-scaffold-audit.json is missing passed=true.")
    for key in [
        "app_shell_created",
        "route_registry_created",
        "style_system_locked",
        "page_slots_created",
        "worker_ownership_map_created",
        "shared_navigation_contract_created",
    ]:
        if data.get(key) is not True:
            add(blockers, "REACT_SCAFFOLD_FIELD_MISSING", f"React scaffold audit missing or failed field: {key}.")
    try:
        scaffold_page_count = int(data.get("required_page_count"))
    except (TypeError, ValueError):
        add(blockers, "REACT_SCAFFOLD_PAGE_COUNT_MISSING", "React scaffold required_page_count is missing or invalid.")
        scaffold_page_count = 0
    if scaffold_page_count < required_count:
        add(blockers, "REACT_SCAFFOLD_PAGE_COUNT_LOW", "React scaffold covers fewer pages than required.")
    if data.get("hard_failures"):
        add(blockers, "REACT_SCAFFOLD_HARD_FAILURES", "React scaffold audit contains hard failures.")
    slots = data.get("page_slots") or []
    if not isinstance(slots, list):
        add(blockers, "REACT_SCAFFOLD_PAGE_SLOTS_INVALID", "React scaffold page_slots must be a list.")
        return
    seen_ids: set[str] = set()
    for item in slots:
        if not isinstance(item, dict):
            add(blockers, "REACT_SCAFFOLD_PAGE_SLOT_INVALID", "React scaffold page_slots entries must be objects.")
            continue
        page_id = str(item.get("page_id") or item.get("id") or "")
        if page_id:
            seen_ids.add(page_id)
        if not item.get("route"):
            add(blockers, "REACT_SCAFFOLD_PAGE_SLOT_ROUTE_MISSING", "React scaffold page slot missing route.", page_id or None)
        owned_files = item.get("owned_files") or []
        if not isinstance(owned_files, list) or not owned_files:
            add(blockers, "REACT_SCAFFOLD_PAGE_SLOT_OWNERSHIP_MISSING", "React scaffold page slot missing owned_files.", page_id or None)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, "REACT_SCAFFOLD_PAGE_SLOT_MISSING", "React scaffold missing page slot for required page.", missing_page_id)


def validate_react_navigation_audit(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    data, error = load_artifact_json(run_dir, manifest, "react_navigation_audit")
    if error:
        add(blockers, "REACT_NAVIGATION_AUDIT_MISSING", error)
        return
    if data.get("passed") is not True:
        add(blockers, "REACT_NAVIGATION_AUDIT_NOT_PASSED", "react-navigation-audit.json is missing passed=true.")
    for key in [
        "global_navigation_passed",
        "route_target_coverage_passed",
        "cross_page_state_passed",
        "recovery_paths_passed",
    ]:
        if data.get(key) is not True:
            add(blockers, "REACT_NAVIGATION_AUDIT_FIELD_MISSING", f"React navigation audit missing or failed field: {key}.")
    if data.get("hard_failures"):
        add(blockers, "REACT_NAVIGATION_HARD_FAILURES", "React navigation audit contains hard failures.")
    flow_results = data.get("cross_page_flow_results") or data.get("flow_results") or []
    if not isinstance(flow_results, list) or not flow_results:
        add(blockers, "REACT_NAVIGATION_FLOW_RESULTS_MISSING", "React navigation audit must include flow results.")
        return
    for item in flow_results:
        if not isinstance(item, dict):
            add(blockers, "REACT_NAVIGATION_FLOW_RESULT_INVALID", "React navigation flow results must be objects.")
            continue
        if item.get("passed") is not True:
            add(blockers, "REACT_NAVIGATION_FLOW_NOT_PASSED", "React navigation flow did not pass.")


def validate_react_page_visual_artifacts(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    registry, error = load_artifact_json(run_dir, manifest, "react_page_worker_registry")
    if error:
        return
    pages = registry.get("pages") or []
    if not isinstance(pages, list):
        return
    threshold = float((manifest.get("prototype_policy") or {}).get("visual_similarity_threshold", 0.80))
    for item in pages:
        if not isinstance(item, dict):
            continue
        page_id = str(item.get("page_id") or "")
        visual_decomposition = validate_referenced_worker_file(
            run_dir,
            item.get("visual_decomposition"),
            blockers,
            "REACT_VISUAL_DECOMPOSITION_MISSING",
            "REACT_VISUAL_DECOMPOSITION_INVALID",
            page_id or None,
        )
        if visual_decomposition:
            for key in [
                "approved_image_analyzed",
                "all_major_regions_listed",
                "all_visible_controls_listed",
                "nonstandard_layouts_identified",
                "must_not_simplify_rules_created",
            ]:
                if visual_decomposition.get(key) is not True:
                    add(blockers, "REACT_VISUAL_DECOMPOSITION_FIELD_FAILED", f"React visual decomposition failed field: {key}.", page_id or None)
            if not visual_decomposition.get("screen_regions"):
                add(blockers, "REACT_VISUAL_DECOMPOSITION_REGIONS_EMPTY", "React visual decomposition has no screen_regions.", page_id or None)
            if not visual_decomposition.get("element_inventory"):
                add(blockers, "REACT_VISUAL_DECOMPOSITION_ELEMENTS_EMPTY", "React visual decomposition has no element_inventory.", page_id or None)
            if visual_decomposition.get("hard_failures"):
                add(blockers, "REACT_VISUAL_DECOMPOSITION_HARD_FAILURES", "React visual decomposition contains hard failures.", page_id or None)

        dom_inventory = validate_referenced_worker_file(
            run_dir,
            item.get("dom_inventory"),
            blockers,
            "REACT_DOM_INVENTORY_MISSING",
            "REACT_DOM_INVENTORY_INVALID",
            page_id or None,
        )
        if dom_inventory:
            for key in [
                "all_required_sections_implemented",
                "all_visible_controls_implemented",
                "component_mapping_complete",
                "no_unmapped_required_elements",
            ]:
                if dom_inventory.get(key) is not True:
                    add(blockers, "REACT_DOM_INVENTORY_FIELD_FAILED", f"React DOM inventory failed field: {key}.", page_id or None)
            if dom_inventory.get("unmapped_required_elements"):
                add(blockers, "REACT_DOM_INVENTORY_UNMAPPED_ELEMENTS", "React DOM inventory has unmapped required elements.", page_id or None)

        visual_audit = validate_referenced_worker_file(
            run_dir,
            item.get("visual_replica_audit"),
            blockers,
            "REACT_VISUAL_REPLICA_AUDIT_MISSING",
            "REACT_VISUAL_REPLICA_AUDIT_INVALID",
            page_id or None,
        )
        if visual_audit:
            for key in [
                "visual_replica_passed",
                "all_visible_ai_elements_represented",
                "structural_layout_matched",
                "copy_and_iconography_matched",
                "nonstandard_layouts_preserved",
                "no_unapproved_simplification",
            ]:
                if visual_audit.get(key) is not True:
                    add(blockers, "REACT_VISUAL_REPLICA_FIELD_FAILED", f"React visual replica audit failed field: {key}.", page_id or None)
            score = score_value(visual_audit)
            if score is None:
                add(blockers, "REACT_VISUAL_REPLICA_SCORE_MISSING", "React visual replica audit missing visual_similarity_score.", page_id or None)
            elif score < threshold:
                add(blockers, "REACT_VISUAL_REPLICA_SCORE_LOW", f"React visual replica score {score:.2f} is below {threshold:.2f}.", page_id or None)
            for key in [
                "missing_visible_elements",
                "simplified_structures",
                "layout_drift",
                "copy_mismatches",
                "icon_or_asset_mismatches",
                "hard_failures",
            ]:
                if visual_audit.get(key):
                    add(blockers, "REACT_VISUAL_REPLICA_UNRESOLVED_DIFFS", f"React visual replica audit has unresolved {key}.", page_id or None)


def validate_react_worker(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    required_ids = {str(page.get("page_id")) for page in required_pages(manifest)}
    required_count = len(required_ids)

    validate_react_scaffold(run_dir, manifest, blockers)
    validate_page_worker_registry(
        run_dir,
        manifest,
        "react_page_worker_registry",
        required_ids,
        blockers,
        "REACT",
        ["worker_result", "interaction_audit", "visual_decomposition", "dom_inventory", "visual_replica_audit", "review"],
    )
    validate_react_page_visual_artifacts(run_dir, manifest, blockers)
    validate_react_navigation_audit(run_dir, manifest, blockers)

    result, error = load_artifact_json(run_dir, manifest, "react_worker_result")
    if error:
        add(blockers, "REACT_WORKER_RESULT_MISSING", error)
        return

    if result.get("passed") is not True:
        add(blockers, "REACT_WORKER_NOT_PASSED", "react-worker-result.json is missing passed=true.")
    if result.get("implementation_type") != "component_frontend":
        add(blockers, "REACT_IMPLEMENTATION_TYPE_INVALID", "React prototype must be a component_frontend implementation.")
    if result.get("screenshot_or_hotspot_demo") is not False:
        add(blockers, "REACT_SCREENSHOT_OR_HOTSPOT_DEMO", "React prototype appears to be a screenshot, hotspot, or image-browser demo.")
    validate_max_active_subagents(result, blockers, "REACT")
    required_flags = [
        "source_requirements_aligned",
        "structured_design_doc_aligned",
        "approved_images_replicated",
        "all_required_routes_implemented",
        "all_declared_interactions_implemented",
        "dev_server_verified",
        "build_verified",
        "main_agent_scaffold_passed",
        "style_system_locked",
        "page_workers_started_after_scaffold",
        "page_workers_used_shared_scaffold",
        "global_navigation_passed",
        "cross_page_state_passed",
    ]
    for key in required_flags:
        if result.get(key) is not True:
            add(blockers, "REACT_WORKER_FIELD_MISSING", f"React worker result missing or failed field: {key}.")
    try:
        implemented_route_count = int(result.get("implemented_route_count"))
    except (TypeError, ValueError):
        add(blockers, "REACT_IMPLEMENTED_ROUTE_COUNT_MISSING", "implemented_route_count is missing or invalid.")
        implemented_route_count = 0
    if implemented_route_count < required_count:
        add(blockers, "REACT_IMPLEMENTED_ROUTE_COUNT_LOW", "React worker implemented fewer routes than required pages.")
    if result.get("unresolved_blockers"):
        add(blockers, "REACT_WORKER_UNRESOLVED_BLOCKERS", "React worker result contains unresolved blockers.")
    page_worker_payloads = validate_page_worker_coverage(
        run_dir,
        result,
        required_ids,
        blockers,
        "REACT",
        ["worker_result", "interaction_audit", "visual_decomposition", "dom_inventory", "visual_replica_audit"],
    )
    for payload in page_worker_payloads:
        page_id = str(payload.get("page_id") or "")
        if payload.get("passed") is not True:
            add(blockers, "REACT_PAGE_WORKER_FILE_NOT_PASSED", "Referenced React page worker file is not passed.", page_id or None)
        if payload.get("implementation_type") and payload.get("implementation_type") != "component_frontend":
            add(blockers, "REACT_PAGE_WORKER_IMPLEMENTATION_TYPE_INVALID", "React page worker must use component_frontend implementation.", page_id or None)
        if payload.get("screenshot_or_hotspot_demo") is True:
            add(blockers, "REACT_PAGE_WORKER_SCREENSHOT_DEMO", "React page worker used screenshot or hotspot implementation.", page_id or None)
        for key in [
            "main_scaffold_used",
            "style_system_followed",
            "owned_page_slot_used",
            "visual_decomposition_completed",
            "dom_inventory_matches_design",
            "visual_replica_audit_passed",
            "all_visible_ai_elements_represented",
            "nonstandard_layouts_preserved",
            "no_unapproved_simplification",
            "page_interactions_verified",
            "declared_states_reachable",
            "outbound_route_targets_recorded",
        ]:
            if key in payload and payload.get(key) is not True:
                add(blockers, "REACT_PAGE_WORKER_FIELD_FAILED", f"React page worker file failed field: {key}.", page_id or None)
        if payload.get("hard_failures"):
            add(blockers, "REACT_PAGE_WORKER_HARD_FAILURES", "React page worker audit contains hard failures.", page_id or None)
        if payload.get("unresolved_blockers"):
            add(blockers, "REACT_PAGE_WORKER_UNRESOLVED_BLOCKERS", "React page worker file contains unresolved blockers.", page_id or None)

    audit, error = load_artifact_json(run_dir, manifest, "react_interaction_audit")
    if error:
        add(blockers, "REACT_INTERACTION_AUDIT_MISSING", error)
        return
    if audit.get("passed") is not True:
        add(blockers, "REACT_INTERACTION_AUDIT_NOT_PASSED", "react-interaction-audit.json is missing passed=true.")
    if audit.get("global_navigation_passed") is not True:
        add(blockers, "REACT_GLOBAL_NAVIGATION_NOT_PASSED", "React aggregate interaction audit must have global_navigation_passed=true.")
    if audit.get("hard_failures"):
        add(blockers, "REACT_INTERACTION_HARD_FAILURES", "React interaction audit contains hard failures.")
    try:
        tested_route_count = int(audit.get("tested_route_count"))
    except (TypeError, ValueError):
        add(blockers, "REACT_TESTED_ROUTE_COUNT_MISSING", "tested_route_count is missing or invalid.")
        tested_route_count = 0
    if tested_route_count < required_count:
        add(blockers, "REACT_TESTED_ROUTE_COUNT_LOW", "React interaction audit tested fewer routes than required pages.")

    seen_ids: set[str] = set()
    for item in audit.get("page_results") or []:
        if not isinstance(item, dict):
            continue
        page_id = str(item.get("page_id") or item.get("id") or "")
        if page_id:
            seen_ids.add(page_id)
        for key in [
            "route_reachable",
            "primary_actions_passed",
            "declared_states_reachable",
            "forms_and_controls_passed",
            "recovery_paths_passed",
        ]:
            if item.get(key) is not True:
                add(blockers, "REACT_PAGE_INTERACTION_FIELD_FAILED", f"React interaction audit failed field: {key}.", page_id or None)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, "REACT_INTERACTION_PAGE_MISSING", "React interaction audit missing required page.", missing_page_id)
    cross_page_results = audit.get("cross_page_flow_results") or []
    if not isinstance(cross_page_results, list) or not cross_page_results:
        add(blockers, "REACT_CROSS_PAGE_FLOW_RESULTS_MISSING", "React interaction audit must include cross_page_flow_results.")
    else:
        for item in cross_page_results:
            if not isinstance(item, dict):
                add(blockers, "REACT_CROSS_PAGE_FLOW_RESULT_INVALID", "cross_page_flow_results entries must be objects.")
                continue
            if item.get("passed") is not True:
                add(blockers, "REACT_CROSS_PAGE_FLOW_NOT_PASSED", "React cross-page flow did not pass.")


def validate_feishu_delivery(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    if not companion_loaded(manifest, "feishu_doc"):
        add(blockers, "FEISHU_COMPANION_NOT_LOADED", "design-doc-to-ui-feishu-doc must be loaded before Feishu delivery.")
    data, error = load_artifact_json(run_dir, manifest, "feishu_doc_audit")
    if error:
        add(blockers, "FEISHU_DOC_AUDIT_MISSING", error)
        return
    if not data.get("passed"):
        add(blockers, "FEISHU_DOC_AUDIT_NOT_PASSED", "feishu-doc-audit.json is missing passed=true.")
    if int(data.get("whiteboard_count") or 0) < 4:
        add(blockers, "FEISHU_WHITEBOARD_COUNT_LOW", "Feishu rich document must include at least 4 whiteboard/diagram blocks.")
    if int(data.get("table_count") or 0) < 6:
        add(blockers, "FEISHU_TABLE_COUNT_LOW", "Feishu rich document must include at least 6 structured tables.")
    required_flags = [
        "structured_doc_quality_present",
        "source_traceability_present",
        "user_story_acceptance_criteria_present",
        "interaction_state_matrix_present",
        "component_token_system_present",
        "accessibility_review_present",
        "handoff_acceptance_criteria_present",
    ]
    for key in required_flags:
        if data.get(key) is not True:
            add(blockers, "FEISHU_DOC_QUALITY_FIELD_MISSING", f"Feishu document audit missing or failed field: {key}.")
    if not data.get("design_narrative_present"):
        add(blockers, "FEISHU_DESIGN_NARRATIVE_MISSING", "Feishu document must include design thinking/narrative.")
    if not data.get("page_linkage_present"):
        add(blockers, "FEISHU_PAGE_LINKAGE_MISSING", "Feishu document must explain page linkage and task flow.")
    if data.get("blockers"):
        add(blockers, "FEISHU_DOC_AUDIT_BLOCKERS", "Feishu document audit contains blockers.")


def validate_figma_scaffold(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    required_ids = {str(page.get("page_id")) for page in required_pages(manifest)}
    data, error = load_artifact_json(run_dir, manifest, "figma_scaffold_audit")
    if error:
        add(blockers, "FIGMA_SCAFFOLD_AUDIT_MISSING", error)
        return
    if data.get("passed") is not True:
        add(blockers, "FIGMA_SCAFFOLD_NOT_PASSED", "figma-scaffold-audit.json is missing passed=true.")
    for key in [
        "figma_file_ready",
        "page_frame_slots_created",
        "worker_ownership_map_created",
        "prototype_target_contract_created",
    ]:
        if data.get(key) is not True:
            add(blockers, "FIGMA_SCAFFOLD_FIELD_MISSING", f"Figma scaffold audit missing or failed field: {key}.")
    if data.get("shared_styles_or_variables_created") is not True and data.get("shared_styles_documented") is not True:
        add(blockers, "FIGMA_SCAFFOLD_SHARED_STYLES_MISSING", "Figma scaffold must create or document shared styles/variables.")
    if data.get("hard_failures"):
        add(blockers, "FIGMA_SCAFFOLD_HARD_FAILURES", "Figma scaffold audit contains hard failures.")
    slots = data.get("frame_slots") or data.get("page_slots") or []
    if not isinstance(slots, list):
        add(blockers, "FIGMA_SCAFFOLD_FRAME_SLOTS_INVALID", "Figma scaffold frame_slots must be a list.")
        return
    seen_ids: set[str] = set()
    for item in slots:
        if not isinstance(item, dict):
            add(blockers, "FIGMA_SCAFFOLD_FRAME_SLOT_INVALID", "Figma scaffold frame slot entries must be objects.")
            continue
        page_id = str(item.get("page_id") or item.get("id") or "")
        if page_id:
            seen_ids.add(page_id)
        if not (item.get("frame_name") or item.get("frame_node_id")):
            add(blockers, "FIGMA_SCAFFOLD_FRAME_SLOT_TARGET_MISSING", "Figma scaffold frame slot missing frame target.", page_id or None)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, "FIGMA_SCAFFOLD_FRAME_SLOT_MISSING", "Figma scaffold missing frame slot for required page.", missing_page_id)


def validate_figma_link_plan(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    data, error = load_artifact_json(run_dir, manifest, "figma_prototype_link_plan")
    if error:
        add(blockers, "FIGMA_PROTOTYPE_LINK_PLAN_MISSING", error)
        return
    if data.get("passed") is not True:
        add(blockers, "FIGMA_PROTOTYPE_LINK_PLAN_NOT_PASSED", "figma-prototype-link-plan.json is missing passed=true.")
    for key in ["all_page_targets_mapped", "primary_navigation_mapped", "main_actions_mapped"]:
        if data.get(key) is not True:
            add(blockers, "FIGMA_PROTOTYPE_LINK_PLAN_FIELD_MISSING", f"Figma prototype link plan missing or failed field: {key}.")
    if data.get("unresolved_targets"):
        add(blockers, "FIGMA_PROTOTYPE_LINK_PLAN_UNRESOLVED_TARGETS", "Figma prototype link plan has unresolved targets.")


def validate_figma_integration_audit(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    data, error = load_artifact_json(run_dir, manifest, "figma_integration_audit")
    if error:
        add(blockers, "FIGMA_INTEGRATION_AUDIT_MISSING", error)
        return
    if data.get("passed") is not True:
        add(blockers, "FIGMA_INTEGRATION_AUDIT_NOT_PASSED", "figma-integration-audit.json is missing passed=true.")
    for key in [
        "global_prototype_links_passed",
        "cross_frame_navigation_passed",
        "shared_styles_consistent",
        "frontend_handoff_ready",
    ]:
        if data.get(key) is not True:
            add(blockers, "FIGMA_INTEGRATION_AUDIT_FIELD_MISSING", f"Figma integration audit missing or failed field: {key}.")
    if data.get("hard_failures"):
        add(blockers, "FIGMA_INTEGRATION_HARD_FAILURES", "Figma integration audit contains hard failures.")


def validate_figma_delivery(run_dir: Path, manifest: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    if not companion_loaded(manifest, "figma_replica"):
        add(blockers, "FIGMA_COMPANION_NOT_LOADED", "design-doc-to-ui-figma-replica must be loaded before Figma delivery.")
    required_ids = {str(page.get("page_id")) for page in required_pages(manifest)}
    validate_figma_scaffold(run_dir, manifest, blockers)
    validate_page_worker_registry(
        run_dir,
        manifest,
        "figma_page_worker_registry",
        required_ids,
        blockers,
        "FIGMA",
        ["worker_result", "frame_audit", "review"],
    )
    validate_figma_link_plan(run_dir, manifest, blockers)
    validate_figma_integration_audit(run_dir, manifest, blockers)
    worker_result, error = load_artifact_json(run_dir, manifest, "figma_worker_result")
    if error:
        add(blockers, "FIGMA_WORKER_RESULT_MISSING", error)
    else:
        if worker_result.get("passed") is not True:
            add(blockers, "FIGMA_WORKER_NOT_PASSED", "figma-worker-result.json is missing passed=true.")
        if worker_result.get("implementation_type") != "editable_figma_frames":
            add(blockers, "FIGMA_IMPLEMENTATION_TYPE_INVALID", "Figma output must be editable_figma_frames.")
        if worker_result.get("full_screen_image_implementation") is not False:
            add(blockers, "FIGMA_FULL_SCREEN_IMAGE_IMPLEMENTATION", "Figma output uses full-screen images as implementation.")
        validate_max_active_subagents(worker_result, blockers, "FIGMA")
        try:
            worker_editable_coverage = float(worker_result.get("editable_element_coverage"))
        except (TypeError, ValueError):
            add(blockers, "FIGMA_WORKER_EDITABLE_COVERAGE_MISSING", "Figma worker editable_element_coverage is missing or invalid.")
            worker_editable_coverage = 0.0
        if worker_editable_coverage < 0.95:
            add(blockers, "FIGMA_WORKER_EDITABLE_COVERAGE_LOW", f"Figma worker editable_element_coverage {worker_editable_coverage:.2f} is below 0.95.")
        for key in [
            "all_required_frames_created",
            "all_major_elements_editable",
            "icons_replicated",
            "assets_reconstructed",
            "frontend_handoff_ready",
            "prototype_links_verified",
            "global_prototype_links_passed",
            "figma_scaffold_passed",
            "page_workers_started_after_scaffold",
            "page_workers_used_shared_frame_slots",
        ]:
            if worker_result.get(key) is not True:
                add(blockers, "FIGMA_WORKER_FIELD_MISSING", f"Figma worker result missing or failed field: {key}.")
        if worker_result.get("unresolved_blockers"):
            add(blockers, "FIGMA_WORKER_UNRESOLVED_BLOCKERS", "Figma worker result contains unresolved blockers.")
        page_worker_payloads = validate_page_worker_coverage(
            run_dir,
            worker_result,
            {str(page.get("page_id")) for page in required_pages(manifest)},
            blockers,
            "FIGMA",
            ["worker_result", "frame_audit"],
        )
        for payload in page_worker_payloads:
            page_id = str(payload.get("page_id") or "")
            if payload.get("passed") is not True:
                add(blockers, "FIGMA_PAGE_WORKER_FILE_NOT_PASSED", "Referenced Figma page worker file is not passed.", page_id or None)
            if payload.get("implementation_type") and payload.get("implementation_type") != "editable_figma_frame":
                add(blockers, "FIGMA_PAGE_WORKER_IMPLEMENTATION_TYPE_INVALID", "Figma page worker must create an editable_figma_frame.", page_id or None)
            if payload.get("full_screen_image_implementation") is True:
                add(blockers, "FIGMA_PAGE_WORKER_FULL_SCREEN_IMAGE", "Figma page worker used full-screen image implementation.", page_id or None)
            for key in [
                "main_figma_scaffold_used",
                "shared_styles_followed",
                "owned_frame_slot_used",
                "baseline_replica_passed",
                "editable_elements_passed",
                "frontend_handoff_ready",
            ]:
                if key in payload and payload.get(key) is not True:
                    add(blockers, "FIGMA_PAGE_WORKER_FIELD_FAILED", f"Figma page worker file failed field: {key}.", page_id or None)
            for key in ["icons_replicated", "assets_reconstructed", "page_prototype_links_recorded"]:
                if key in payload and payload.get(key) is not True:
                    add(blockers, "FIGMA_PAGE_WORKER_FIELD_FAILED", f"Figma page worker file failed field: {key}.", page_id or None)
            if payload.get("hard_failures"):
                add(blockers, "FIGMA_PAGE_WORKER_HARD_FAILURES", "Figma page worker audit contains hard failures.", page_id or None)
            if payload.get("missing_assets"):
                add(blockers, "FIGMA_PAGE_WORKER_MISSING_ASSETS", "Figma page worker audit contains missing assets.", page_id or None)
            if payload.get("repair_required"):
                add(blockers, "FIGMA_PAGE_WORKER_REPAIR_REQUIRED", "Figma page worker audit requires repair.", page_id or None)
            if payload.get("unresolved_blockers"):
                add(blockers, "FIGMA_PAGE_WORKER_UNRESOLVED_BLOCKERS", "Figma page worker file contains unresolved blockers.", page_id or None)

    data, error = load_artifact_json(run_dir, manifest, "figma_replica_audit")
    if error:
        add(blockers, "FIGMA_REPLICA_AUDIT_MISSING", error)
        return
    if not data.get("passed"):
        add(blockers, "FIGMA_REPLICA_AUDIT_NOT_PASSED", "figma-replica-audit.json is missing passed=true.")
    required_count = len(required_pages(manifest))
    if int(data.get("frame_count") or 0) < required_count:
        add(blockers, "FIGMA_FRAME_COUNT_LOW", "Figma frame count is lower than required page count.")
    if int(data.get("editable_frame_count") or 0) < required_count:
        add(blockers, "FIGMA_EDITABLE_FRAME_COUNT_LOW", "Figma editable frame count is lower than required page count.")
    if int(data.get("full_screen_image_layer_count") or 0) > 0:
        add(blockers, "FIGMA_FULL_SCREEN_IMAGE_LAYERS", "Figma replica audit reports full-screen image implementation layers.")
    try:
        editable_coverage = float(data.get("editable_element_coverage"))
    except (TypeError, ValueError):
        add(blockers, "FIGMA_EDITABLE_COVERAGE_MISSING", "Figma editable_element_coverage is missing or invalid.")
        editable_coverage = 0.0
    if editable_coverage < 0.95:
        add(blockers, "FIGMA_EDITABLE_COVERAGE_LOW", f"Figma editable_element_coverage {editable_coverage:.2f} is below 0.95.")
    if data.get("frontend_handoff_ready") is not True:
        add(blockers, "FIGMA_FRONTEND_HANDOFF_NOT_READY", "Figma replica is not marked frontend_handoff_ready.")
    if data.get("global_prototype_links_passed") is not True:
        add(blockers, "FIGMA_GLOBAL_PROTOTYPE_LINKS_NOT_PASSED", "Figma replica audit must have global_prototype_links_passed=true.")
    if data.get("missing_assets"):
        add(blockers, "FIGMA_MISSING_ASSETS", "Figma replica audit lists missing assets.")
    if data.get("repair_required"):
        add(blockers, "FIGMA_REPAIR_REQUIRED", "Figma replica audit requires repairs.")
    if data.get("hard_failures"):
        add(blockers, "FIGMA_HARD_FAILURES", "Figma replica audit contains hard failures.")
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
        if item.get("baseline_replica_passed") is not True:
            add(blockers, "FIGMA_BASELINE_REPLICA_NOT_PASSED", "Figma frame does not pass baseline replication against approved imagegen design.", page_id or None)
        if item.get("editable_elements_passed") is not True:
            add(blockers, "FIGMA_EDITABLE_ELEMENTS_NOT_PASSED", "Figma frame does not pass editable elements check.", page_id or None)
        if item.get("icon_replication_passed") is not True:
            add(blockers, "FIGMA_ICON_REPLICATION_NOT_PASSED", "Figma frame does not pass icon replication check.", page_id or None)
        if item.get("asset_reconstruction_passed") is not True:
            add(blockers, "FIGMA_ASSET_RECONSTRUCTION_NOT_PASSED", "Figma frame does not pass asset reconstruction check.", page_id or None)
        if item.get("prototype_links_passed") is not True:
            add(blockers, "FIGMA_PROTOTYPE_LINKS_NOT_PASSED", "Figma frame is missing required primary prototype links or link verification.", page_id or None)
        if item.get("frontend_handoff_ready") is not True:
            add(blockers, "FIGMA_PAGE_FRONTEND_HANDOFF_NOT_READY", "Figma frame is not ready for frontend handoff.", page_id or None)
    for missing_page_id in sorted(required_ids - seen_ids):
        add(blockers, "FIGMA_AUDIT_PAGE_MISSING", "Figma audit missing required page.", missing_page_id)
    cross_frame_results = data.get("cross_frame_navigation_results") or []
    if not isinstance(cross_frame_results, list) or not cross_frame_results:
        add(blockers, "FIGMA_CROSS_FRAME_NAVIGATION_RESULTS_MISSING", "Figma audit must include cross_frame_navigation_results.")
    else:
        for item in cross_frame_results:
            if not isinstance(item, dict):
                add(blockers, "FIGMA_CROSS_FRAME_NAVIGATION_RESULT_INVALID", "cross_frame_navigation_results entries must be objects.")
                continue
            if item.get("passed") is not True:
                add(blockers, "FIGMA_CROSS_FRAME_NAVIGATION_NOT_PASSED", "Figma cross-frame navigation did not pass.")


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
    if not structured_doc_quality_passed(run_dir, manifest):
        validate_structured_doc_audit(run_dir, manifest, blockers)

    phase_status = refresh_phase_status(manifest, run_dir)
    react_allowed = not blockers and phase_status.get("react_allowed", phase_status.get("html_allowed", False))
    html_allowed = react_allowed

    if phase in {"prototype", "final", "delivery"}:
        validate_react_worker(run_dir, manifest, blockers)
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
