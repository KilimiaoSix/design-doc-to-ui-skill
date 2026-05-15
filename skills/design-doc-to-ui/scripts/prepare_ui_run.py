from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from _ui_run_lib import (
    RUN_FILE,
    ensure_dirs,
    now_iso,
    page_slug_from_name,
    save_manifest,
    sha256_text,
    unique_page_id,
    write_json,
    write_text,
)


DIRECTORIES = [
    "source",
    "page-briefs",
    "style-samples",
    "workers",
    "design-images",
    "prototype",
    "qa",
    "figma-assets",
]

def detect_language(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh-CN"
    return "en"


def is_chinese(language: str) -> bool:
    return language.lower().startswith("zh") or "中文" in language


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:80]
    return fallback


def is_page_section_heading(line: str) -> bool:
    stripped = line.strip().strip(":：")
    stripped_lower = stripped.lower().lstrip("#").strip()
    if not stripped_lower:
        return False
    section_labels = {
        "页面",
        "页面清单",
        "页面列表",
        "原型页",
        "需求页",
        "screens",
        "screen list",
        "pages",
        "page list",
        "prototype screens",
        "required pages",
    }
    return stripped_lower in section_labels or any(word in stripped_lower for word in ["清单", "列表", "inventory"])


def is_section_boundary(line: str) -> bool:
    return bool(re.match(r"^\s{0,3}#{1,6}\s+", line))


def make_page(name: str, default_endpoint: str, evidence: str, desc: str, pages: list[dict[str, Any]], used: set[str]) -> dict[str, Any]:
    name = name.strip(" .:-：")
    page_id = unique_page_id(page_slug_from_name(name, len(pages) + 1), used, len(pages) + 1)
    return {
        "page_id": page_id,
        "page_name": name,
        "endpoint": default_endpoint,
        "priority": "must",
        "required_for_delivery": True,
        "source_evidence": [evidence.strip()],
        "source_summary": desc.strip(),
        "deferred_status": "not_deferred",
        "deferred_reason": "",
        "route": f"#{page_id}",
        "status": "pending",
        "artifacts": {
            "brief_path": f"page-briefs/{page_id}.json",
            "worker_dir": f"workers/{page_id}",
            "design_image_target": f"design-images/{page_id}.png",
        },
    }


def extract_pages_from_text(text: str, default_endpoint: str) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    used: set[str] = set()
    in_page_section = False

    numbered_pattern = re.compile(
        r"^\s*(?:[-*]|\d+[.)、])\s*(?P<name>[^:：\n]+?)\s*(?:[:：]\s*(?P<desc>.*))?$"
    )
    heading_pattern = re.compile(r"^\s{0,3}#{2,6}\s*(?P<name>.+?(?:页|页面|screen|page))\s*$", re.I)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if is_section_boundary(raw_line) and is_page_section_heading(raw_line):
            in_page_section = True
            continue

        heading = heading_pattern.match(raw_line)
        if heading and not is_page_section_heading(raw_line):
            name = heading.group("name").strip(" .:-：")
            if 1 <= len(name) <= 80:
                pages.append(make_page(name, default_endpoint, line, "", pages, used))
            continue

        if not in_page_section:
            continue

        if is_section_boundary(raw_line) and not is_page_section_heading(raw_line):
            in_page_section = False
            continue

        match = numbered_pattern.match(raw_line)
        if not match:
            continue
        name = match.group("name").strip(" .:-：")
        if not name or len(name) > 80:
            continue
        desc = match.group("desc") or ""
        pages.append(make_page(name, default_endpoint, raw_line, desc, pages, used))

    return pages


def load_pages_json(path: Path, default_endpoint: str) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("pages") or data.get("page_inventory") or []
    if not isinstance(data, list):
        raise ValueError("--pages-json must contain an array or an object with pages/page_inventory")

    used: set[str] = set()
    pages = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Page entry {index} must be an object")
        name = str(item.get("page_name") or item.get("name") or item.get("title") or f"Page {index}")
        base_id = str(item.get("page_id") or item.get("id") or page_slug_from_name(name, index))
        page_id = unique_page_id(base_id, used, index)
        page = {
            "page_id": page_id,
            "page_name": name,
            "endpoint": item.get("endpoint") or default_endpoint,
            "priority": item.get("priority") or "must",
            "required_for_delivery": bool(item.get("required_for_delivery", True)),
            "source_evidence": item.get("source_evidence") or item.get("evidence") or [],
            "source_summary": item.get("source_summary") or item.get("description") or "",
            "deferred_status": item.get("deferred_status") or "not_deferred",
            "deferred_reason": item.get("deferred_reason") or "",
            "route": item.get("route") or f"#{page_id}",
            "status": item.get("status") or "pending",
            "artifacts": item.get("artifacts") if isinstance(item.get("artifacts"), dict) else {},
        }
        page["artifacts"].setdefault("brief_path", f"page-briefs/{page_id}.json")
        page["artifacts"].setdefault("worker_dir", f"workers/{page_id}")
        page["artifacts"].setdefault("design_image_target", f"design-images/{page_id}.png")
        pages.append(page)
    return pages


