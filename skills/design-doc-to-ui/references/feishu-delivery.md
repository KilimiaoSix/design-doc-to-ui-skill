# Feishu/Lark Rich Design Document Delivery

Use this reference only when the user explicitly asks to upload, publish, or sync the final design package to Feishu/Lark.

## Required Companion Skill

Before Feishu work, load `design-doc-to-ui-feishu-doc/SKILL.md`.

If the companion skill is unavailable, mark Feishu delivery blocked. Do not fall back to a plain Markdown upload.

## Preconditions

Do not upload partial work unless the user explicitly approves partial delivery.

Required before Feishu upload:

- structured design document exists and uses `requested_output_language`;
- `qa/structured-design-doc-audit.json` exists and passes the quality gate;
- every non-deferred required page image exists and is referenced in the document;
- design narrative, source traceability, user stories, acceptance criteria, page linkage, interaction/state matrix, component/token matrix, accessibility notes, and handoff acceptance criteria are present;
- React prototype exists and has passed the Final Functional Audit;
- blocked, infeasible, and deferred pages are clearly marked.

## Rich Document Requirements

The Feishu document must use the document platform, not merely host text.

Minimum requirements:

- one opening callout that states the design proposition and product-level conclusion;
- at least 4 whiteboard/diagram blocks: source-to-page traceability or page map, primary user flow, state/exception flow, and implementation handoff/replication flow;
- at least 6 structured tables: source traceability matrix, user story/acceptance matrix, page matrix, interaction/state matrix, component/token matrix, risk/open-question matrix;
- grid or two-column sections for design principles, before/after choices, or strategy comparisons;
- no more than 3 consecutive plain text paragraphs without a non-text block;
- page sections include generated page images near the related spec;
- each page spec includes route, source evidence, user story, states, interactions, acceptance criteria, accessibility notes, and React/Figma replication notes;
- document language follows `requested_output_language`.

## Tooling

- Use the relevant `lark-*` skill or `lark-cli` workflow available in the environment.
- Prefer `lark-doc` XML when creating/updating rich documents.
- Use `lark-whiteboard` for complex diagrams; simple diagrams may use embedded Mermaid/PlantUML whiteboards.
- Use `lark-sheets` or `lark-base` only when the document needs real spreadsheet/base data, not for static UI specs.
- Upload page images as document images/attachments and insert them near each page spec.
- If the React project is too large to embed, upload a ZIP or provide the local project path and include run instructions in the Feishu document.

## Output Contract

Write `qa/feishu-doc-audit.json` with:

```json
{
  "passed": true,
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

After upload, update the local structured design document with the Feishu link and upload notes.
