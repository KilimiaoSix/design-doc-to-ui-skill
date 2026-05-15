---
name: design-doc-to-ui
description: "Convert PRDs, design docs, Feishu/Lark docs, Markdown specs, prototypes, wireframes, screenshots, and brand assets into complete UI design packages with source-backed page inventory, imagegen UI images, structured design docs with design thinking, dedicated SubAgent-built runnable React prototypes, optional Feishu rich documents, optional Figma replicas, user-feedback revisions, and 80% visual parity gates. Use when Codex needs page coverage, SubAgent image generation/review, user-requested design changes, formal React demo implementation and interaction verification, React visual parity, Feishu design docs, or Figma output. Requires direct SubAgent delegation and mandatory companion skills for Feishu, Figma, and visual audit stages."
---

# Design Doc To UI

Use this skill to turn a source product/design document into an approved UI design package. The required package contains:

- a structured design document in the requested language, with design thinking, page linkage, and imagegen-generated page images for every required page;
- a runnable React frontend prototype project that visually recreates the approved AI page images and adds the declared interactions.

Optional package outputs:

- upload the design document and image attachments to Feishu/Lark only when the user asks for Feishu output;
- create/update Figma only when the user provides a Figma link/file or explicitly asks for Figma output.

## Required Workflow

1. Ingest the source document and assets.
2. Produce an `app_requirements_summary` with `source_language`, `requested_output_language`, and `page_inventory`.
3. Initialize a scripted run manifest with `scripts/prepare_ui_run.py`; `ui-run.json` becomes the single source of truth for page count, artifacts, and gates.
4. Run the SubAgent Direct-Use Gate.
5. Run the Style Exploration Gate before page generation.
6. Run the Page Coverage Gate against `ui-run.json`.
7. Create one page brief for every required page.
8. Use `scripts/ui_job_status.py` to plan page worker batches of at most 6 active SubAgents.
9. Run one page-level SubAgent for each required page to generate the UI image and complete page calibration/review.
10. After each page worker returns, use `scripts/record_ui_worker_result.py` from the main thread to register its artifacts in `ui-run.json`.
11. Run the Per-Page SubAgent Gate.
12. Perform the main-agent audit across all pages.
13. Generate a structured design document in `requested_output_language`; it must pass the Structured Design Document Quality Gate and explain source traceability, user stories, acceptance criteria, design rationale, page linkage, interaction/state matrices, component tokens, accessibility, handoff requirements, and revision history, not only list screens.
14. Write `qa/structured-design-doc-audit.json`, then run `scripts/validate_design_run.py --phase design-completion`; React/Figma remains blocked unless this passes with `react_allowed: true`.
15. Run the Companion Skill Gate for visual audit, then generate a React prototype project with `scripts/build_prototype_data.py --template react --copy-template`.
16. In the main thread, create the React scaffold first: app shell, route registry, shared layout, style tokens/CSS, base components, page slots, and page-worker ownership map. Write passing `prototype/qa/react-scaffold-audit.json` before starting React page workers.
17. Start one page-level React Prototype SubAgent per required page using `references/react-prototype-worker-prompt.md`, batching with at most 6 active SubAgents. Each page worker must build its assigned route inside the main-agent scaffold, follow the shared style system, self-review page-local interactions, and write page-level QA before returning.
18. Integrate the React app in the main thread: shared shell adjustments, route targets, cross-page state, and whole-product jump logic. Run the React Prototype Worker Gate: require the scaffold audit, every page worker result, plus aggregate `prototype/qa/react-worker-result.json` and `prototype/qa/react-interaction-audit.json` to pass, including `global_navigation_passed: true`. Screenshot/hotspot/image-browser demos are non-compliant.
19. Run the React Visual Parity Gate with `design-doc-to-ui-visual-audit`: render every required route, compare screenshots to approved AI page images, and repair until every page is at least 80% similar.
20. Optionally upload a rich Feishu/Lark design document only when requested; this stage must use `design-doc-to-ui-feishu-doc`.
21. Optionally create/update Figma only when requested; this stage must use `design-doc-to-ui-figma-replica`, start one page-level Figma Replica SubAgent per required page with at most 6 active SubAgents, then have the main agent wire global prototype links/cross-frame jumps and pass the editable-frame, frontend-handoff, asset-reconstruction, prototype-link, and 80% per-page replica gates.
22. Run `scripts/validate_design_run.py --phase delivery` and perform the Final Functional Audit on React plus any requested Feishu/Figma outputs.

