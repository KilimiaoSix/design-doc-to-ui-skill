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
    parser.add_argument("--review", required=True)
    parser.add_argument("--status", help="Override worker status.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    manifest = load_manifest(run_dir)
    page = find_page(manifest, args.page_id)

    worker_result = require_file("worker-result.json", Path(args.worker_result), run_dir)
    interaction_audit = require_file("interaction-audit.json", Path(args.interaction_audit), run_dir)
    review = require_file("review.md", Path(args.review), run_dir)

    result_json = load_json(worker_result)
    audit_json = load_json(interaction_audit)
    status = args.status or result_json.get("status") or ("passed" if result_json.get("passed") is True else "unknown")
    passed = result_json.get("passed") is True and audit_json.get("passed") is True and str(status).lower() in {
        "passed",
        "pass",
        "approved",
    }

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
