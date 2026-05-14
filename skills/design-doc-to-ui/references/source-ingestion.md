# Source Ingestion

Normalize every input source before generating UI.

## Feishu/Lark Source

When the user provides a Feishu/Lark wiki or doc URL:

1. Use the `lark-doc` skill and follow its fetch rules.
2. Fetch the outline first when the document is long.
3. Fetch relevant sections with IDs where possible.
4. Extract:
   - title and headings
   - requirement text
   - tables
   - image tokens/URLs
   - referenced docs
   - embedded sheet/base/doc citations
   - source outline IDs and section IDs
5. Download relevant document images into the project output folder.
6. If the document references another Feishu doc that affects the design, fetch that referenced doc too.

## Markdown Source

When the user provides a Markdown file:

1. Read the file.
2. Parse headings as sections.
3. Resolve local image references relative to the Markdown file.
4. Preserve tables, bullet requirements, and code blocks.
5. Extract linked design references and remote images when needed.

## Language Detection

Set these fields before writing page briefs:

- `source_language`: primary language of the source document.
- `requested_output_language`: language requested by the user. If the user does not specify a language, use `source_language`.

All final design documentation, React metadata, HTML document metadata, navigation labels, table headers, and review summaries must use `requested_output_language`.

## Normalized `source_bundle`

Produce this structure before summarizing requirements:

```json
{
  "source_type": "feishu|markdown|pdf|docx|image|mixed",
  "source_refs": [],
  "raw_sections": [
    {
      "id": "",
      "heading": "",
      "level": 1,
      "text": "",
      "source_ref": ""
    }
  ],
  "tables": [],
  "images": [
    {
      "path": "",
      "source": "",
      "role": "brand|reference|prototype|content|unknown",
      "notes": ""
    }
  ],
  "links": [],
  "constraints": [],
  "open_questions": []
}
```

## `app_requirements_summary`

Create this before page briefs:

```json
{
  "product_name": "",
  "source_language": "",
  "requested_output_language": "",
  "target_users": [],
  "core_scenarios": [],
  "business_goals": [],
  "page_list": [],
  "page_inventory": [
    {
      "page_id": "",
      "page_name": "",
      "endpoint": "web|pc|mobile|tablet",
      "priority": "must|should|optional",
      "required_for_delivery": true,
      "source_evidence": [],
      "deferred_status": "not_deferred|user-approved deferred|blocked",
      "deferred_reason": ""
    }
  ],
  "user_flows": [],
  "must_include_copy": [],
  "must_not_include": [],
  "brand_assets": [],
  "visual_style_signals": [],
  "platforms": ["web", "pc", "mobile", "tablet"],
  "acceptance_criteria": [],
  "unknowns": []
}
```

## Page Inventory Rules

After `app_requirements_summary` is complete, initialize the run manifest:

```bash
python scripts/prepare_ui_run.py --source <normalized-source.md> --run-dir <output-run-dir> --requested-output-language <language>
```

If the page inventory was produced by the main agent instead of being parsed directly from a source file, write it as JSON and pass `--pages-json <page-inventory.json>`. The generated `ui-run.json` becomes the canonical source for required page count, routes, artifact paths, and React/Figma gates.

- Derive `page_inventory` from source outline headings, prototype screenshots, named screens, user-flow steps, and explicit feature requirements.
- Mark pages as `required_for_delivery: true` when they are source screens, required feature pages, main flow pages, or required states.
- List optional pages too. Do not omit them; mark them optional and explain why.
- Do not silently collapse pages into "core flow", "pilot", "trial", or one overview screen.
- A required page may be deferred only after explicit user approval. Record that as `user-approved deferred`.

If key information is missing but reasonable defaults are possible, state the assumption and continue. Ask the user only when the missing information changes the design direction or product scope.
