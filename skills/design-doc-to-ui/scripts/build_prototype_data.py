from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from _ui_run_lib import (
    load_json,
    load_manifest,
    page_artifacts,
    refresh_phase_status,
    required_pages,
    resolve_run_path,
    save_manifest,
    to_run_relative,
    write_json,
    write_text,
)


def is_chinese(language: str) -> bool:
    return language.lower().startswith("zh") or "中文" in language


def labels_for(language: str) -> dict[str, str]:
    if is_chinese(language):
        return {
            "pages": "页面",
            "status": "状态",
            "actions": "操作",
            "controls": "控件",
            "states": "页面状态",
            "reference": "视觉参考",
            "close": "关闭",
            "saved": "已保存",
            "noPages": "没有页面数据",
            "blocked": "阻断",
            "approved": "已通过",
            "visualParity": "视觉复刻",
        }
    return {
        "pages": "Pages",
        "status": "Status",
        "actions": "Actions",
        "controls": "Controls",
        "states": "Page states",
        "reference": "Visual reference",
        "close": "Close",
        "saved": "Saved",
        "noPages": "No page data",
        "blocked": "Blocked",
        "approved": "Approved",
        "visualParity": "Visual parity",
    }


def read_brief(run_dir: Path, page: dict[str, Any]) -> dict[str, Any]:
    path = resolve_run_path(run_dir, page_artifacts(page).get("brief_path"))
    if path and path.exists():
        return load_json(path)
    return {}


def rel_from_dir(run_dir: Path, output_dir: Path, value: str | None) -> str:
    path = resolve_run_path(run_dir, value)
    if not path:
        return ""
    try:
        return Path("../" + Path(to_run_relative(run_dir, path)).as_posix()).as_posix()
    except Exception:
        return path.as_posix()


def interactions_to_actions(brief: dict[str, Any], page_ids: set[str], language: str) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    interactions = brief.get("prototype_interactions") or []
    default_label = "查看" if is_chinese(language) else "Open"
    for index, interaction in enumerate(interactions, start=1):
        if not isinstance(interaction, dict):
            continue
        target = str(interaction.get("target_route_or_state") or "").lstrip("#")
        action: dict[str, Any] = {
            "label": interaction.get("trigger") or f"{default_label} {index}",
        }
        if target in page_ids:
            action["target"] = target
        else:
            result = interaction.get("result") or interaction.get("target_route_or_state") or ""
            action["dialog"] = result
        actions.append(action)
    return actions


