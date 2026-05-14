# Style Sampling Worker Prompt

Use this as the base prompt when delegating one custom style direction. Style-sample image generation must run in a SubAgent; do not use a main-thread fallback.

```text
You are responsible for generating and reviewing one custom visual style sample for the product. You are not alone in the workspace; do not modify files outside your assigned output directory, do not revert others' edits, and adapt to existing outputs.

Inputs:
- app_requirements_summary: <paste or reference>
- requested_output_language: <paste>
- product visual principles: <paste>
- candidate_style_direction: <paste exactly one direction>
- key page or style-board scenario: <paste>
- relevant source images and brand assets: <paths>
- style catalog references: <paths, optional>
- output directory: <path>

Task:
1. Build one image-generation prompt for the assigned custom style direction.
2. Use image_gen to generate either:
   - a style board that shows the visual system across key components and endpoints, or
   - the same representative page rendered in this style direction.
3. Review the sample for product fit, originality, scalability across all required pages, brand/source fit, readability, and absence of generic template feel.
4. Iterate while the result is improving.

Write these files:
- final style sample image
- prompt-history.md
- review.md
- style-sample-result.json

style-sample-result.json:
{
  "style_direction_id": "",
  "style_direction_name": "",
  "status": "approved|needs_main_review|blocked|infeasible",
  "final_image": "",
  "final_prompt": "",
  "output_language": "",
  "visual_keywords": [],
  "recommended_contract_changes": [],
  "review_summary": [],
  "unresolved_risks": [],
  "recommendation": "select|revise|reject|clarify_requirements"
}

Do not mark approved unless the generated sample exists and passes your review. Do not generate page deliverables for the final app; this worker only explores style.
```

If SubAgents are not available, do not run this contract sequentially in the main thread. Report style sampling as blocked and name the missing SubAgent capability.
