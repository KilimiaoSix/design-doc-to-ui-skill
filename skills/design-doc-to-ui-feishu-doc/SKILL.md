---
name: design-doc-to-ui-feishu-doc
description: "Create clean rich Feishu/Lark product design documents for design-doc-to-ui runs. Use when an approved design document must be uploaded or synced to Feishu/Lark with design thinking, source traceability, user stories, design acceptance criteria, page linkage, interaction/state matrices, component tokens, accessibility notes, diagrams, tables, callouts, grids, and generated page images. Requires reading and following lark-doc, lark-doc XML/style references, and lark-whiteboard when diagrams are needed. Blocks delivery if the output would be a plain Markdown dump, screenshot directory, shallow page-by-page catalog, delivery/audit report, React/Figma/Feishu verification report, stale/failed update, mojibake-corrupted remote document, or document that fails the structured design document quality gate. Delivery materials stay local in qa artifacts and must not be uploaded to Feishu."
---

# Design Doc To UI Feishu Doc

Use this companion skill only from `$design-doc-to-ui` when the user explicitly asks for Feishu/Lark design document delivery.

## Required External Skills

Before writing or updating Feishu content, read and follow:

- `lark-doc/SKILL.md`
- `lark-doc/references/lark-doc-xml.md`
- `lark-doc/references/style/lark-doc-style.md`
- `lark-whiteboard/SKILL.md` when creating or updating whiteboards/diagrams

Use `lark-sheets` or `lark-base` only when the design document needs real spreadsheet/base data. Do not use them for static UI spec tables.

If required Feishu/Lark skills or `lark-cli` are unavailable, mark Feishu delivery blocked.

## Input Contract

Use the completed `design-doc-to-ui` run package:

- `ui-run.json`
- `qa/structured-design-doc.md`
- `qa/structured-design-doc-audit.json`
- `qa/design-thinking-map.md` when present
- approved page images in `design-images/`
- page briefs and approved page images as source material for the clean design document

Do not create Feishu output from requirements alone. If the structured design document quality audit is missing or failed, block Feishu delivery and repair the local structured design document first.

The local structured design document must already be approved by the user in `qa/stage-approval-design-doc.json`. Do not use Feishu delivery as the first time the user sees the full design document.

Do not upload delivery materials to Feishu. Keep worker reviews, main audit, React/Figma audits, visual parity scores, run commands, upload verification, artifact paths, and final acceptance records in local `qa/` artifacts only.

## Document Structure

The Feishu document must tell a connected design story and remain a clean design document. Required sections:

- executive summary, design proposition, and scope boundaries;
- source traceability, assumptions, and evidence boundaries;
- target users, user stories, goals, and acceptance criteria;
- user journey and activation/conversion/recovery moments;
- page map and information architecture;
- primary task flows, decision points, page linkage, and recovery paths;
- design decisions and tradeoffs;
- visual style, design tokens, component system, and interaction principles;
- state, exception, accessibility, content, localization, and monetization strategy;
- detailed page specs with imagegen-generated page images;
- design acceptance criteria, revision history, open questions, and product/design risks.

A page-by-page catalog without traceability, design thinking, acceptance criteria, state strategy, component rules, and design acceptance checks is non-compliant.

Do not produce a new shallow Feishu-only summary. The Feishu document must preserve and enrich the approved structured design document's substance. It may restructure content into callouts, grids, tables, diagrams, and page image sections, but it must not drop rationale, source evidence, state behavior, component rules, or open questions.

Forbidden Feishu content:

- delivery conclusions, delivery index, audit matrix, page evidence matrix, final acceptance, encoding repair notes;
- React/Figma/Feishu verification results, visual parity scores, run commands, worker evidence, local file paths, or upload verification details;
- a wrapper heading such as "Structured design document" around the actual design body.

## Rich Block Requirements

Use Feishu rich document capabilities deliberately:

- opening `<callout>` with design proposition and main conclusion;
- at least 4 whiteboard/diagram blocks: source-to-page traceability or page map, primary user flow, information architecture/route graph, and state/exception flow;
- at least 6 structured tables: source traceability matrix, user story/acceptance matrix, page matrix, interaction/state matrix, component/token matrix, risk/open-question matrix;
- `<grid>` for comparisons, design principles, or strategy tradeoffs;
- page images inserted near their page specs;
- page specs include route, source evidence, user story, states, interactions, design acceptance criteria, accessibility notes, and responsive/content notes;
- no more than 3 consecutive plain paragraphs without a non-text block.

Simple diagrams may use embedded Mermaid/PlantUML whiteboards. Complex diagrams should use `lark-whiteboard`.

## Audit Output

Write `qa/feishu-doc-audit.json`:

```json
{
  "passed": true,
  "feishu_url": "",
  "rich_block_density": 0.4,
  "whiteboard_count": 4,
  "table_count": 6,
  "structured_doc_quality_present": true,
  "source_traceability_present": true,
  "user_story_acceptance_criteria_present": true,
  "interaction_state_matrix_present": true,
  "component_token_system_present": true,
  "accessibility_review_present": true,
  "design_acceptance_criteria_present": true,
  "design_narrative_present": true,
  "page_linkage_present": true,
  "clean_design_document_only": true,
  "no_delivery_or_audit_material_uploaded": true,
  "no_delivery_index_or_repair_heading": true,
  "blockers": []
}
```

Do not mark `passed: true` if required diagrams/tables, structured design document quality, source traceability, user story acceptance criteria, design narrative, page linkage, interaction/state matrix, component tokens, accessibility notes, design acceptance criteria, or clean-document checks are missing.

## Remote Content Verification

After every Feishu create/update, immediately fetch the published link back and inspect the remote content. This is a hard gate. The local source XML or local Markdown is not enough evidence.

Required verification:

- use `lark-cli docs +fetch` or the `lark-doc` skill against the Feishu URL/document id after upload;
- save the fetched payload under `qa/`, for example `qa/feishu-doc-fetch.json` and/or `qa/feishu-doc-fetch.xml`;
- confirm the fetched remote content is the current update by checking document id/title/revision or timestamp when available, plus required headings, page ids, and page image count;
- confirm every required page id appears in the fetched remote content;
- confirm design-document substance survived upload: design proposition, source traceability, user stories and acceptance criteria, journey/page linkage, interaction/state matrix, component/token matrix, accessibility notes, design acceptance criteria, risks/open questions, and page specs;
- confirm delivery/audit material did not leak into the remote document: no delivery index, audit matrix, worker evidence, run commands, visual parity scores, React/Figma/Feishu verification, upload verification, or local artifact paths;
- scan the fetched remote content for mojibake, Unicode replacement characters, `[object Object]`, `???` replacement runs, and stale placeholders;
- if remote fetch, update verification, coverage, or text integrity fails, repair/re-upload and fetch again before passing.

Write `qa/feishu-doc-content-audit.json`:

```json
{
  "passed": true,
  "feishu_url": "",
  "remote_fetch_verified": true,
  "remote_fetch_path": "qa/feishu-doc-fetch.json",
  "remote_content_updated": true,
  "remote_content_matches_expected_sections": true,
  "remote_page_inventory_covered": true,
  "remote_page_spec_count": 12,
  "remote_page_image_count": 12,
  "required_sections_present": true,
  "source_traceability_present": true,
  "user_story_acceptance_criteria_present": true,
  "interaction_state_matrix_present": true,
  "component_token_system_present": true,
  "accessibility_review_present": true,
  "design_acceptance_criteria_present": true,
  "page_specs_present": true,
  "remote_content_is_clean_design_doc": true,
  "no_delivery_or_audit_material_uploaded": true,
  "no_delivery_index_or_repair_heading": true,
  "missing_required_sections": [],
  "missing_page_ids": [],
  "stale_content_detected": false,
  "mojibake_detected": false,
  "no_mojibake_detected": true,
  "question_mark_replacement_runs": 0,
  "blockers": []
}
```

Then present the Feishu link and a short summary of the local remote-content audit to the user. Only after the user confirms the linked design document is correct may the main `design-doc-to-ui` workflow write `qa/stage-approval-feishu-doc.json` and proceed to React/Figma.