def brief_to_sections(brief: dict[str, Any], language: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    components = brief.get("required_components") or []
    visible_copy = brief.get("visible_copy") or []
    data_examples = brief.get("data_examples") or []
    route_targets = brief.get("route_targets") or []

    def section(title: str, values: list[Any]) -> None:
        if not values:
            return
        items = []
        for value in values:
            if isinstance(value, dict):
                item_title = value.get("title") or value.get("name") or value.get("label") or json.dumps(value, ensure_ascii=False)
                desc = value.get("description") or value.get("body") or value.get("text") or ""
            else:
                item_title = str(value)
                desc = ""
            items.append({"title": item_title, "description": desc})
        sections.append({"title": title, "items": items})

    if is_chinese(language):
        section("关键组件", components)
        section("可见文案", visible_copy)
        section("数据示例", data_examples)
        section("路由目标", route_targets)
    else:
        section("Key components", components)
        section("Visible copy", visible_copy)
        section("Example data", data_examples)
        section("Route targets", route_targets)

    if not sections:
        sections.append(
            {
                "title": "页面内容" if is_chinese(language) else "Page content",
                "body": brief.get("purpose") or "",
                "items": [],
            }
        )
    return sections


def brief_to_states(brief: dict[str, Any]) -> list[dict[str, str]]:
    states = []
    for item in brief.get("state_requirements") or []:
        if not isinstance(item, dict):
            continue
        states.append(
            {
                "name": str(item.get("state") or "default"),
                "description": str(item.get("description") or ""),
            }
        )
    return states or [{"name": "default", "description": ""}]


def copy_template_files(skill_dir: Path, prototype_dir: Path, template: str) -> None:
    template_dir = skill_dir / "assets" / ("react-prototype-template" if template == "react" else "html-prototype-template")
    if not template_dir.exists():
        raise FileNotFoundError(f"Missing prototype template: {template_dir}")
    for source in template_dir.rglob("*"):
        if source.is_dir():
            continue
        relative = source.relative_to(template_dir)
        target = prototype_dir / relative
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def build_data(run_dir: Path, copy_template: bool, template: str) -> dict[str, Any]:
    manifest = load_manifest(run_dir)
    phase_status = refresh_phase_status(manifest, run_dir)
    if not phase_status.get("react_allowed", phase_status.get("html_allowed")):
        raise SystemExit("React is blocked: run validate_design_run.py --phase design-completion and fix blockers first.")

    language = manifest.get("requested_output_language") or manifest.get("source", {}).get("source_language") or "zh-CN"
    page_ids = {str(page.get("page_id")) for page in required_pages(manifest)}
    prototype_dir = run_dir / "prototype"
    prototype_dir.mkdir(parents=True, exist_ok=True)

    if copy_template:
        copy_template_files(Path(__file__).resolve().parents[1], prototype_dir, template)

    data_output_dir = prototype_dir / "src" if template == "react" else prototype_dir
    data_output_dir.mkdir(parents=True, exist_ok=True)

    pages = []
    missing_images = []
    missing_interactions = []
    missing_states = []

    for page in required_pages(manifest):
        brief = read_brief(run_dir, page)
        artifacts = page_artifacts(page)
        final_image = artifacts.get("final_image_path")
        image_path = resolve_run_path(run_dir, final_image)
        if not final_image or not image_path or not image_path.exists():
            missing_images.append(page.get("page_id"))
        actions = interactions_to_actions(brief, page_ids, language)
        if not actions:
            missing_interactions.append(page.get("page_id"))
        states = brief_to_states(brief)
        if not states:
            missing_states.append(page.get("page_id"))
        page_entry = {
            "id": page.get("page_id"),
            "name": page.get("page_name"),
            "navLabel": page.get("page_name"),
            "endpoint": page.get("endpoint"),
            "status": page.get("status") or "approved",
            "headline": brief.get("page_name") or page.get("page_name"),
            "purpose": brief.get("purpose") or page.get("source_summary") or "",
            "controls": [],
            "sections": brief_to_sections(brief, language),
            "states": states,
            "actions": actions,
            "referenceImage": rel_from_dir(run_dir, data_output_dir, final_image),
            "visualParityStatus": "needs_review",
        }
        pages.append(page_entry)

    title = manifest.get("product_name") or "Interactive Prototype"
    if is_chinese(language):
        kicker = "React 交互原型"
        summary = "基于已批准 AI 原型图、页面 brief、评审结果和结构化设计文档生成；React 页面必须复刻 AI 原型图的视觉效果并补齐交互。"
        data_title = f"{title} React 原型"
    else:
        kicker = "React Prototype"
        summary = "Generated from approved AI UI images, page briefs, reviews, and the structured design document. React screens must visually recreate the approved images and add interactions."
        data_title = f"{title} React Prototype"

    data = {
        "lang": language,
        "title": data_title,
        "kicker": kicker,
        "summary": summary,
        "labels": labels_for(language),
        "pages": pages,
    }

    prototype_data_path = data_output_dir / "prototype-data.js"
    if template == "react":
        text = (
            "const prototypeData = "
            + json.dumps(data, ensure_ascii=False, indent=2)
            + ";\n\nwindow.PROTOTYPE_DATA = prototypeData;\nexport default prototypeData;\n"
        )
    else:
        text = "window.PROTOTYPE_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    write_text(prototype_data_path, text)

    report = {
        "passed": not missing_images and not missing_states,
        "template": template,
        "route_count": len(pages),
        "required_page_count": len(page_ids),
        "routes": [page["id"] for page in pages],
        "missing_images": missing_images,
        "missing_interactions": missing_interactions,
        "missing_states": missing_states,
        "visual_parity_required": True,
        "notes": "missing_interactions is advisory; visual parity must be audited after the React implementation is rendered.",
    }
    write_json(prototype_dir / "prototype-data-report.json", report)

    manifest.setdefault("artifacts", {})["prototype_data"] = to_run_relative(run_dir, prototype_data_path)
    manifest.setdefault("artifacts", {})["prototype_data_report"] = to_run_relative(run_dir, prototype_dir / "prototype-data-report.json")
    manifest.setdefault("phase_status", {})["prototype_data_ready"] = True
    save_manifest(run_dir, manifest)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build prototype data from a completed design-doc-to-ui run.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--copy-template", action="store_true", help="Copy the bundled prototype template if absent.")
    parser.add_argument("--template", choices=["react", "static"], default="react", help="Prototype template type. Default: react.")
    args = parser.parse_args()

    report = build_data(Path(args.run_dir), args.copy_template, args.template)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
