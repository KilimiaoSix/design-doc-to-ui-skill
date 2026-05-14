# Page Brief Schema

Create one page brief per required source page before image generation. The `page_inventory` in `app_requirements_summary` is the source of truth for delivery coverage.

When a scripted run exists, `ui-run.json` is the canonical copy of `page_inventory`. Store each page brief at the `artifacts.brief_path` recorded for that page. `prepare_ui_run.py --write-brief-stubs` may create draft brief files, but the main agent must still complete them from the source document before spawning page workers.

## Page Brief

```json
{
  "page_id": "",
  "page_name": "",
  "source_page_ref": "",
  "output_language": "",
  "endpoint": "web|pc|mobile|tablet",
  "target_resolution": "",
  "priority": "must|should|optional",
  "required_for_delivery": true,
  "purpose": "",
  "entry_points": [],
  "next_actions": [],
  "route_targets": [],
  "required_components": [],
  "visible_copy": [],
  "data_examples": [],
  "layout": {
    "navigation": "",
    "primary_regions": [],
    "content_hierarchy": [],
    "responsive_notes": ""
  },
  "prototype_interactions": [
    {
      "trigger": "",
      "result": "",
      "target_route_or_state": ""
    }
  ],
  "interactions": [],
  "states": ["default"],
  "state_requirements": [
    {
      "state": "default|success|error|empty|loading|blocked|modal",
      "required": true,
      "description": ""
    }
  ],
  "assets": [],
  "style_constraints": [],
  "negative_constraints": [],
  "acceptance_criteria": [],
  "open_questions": []
}
```

## Brief Rules

- Keep each brief single-page and concrete.
- Create one brief for every `page_inventory` item with `required_for_delivery: true`.
- Do not merge multiple source pages into one brief.
- Do not ask image generation to create one overview image for multiple pages.
- Use exact visible copy when the source provides it.
- If exact copy is unknown, use short generic labels in `output_language` and mark copy as draft.
- Do not ask image generation to produce dense paragraphs.
- Do not overload one image with too many states. Use `state_requirements` to decide which states need separate page briefs or separate React states.
- For mascot/IP requirements, specify whether the asset is a provided image, a generated transparent cutout, or a visual reference.
- Include the route and interaction expectations needed for the React prototype.

## Page Coverage Gate

Before generating screens, produce and verify a page inventory:

```json
{
  "pages": [
    {
      "page_id": "home",
      "page_name": "首页",
      "endpoint": "mobile",
      "priority": "must|should|optional",
      "required_for_delivery": true,
      "source_evidence": []
    }
  ]
}
```

Then verify:

- Required page count equals required page brief count.
- Every brief has `source_page_ref`, `output_language`, `prototype_interactions`, `route_targets`, and `state_requirements`.
- Every optional page is listed and either generated, explicitly deferred by the user, or marked blocked with a reason.
- No page is marked approved before its SubAgent worker artifacts exist.

If this gate fails, repair the inventory or briefs before image generation. Do not proceed with a partial "core flow" unless the user explicitly approves reduced scope.

Use `scripts/ui_job_status.py --run-dir <output-run-dir>` before spawning page workers. Pages with `state: missing_brief` are blocking failures. Pages with `state: ready_for_subagent` can be assigned to the next SubAgent batch, up to 6 active workers.
