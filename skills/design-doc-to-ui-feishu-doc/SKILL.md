---
name: design-doc-to-ui-feishu-doc
description: "Create rich Feishu/Lark design documents for design-doc-to-ui runs. Use when a UI design package must be uploaded or synced to Feishu/Lark with design thinking, page linkage, diagrams, tables, callouts, grids, generated page images, and audit evidence. Requires reading and following lark-doc, lark-doc XML/style references, and lark-whiteboard when diagrams are needed. Blocks delivery if the output would be a plain Markdown dump or page-by-page catalog."
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
- `qa/design-thinking-map.md` when present
- approved page images in `design-images/`
- page briefs, worker reviews, main audit, React audit, and requested Figma audit when present

Do not create Feishu output from requirements alone.

## Document Structure

The Feishu document must tell a connected design story. Required sections:

- design proposition and product overview;
- target users, mindset, and core tension;
- user journey and activation/conversion/recovery moments;
- page map and information architecture;
- primary task flows and page linkage;
- visual style, component system, and interaction principles;
- state, exception, and monetization strategy;
- page specs with imagegen-generated page images;
- audit results and risks.

A page-by-page catalog without design thinking and linkage is non-compliant.

## Rich Block Requirements

Use Feishu rich document capabilities deliberately:

- opening `<callout>` with design proposition and main conclusion;
- at least 3 whiteboard/diagram blocks: page map, primary user flow, state/exception flow;
- at least 4 structured tables: page matrix, interaction matrix, component matrix, risk/open-question matrix;
- `<grid>` for comparisons, design principles, or strategy tradeoffs;
- page images inserted near their page specs;
- no more than 3 consecutive plain paragraphs without a non-text block.

Simple diagrams may use embedded Mermaid/PlantUML whiteboards. Complex diagrams should use `lark-whiteboard`.

## Audit Output

Write `qa/feishu-doc-audit.json`:

```json
{
  "passed": true,
  "feishu_url": "",
  "rich_block_density": 0.4,
  "whiteboard_count": 3,
  "table_count": 4,
  "design_narrative_present": true,
  "page_linkage_present": true,
  "blockers": []
}
```

Do not mark `passed: true` if required diagrams/tables/design narrative/page linkage are missing.
