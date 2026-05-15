from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _ui_run_lib import (
    load_json,
    load_manifest,
    now_iso,
    refresh_phase_status,
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


def artifact_path(run_dir: Path, manifest: dict[str, Any], key: str, fallback: str) -> Path:
    artifacts = manifest.get("artifacts") or {}
    path = resolve_run_path(run_dir, artifacts.get(key))
    return path or (run_dir / fallback)


def load_registry(path: Path, revision_id: str) -> dict[str, Any]:
    if not path.exists():
        return {"channel": "revision", "revision_id": revision_id, "subagents": []}
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"Revision SubAgent registry must be a JSON object: {path}")
    if data.get("revision_id") != revision_id:
        return {"channel": "revision", "revision_id": revision_id, "subagents": []}
    data.setdefault("channel", "revision")
    data.setdefault("revision_id", revision_id)
    data.setdefault("subagents", [])
    return data


def load_revision_plan(run_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    path = artifact_path(run_dir, manifest, "revision_plan", "qa/revision-plan.json")
    if not path.exists():
        return {}
    data = load_json(path)
    return data if isinstance(data, dict) else {}


def same_scope(entry: dict[str, Any], expected: dict[str, Any]) -> bool:
    if str(entry.get("scope") or "") != str(expected.get("scope") or ""):
        return False
    expected_page = str(expected.get("page_id") or "")
    if expected_page and str(entry.get("page_id") or "") != expected_page:
        return False
    expected_channel = str(expected.get("channel") or "")
    if expected_channel and str(entry.get("channel") or "") != expected_channel:
        return False
    return True


def compute_registry_passed(registry: dict[str, Any], revision_plan: dict[str, Any]) -> bool:
    entries = [item for item in registry.get("subagents") or [] if isinstance(item, dict)]
    expected = [item for item in revision_plan.get("expected_subagents") or [] if isinstance(item, dict)]
    if not entries:
        return False
    if not all(item.get("passed") is True for item in entries):
        return False
    if not expected:
        return True
    for item in expected:
        if item.get("required") is False:
            continue
        match = next((entry for entry in entries if same_scope(entry, item) and entry.get("passed") is True), None)
        if not match:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a revision SubAgent result in the revision registry.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--revision-id", required=True)
    parser.add_argument("--scope", required=True, help="Revision scope, for example design-image-page, react-page, figma-page, feishu-doc, or global-style.")
    parser.add_argument("--subagent-id", required=True, help="SubAgent id returned by spawn_agent.")
    parser.add_argument("--page-id", default="")
    parser.add_argument("--channel", default="")
    parser.add_argument("--worker-result", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--status", help="Override worker status.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    manifest = load_manifest(run_dir)
    worker_result = require_file("worker-result.json", Path(args.worker_result), run_dir)
    review = require_file("review.md", Path(args.review), run_dir)
    result_json = load_json(worker_result)
    if not isinstance(result_json, dict):
        raise ValueError(f"worker-result.json must be a JSON object: {worker_result}")

    status = args.status or result_json.get("status") or ("passed" if result_json.get("passed") is True else "unknown")
    passed = (
        result_json.get("passed") is True
        and result_json.get("subagent_used") is True
        and result_json.get("main_thread_direct_implementation") is False
        and not result_json.get("unresolved_blockers")
        and str(status).lower() in {"passed", "pass", "approved"}
    )

    revision_plan = load_revision_plan(run_dir, manifest)
    path = artifact_path(run_dir, manifest, "revision_subagent_registry", "qa/revision-subagent-registry.json")
    registry = load_registry(path, args.revision_id)
    entries = [
        item
        for item in registry.get("subagents") or []
        if not (
            isinstance(item, dict)
            and item.get("scope") == args.scope
            and str(item.get("page_id") or "") == args.page_id
            and str(item.get("channel") or "") == args.channel
        )
    ]
    entries.append(
        {
            "revision_id": args.revision_id,
            "scope": args.scope,
            "page_id": args.page_id,
            "channel": args.channel,
            "subagent_id": args.subagent_id,
            "status": str(status).lower(),
            "passed": passed,
            "worker_result": to_run_relative(run_dir, worker_result),
            "review": to_run_relative(run_dir, review),
            "updated_at": now_iso(),
        }
    )
    entries.sort(key=lambda item: (str(item.get("scope") or ""), str(item.get("page_id") or ""), str(item.get("channel") or "")))

    expected = [item for item in revision_plan.get("expected_subagents") or [] if isinstance(item, dict)]
    registry.update(
        {
            "channel": "revision",
            "revision_id": args.revision_id,
            "passed": False,
            "updated_at": now_iso(),
            "max_active_subagents": 6,
            "expected_count": len([item for item in expected if item.get("required") is not False]),
            "registered_count": len(entries),
            "passed_count": sum(1 for item in entries if item.get("passed") is True),
            "subagents": entries,
            "unresolved_blockers": [],
        }
    )
    registry["passed"] = compute_registry_passed(registry, revision_plan)

    write_json(path, registry)
    refresh_phase_status(manifest, run_dir)
    save_manifest(run_dir, manifest)

    output = {
        "revision_id": args.revision_id,
        "scope": args.scope,
        "page_id": args.page_id,
        "channel": args.channel,
        "passed": passed,
        "registry_passed": registry["passed"],
        "registry": to_run_relative(run_dir, path),
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
