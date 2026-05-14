# Design Doc To UI Skill

[中文文档](README.zh-CN.md)

Installable Codex skill for converting product/design documents into complete reviewed UI design packages.

This repository follows the common Codex skill catalog layout:

```text
skills/
  design-doc-to-ui/
    SKILL.md
    agents/
    references/
    assets/
    scripts/
```

## What It Does

`design-doc-to-ui` turns PRDs, design docs, Feishu/Lark docs, Markdown specs, wireframes, screenshots, and brand assets into:

- source-backed page inventory and requirements summary;
- scripted `ui-run.json` manifests and gate validation;
- custom style exploration with SubAgent-generated visual samples;
- one imagegen-generated and reviewed UI image per required page;
- per-page SubAgent review records;
- structured design documentation in the request language, with the generated page images embedded;
- a runnable local React frontend project that visually recreates the approved AI page images and implements interactions;
- optional Feishu/Lark document upload when requested;
- optional Figma output when requested, matching the React prototype's style and interaction model.

The skill is intentionally strict: it blocks incomplete delivery instead of silently reducing scope to a small pilot flow.

## Key Guarantees

- Every required source page must have its own page brief.
- Every required page image must be generated and reviewed by a page-level SubAgent.
- At most 6 SubAgents may be active at the same time; larger runs are batched.
- React and Figma work starts only after the design images, main audit, and structured design document are complete.
- `validate_design_run.py` blocks React/Figma until page briefs, worker artifacts, final images, main audit, and the structured design document all exist.
- `build_prototype_data.py --template react --copy-template` generates a Vite React starter and route data from the approved run package so required pages are not dropped.
- The React prototype must use real components and interactions, not full-screen screenshot switching.
- Final docs, React metadata, and optional Feishu/Figma outputs follow the user's request language.

## Install

Inside Codex, ask the built-in skill installer:

```text
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui
```

Or run the installer script directly:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo KilimiaoSix/design-doc-to-ui-skill \
  --path skills/design-doc-to-ui
```

Restart Codex after installation so it reloads skill metadata.

## Update An Existing Install

The installer aborts if `design-doc-to-ui` already exists in your skills directory. To update an existing install, remove or back up the old folder first, then reinstall:

```bash
rm -rf ~/.codex/skills/design-doc-to-ui
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo KilimiaoSix/design-doc-to-ui-skill \
  --path skills/design-doc-to-ui
```

On Windows PowerShell:

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\design-doc-to-ui"
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo KilimiaoSix/design-doc-to-ui-skill `
  --path skills/design-doc-to-ui
```

Restart Codex after updating.

## Usage

Ask Codex to use the skill with a source document, for example:

```text
Use $design-doc-to-ui to convert this PRD into a reviewed mobile app UI package with a structured design document and runnable React prototype.
```

The skill will:

1. ingest the source document and assets;
2. derive a complete page inventory and initialize `ui-run.json`;
3. explore and sample custom visual directions through SubAgents;
4. generate and review every required page image with SubAgents;
5. register every worker result in the manifest;
6. write the structured design document with page images;
7. run the design-completion script gate;
8. build a local React prototype from approved design images and documentation;
9. run a React visual parity and interaction audit;
10. optionally upload to Feishu/Lark only when requested;
11. optionally create or update Figma output only when requested.

## Scripted Gates

The skill includes deterministic helper scripts under `skills/design-doc-to-ui/scripts/`:

```bash
python skills/design-doc-to-ui/scripts/prepare_ui_run.py --source prd.md --run-dir out/minihire --requested-output-language zh-CN
python skills/design-doc-to-ui/scripts/ui_job_status.py --run-dir out/minihire
python skills/design-doc-to-ui/scripts/record_ui_worker_result.py --run-dir out/minihire --page-id home
python skills/design-doc-to-ui/scripts/validate_design_run.py --run-dir out/minihire --phase design-completion
python skills/design-doc-to-ui/scripts/build_prototype_data.py --run-dir out/minihire --template react --copy-template
```

These scripts enforce the HatchPet-style manifest pattern: page count stays dynamic, but `page_inventory` becomes the single source of truth for worker jobs, approved images, docs, React routes, and React/Figma eligibility.

## Validation

The skill folder validates with the official skill creator validator:

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui
```

Representative script checks:

- `prepare_ui_run.py` extracts a MiniHire fixture into 7 required pages.
- `ui_job_status.py --batch-size 12` caps the next worker batch at 6.
- `validate_design_run.py --phase design-completion` returns `react_allowed=false` before design artifacts and docs exist.
- With mock worker artifacts, locked style contract, main audit, and structured design doc, the gate passes.
- `build_prototype_data.py --template react --copy-template` creates a runnable React project with all required routes.
- Missing brief, worker result, final image, structured doc, or prototype route each produce explicit blocker codes.

Expected result:

```text
Skill is valid!
```

## Notes

- Keep repository-level docs like this README at the repo root.
- Do not add README/changelog files inside `skills/design-doc-to-ui/`; Codex skill folders should stay focused on executable skill instructions and resources.
- Large style-board images are included intentionally because the skill uses them as visual references and guardrails.
