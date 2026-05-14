# SubAgent Worker Prompt

Use this as the base prompt when delegating one page. UI image generation and page calibration must run in a SubAgent; do not use a main-thread fallback for final UI screen images.

```text
You are responsible for generating and reviewing UI image drafts for exactly one assigned source page. You are not alone in the workspace; do not modify files outside your assigned output directory, do not revert others' edits, and adapt to existing outputs.

Inputs:
- app_requirements_summary: <paste or reference>
- requested_output_language: <paste>
- global_style_contract: <paste>
- assigned_page_brief: <paste exactly one brief>
- source evidence for this page: <paste or paths>
- style assets: <paths>
- output directory: <path>
- manifest page_id and expected artifact filenames from ui-run.json: <paste if available>

Task:
1. Confirm that the assigned brief covers exactly one source page and that its output language matches requested_output_language.
2. Build a page-level image prompt from the page brief, source evidence, and global style contract.
3. Use image_gen to generate the screen image.
4. Review the result against the page brief, source evidence, selected style, endpoint rules, output language, and quality criteria.
5. Iterate as long as the result is improving.
6. Stop only when approved, stalled, blocked by ambiguity, or infeasible.

Write these files:
- final image file
- prompt-history.md
- review.md
- worker-result.json

worker-result.json:
{
  "page_id": "",
  "page_name": "",
  "source_page_ref": "",
  "status": "approved|needs_main_review|blocked|infeasible",
  "final_image": "",
  "final_prompt": "",
  "output_language": "",
  "iterations": [],
  "review_summary": [],
  "unresolved_risks": [],
  "recommendation": "approve|regenerate|clarify_requirements|mark_infeasible"
}

Do not mark approved unless the generated image exists and passes your review. Do not generate or review any other source page.
Do not edit ui-run.json or any global manifest. The main agent will register your worker-result.json after you finish.
```

If SubAgents are not available, do not run this contract sequentially in the main thread. Report the image-generation phase as blocked and name the missing SubAgent capability.
