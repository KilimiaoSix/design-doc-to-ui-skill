# Design Doc To UI Skill

Installable Codex skill for converting product/design documents into complete reviewed UI design packages.

This repository follows the common Codex skill catalog layout:

```text
skills/
  design-doc-to-ui/
    SKILL.md
    agents/
    references/
    assets/
```

## What It Does

`design-doc-to-ui` turns PRDs, design docs, Feishu/Lark docs, Markdown specs, wireframes, screenshots, and brand assets into:

- source-backed page inventory and requirements summary;
- custom style exploration with SubAgent-generated visual samples;
- one approved UI image per required page;
- per-page SubAgent review records;
- structured design documentation in the request language;
- real interactive local HTML prototypes;
- optional Figma prototype output when requested.

The skill is intentionally strict: it blocks incomplete delivery instead of silently reducing scope to a small pilot flow.

## Key Guarantees

- Every required source page must have its own page brief.
- Every required page image must be generated and reviewed by a page-level SubAgent.
- At most 6 SubAgents may be active at the same time; larger runs are batched.
- HTML and Figma prototypes start only after the design images and structured design document are complete.
- HTML prototypes must use real components and interactions, not full-screen screenshot switching.
- Final docs and prototype metadata follow the user's request language.

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
Use $design-doc-to-ui to convert this PRD into a full reviewed mobile app UI package and interactive HTML prototype.
```

The skill will:

1. ingest the source document and assets;
2. derive a complete page inventory;
3. explore and sample custom visual directions;
4. generate and review every required page image with SubAgents;
5. write the structured design document;
6. build the HTML prototype from approved design images and documentation;
7. optionally create or update Figma output when requested.

## Validation

The skill folder validates with the official skill creator validator:

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui
```

Expected result:

```text
Skill is valid!
```

## Notes

- Keep repository-level docs like this README at the repo root.
- Do not add README/changelog files inside `skills/design-doc-to-ui/`; Codex skill folders should stay focused on executable skill instructions and resources.
- Large style-board images are included intentionally because the skill uses them as visual references and guardrails.
