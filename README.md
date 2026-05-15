# Design Doc To UI Skill

[中文文档](README.zh-CN.md)

Installable Codex skill package for converting product/design documents into complete reviewed UI design deliverables.

This repository now uses a main skill plus three companion skills:

```text
skills/
  design-doc-to-ui/                 # main orchestrator
  design-doc-to-ui-feishu-doc/      # rich Feishu/Lark document delivery
  design-doc-to-ui-figma-replica/   # editable Figma replica delivery
  design-doc-to-ui-visual-audit/    # React/Figma visual parity audit
```

## What It Does

`design-doc-to-ui` turns PRDs, design docs, Feishu/Lark docs, Markdown specs, wireframes, screenshots, and brand assets into:

- source-backed `page_inventory` and requirements summary;
- scripted `ui-run.json` manifests and gate validation;
- custom style exploration with SubAgent-generated visual samples;
- one imagegen-generated and reviewed UI image per required page;
- per-page SubAgent review records;
- a structured design document in the request language, including design thinking, page linkage, and generated page images;
- a runnable local React frontend project that starts from a main-agent scaffold, uses page-level SubAgents for detailed page implementation, visually recreates the approved AI page images, and implements verified interactions;
- optional rich Feishu/Lark document delivery when requested;
- optional editable Figma replica delivery when requested, using page-level frame workers plus global prototype-link validation.

The skill is intentionally strict: incomplete page coverage, missing SubAgent evidence, missing audits, or premature React/Figma work are blockers.

## Companion Skills

The main skill does not silently downgrade companion work:

- `design-doc-to-ui-visual-audit` is required for React visual parity and any Figma parity check. Every required page must score at least `0.80`.
- `design-doc-to-ui-feishu-doc` is required when Feishu/Lark delivery is requested. It requires rich document structure, design narrative, diagrams, tables, callouts, and `qa/feishu-doc-audit.json`.
- `design-doc-to-ui-figma-replica` is required when Figma delivery is requested. It uses approved AI images plus React screenshots as references and must produce editable frames, not full-screen pasted screenshots.

If a required companion skill is missing or unreadable, that delivery stage is blocked.

## Key Guarantees

- Every required source page must have its own page brief.
- Every required page image must be generated and reviewed by a page-level SubAgent.
- At most 6 SubAgents may be active at the same time; larger runs are batched.
- React and Figma work starts only after design images, main audit, and structured design document are complete.
- React output is a component-level Vite project, not an image viewer. The main agent must first create the app shell, route registry, style system, page slots, and worker ownership map.
- React page workers must produce `visual-decomposition.json`, `dom-element-inventory.json`, and `visual-replica-audit.json` before registration in `prototype/qa/react-page-worker-registry.json`; the main agent must pass `react-navigation-audit.json` for global route targets, cross-page state, and whole-flow navigation.
- React demo usability is gated by `prototype/qa/react-usability-audit.json`: every page must be scrollable when content exceeds the viewport, bottom content must be reachable, and a right-side page switcher must navigate to every required route without affecting visual parity screenshots.
- Figma output must start from `qa/figma-scaffold-audit.json`, register page workers in `qa/figma-page-worker-registry.json`, and pass `qa/figma-prototype-link-plan.json` plus `qa/figma-integration-audit.json`. Each Figma page worker must also produce `visual-decomposition.json`, `figma-layer-inventory.json`, and `figma-visual-replica-audit.json`.
- Redo/revision work must write `qa/revision-plan.json`, start the expected SubAgents for affected page images, React pages, Figma pages, or Feishu delivery artifacts, and register them in `qa/revision-subagent-registry.json`; direct main-thread implementation of affected revision work is a blocker.
- React and Figma visual parity are judged per page. Average score cannot hide a failed page.
- Final docs, React metadata, and optional Feishu/Figma outputs follow the user's request language.

## Install

Install all four skill folders. In Codex, ask the built-in installer for each path:

```text
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-feishu-doc
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-figma-replica
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-visual-audit
```

Or run the installer script directly:

```bash
for skill in \
  design-doc-to-ui \
  design-doc-to-ui-feishu-doc \
  design-doc-to-ui-figma-replica \
  design-doc-to-ui-visual-audit
do
  python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
    --repo KilimiaoSix/design-doc-to-ui-skill \
    --path "skills/$skill"
done
```

Windows PowerShell:

