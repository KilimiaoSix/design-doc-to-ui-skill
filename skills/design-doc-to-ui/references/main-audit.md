# Main-Agent Audit

Run this after all page workers return and before writing the final design document or React prototype.

When a scripted run exists, run `scripts/ui_job_status.py --run-dir <output-run-dir>` before the audit and use `ui-run.json` as the page/artifact inventory.

## Audit Inputs

- Original source document or summary
- `app_requirements_summary`
- `page_inventory`
- `global_style_contract`
- all page briefs
- all generated images
- all worker output directories
- all worker `worker-result.json`, `review.md`, and `prompt-history.md` files

## Coverage Checks

Verify these counts and mappings:

- Source required page count equals required page brief count.
- Required page brief count equals worker-result count, excluding only `user-approved deferred` pages.
- Every non-deferred required page has a final image file.
- Every non-deferred required page appears in the design document plan.
- Every non-deferred required page has a planned React route/view.

Missing pages are blocking failures. A missing page may be reported only as `blocked`, `infeasible`, or `user-approved deferred`; it must not be counted as approved.

## Visual And Requirement Checks

- Every page matches its brief.
- Every page is grounded in its source evidence.
- Cross-page visual language is consistent.
- Navigation and user flow are coherent.
- Typography, colors, components, icons, and mascot/IP usage are consistent.
- Text is readable, uses `requested_output_language`, and does not introduce unsupported claims.
- AI artifacts, layout breaks, fake words, and poster-like compositions are absent.
- Endpoint-specific constraints are respected.
- Important success, error, empty, blocked, modal, and loading states are covered by page images or by the React prototype plan.

## Failure Handling

If a page fails:

1. Identify the cause:
   - weak prompt
   - weak page brief
   - missing asset
   - conflicting requirements
   - image-generation limitation
   - missing worker artifact
   - output language mismatch
2. Revise the prompt or brief when possible.
3. Start a new SubAgent for that page.
   - If SubAgent delegation is technically unavailable, mark regeneration blocked.
   - Respect the global 6-active-SubAgent limit when launching regeneration workers.
   - Do not regenerate UI screen images sequentially in the main thread.
4. If repeated attempts fail, reassess feasibility.
5. Mark infeasible only after explaining the exact blocker and a practical alternative.

Main-agent approval is required before generating final design documents and React prototype.

## Design Completion Gate

Before writing the structured design document, React prototype, or Figma prototype, verify:

- `global_style_contract` is locked.
- Every non-deferred required page has an approved worker result and final image.
- Every non-deferred required page passed main-agent audit.
- No required page is missing a brief, worker result, review, prompt history, or final image.
- No style-sampling, page-generation, or regeneration SubAgent is still running.

If this gate fails, do not start React or Figma work. A partial prototype is allowed only after the user explicitly approves partial output with the missing pages listed.

After the structured design document is written, enforce the gate with:

```bash
python scripts/validate_design_run.py --run-dir <output-run-dir> --phase design-completion
```

Treat `passed: false` or `react_allowed: false` as blocking. Existing manifests may also expose `html_allowed` with the same value. Do not start React/Figma from requirements alone.

## Final Functional Audit

Run this after creating the React prototype:

- Open or inspect the prototype when browser tools are available.
- Verify every non-deferred required page has a route/view.
- Click or inspect every main navigation target and primary action.
- Verify form controls, selectors, tabs, dialogs, toasts, and declared page states work.
- Verify visible UI copy, document title, HTML `lang`, navigation labels, metadata, and review labels use `requested_output_language`.
- Verify rendered React screenshots visually recreate the approved AI page images.
- Verify `qa/visual-parity-audit.json` exists and every required page has `visual_similarity_score >= 0.80`.
- Verify screenshots are not the main UI implementation. Full-page images may appear only as visual references, thumbnails, or review attachments.
- Record pass/fail results and required fixes.

Do not mark the delivery complete until the Final Functional Audit, React Visual Parity Gate, and requested Feishu/Figma delivery gates pass or every failed item is explicitly blocked with a reason.
