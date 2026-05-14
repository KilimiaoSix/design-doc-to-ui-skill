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
]


def detect_language(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh-CN"
    return "en"


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


def extract_pages_from_text(text: str, default_endpoint: str) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    used: set[str] = set()
    in_page_section = False

    page_section_pattern = re.compile(
        r"^\s{0,3}#{0,6}\s*(页面|页面清单|原型页|需求页|screens?|pages?)\s*[:：]?\s*$",
        re.I,
    )
    numbered_pattern = re.compile(
        r"^\s*(?:[-*]|\d+[.)、])\s*(?P<name>[^:：\n]+?)\s*(?:[:：]\s*(?P<desc>.*))?$"
    )
    heading_pattern = re.compile(r"^\s{0,3}#{2,6}\s*(?P<name>.+?(?:页|页面|screen|page))\s*$", re.I)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if page_section_pattern.match(line):
            in_page_section = True
            continue
        heading = heading_pattern.match(raw_line)
        if heading:
            name = heading.group("name").strip(" :-：")
            page_id = unique_page_id(page_slug_from_name(name, len(pages) + 1), used, len(pages) + 1)
            pages.append(
                {
                    "page_id": page_id,
                    "page_name": name,
                    "endpoint": default_endpoint,
                    "priority": "must",
                    "required_for_delivery": True,
                    "source_evidence": [line],
                    "deferred_status": "not_deferred",
                    "deferred_reason": "",
                    "route": f"#{page_id}",
                }
            )
            continue
        if not in_page_section:
            continue
        match = numbered_pattern.match(raw_line)
        if not match:
            if re.match(r"^\s{0,3}#{1,6}\s+", raw_line):
                in_page_section = False
            continue
        name = match.group("name").strip(" .:-：")
        if not name or len(name) > 80:
            continue
        desc = (match.group("desc") or "").strip()
        page_id = unique_page_id(page_slug_from_name(name, len(pages) + 1), used, len(pages) + 1)
        pages.append(
            {
                "page_id": page_id,
                "page_name": name,
                "endpoint": default_endpoint,
                "priority": "must",
                "required_for_delivery": True,
                "source_evidence": [raw_line.strip()],
                "source_summary": desc,
                "deferred_status": "not_deferred",
                "deferred_reason": "",
                "route": f"#{page_id}",
            }
        )

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
        }
        pages.append(page)
    return pages


def brief_for_page(page: dict[str, Any], output_language: str) -> dict[str, Any]:
    page_id = page["page_id"]
    page_name = page["page_name"]
    is_chinese = output_language.lower().startswith("zh") or "中文" in output_language
    default_purpose = (
        f"根据源文档要求呈现{page_name}。"
        if is_chinese
        else f"Represent the {page_name} requirements from the source document."
    )
    default_state_description = (
        "设计图和 React 原型必须覆盖该页面的默认状态。"
        if is_chinese
        else "Default page state required for design and React prototype coverage."
    )
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


