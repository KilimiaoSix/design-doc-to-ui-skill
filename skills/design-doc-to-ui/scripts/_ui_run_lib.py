from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_FILE = "ui-run.json"

REQUIRED_BRIEF_FIELDS = [
    "page_id",
    "page_name",
    "source_page_ref",
    "output_language",
    "endpoint",
    "required_for_delivery",
    "purpose",
    "prototype_interactions",
    "route_targets",
    "state_requirements",
]

TERMINAL_DEFERRED_STATUSES = {"user-approved deferred", "user_approved_deferred"}
BLOCKED_STATUSES = {"blocked", "infeasible"}
APPROVED_STATUSES = {"approved", "pass", "passed"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_manifest(run_dir: Path) -> dict[str, Any]:
    path = run_dir / RUN_FILE
    if not path.exists():
        raise FileNotFoundError(f"Missing {RUN_FILE}: {path}")
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{RUN_FILE} must contain a JSON object")
    return data


def save_manifest(run_dir: Path, manifest: dict[str, Any]) -> None:
    write_json(run_dir / RUN_FILE, manifest)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def to_run_relative(run_dir: Path, path: Path) -> str:
    path = path.resolve()
    run_dir = run_dir.resolve()
    try:
        return as_posix(path.relative_to(run_dir))
    except ValueError:
        return str(path)


def resolve_run_path(run_dir: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return run_dir / path


def ensure_dirs(run_dir: Path, names: list[str]) -> dict[str, str]:
    directories: dict[str, str] = {}
    for name in names:
        path = run_dir / name
        path.mkdir(parents=True, exist_ok=True)
        directories[name.replace("-", "_")] = name
    return directories


def page_slug_from_name(name: str, index: int) -> str:
    lowered = name.lower()
    known = [
        ("启动", "splash"),
        ("欢迎", "welcome"),
        ("首页", "home"),
        ("主页", "home"),
        ("详情", "detail"),
        ("岗位", "job-detail"),
        ("职位", "job-detail"),
        ("面试准备", "interview-prep"),
        ("准备", "prep"),
        ("复盘", "review"),
        ("会员", "membership"),
        ("订阅", "subscription"),
        ("错误", "error"),
        ("失败", "error"),
        ("空状态", "empty"),
        ("设置", "settings"),
        ("profile", "profile"),
        ("home", "home"),
        ("detail", "detail"),
        ("review", "review"),
        ("error", "error"),
    ]
    for marker, slug in known:
        if marker in lowered:
            return slug

    chars: list[str] = []
    last_dash = False
    for char in lowered:
        if char.isascii() and char.isalnum():
            chars.append(char)
            last_dash = False
        elif char in {"-", "_", " "} and not last_dash:
            chars.append("-")
            last_dash = True
    slug = "".join(chars).strip("-")
    return slug or f"page-{index:02d}"


def unique_page_id(base: str, used: set[str], index: int) -> str:
    candidate = base or f"page-{index:02d}"
    if candidate not in used:
        used.add(candidate)
        return candidate
    suffix = 2
    while f"{candidate}-{suffix}" in used:
        suffix += 1
    unique = f"{candidate}-{suffix}"
    used.add(unique)
    return unique


def page_artifacts(page: dict[str, Any]) -> dict[str, Any]:
    artifacts = page.setdefault("artifacts", {})
    if not isinstance(artifacts, dict):
        artifacts = {}
        page["artifacts"] = artifacts
    return artifacts


def required_pages(manifest: dict[str, Any], include_blocked: bool = True) -> list[dict[str, Any]]:
    pages = manifest.get("page_inventory") or []
    result = []
    for page in pages:
        if not isinstance(page, dict):
            continue
        if not page.get("required_for_delivery"):
            continue
        deferred_status = str(page.get("deferred_status") or "not_deferred")
        if deferred_status in TERMINAL_DEFERRED_STATUSES:
            continue
        if not include_blocked and deferred_status in BLOCKED_STATUSES:
            continue
        result.append(page)
    return result


def find_page(manifest: dict[str, Any], page_id: str) -> dict[str, Any]:
    for page in manifest.get("page_inventory") or []:
        if isinstance(page, dict) and page.get("page_id") == page_id:
            return page
    raise KeyError(f"Unknown page_id: {page_id}")


def worker_result_status(run_dir: Path, page: dict[str, Any]) -> str | None:
    artifacts = page_artifacts(page)
    result_path = resolve_run_path(run_dir, artifacts.get("worker_result_path"))
    if not result_path or not result_path.exists():
        return None
    try:
        result = load_json(result_path)
    except Exception:
        return None
    status = result.get("status") or result.get("review_status") or result.get("approval_status")
    return str(status).lower() if status is not None else None


def final_image_path_from_result(run_dir: Path, result_path: Path) -> Path | None:
    try:
        result = load_json(result_path)
    except Exception:
        return None
    value = (
        result.get("final_image")
        or result.get("finalImage")
        or result.get("final_image_path")
        or result.get("finalImagePath")
    )
    if not value:
        return None
    path = Path(str(value))
    if path.is_absolute():
        return path
    return result_path.parent / path


def page_has_required_worker_artifacts(run_dir: Path, page: dict[str, Any]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    artifacts = page_artifacts(page)
    for key in ["worker_result_path", "review_path", "prompt_history_path", "final_image_path"]:
        path = resolve_run_path(run_dir, artifacts.get(key))
        if not path or not path.exists():
            missing.append(key)
    return not missing, missing


def page_is_worker_approved(run_dir: Path, page: dict[str, Any]) -> bool:
    status = worker_result_status(run_dir, page)
    has_artifacts, _ = page_has_required_worker_artifacts(run_dir, page)
    return has_artifacts and status in APPROVED_STATUSES


def style_contract_locked(run_dir: Path, manifest: dict[str, Any]) -> bool:
    artifacts = manifest.get("artifacts") or {}
    path = resolve_run_path(run_dir, artifacts.get("global_style_contract"))
    if not path or not path.exists():
        return False
    try:
        data = load_json(path)
    except Exception:
        return True
    if isinstance(data, dict):
        status = str(data.get("status") or "").lower()
        return bool(data.get("locked")) or status in {"locked", "approved", "selected"}
    return True


def audit_passed(run_dir: Path, manifest: dict[str, Any]) -> bool:
    artifacts = manifest.get("artifacts") or {}
    path = resolve_run_path(run_dir, artifacts.get("main_audit"))
    if not path or not path.exists():
        return False
    try:
        data = load_json(path)
    except Exception:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        return "passed" in text or "通过" in text
    if not isinstance(data, dict):
        return False
    status = str(data.get("status") or data.get("result") or "").lower()
    return bool(data.get("passed")) or status in APPROVED_STATUSES


def structured_doc_ready(run_dir: Path, manifest: dict[str, Any]) -> bool:
    artifacts = manifest.get("artifacts") or {}
    path = resolve_run_path(run_dir, artifacts.get("structured_design_doc"))
    return bool(path and path.exists() and path.stat().st_size > 0)


def page_brief_ready(run_dir: Path, page: dict[str, Any]) -> bool:
    path = resolve_run_path(run_dir, page_artifacts(page).get("brief_path"))
    if not path or not path.exists():
        return False
    try:
        brief = load_json(path)
    except Exception:
        return False
    return all(field in brief for field in REQUIRED_BRIEF_FIELDS)


def active_subagents(manifest: dict[str, Any]) -> list[Any]:
    active = manifest.get("active_subagents") or manifest.get("subagents_active") or []
    if isinstance(active, list):
        return active
    return [active]


def refresh_phase_status(manifest: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    status = manifest.setdefault("phase_status", {})
    pages = required_pages(manifest)
    status["all_page_briefs_ready"] = bool(pages) and all(page_brief_ready(run_dir, page) for page in pages)
    status["style_contract_locked"] = style_contract_locked(run_dir, manifest)
    status["all_required_designs_approved"] = bool(pages) and all(
        page_is_worker_approved(run_dir, page) for page in pages
    )
    status["main_audit_passed"] = audit_passed(run_dir, manifest)
    status["structured_design_doc_ready"] = structured_doc_ready(run_dir, manifest)
    status["no_active_subagents"] = not active_subagents(manifest)
    allowed = all(
        [
            status["style_contract_locked"],
            status["all_page_briefs_ready"],
            status["all_required_designs_approved"],
            status["main_audit_passed"],
            status["structured_design_doc_ready"],
            status["no_active_subagents"],
        ]
    )
    status["react_allowed"] = allowed
    # Kept as html_allowed for backward compatibility with existing manifests.
    status["html_allowed"] = allowed
    return status