Do not skip requirement summarization, SubAgent Direct-Use Gate, Style Exploration Gate, Page Coverage Gate, per-page SubAgent review, main-agent audit, Design Completion Gate, Companion Skill Gate, React Scaffold Gate, React Page Worker Gate, Visual Parity Gate, Delivery Gate, or Final Functional Audit.

Do not silently reduce scope with labels such as "pilot", "core flow", "trial", or "MVP slice". A page from `page_inventory` may be deferred only when the user explicitly approves the deferral; record it as `user-approved deferred`, not approved.

## User Feedback Revision Workflow

Read `references/user-feedback-revision.md` whenever the user says the overall design, page style, a page, a component, an element, copy, interaction, React prototype, Feishu document, or Figma replica is unsatisfactory after any draft or delivery artifact exists.

Treat feedback as a scoped revision, not as a new untracked run. First classify the feedback as one or more of:

- global style change;
- page-level layout/content change;
- element/component-level change;
- source requirement/page inventory change;
- React implementation mismatch against approved images;
- Feishu/Figma delivery mismatch against the approved design package.

Use the smallest scope that honestly satisfies the feedback. React-only fixes are allowed only when the approved design image remains valid and the rendered prototype is the artifact that drifted. If the approved image is wrong, revise the style contract, page brief, or page prompt and start a new page-level SubAgent for each affected page before updating React/Figma/Feishu.

Do not overwrite prior approved artifacts in place. Preserve the previous worker directory, final image, audit report, and delivery links as revision history when possible. New or regenerated page images still require SubAgent generation, `record_ui_worker_result.py`, main-agent audit, structured design document updates, and the normal validation gates. If a global style change affects multiple pages, update or replace `global_style_contract`, identify every affected page, and regenerate all affected approved images before claiming the revision is complete.

This workflow is built into the main skill because it depends on `ui-run.json`, page briefs, worker registration, design completion gates, visual parity gates, and optional Feishu/Figma companion stages. Split it into a separate companion skill only if revisions become a standalone task that must be invoked independently against already completed design packages; even then, the companion skill must reuse the same manifest and gates instead of creating a parallel status system.

## Scripted Run Manifest

Use the bundled scripts whenever filesystem access is available. These scripts do not replace design judgment; they prevent missing pages, forged completion, premature React/Figma work, and manifest drift.

Start every run with:

```bash
python scripts/prepare_ui_run.py --source <source.md> --run-dir <output-run-dir> --requested-output-language <language>
```

If the source page list is already extracted as JSON, pass it with `--pages-json`. If useful, `--write-brief-stubs` can create draft brief JSON files that must still be completed from the source before page generation.

Use these scripts during the run:

- `scripts/ui_job_status.py --run-dir <output-run-dir>`: show missing/ready/approved pages and the next page-worker batch, capped at 6.
- `scripts/record_ui_worker_result.py --run-dir <output-run-dir> --page-id <page_id>`: register a returned SubAgent worker directory and final image.
- `scripts/validate_design_run.py --run-dir <output-run-dir> --phase design-completion`: block or allow React/Figma.
- `scripts/validate_companion_skills.py --run-dir <output-run-dir>`: verify required companion skills are installed/readable before visual audit, Feishu, or Figma stages.
- `scripts/build_prototype_data.py --run-dir <output-run-dir> --template react --copy-template`: generate a React prototype starter project and `prototype/src/prototype-data.js` from the approved run package.
- `scripts/record_react_page_worker_result.py --run-dir <output-run-dir> --page-id <page_id>`: register a returned React page worker in `prototype/qa/react-page-worker-registry.json`.
- `scripts/record_figma_page_worker_result.py --run-dir <output-run-dir> --page-id <page_id>`: register a returned Figma page worker in `qa/figma-page-worker-registry.json`.
- `scripts/validate_design_run.py --run-dir <output-run-dir> --phase delivery`: verify visual parity and requested Feishu/Figma delivery audits.

