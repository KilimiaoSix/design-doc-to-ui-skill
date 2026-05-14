from __future__ import annotations

import argparse
import json
from pathlib import Path

from _ui_run_lib import (
    final_image_path_from_result,
    find_page,
    load_json,
    load_manifest,
    page_artifacts,
    refresh_phase_status,
    resolve_run_path,
    save_manifest,
    sha256_file,
    to_run_relative,
)


def require_file(label: str, path: Path | None) -> Path:
    if not path or not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a page SubAgent worker result in ui-run.json.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--worker-dir", help="Worker output directory. Defaults to manifest worker_dir.")
    parser.add_argument("--worker-result", help="worker-result.json path.")
    parser.add_argument("--review", help="review.md path.")
    parser.add_argument("--prompt-history", help="prompt-history.md path.")
    parser.add_argument("--final-image", help="Final image path. If omitted, read from worker-result.json.")
    parser.add_argument("--status", help="Override worker status.")
    parser.add_argument("--main-audit-status", default="pending")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    manifest = load_manifest(run_dir)
    page = find_page(manifest, args.page_id)
    artifacts = page_artifacts(page)

    worker_dir = Path(args.worker_dir) if args.worker_dir else resolve_run_path(run_dir, artifacts.get("worker_dir"))
    if worker_dir and not worker_dir.is_absolute():
        worker_dir = run_dir / worker_dir
    worker_dir = require_file("worker directory", worker_dir)

    worker_result = Path(args.worker_result) if args.worker_result else worker_dir / "worker-result.json"
    review = Path(args.review) if args.review else worker_dir / "review.md"
    prompt_history = Path(args.prompt_history) if args.prompt_history else worker_dir / "prompt-history.md"
    if not worker_result.is_absolute():
        worker_result = run_dir / worker_result
    if not review.is_absolute():
        review = run_dir / review
    if not prompt_history.is_absolute():
        prompt_history = run_dir / prompt_history

    worker_result = require_file("worker-result.json", worker_result)
    review = require_file("review.md", review)
    prompt_history = require_file("prompt-history.md", prompt_history)

    final_image = Path(args.final_image) if args.final_image else final_image_path_from_result(run_dir, worker_result)
    if final_image and not final_image.is_absolute():
        final_image = run_dir / final_image
    final_image = require_file("final image", final_image)

    result = load_json(worker_result)
    status = args.status or result.get("status") or result.get("review_status") or result.get("approval_status") or "unknown"

    artifacts["worker_dir"] = to_run_relative(run_dir, worker_dir)
    artifacts["worker_result_path"] = to_run_relative(run_dir, worker_result)
    artifacts["review_path"] = to_run_relative(run_dir, review)
    artifacts["prompt_history_path"] = to_run_relative(run_dir, prompt_history)
    artifacts["final_image_path"] = to_run_relative(run_dir, final_image)
    artifacts["final_image_sha256"] = sha256_file(final_image)
    artifacts["main_audit_status"] = args.main_audit_status
    page["status"] = str(status).lower()

    refresh_phase_status(manifest, run_dir)
    save_manifest(run_dir, manifest)

    output = {
        "page_id": args.page_id,
        "status": page["status"],
        "final_image": artifacts["final_image_path"],
        "final_image_sha256": artifacts["final_image_sha256"],
        "react_allowed": manifest["phase_status"].get("react_allowed", False),
        "html_allowed": manifest["phase_status"].get("html_allowed", False),
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
