---
name: design-doc-to-ui-feishu-doc
description: "Create rich Feishu/Lark design documents for design-doc-to-ui runs. Use when a UI design package must be uploaded or synced to Feishu/Lark with design thinking, source traceability, user stories, acceptance criteria, page linkage, interaction/state matrices, component tokens, accessibility notes, diagrams, tables, callouts, grids, generated page images, and audit evidence. Requires reading and following lark-doc, lark-doc XML/style references, and lark-whiteboard when diagrams are needed. Blocks delivery if the output would be a plain Markdown dump, screenshot directory, shallow page-by-page catalog, or document that fails the structured design document quality gate."
---

# Design Doc To UI Feishu Doc

Use this companion skill only from `$design-doc-to-ui` when the user explicitly asks for Feishu/Lark delivery.

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
- page briefs, worker reviews, main audit, React audit, and requested Figma audit when present

Do not create Feishu output from requirements alone. If the structured design document quality audit is missing or failed, block Feishu delivery and repair the local structured design document first.

## Document Structure

The Feishu document must tell a connected design story. Required sections:

- executive summary, design proposition, and delivery conclusion;
- source traceability, assumptions, and evidence boundaries;
- target users, user stories, goals, and acceptance criteria;
- user journey and activation/conversion/recovery moments;
- page map and information architecture;
- primary task flows, decision points, page linkage, and recovery paths;
- design decisions and tradeoffs;
- visual style, design tokens, component system, and interaction principles;
- state, exception, accessibility, content, localization, and monetization strategy;
- detailed page specs with imagegen-generated page images;
- React/Figma/Feishu handoff acceptance criteria;
- audit results, revision history, blockers, and risks.

A page-by-page catalog without traceability, design thinking, acceptance criteria, state strategy, component rules, and handoff checks is non-compliant.

## Rich Block Requirements

Use Feishu rich document capabilities deliberately:

- opening `<callout>` with design proposition and main conclusion;
- at least 4 whiteboard/diagram blocks: source-to-page traceability or page map, primary user flow, state/exception flow, and implementation handoff/replication flow;
- at least 6 structured tables: source traceability matrix, user story/acceptance matrix, page matrix, interaction/state matrix, component/token matrix, risk/open-question matrix;
- `<grid>` for comparisons, design principles, or strategy tradeoffs;
- page images inserted near their page specs;
- page specs include route, source evidence, user story, states, interactions, acceptance criteria, accessibility notes, and React/Figma replication notes;
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
  "handoff_acceptance_criteria_present": true,
  "design_narrative_present": true,
  "page_linkage_present": true,
  "blockers": []
}
```

Do not mark `passed: true` if required diagrams/tables, structured design document quality, source traceability, user story acceptance criteria, design narrative, page linkage, interaction/state matrix, component tokens, accessibility notes, or handoff acceptance criteria are missing.