Do not let a SubAgent edit `ui-run.json` directly. SubAgents write only their assigned worker directory; the main agent records worker artifacts with `record_ui_worker_result.py`.

## Companion Skill Gate

The main skill orchestrates delivery, but detailed Feishu, Figma, and visual audit work must be handled by companion skills.

Before a gated stage, load the required companion skill by reading its `SKILL.md`:

- Visual audit for React/Figma: `design-doc-to-ui-visual-audit`.
- Feishu/Lark rich design document: `design-doc-to-ui-feishu-doc`.
- Figma replica output: `design-doc-to-ui-figma-replica`.

Resolve companion skills in this order:

1. sibling skill in the same repository root, for example `../design-doc-to-ui-feishu-doc/SKILL.md`;
2. installed skill under `$CODEX_HOME/skills/<skill-name>/SKILL.md`.

If the required companion skill is missing, unreadable, or has invalid frontmatter, block that stage. Do not downgrade to a simplified main-thread implementation.

Use:

```bash
python scripts/validate_companion_skills.py --run-dir <output-run-dir>
```

For release or installation validation, use `--require-all`.

## Source Ingestion

Read `references/source-ingestion.md` when handling input sources.

- For Feishu/Lark wiki/doc URLs, use the `lark-doc` skill. Extract text, tables, references, images, and source outline/heading IDs. Download relevant images into the project output folder.
- For Markdown, parse the heading structure, local image links, remote image links, tables, and code blocks.
- Normalize every source into `source_bundle` and `app_requirements_summary` before generating images.
- Set `requested_output_language` from the user's request language. If the user gives no clear preference, use the source document's primary language.

## SubAgent Direct-Use Gate

SubAgent use is part of this skill's required workflow. Do not ask the user for a separate SubAgent confirmation step.

Before spawning any SubAgent:

- Create the required SubAgent directly when the SubAgent tool is available.
- Keep at most 6 SubAgents active at the same time across this skill run, including style-sampling workers, page-generation workers, and regeneration workers.
- If more than 6 workers are needed, start them in batches. Wait for at least one active worker to finish before starting another batch.
- Do not ask the user to confirm normal SubAgent use.
- If the SubAgent tool, image generation tool, or required file access is technically unavailable, stop before style sampling/page image generation and report the exact blocked capability.
- Do not work around a technical block by generating images in the main thread or by replacing image generation with local mockups.

## Style Exploration Gate

Read `references/style-gate.md` before page image generation.

- First derive product-specific visual principles from the source, brand assets, target users, emotional tone, and interaction model.
- Use `assets/style-catalog/catalog.md` and `assets/style-catalog/style-presets.json` only as references and guardrails, not as the default final style set.
- Create 2-3 custom style directions unless the user explicitly requests one known style or provides strict brand guidelines.
- Generate style samples in SubAgents with `image_gen`: one SubAgent per candidate style direction, while respecting the global 6-active-SubAgent limit.
- Main agent reviews style samples, rejects template-looking directions, and locks the selected direction into `global_style_contract`.
- If SubAgent creation or style-sample generation is technically unavailable, block style exploration instead of silently choosing a catalog preset.

## Page Coverage Gate

Read `references/page-brief-schema.md` before generating screens.

Create `page_inventory` from the source outline, product sections, prototype images, screen lists, user flows, and explicit requirements. Treat `page_inventory` as the delivery source of truth.