def brief_for_page(page: dict[str, Any], output_language: str) -> dict[str, Any]:
    page_id = page["page_id"]
    page_name = page["page_name"]
    if is_chinese(output_language):
        default_purpose = f"根据源文档要求呈现{page_name}。"
        default_state_description = "设计图和 React 原型必须覆盖该页面的默认状态。"
    else:
        default_purpose = f"Represent the {page_name} requirements from the source document."
        default_state_description = "Default page state required for design and React prototype coverage."

    return {
        "page_id": page_id,
        "page_name": page_name,
        "source_page_ref": "; ".join(page.get("source_evidence") or []) or page_name,
        "output_language": output_language,
        "endpoint": page.get("endpoint") or "mobile",
        "target_resolution": "390x844" if (page.get("endpoint") or "mobile") == "mobile" else "",
        "priority": page.get("priority") or "must",
        "required_for_delivery": bool(page.get("required_for_delivery", True)),
        "purpose": page.get("source_summary") or default_purpose,
        "entry_points": [],
        "next_actions": [],
        "route_targets": [],
        "required_components": [],
        "visible_copy": [],
        "data_examples": [],
        "layout": {
            "navigation": "",
            "primary_regions": [],
            "content_hierarchy": [],
            "responsive_notes": "",
        },
        "prototype_interactions": [],
        "interactions": [],
        "states": ["default"],
        "state_requirements": [
            {
                "state": "default",
                "required": True,
                "description": default_state_description,
            }
        ],
        "assets": [],
        "style_constraints": [],
        "negative_constraints": [],
        "acceptance_criteria": [],
        "open_questions": [],
    }


def companion_entry(skill_name: str) -> dict[str, Any]:
    return {
        "skill_name": skill_name,
        "required": True,
        "loaded": False,
        "path": "",
        "status": "pending",
        "blocker": "",
    }


