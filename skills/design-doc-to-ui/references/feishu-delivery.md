# Feishu/Lark Rich Design Document Delivery

Use this reference only when the user explicitly asks to upload, publish, or sync the clean design document to Feishu/Lark. Do not upload the delivery package, audit package, or local QA materials to Feishu.

## Required Companion Skill

Before Feishu work, load `design-doc-to-ui-feishu-doc/SKILL.md`.

If the companion skill is unavailable, mark Feishu delivery blocked. Do not fall back to a plain Markdown upload.

## Preconditions

Do not upload partial work unless the user explicitly approves partial delivery.

Required before Feishu upload:

- structured design document exists and uses `requested_output_language`;
- `qa/structured-design-doc-audit.json` exists and passes the quality gate;
- every non-deferred required page image exists and is referenced in the document;
- design narrative, source traceability, user stories, acceptance criteria, page linkage, interaction/state matrix, component/token matrix, accessibility notes, and design acceptance criteria are present;
- `qa/stage-approval-design-doc.json` records explicit user approval of the local structured design document;
- blocked, infeasible, and deferred pages are clearly marked.
- the local structured design document contains no delivery links, worker evidence, audit result sections, run commands, React/Figma/Feishu delivery verification, visual parity scores, or local artifact paths.

## Rich Document Requirements

The Feishu document must use the document platform, not merely host text. It must be a clean product design document.

Minimum requirements:

- one opening callout that states the design proposition and product-level conclusion;
- at least 4 whiteboard/diagram blocks: source-to-page traceability or page map, primary user flow, information architecture/route graph, and state/exception flow;
- at least 6 structured tables: source traceability matrix, user story/acceptance matrix, page matrix, interaction/state matrix, component/token matrix, risk/open-question matrix;
- grid or two-column sections for design principles, before/after choices, or strategy comparisons;
- no more than 3 consecutive plain text paragraphs without a non-text block;
- page sections include generated page images near the related spec;
- each page spec includes route, source evidence, user story, states, interactions, design acceptance criteria, accessibility notes, and responsive/content notes;
- document language follows `requested_output_language`.
- the Feishu document content must be derived from the approved structured design document; do not generate a separate shallow page catalog for Feishu.
- the Feishu document must not include delivery conclusions, delivery index, audit matrix, page evidence matrix, final acceptance, worker evidence, run commands, visual parity scores, React/Figma/Feishu verification, upload verification, or local artifact paths.

## Remote Link Content Verification

Creating or updating the Feishu document is not enough. After every create/update:

1. Fetch the published Feishu link back with `lark-doc`/`lark-cli docs +fetch`, preferably in both markdown/text and XML/detail forms when available.
2. Save the fetched result under `qa/` and reference that path from `qa/feishu-doc-content-audit.json`.
3. Verify the remote linked content is the newly updated document, not a stale previous version. Use title, document id, updated timestamp/revision when available, required section headings, page ids, and page image count.
4. Verify required design-document substance exists in the fetched content: design proposition, source traceability, user stories/acceptance criteria, IA/page linkage, interaction/state matrix, component/token system, accessibility notes, design acceptance criteria, page specs for every required page, and risk/open questions.
5. Verify delivery/audit material did not leak into the fetched content: no delivery index, audit matrix, worker evidence, run commands, visual parity scores, React/Figma/Feishu verification, upload verification, or local artifact paths.
6. Verify no mojibake, Unicode replacement characters, `???` question-mark replacement runs, `[object Object]`, or placeholder/template residue appears in the fetched remote content.
7. If any verification fails, repair and re-upload the Feishu document, then fetch and audit again. Do not mark Feishu delivery passed until the remote linked content audit passes.

## Tooling

- Use the relevant `lark-*` skill or `lark-cli` workflow available in the environment.
- Prefer `lark-doc` XML when creating/updating rich documents.
- Use `lark-whiteboard` for complex diagrams; simple diagrams may use embedded Mermaid/PlantUML whiteboards.
- Use `lark-sheets` or `lark-base` only when the document needs real spreadsheet/base data, not for static UI specs.
- Upload page images as document images/attachments and insert them near each page spec.
- Do not embed React/Figma project files, ZIPs, run commands, local paths, delivery audit results, or delivery links in the Feishu document. Keep those in local delivery artifacts.

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
  "design_acceptance_criteria_present": true,
  "design_narrative_present": true,
  "page_linkage_present": true,
  "clean_design_document_only": true,
  "no_delivery_or_audit_material_uploaded": true,
  "no_delivery_index_or_repair_heading": true,
  "blockers": []
}
```

Also write `qa/feishu-doc-content-audit.json` with:

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

Finally present the Feishu link to the user for review. Only after the user approves the remote document may the agent write `qa/stage-approval-feishu-doc.json`.

After upload, record the Feishu link and upload notes in local `qa/` or delivery artifacts only, for example `qa/delivery-index.md` or `qa/final-delivery-audit.json`. Do not update the clean design document with delivery metadata.