When `ui-run.json` exists, treat its `page_inventory` as the canonical delivery inventory. If you discover missing source pages later, update `app_requirements_summary`, rerun or repair `ui-run.json`, and re-check coverage before image generation.

Before page generation, verify:

- Every required source page has `required_for_delivery: true`.
- Every required source page has one page brief.
- Optional pages are listed and either generated, explicitly deferred by the user, or marked blocked with the reason.
- No required page is collapsed into a single overview image or merged with another page.

If the coverage check fails, fix the inventory or briefs before starting image generation.

## Image Generation And Per-Page Review

Read `references/image-generation-loop.md` and `references/subagent-worker-prompt.md`.

All final UI screen images and page calibration loops must run in SubAgents. The main agent must not call `image_gen` for final UI screen generation and must not perform the per-page image calibration itself.

Before any image-generation task:

- Create the required SubAgent directly.
- Respect the global 6-active-SubAgent limit. For more than 6 required pages, generate pages in batches and start the next worker only after another worker finishes.
- If SubAgents are unavailable or unable to access `image_gen`, mark the image-generation phase blocked and stop before final screen generation. Do not fall back to generating UI screens in the main thread.

Use exactly one page-level SubAgent for each required page. A SubAgent may handle important states for the same page only when the page brief explicitly scopes those states; it must not own multiple source pages.

Each page-generation SubAgent must:

- Build the prompt from `app_requirements_summary`, `global_style_contract`, and the assigned page brief.
- Generate the screen image with `image_gen`.
- Review the result against the page brief, source evidence, output language, style contract, endpoint rules, and artifact quality.
- Iterate as long as the result is improving.
- Write `final_image`, `prompt-history.md`, `review.md`, and `worker-result.json` in its assigned output directory.
- Stop only when approved, blocked by ambiguity, stalled, or infeasible.

## Per-Page SubAgent Gate

After workers return, verify that every required page has:

- A disjoint worker output directory.
- `worker-result.json`.
- `review.md`.
- `prompt-history.md`.
- A final image file referenced by `worker-result.json`.
- Status `approved`, `blocked`, `infeasible`, or `user-approved deferred`.

Do not count a page as approved when any required worker artifact is missing.

Run `scripts/record_ui_worker_result.py` for each returned page worker before this gate. Then run `scripts/ui_job_status.py` to verify there are no unregistered or missing required pages.

## Main Audit

Read `references/main-audit.md` after page workers return.

SubAgent approval is not final. The main agent must audit the full screen set against the original requirements and style contract. If a page fails, revise the brief or prompt and start a new SubAgent worker for that page. If SubAgent delegation is technically unavailable, mark regeneration blocked instead of regenerating in the main thread. If repeated attempts fail, reassess the requirement and mark the page infeasible only after explaining why.

Main-agent approval is required before generating final design documents and the React prototype.

## Design Completion Gate

Do not start React or Figma work until the design phase is complete.

The design phase is complete only when:

- `global_style_contract` is locked.
- Every non-deferred required page has a page brief.
- Every non-deferred required page has a SubAgent `worker-result.json`, `review.md`, `prompt-history.md`, and final design image.
- Every non-deferred required page has status `approved` after main-agent audit.
- The main-agent audit has passed across all approved design images.
- No style-sampling, page-generation, or regeneration SubAgent is still running.

If any required page is `blocked`, `infeasible`, or missing an approved final image, do not generate React/Figma by default. Generate a partial React/Figma prototype only if the user explicitly approves a partial prototype after the missing pages are listed.

After the structured design document exists, enforce this gate with:

```bash
python scripts/validate_design_run.py --run-dir <output-run-dir> --phase design-completion
```

Proceed to React/Figma only when the script reports `passed: true` and `react_allowed: true`. Existing manifests may also expose the backward-compatible `html_allowed` field with the same value.

## Structured Design Document

Read `references/design-doc-output.md` and `references/design-doc-quality-gate.md`.