```powershell
$skills = @(
  "design-doc-to-ui",
  "design-doc-to-ui-feishu-doc",
  "design-doc-to-ui-figma-replica",
  "design-doc-to-ui-visual-audit"
)
foreach ($skill in $skills) {
  python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
    --repo KilimiaoSix/design-doc-to-ui-skill `
    --path "skills/$skill"
}
```

Restart Codex after installation so skill metadata reloads.

## Update Existing Install

The installer aborts when a target skill folder already exists. Remove or back up all four folders first, then reinstall:

```powershell
$skills = @(
  "design-doc-to-ui",
  "design-doc-to-ui-feishu-doc",
  "design-doc-to-ui-figma-replica",
  "design-doc-to-ui-visual-audit"
)
foreach ($skill in $skills) {
  Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\$skill"
}
```

Then run the install commands above and restart Codex.

## Usage

Ask Codex to use the main skill with a source document:

```text
Use $design-doc-to-ui to convert this PRD into a reviewed mobile app UI package with a structured design document and runnable React prototype.
```

The main flow:

1. Ingest source document and assets.
2. Derive complete `page_inventory` and initialize `ui-run.json`.
3. Explore custom visual directions through SubAgents.
4. Generate and review every required page image with one page-level SubAgent each.
5. Register worker results in the manifest.
6. Write a structured design document with design thinking, page linkage, and page images.
7. Run the design-completion gate.
8. Build the React scaffold, register page-level React workers, and run global navigation audit.
9. Run visual parity audit and repair until every page reaches `0.80`.
10. Upload rich Feishu/Lark docs only when requested.
11. Create or update Figma replica only when requested.
12. Run final delivery validation.

## Scripted Gates

The main skill includes deterministic helper scripts under `skills/design-doc-to-ui/scripts/`:

```bash
python skills/design-doc-to-ui/scripts/prepare_ui_run.py --source prd.md --run-dir out/minihire --requested-output-language zh-CN
python skills/design-doc-to-ui/scripts/ui_job_status.py --run-dir out/minihire
python skills/design-doc-to-ui/scripts/record_ui_worker_result.py --run-dir out/minihire --page-id home
python skills/design-doc-to-ui/scripts/validate_companion_skills.py --run-dir out/minihire --require-all
python skills/design-doc-to-ui/scripts/validate_design_run.py --run-dir out/minihire --phase design-completion
python skills/design-doc-to-ui/scripts/build_prototype_data.py --run-dir out/minihire --template react --copy-template
python skills/design-doc-to-ui/scripts/record_react_page_worker_result.py --run-dir out/minihire --page-id home --worker-result prototype/qa/react-page-workers/home/worker-result.json --interaction-audit prototype/qa/react-page-workers/home/interaction-audit.json --visual-decomposition prototype/qa/react-page-workers/home/visual-decomposition.json --dom-inventory prototype/qa/react-page-workers/home/dom-element-inventory.json --visual-replica-audit prototype/qa/react-page-workers/home/visual-replica-audit.json --review prototype/qa/react-page-workers/home/review.md
python skills/design-doc-to-ui/scripts/record_figma_page_worker_result.py --run-dir out/minihire --page-id home --worker-result qa/figma-page-workers/home/worker-result.json --frame-audit qa/figma-page-workers/home/frame-audit.json --visual-decomposition qa/figma-page-workers/home/visual-decomposition.json --layer-inventory qa/figma-page-workers/home/figma-layer-inventory.json --visual-replica-audit qa/figma-page-workers/home/figma-visual-replica-audit.json --review qa/figma-page-workers/home/review.md
python skills/design-doc-to-ui/scripts/record_revision_subagent_result.py --run-dir out/minihire --revision-id rev-002 --scope react-page --page-id home --channel react --subagent-id <spawn_agent_id> --worker-result prototype/qa/react-page-workers/home/worker-result.json --review prototype/qa/react-page-workers/home/review.md
python skills/design-doc-to-ui/scripts/validate_design_run.py --run-dir out/minihire --phase delivery
```

`page_inventory` remains dynamic and source-derived, but becomes the single source of truth for page briefs, worker jobs, approved images, docs, React routes, Feishu/Figma eligibility, and final delivery gates.

## Validation

Validate each skill folder:

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-feishu-doc
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-figma-replica
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-visual-audit
```

Representative regression checks:

- MiniHire fixture extracts 7 required pages.
- `ui_job_status.py --batch-size 12` caps the next worker batch at 6.
- `validate_design_run.py --phase design-completion` returns `react_allowed=false` before design artifacts and docs exist.
- With mock worker artifacts, locked style contract, main audit, and structured design doc, the design-completion gate passes.
- `build_prototype_data.py --template react --copy-template` creates a runnable React project with all required routes.
- Missing React scaffold audit, React page visual decomposition, React DOM inventory, React page visual replica audit, React page worker registry, React navigation audit, React usability audit, Figma scaffold audit, Figma page visual decomposition, Figma layer inventory, Figma visual replica audit, Figma page worker registry, Figma prototype link plan, Figma integration audit, revision SubAgent registry when a revision plan exists, companion skills, visual parity audit, Feishu audit, routes, page briefs, worker results, final images, or structured docs produce explicit blocker codes.

## Notes

- Keep repository-level docs at the repo root.
- Do not add README/changelog files inside individual skill folders; skill folders should contain executable instructions, references, scripts, and assets only.
- Feishu/Figma delivery is optional, but once requested it is gated by the corresponding companion skill and audit JSON.
