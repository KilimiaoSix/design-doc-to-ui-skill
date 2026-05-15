# Style Sampling Worker Prompt

Use this as the base prompt when delegating one custom style direction. Style-sample image generation must run in a SubAgent; do not use a main-thread fallback.

```text
You are responsible for generating and reviewing one custom visual style sample for the product. You are not alone in the workspace; do not modify files outside your assigned output directory, do not revert others' edits, and adapt to existing outputs.

Inputs:
- app_requirements_summary: <paste or reference>
- requested_output_language: <paste>
- product visual principles: <paste>
- source_style_expectations: <paste; include explicit expected style types and evidence from the original source>
- candidate_style_direction: <paste exactly one direction>
- key page or style-board scenario: <paste>
- relevant source images and brand assets: <paths>
- style catalog references: <paths, optional>
- output directory: <path>

Task:
1. Review `source_style_expectations` before writing the prompt. If the source explicitly names or strongly implies an expected style type, treat it as a high-weight constraint and preserve its key traits unless the candidate direction explicitly marks itself as exploratory.
2. Build one image-generation prompt for the assigned custom style direction.
   - Include source style evidence in the prompt when present.
   - Do not let generic catalog vocabulary override an explicit source style request.
   - If the candidate direction differs from the source expectation, state the deviation in `review.md` and lower the recommendation unless the deviation solves a documented risk.
3. Use image_gen to generate either:
   - a style board that shows the visual system across key components and endpoints, or
   - the same representative page rendered in this style direction.
4. Review the sample for product fit, originality, scalability across all required pages, brand/source fit, explicit source-style alignment, readability, and absence of generic template feel.
5. Iterate while the result is improving.

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
  "source_style_expectations_used": true,
  "source_style_alignment": "aligned|partially_aligned|conflicts|not_applicable",
  "source_style_alignment_notes": [],
  "visual_keywords": [],
  "recommended_contract_changes": [],
  "review_summary": [],
  "unresolved_risks": [],
  "recommendation": "select|revise|reject|clarify_requirements"
}

Do not mark approved unless the generated sample exists, passes your review, and respects explicit source style expectations or clearly documents why the candidate is exploratory. Do not generate page deliverables for the final app; this worker only explores style.
```

If SubAgents are not available, do not run this contract sequentially in the main thread. Report style sampling as blocked and name the missing SubAgent capability.
