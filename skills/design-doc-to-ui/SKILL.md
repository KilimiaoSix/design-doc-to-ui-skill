---
name: design-doc-to-ui
description: Convert product requirements, design documents, Feishu/Lark docs, Markdown specs, product prototypes, wireframes, screenshots, and brand assets into fully covered cross-device APP UI image drafts, structured design documentation, real interactive local HTML prototype folders, and optional Figma updates. Use when Codex needs to read a design/product document, summarize app requirements, derive a complete source-backed page inventory, explore custom visual directions with style-sample image generation, lock a global style contract, generate every required UI page with page-level SubAgents, review each page independently, perform a main-agent functional audit, or build an interactive prototype. Requires direct SubAgent delegation for every style-sample image-generation, UI image-generation, and calibration task; create SubAgents directly when the tool is available and block the phase only when SubAgents or image generation are technically unavailable.
---

# Design Doc To UI

Use this skill to turn a source product/design document into an approved UI design package. The package must contain source-backed page coverage, reviewed UI image drafts for every required page, a structured design document in the requested language, and a local component-level HTML prototype. Use Figma only when the user provides a Figma link/file or explicitly asks for Figma output.

## Required Workflow

1. Ingest the source document and assets.
2. Produce an `app_requirements_summary` with `source_language`, `requested_output_language`, and `page_inventory`.
3. Run the SubAgent Direct-Use Gate.
4. Run the Style Exploration Gate before page generation.
5. Run the Page Coverage Gate.
6. Create one page brief for every required page.
7. Run one page-level SubAgent for each required page to generate the UI image and complete page calibration/review.
8. Run the Per-Page SubAgent Gate.
9. Perform the main-agent audit across all pages.
10. Run the Design Completion Gate.
11. Generate a structured design document in `requested_output_language`.
12. Generate a local component-level interactive HTML prototype folder from the completed design images and structured design document.
13. Optionally create/update Figma prototype content from the completed design images and structured design document only when the user has provided Figma context or requested Figma.
14. Perform the Final Functional Audit on the HTML prototype and any requested Figma prototype.

Do not skip requirement summarization, SubAgent Direct-Use Gate, Style Exploration Gate, Page Coverage Gate, per-page SubAgent review, main-agent audit, Design Completion Gate, or Final Functional Audit.

Do not silently reduce scope with labels such as "pilot", "core flow", "trial", or "MVP slice". A page from `page_inventory` may be deferred only when the user explicitly approves the deferral; record it as `user-approved deferred`, not approved.

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

## Main Audit

Read `references/main-audit.md` after page workers return.

SubAgent approval is not final. The main agent must audit the full screen set against the original requirements and style contract. If a page fails, revise the brief or prompt and start a new SubAgent worker for that page. If SubAgent delegation is technically unavailable, mark regeneration blocked instead of regenerating in the main thread. If repeated attempts fail, reassess the requirement and mark the page infeasible only after explaining why.

Main-agent approval is required before generating final design documents and HTML prototype.

## Design Completion Gate

Do not start HTML or Figma work until the design phase is complete.

The design phase is complete only when:

- `global_style_contract` is locked.
- Every non-deferred required page has a page brief.
- Every non-deferred required page has a SubAgent `worker-result.json`, `review.md`, `prompt-history.md`, and final design image.
- Every non-deferred required page has status `approved` after main-agent audit.
- The main-agent audit has passed across all approved design images.
- No style-sampling, page-generation, or regeneration SubAgent is still running.

If any required page is `blocked`, `infeasible`, or missing an approved final image, do not generate HTML/Figma by default. Generate a partial HTML/Figma prototype only if the user explicitly approves a partial prototype after the missing pages are listed.

## Structured Design Document

Read `references/design-doc-output.md`.

Generate the structured design document before HTML/Figma implementation. Include the product summary, page inventory, user flow, visual style contract, screen specs for every required page, UI images, interaction notes, per-page review results, main-agent audit, prototype implementation requirements, and open questions. Mark HTML/Figma paths as `pending` at this stage, then update the document after the HTML/Figma outputs are created.

## HTML Prototype

Read `references/html-prototype.md`.

Do not begin HTML implementation until the Design Completion Gate has passed and the structured design document exists. Build the HTML prototype from the approved design images, structured design document, page briefs, and worker reviews. Do not build HTML from requirements alone while design images are still pending. After HTML is generated and audited, update the structured design document with the HTML path and audit result.

Default output is a local folder, not a hosted link:

```text
prototype/
  index.html
  assets/
  screens/
  styles.css
  prototype-data.js
```

Build a component-level interactive HTML/CSS/JS prototype by default. Use generated images only as visual references, thumbnails, or review attachments; do not use full-screen images as the primary UI implementation. If only an image browser can be produced, mark the prototype `blocked/non-compliant` and do not present it as complete.

## Final Functional Audit

After the HTML prototype is created, the main agent must inspect or open it when browser tools are available and verify:

- Every required page has a route/view.
- Primary buttons, navigation, form controls, selectors, modals, and declared states are reachable.
- Success, error, empty, and blocked states declared in page briefs are implemented or explicitly marked unavailable.
- HTML language, page title, navigation, metadata, and visible UI copy follow `requested_output_language`.
- The prototype is not a full-screen screenshot/image browser.
- Cross-page function flow and visual consistency remain coherent.

If the audit fails, fix the HTML prototype or mark the failing area blocked before final response.

## Figma

Read `references/figma-workflow.md` only if the user provides a Figma link/file, asks to sync to Figma, or asks to create a Figma prototype. Do not assume Figma is required.

Do not begin Figma implementation until the Design Completion Gate has passed and the structured design document exists. Figma output must be based on the approved design images and structured design document; HTML may be used as an implementation source only after it has been generated from those approved design artifacts. After Figma output is generated, update the structured design document with the Figma link and audit notes.

## Output Checklist

Before finishing, report:

- Source files read and major assets extracted.
- SubAgent direct-use status and any technical blockers.
- `requested_output_language`.
- Custom style directions explored, style samples generated, selected style, and whether the user confirmed it.
- Page coverage count: source required pages, page briefs, worker results, approved/blocked/deferred pages, HTML routes.
- Pages generated and each page's review status.
- Design Completion Gate result.
- Structured design document path.
- HTML prototype folder path and Final Functional Audit result.
- Figma link or "not generated because not requested/provided".
- Known residual risks, blocked pages, infeasible pages, or user-approved deferred pages.
