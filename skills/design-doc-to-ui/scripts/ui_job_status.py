from __future__ import annotations

import argparse
import json
from pathlib import Path

from _ui_run_lib import (
    BLOCKED_STATUSES,
    load_manifest,
    page_artifacts,
    page_brief_ready,
    page_has_required_worker_artifacts,
    page_is_worker_approved,
    refresh_phase_status,
    required_pages,
    resolve_run_path,
)


def classify_page(run_dir: Path, page: dict) -> dict:
    artifacts = page_artifacts(page)
    deferred_status = str(page.get("deferred_status") or "not_deferred")
    brief_ok = page_brief_ready(run_dir, page)
    worker_ok, missing_worker = page_has_required_worker_artifacts(run_dir, page)
    approved = page_is_worker_approved(run_dir, page)
    status = str(page.get("status") or "").lower()

    if deferred_status == "user-approved deferred":
        state = "deferred"
    elif deferred_status in BLOCKED_STATUSES or status in BLOCKED_STATUSES:
        state = "blocked"
    elif approved:
        state = "approved"
    elif brief_ok:
        state = "ready_for_subagent"
    else:
        state = "missing_brief"

    missing = []
    if not brief_ok:
        missing.append("brief_path")
    if not worker_ok:
        missing.extend(missing_worker)

    return {
        "page_id": page.get("page_id"),
        "page_name": page.get("page_name"),
        "state": state,
        "brief_path": artifacts.get("brief_path"),
        "worker_dir": artifacts.get("worker_dir"),
        "missing": sorted(set(missing)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Show design-doc-to-ui page job status and next SubAgent batch.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--batch-size", type=int, default=6)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    manifest = load_manifest(run_dir)
    phase_status = refresh_phase_status(manifest, run_dir)

    batch_size = min(max(args.batch_size, 1), 6)
    pages = [classify_page(run_dir, page) for page in required_pages(manifest)]
    ready = [page for page in pages if page["state"] == "ready_for_subagent"]

    output = {
        "run_dir": str(run_dir),
        "max_active_subagents": 6,
        "requested_batch_size": args.batch_size,
        "effective_batch_size": batch_size,
        "phase_status": phase_status,
        "counts": {
            "required": len(pages),
            "approved": sum(1 for page in pages if page["state"] == "approved"),
            "ready_for_subagent": len(ready),
            "missing_brief": sum(1 for page in pages if page["state"] == "missing_brief"),
            "blocked": sum(1 for page in pages if page["state"] == "blocked"),
            "deferred": sum(1 for page in pages if page["state"] == "deferred"),
        },
        "next_batch": ready[:batch_size],
        "pages": pages,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