Generate the structured design document before React/Figma implementation. Include the product summary, page inventory, user flow, visual style contract, screen specs for every required page, UI images, interaction notes, per-page review results, main-agent audit, prototype implementation requirements, and open questions. Mark React/Figma/Feishu paths as `pending` at this stage, then update the document after those outputs are created.

The document must include a design narrative and a delivery-grade specification: design proposition, source traceability, user stories and acceptance criteria, user mindset, core tension, information architecture, page linkage, state strategy, component/token principles, accessibility/content notes, handoff acceptance criteria, and risks. A page-by-page catalog, screenshot directory, or delivery status report is non-compliant.

Before React/Figma/Feishu work, audit the document against `references/design-doc-quality-gate.md` and write `qa/structured-design-doc-audit.json`. The Design Completion Gate must fail if the audit is missing, if `passed` is not true, if `quality_score < 0.85`, if any required quality pillar is false, if documented page specs do not cover all required pages, or if the document is effectively only a screenshot catalog.

## React Prototype

Read `references/html-prototype.md` and `references/react-prototype-worker-prompt.md`.

Do not begin React implementation until the Design Completion Gate has passed and the structured design document exists. Build the React prototype from the approved design images, structured design document, original requirements, page briefs, and worker reviews. Do not build React from requirements alone while design images are still pending. After React is generated and audited, update the structured design document with the React project path, run command, React worker result, interaction audit, visual parity result, and audit result.

Generate or verify the React prototype data layer with:

```bash
python scripts/build_prototype_data.py --run-dir <output-run-dir> --template react --copy-template
```

Use the generated `prototype/src/prototype-data.js` as the route/page coverage baseline. Custom React components/CSS may extend it, but must not remove required routes or declared interactions.

Default output is a local folder, not a hosted link:

```text
prototype/
  index.html
  package.json
  src/
    main.jsx
    prototype-data.js
    styles.css
  assets/
  screens/
```

Build a component-level interactive React prototype through a main-agent scaffold plus page-level React Prototype SubAgents. The main agent first creates the app shell, route registry, shared layout, style tokens/CSS, base components, page slots, and worker ownership map, then writes `prototype/qa/react-scaffold-audit.json`. Each required page then gets its own worker, and workers run in batches with at most 6 active SubAgents. After each worker returns, the main thread records it with `scripts/record_react_page_worker_result.py` into `prototype/qa/react-page-worker-registry.json`. The React UI must basically replicate the approved AI-generated page images page by page: layout, hierarchy, component shapes, spacing, color, typography, navigation, states, and main visual motifs must be close enough for product/design review without reinterpreting the screen. Use generated images only as visual references, thumbnails, review attachments, or cropped/local decorative assets when needed; do not use full-screen images as the primary UI implementation. If only an image browser, full-page screenshot wrapper, or hotspot demo can be produced, mark the prototype `blocked/non-compliant` and do not present it as complete.

Before visual parity scoring, require the scaffold audit, page-worker registry, every page-level worker result under `prototype/qa/react-page-workers/`, `prototype/qa/react-navigation-audit.json`, plus aggregate `prototype/qa/react-worker-result.json` and `prototype/qa/react-interaction-audit.json` to pass. The aggregate audit must confirm page workers used the shared scaffold/style system and that the main agent verified global router behavior, cross-page state, route targets, and whole-product jumps. After React is rendered, use `design-doc-to-ui-visual-audit` to write `qa/visual-parity-audit.json`. Every required page must have `visual_similarity_score >= 0.80`; average score cannot hide a failed page. Missing or broken primary interactions, dead navigation, unreachable declared states, wrong-language UI, and material visual drift from the approved image are hard failures even when a rough visual score appears high.

## Final Functional Audit

After the React prototype is created, the main agent must install dependencies if needed, run it locally, inspect or open it when browser tools are available, and verify:

- Every required page has a route/view.
- Primary buttons, navigation, form controls, selectors, modals, and declared states are reachable.
- Success, error, empty, and blocked states declared in page briefs are implemented or explicitly marked unavailable.
- HTML document `lang`, page title, navigation, metadata, and visible UI copy follow `requested_output_language`.
- The prototype is not a full-screen screenshot/image browser.
- The rendered React route screenshot for every required page visually recreates the approved AI page image; material visual differences are blocking failures.
- Cross-page function flow and visual consistency remain coherent.

If the audit fails, fix the React prototype or mark the failing area blocked before final response.

## Feishu/Lark Delivery

Read `references/feishu-delivery.md` and `design-doc-to-ui-feishu-doc/SKILL.md` only if the user asks to upload, publish, or sync the final design package to Feishu/Lark. Do not upload to Feishu by default.

Feishu output must be a rich design document, not a plain Markdown dump. It must use suitable Feishu blocks such as callouts, grids, tables, and whiteboards/diagrams, and must produce `qa/feishu-doc-audit.json`.

## Figma

Read `references/figma-workflow.md` and `design-doc-to-ui-figma-replica/SKILL.md` only if the user provides a Figma link/file, asks to sync to Figma, or asks to create a Figma prototype. Do not assume Figma is required.

Do not begin Figma implementation until the Design Completion Gate has passed, the structured design document exists, and the React prototype has passed visual parity and interaction audit. Figma output must be based on the approved design images, structured design document, and React prototype. It must basically replicate the approved image-generated screen set as fully editable, frontend-handoff-ready Figma frames, not reinterpret the product from requirements, use mismatched generic layouts, or paste full-page screenshots as implementation. The main agent first writes `qa/figma-scaffold-audit.json`, then uses one page-level Figma Replica SubAgent per required page, batched with at most 6 active SubAgents; after each page worker returns, the main thread records it with `scripts/record_figma_page_worker_result.py` into `qa/figma-page-worker-registry.json`, then wires global prototype links and cross-frame jumps. Each required page must have a Figma frame with `visual_similarity_score >= 0.80` in `qa/figma-replica-audit.json`, `editable_element_coverage >= 0.95`, passing icon/asset reconstruction checks, and primary prototype links. Missing required frames, flattened major UI regions, non-editable icons/assets, full-screen pasted screenshots as implementation, missing prototype links for primary flows, failed global prototype links, or material mismatch against the approved AI page image are blocking failures. Missing assets must follow the crop-reference -> image-gen isolated asset -> background cleanup -> individual Figma layer/component -> asset manifest flow. After Figma output is generated, update the structured design document with the Figma link and audit notes.

## Output Checklist

Before finishing, report:

- Source files read and major assets extracted.
- SubAgent direct-use status and any technical blockers.
- `requested_output_language`.
- Custom style directions explored, style samples generated, selected style, and whether the user confirmed it.
- Page coverage count: source required pages, page briefs, worker results, approved/blocked/deferred pages, React routes.
- Script gate results: `ui-run.json`, latest validation report, and prototype-data report.
- Companion Skill Gate result and companion-skill report.
- Structured design document quality audit path, quality score, and blockers/warnings.
- User feedback revisions applied, affected pages/channels, revision plan/log path, and rerun gates when applicable.
- Pages generated and each page's review status.
- Design Completion Gate result.
- Structured design document path.
- React prototype folder path, run command, visual parity score summary, and Final Functional Audit result.
- React scaffold audit path, shared style system status, and worker ownership map status.
- React page SubAgent batch result, aggregate interaction-flow audit path, global navigation result, and any blocked/infeasible interactions.
- Feishu/Lark document link and rich document audit, or "not uploaded because not requested".
- Figma link, Figma page SubAgent batch result, editable-frame/front-end handoff audit, asset manifest, global prototype-link result, and 80% replica audit, or "not generated because not requested/provided".
- Known residual risks, blocked pages, infeasible pages, or user-approved deferred pages.