def build_manifest(args: argparse.Namespace, source_text: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
    source_language = args.source_language or detect_language(source_text)
    output_language = args.requested_output_language or source_language
    title = args.source_title or extract_title(source_text, Path(args.source).stem if args.source else "Source document")
    product_name = args.product_name or title

    manifest = {
        "schema_version": "1.0",
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
        "directories": {
            "source": "source",
            "page_briefs": "page-briefs",
            "style_samples": "style-samples",
            "workers": "workers",
            "design_images": "design-images",
            "prototype": "prototype",
            "qa": "qa",
        },
        "artifacts": {
            "app_requirements_summary": "source/app_requirements_summary.json",
            "source_bundle": "source/source-bundle.json",
            "global_style_contract": "style-samples/global-style-contract.json",
            "main_audit": "qa/main-audit.json",
            "structured_design_doc": "qa/structured-design-doc.md",
            "validation_report": "qa/validation-report.json",
            "prototype_data": "prototype/src/prototype-data.js",
            "prototype_data_report": "prototype/prototype-data-report.json",
        },
        "active_subagents": [],
        "page_inventory": [],
        "phase_status": {
            "requirements_prepared": True,
            "style_contract_locked": False,
            "all_page_briefs_ready": False,
            "all_required_designs_approved": False,
            "main_audit_passed": False,
            "structured_design_doc_ready": False,
            "no_active_subagents": True,
            "react_allowed": False,
            "html_allowed": False,
            "prototype_data_ready": False,
        },
    }

    for page in pages:
        page_id = page["page_id"]
        worker_dir = f"workers/{page_id}"
        enriched = dict(page)
        enriched["artifacts"] = {
            "brief_path": f"page-briefs/{page_id}.json",
            "worker_dir": worker_dir,
            "worker_result_path": f"{worker_dir}/worker-result.json",
            "review_path": f"{worker_dir}/review.md",
            "prompt_history_path": f"{worker_dir}/prompt-history.md",
            "final_image_path": f"design-images/{page_id}.png",
            "final_image_sha256": "",
            "main_audit_status": "pending",
        }
        enriched["status"] = "pending"
        manifest["page_inventory"].append(enriched)

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a design-doc-to-ui run manifest.")
    parser.add_argument("--source", help="Source requirements/design document path.")
    parser.add_argument("--source-text", help="Inline source text. Prefer --source for real runs.")
    parser.add_argument("--pages-json", help="Optional JSON page inventory override.")
    parser.add_argument("--run-dir", required=True, help="Output run directory.")
    parser.add_argument("--product-name", default="")
    parser.add_argument("--source-title", default="")
    parser.add_argument("--source-type", default="markdown")
    parser.add_argument("--source-language", default="")
    parser.add_argument("--requested-output-language", default="")
    parser.add_argument("--default-endpoint", default="mobile", choices=["web", "pc", "mobile", "tablet"])
    parser.add_argument("--platforms", nargs="*", default=["mobile"])
    parser.add_argument("--write-brief-stubs", action="store_true", help="Write draft page brief JSON files.")
    args = parser.parse_args()

    if not args.source and not args.source_text:
        parser.error("Provide --source or --source-text")

    source_text = args.source_text or Path(args.source).read_text(encoding="utf-8-sig")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    ensure_dirs(run_dir, DIRECTORIES)

    pages = (
        load_pages_json(Path(args.pages_json), args.default_endpoint)
        if args.pages_json
        else extract_pages_from_text(source_text, args.default_endpoint)
    )
    if not pages:
        raise SystemExit("No pages found. Provide --pages-json or add a source page inventory.")

    manifest = build_manifest(args, source_text, pages)
    write_text(run_dir / "source" / "source.md", source_text)

    source_bundle = {
        "source_type": args.source_type,
        "source_refs": [args.source] if args.source else [],
        "raw_sections": [],
        "tables": [],
        "images": [],
        "links": [],
        "constraints": [],
        "open_questions": [],
    }
    write_json(run_dir / "source" / "source-bundle.json", source_bundle)

    summary = {
        "product_name": manifest["product_name"],
        "source_language": manifest["source"]["source_language"],
        "requested_output_language": manifest["requested_output_language"],
        "target_users": [],
        "core_scenarios": [],
        "business_goals": [],
        "page_list": [page["page_name"] for page in manifest["page_inventory"]],
        "page_inventory": manifest["page_inventory"],
        "user_flows": [],
        "must_include_copy": [],
        "must_not_include": [],
        "brand_assets": [],
        "visual_style_signals": [],
        "platforms": manifest["platforms"],
        "acceptance_criteria": [],
        "unknowns": [],
    }
    write_json(run_dir / "source" / "app_requirements_summary.json", summary)

    if args.write_brief_stubs:
        for page in manifest["page_inventory"]:
            brief = brief_for_page(page, manifest["requested_output_language"])
            write_json(run_dir / page["artifacts"]["brief_path"], brief)
        manifest["phase_status"]["all_page_briefs_ready"] = True

    save_manifest(run_dir, manifest)
    print(json.dumps({"run_dir": str(run_dir), "manifest": str(run_dir / RUN_FILE), "page_count": len(pages)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
