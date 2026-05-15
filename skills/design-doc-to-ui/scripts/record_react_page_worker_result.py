from __future__ import annotations

import argparse
import json
from pathlib import Path

from _ui_run_lib import (
    find_page,
    load_json,
    load_manifest,
    now_iso,
    refresh_phase_status,
    required_pages,
    resolve_run_path,
    save_manifest,
    to_run_relative,
    write_json,
)


def require_file(label: str, path: Path, run_dir: Path) -> Path:
    if not path.is_absolute():
        run_relative = run_dir / path
        path = run_relative if run_relative.exists() else Path.cwd() / path
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    return path


def registry_path(run_dir: Path, manifest: dict) -> Path:
    artifacts = manifest.get("artifacts") or {}
    path = resolve_run_path(run_dir, artifacts.get("react_page_worker_registry"))
    return path or (run_dir / "prototype" / "qa" / "react-page-worker-registry.json")


def load_registry(path: Path) -> dict:
    if not path.exists():
        return {"channel": "react", "pages": []}
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"React page worker registry must be a JSON object: {path}")
    data.setdefault("channel", "react")
    data.setdefault("pages", [])
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a React page worker result in the prototype registry.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--worker-result", required=True)
    parser.add_argument("--interaction-audit", required=True)
    parser.add_argument("--visual-decomposition", help="visual-decomposition.json path. Defaults to worker-result directory.")
    parser.add_argument("--dom-inventory", help="dom-element-inventory.json path. Defaults to worker-result directory.")
    parser.add_argument("--visual-replica-audit", help="visual-replica-audit.json path. Defaults to worker-result directory.")
    parser.add_argument("--review", required=True)
    parser.add_argument("--status", help="Override worker status.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    manifest = load_manifest(run_dir)
    page = find_page(manifest, args.page_id)

    worker_result = require_file("worker-result.json", Path(args.worker_result), run_dir)
    interaction_audit = require_file("interaction-audit.json", Path(args.interaction_audit), run_dir)
    default_dir = worker_result.parent
    visual_decomposition = require_file(
        "visual-decomposition.json",
        Path(args.visual_decomposition) if args.visual_decomposition else default_dir / "visual-decomposition.json",
        run_dir,
    )
    dom_inventory = require_file(
        "dom-element-inventory.json",
        Path(args.dom_inventory) if args.dom_inventory else default_dir / "dom-element-inventory.json",
        run_dir,
    )
    visual_replica_audit = require_file(
        "visual-replica-audit.json",
        Path(args.visual_replica_audit) if args.visual_replica_audit else default_dir / "visual-replica-audit.json",
        run_dir,
    )
    review = require_file("review.md", Path(args.review), run_dir)

    result_json = load_json(worker_result)
    audit_json = load_json(interaction_audit)
    visual_decomposition_json = load_json(visual_decomposition)
    dom_inventory_json = load_json(dom_inventory)
    visual_replica_json = load_json(visual_replica_audit)
    status = args.status or result_json.get("status") or ("passed" if result_json.get("passed") is True else "unknown")
    passed = (
        result_json.get("passed") is True
        and audit_json.get("passed") is True
        and visual_decomposition_json.get("passed") is True
        and dom_inventory_json.get("passed") is True
        and visual_replica_json.get("passed") is True
        and str(status).lower() in {"passed", "pass", "approved"}
    )

    path = registry_path(run_dir, manifest)
    registry = load_registry(path)
    pages = [item for item in registry.get("pages") or [] if isinstance(item, dict) and item.get("page_id") != args.page_id]
    pages.append(
        {
            "page_id": args.page_id,
            "page_name": page.get("page_name"),
            "route": page.get("route"),
            "status": str(status).lower(),
            "passed": passed,
            "worker_result": to_run_relative(run_dir, worker_result),
            "interaction_audit": to_run_relative(run_dir, interaction_audit),
            "visual_decomposition": to_run_relative(run_dir, visual_decomposition),
            "dom_inventory": to_run_relative(run_dir, dom_inventory),
            "visual_replica_audit": to_run_relative(run_dir, visual_replica_audit),
            "review": to_run_relative(run_dir, review),
            "updated_at": now_iso(),
        }
    )
    pages.sort(key=lambda item: str(item.get("page_id") or ""))

    required_count = len(required_pages(manifest))
    passed_count = sum(1 for item in pages if item.get("passed") is True)
    registry.update(
        {
            "channel": "react",
            "passed": required_count > 0 and passed_count >= required_count,
            "updated_at": now_iso(),
            "max_active_subagents": 6,
            "required_page_count": required_count,
            "registered_page_count": len(pages),
            "passed_page_count": passed_count,
            "pages": pages,
        }
    )
    write_json(path, registry)
    refresh_phase_status(manifest, run_dir)
    save_manifest(run_dir, manifest)

    output = {
        "page_id": args.page_id,
        "passed": passed,
        "registry": to_run_relative(run_dir, path),
        "registered_page_count": len(pages),
        "passed_page_count": passed_count,
        "required_page_count": required_count,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
