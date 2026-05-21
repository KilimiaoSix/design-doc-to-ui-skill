# Source Ingestion

Normalize every input source before generating UI.

## Fuzzy Requirement / Conversation Source

Use this path when the user starts with a rough product idea, a vague scenario, a target audience, a problem statement, or an exploratory conversation instead of a finished PRD.

Do not demand a full PRD before helping. Turn the conversation into a reviewable product concept:

1. Capture the user's raw idea and constraints as `source/raw-idea.md` or append them to the normalized source.
2. Ask only high-leverage questions when the answer changes product scope, primary user, platform, monetization, compliance, or design direction. For ordinary gaps, state a clear assumption and continue.
3. Produce `source/expanded-product-brief.md` before page briefs. It must include:
   - product one-liner and target users;
   - user problems, jobs-to-be-done, and core scenarios;
   - business/user goals and non-goals;
   - assumptions vs confirmed requirements;
   - information architecture and candidate page inventory;
   - main task flows, entry points, recovery paths, and state/error strategy;
   - interaction/visual concept hypotheses;
   - demo scope for an early low/mid-fidelity interaction prototype when useful;
   - acceptance criteria, open questions, and risks.
4. Present the expanded brief to the user and wait for approval or edits before freezing scope. Record approval in `qa/stage-approval-product-concept.json`.
5. Convert the approved expanded brief into `app_requirements_summary` and `page_inventory`.
6. Initialize the run with `prepare_ui_run.py --concept-expansion` so the manifest records that the run came from fuzzy requirements.

The early interaction demo is for validating structure and flow, not for replacing the final React prototype. It may be a lightweight local React/HTML demo, storyboard, or clickable wireframe. It must make route targets, primary actions, empty/error/success states, and navigation assumptions visible before detailed UI image generation starts. Do not treat it as final visual parity evidence.

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
   - explicit visual style expectations, including style names, brand adjectives, platform style requests, mood boards, benchmark apps, and "do/don't" visual constraints
5. Download relevant document images into the project output folder.
6. If the document references another Feishu doc that affects the design, fetch that referenced doc too.

## Markdown Source

When the user provides a Markdown file:

1. Read the file.
2. Parse headings as sections.
3. Resolve local image references relative to the Markdown file.
4. Preserve tables, bullet requirements, and code blocks.
5. Extract linked design references and remote images when needed.
6. Extract explicit visual style expectations, including style names, brand adjectives, platform style requests, mood boards, benchmark apps, and "do/don't" visual constraints.

## Language Detection

Set these fields before writing page briefs:

- `source_language`: primary language of the source document.
- `requested_output_language`: language requested by the user. If the user does not specify a language, use `source_language`.

All final design documentation, React metadata, HTML document metadata, navigation labels, table headers, and review summaries must use `requested_output_language`.

## Normalized `source_bundle`

Produce this structure before summarizing requirements:

```json
{
  "source_type": "idea|conversation|feishu|markdown|pdf|docx|image|mixed",
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
  "open_questions": [],
  "concept_expansion": {
    "required": false,
    "expanded_product_brief": "",
    "confirmed_requirements": [],
    "assumptions": []
  }
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
  "problem_statement": "",
  "core_scenarios": [],
  "business_goals": [],
  "non_goals": [],
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
  "visual_style_signals": [
    {
      "signal": "",
      "source_evidence": "",
      "signal_type": "explicit_style_type|brand_adjective|platform_style|benchmark_app|visual_do|visual_dont|inferred_mood",
      "strength": "explicit|strong|weak",
      "priority": "high|medium|low"
    }
  ],
  "expected_style_types": [],
  "platforms": ["web", "pc", "mobile", "tablet"],
  "acceptance_criteria": [],
  "assumptions": [],
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

Style words in the source are not decorative metadata. If the source explicitly requests a style type, for example "企业级", "苹果风", "Material 3", "暗黑专业工具", "高端奢华", "游戏化", "教育可爱", "极简 SaaS", or names a benchmark app, preserve it as a high-priority `visual_style_signals` entry. Later style exploration must weight these signals above catalog defaults and above the agent's own aesthetic preference.
