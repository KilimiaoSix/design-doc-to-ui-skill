from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from _ui_run_lib import load_manifest, save_manifest, write_json


COMPANION_KEYS = {
    "feishu_doc": "design-doc-to-ui-feishu-doc",
    "figma_replica": "design-doc-to-ui-figma-replica",
    "visual_audit": "design-doc-to-ui-visual-audit",
}


def add(blockers: list[dict[str, Any]], code: str, message: str, skill_key: str | None = None) -> None:
    item: dict[str, Any] = {"code": code, "message": message}
    if skill_key:
        item["skill_key"] = skill_key
    blockers.append(item)


def codex_home() -> Path:
    value = os.environ.get("CODEX_HOME")
    if value:
        return Path(value)
    return Path.home() / ".codex"


def candidate_skill_paths(current_skill_dir: Path, skill_name: str) -> list[Path]:
    skills_root = current_skill_dir.parent
    return [
        skills_root / skill_name / "SKILL.md",
        codex_home() / "skills" / skill_name / "SKILL.md",
    ]


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("frontmatter is not closed")
    frontmatter = text[3:end]
    data: dict[str, str] = {}
    for raw_line in frontmatter.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    if not data.get("name") or not data.get("description"):
        raise ValueError("frontmatter must contain name and description")
    return data


def resolve_skill(current_skill_dir: Path, skill_name: str) -> tuple[Path | None, str]:
    for path in candidate_skill_paths(current_skill_dir, skill_name):
        if path.exists():
            return path, ""
    return None, "not found in sibling skills or $CODEX_HOME/skills"


def required_keys(manifest: dict[str, Any], require_all: bool) -> set[str]:
    required = {"visual_audit"} if require_all else set()
    channels = manifest.get("delivery_channels") or {}
    if require_all or (channels.get("feishu") or {}).get("requested"):
        required.add("feishu_doc")
    if require_all or (channels.get("figma") or {}).get("requested"):
        required.add("figma_replica")
    if (manifest.get("prototype_policy") or {}).get("requires_visual_parity_audit", True):
        required.add("visual_audit")
    return required


def validate(run_dir: Path, require_all: bool) -> dict[str, Any]:
    manifest = load_manifest(run_dir)
    blockers: list[dict[str, Any]] = []
    skill_dir = Path(__file__).resolve().parents[1]
    companions = manifest.setdefault("companion_skills", {})
    required = required_keys(manifest, require_all)

    for key, skill_name in COMPANION_KEYS.items():
        entry = companions.setdefault(
            key,
            {
                "skill_name": skill_name,
                "required": True,
                "loaded": False,
                "path": "",
                "status": "pending",
                "blocker": "",
            },
        )
        path, missing_reason = resolve_skill(skill_dir, skill_name)
        if not path:
            entry.update({"loaded": False, "path": "", "status": "missing", "blocker": missing_reason})
            if key in required:
                add(blockers, "COMPANION_SKILL_MISSING", f"Required companion skill is missing: {skill_name}", key)
            continue
        try:
            meta = parse_frontmatter(path)
        except Exception as exc:
            entry.update({"loaded": False, "path": str(path), "status": "invalid", "blocker": str(exc)})
            if key in required:
                add(blockers, "COMPANION_SKILL_INVALID", f"Required companion skill is invalid: {skill_name}: {exc}", key)
            continue
        if meta.get("name") != skill_name:
            entry.update({"loaded": False, "path": str(path), "status": "invalid", "blocker": "frontmatter name mismatch"})
            if key in required:
                add(blockers, "COMPANION_SKILL_NAME_MISMATCH", f"Expected {skill_name}, found {meta.get('name')}", key)
            continue
        entry.update({"loaded": True, "path": str(path), "status": "loaded", "blocker": ""})

    report = {
        "run_dir": str(run_dir),
        "passed": not blockers,
        "required_companion_keys": sorted(required),
        "companion_skills": companions,
        "blockers": blockers,
    }
    write_json(run_dir / "qa" / "companion-skill-report.json", report)
    save_manifest(run_dir, manifest)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required companion skills for design-doc-to-ui delivery gates.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--require-all", action="store_true", help="Require all companion skills regardless of requested channels.")
    args = parser.parse_args()

    report = validate(Path(args.run_dir), args.require_all)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