def build_manifest(args: argparse.Namespace, source_text: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
    source_language = args.source_language or detect_language(source_text)
    output_language = args.requested_output_language or source_language
    title = args.source_title or extract_title(source_text, Path(args.source).stem)
    product_name = args.product_name or title

    return {
        "schema_version": "1.1",
        "run_kind": "design-doc-to-ui",
        "created_at": now_iso(),
        "product_name": product_name,
        "source": {
            "type": args.source_type,
            "title": title,
            "source_language": source_language,
            "source_hash": sha256_text(source_text),
            "path": "source/source.md",
        },
        "requested_output_language": output_language,
        "platforms": args.platforms,
        "limits": {
            "max_active_subagents": 6,
        },
        "prototype_policy": {
            "framework": "react",
            "requires_design_completion": True,
            "requires_visual_parity_audit": True,
            "visual_similarity_threshold": 0.80,
            "allow_partial_prototype": False,
            "partial_prototype_approval": None,
        },
        "html_policy": {
            "legacy_field": True,
            "superseded_by": "prototype_policy",
            "requires_design_completion": True,
            "allow_partial_prototype": False,
            "partial_prototype_approval": None,
        },
        "companion_skills": {
            "feishu_doc": companion_entry("design-doc-to-ui-feishu-doc"),
            "figma_replica": companion_entry("design-doc-to-ui-figma-replica"),
            "visual_audit": companion_entry("design-doc-to-ui-visual-audit"),
        },
        "delivery_channels": {
            "feishu": {
                "requested": bool(args.request_feishu),
                "status": "pending" if args.request_feishu else "not_requested",
                "audit_path": "qa/feishu-doc-audit.json",
            },
            "figma": {
                "requested": bool(args.request_figma),
                "status": "pending" if args.request_figma else "not_requested",
                "audit_path": "qa/figma-replica-audit.json",
            },
        },
        "directories": {name.replace("-", "_"): name for name in DIRECTORIES},
        "artifacts": {
            "app_requirements_summary": "source/app-requirements-summary.json",
            "global_style_contract": "qa/global-style-contract.json",
            "design_thinking_map": "qa/design-thinking-map.md",
            "main_audit": "qa/main-audit.json",
            "structured_design_doc": "qa/structured-design-doc.md",
            "structured_design_doc_audit": "qa/structured-design-doc-audit.json",
            "validation_report": "qa/validation-report.json",
            "companion_skill_report": "qa/companion-skill-report.json",
            "visual_parity_audit": "qa/visual-parity-audit.json",
            "feishu_doc_audit": "qa/feishu-doc-audit.json",
            "figma_replica_audit": "qa/figma-replica-audit.json",
            "figma_worker_result": "qa/figma-worker-result.json",
            "figma_page_worker_results_dir": "qa/figma-page-workers",
            "figma_asset_manifest": "figma-assets/asset-manifest.json",
            "prototype_data": "prototype/src/prototype-data.js",
            "prototype_data_report": "prototype/prototype-data-report.json",
            "react_scaffold_audit": "prototype/qa/react-scaffold-audit.json",
            "react_page_worker_results_dir": "prototype/qa/react-page-workers",
            "react_page_worker_registry": "prototype/qa/react-page-worker-registry.json",
            "react_navigation_audit": "prototype/qa/react-navigation-audit.json",
            "react_worker_result": "prototype/qa/react-worker-result.json",
            "react_interaction_audit": "prototype/qa/react-interaction-audit.json",
            "figma_scaffold_audit": "qa/figma-scaffold-audit.json",
            "figma_page_worker_registry": "qa/figma-page-worker-registry.json",
            "figma_prototype_link_plan": "qa/figma-prototype-link-plan.json",
            "figma_integration_audit": "qa/figma-integration-audit.json",
        },
        "phase_status": {
            "app_requirements_summary_ready": True,
            "page_inventory_ready": bool(pages),
            "style_contract_locked": False,
            "all_page_briefs_ready": False,
            "all_required_designs_approved": False,
            "main_audit_passed": False,
            "structured_design_doc_ready": False,
            "structured_design_doc_quality_passed": False,
            "react_allowed": False,
            "html_allowed": False,
            "prototype_data_ready": False,
            "react_scaffold_passed": False,
            "react_page_workers_passed": False,
            "react_page_worker_registry_passed": False,
            "react_navigation_audit_passed": False,
            "react_worker_passed": False,
            "react_interaction_audit_passed": False,
            "global_navigation_passed": False,
            "figma_scaffold_passed": False,
            "figma_page_workers_passed": False,
            "figma_page_worker_registry_passed": False,
            "figma_worker_passed": False,
            "figma_prototype_link_plan_passed": False,
            "figma_integration_audit_passed": False,
            "figma_global_prototype_links_passed": False,
            "visual_parity_passed": False,
            "delivery_passed": False,
        },
        "active_subagents": [],
        "subagent_batches": [],
        "page_inventory": pages,
    }


def write_brief_stubs(run_dir: Path, manifest: dict[str, Any]) -> None:
    output_language = manifest.get("requested_output_language") or "zh-CN"
    for page in manifest.get("page_inventory") or []:
        artifacts = page.setdefault("artifacts", {})
        page_id = page["page_id"]
        brief_path = run_dir / str(artifacts.get("brief_path") or f"page-briefs/{page_id}.json")
        artifacts["brief_path"] = str(brief_path.relative_to(run_dir)).replace("\\", "/")
        artifacts.setdefault("worker_dir", f"workers/{page_id}")
        artifacts.setdefault("design_image_target", f"design-images/{page_id}.png")
        write_json(brief_path, brief_for_page(page, output_language))


def app_requirements_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_name": manifest.get("product_name"),
        "source_language": (manifest.get("source") or {}).get("source_language"),
        "requested_output_language": manifest.get("requested_output_language"),
        "page_inventory": manifest.get("page_inventory") or [],
        "delivery_channels": manifest.get("delivery_channels") or {},
        "prototype_policy": manifest.get("prototype_policy") or {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a design-doc-to-ui scripted run directory.")
    parser.add_argument("--source", required=True, help="Source PRD/design document path.")
    parser.add_argument("--run-dir", required=True, help="Output run directory.")
    parser.add_argument("--requested-output-language", help="Design document and prototype language. Defaults to source language.")
    parser.add_argument("--source-language", help="Override detected source language.")
    parser.add_argument("--source-title", help="Override source title.")
    parser.add_argument("--product-name", help="Override product name.")
    parser.add_argument("--source-type", default="markdown", help="Source type label.")
    parser.add_argument("--pages-json", help="Optional extracted page inventory JSON.")
    parser.add_argument("--platforms", nargs="+", default=["mobile"], help="Target platform labels.")
    parser.add_argument("--default-endpoint", default="mobile", help="Default endpoint for pages.")
    parser.add_argument("--write-brief-stubs", action="store_true", help="Write draft page brief JSON files.")
    parser.add_argument("--request-feishu", action="store_true", help="Mark Feishu delivery as requested.")
    parser.add_argument("--request-figma", action="store_true", help="Mark Figma delivery as requested.")
    args = parser.parse_args()

    source_path = Path(args.source)
    source_text = source_path.read_text(encoding="utf-8")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    ensure_dirs(run_dir, DIRECTORIES)

    pages = load_pages_json(Path(args.pages_json), args.default_endpoint) if args.pages_json else extract_pages_from_text(
        source_text, args.default_endpoint
    )
    manifest = build_manifest(args, source_text, pages)

    write_text(run_dir / "source" / "source.md", source_text)
    write_json(run_dir / "source" / "app-requirements-summary.json", app_requirements_summary(manifest))
    if args.write_brief_stubs:
        write_brief_stubs(run_dir, manifest)
    save_manifest(run_dir, manifest)

    output = {
        "run_dir": str(run_dir),
        "manifest": str(run_dir / RUN_FILE),
        "page_count": len(pages),
        "required_page_count": sum(1 for page in pages if page.get("required_for_delivery")),
        "requested_output_language": manifest.get("requested_output_language"),
        "react_allowed": False,
        "html_allowed": False,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
