# User Feedback Revision Workflow

Use this workflow when a user asks to change an existing design-doc-to-ui run after style samples, page images, the structured design document, React prototype, Feishu document, or Figma replica already exists.

The goal is to revise the approved design package without losing traceability. Keep `ui-run.json` as the canonical inventory, preserve earlier artifacts when practical, and rerun the same gates that protect initial delivery quality.

## Revision Inputs

Collect or infer:

- run directory and `ui-run.json` path;
- current structured design document;
- current `global_style_contract`;
- affected page ids, routes, or delivery channels;
- user feedback text, screenshots, marked-up images, or examples;
- latest worker results and main-audit status for affected pages;
- latest React visual parity report and optional Feishu/Figma audit reports.

If the run directory is unknown, search the current workspace for `ui-run.json` and ask only if multiple plausible runs exist.

## Feedback Classification

Classify feedback before editing artifacts:

1. Global style change
   - Examples: "overall style is wrong", "too childish", "not premium", "make the whole product more enterprise", "replace the visual language".
   - Update or replace `global_style_contract`.
   - Regenerate style samples when the new direction is broad, ambiguous, or materially changes product personality.
   - Regenerate all pages whose approved images depend on the old style.

2. Page-level layout or content change
   - Examples: "home page hierarchy is wrong", "dashboard is too sparse", "detail page misses the comparison section".
   - Revise the affected page brief and page prompt.
   - Start one new page-level SubAgent for each affected source page.

3. Element or component-level change
   - Examples: "this button should be less rounded", "card spacing is too loose", "replace the hero mascot", "make the tabs look native".
   - Treat as a page revision unless the element exists only in React and the approved design image is still correct.
   - Add concrete constraints to the affected page brief: component, location, old issue, desired behavior, visual rule, and negative rule.

4. Copy, data, or interaction change
   - Examples: label changes, missing empty state, different modal flow, added quota state.
   - Update page briefs, route targets, state requirements, and prototype interactions.
   - Regenerate page images if visible layout, hierarchy, or state presentation changes.
   - Patch React directly only for non-visual logic/copy changes that do not invalidate approved images.

5. Source requirement or page inventory change
   - Examples: new page, removed page, merged flow, newly discovered requirement from source.
   - Update `app_requirements_summary` and `page_inventory`.
   - Add or revise page briefs.
   - Re-run coverage checks before image generation.
   - Do not silently defer new required pages.

6. React implementation mismatch
   - Examples: React spacing differs from approved image, route missing, button interaction broken, declared state unreachable.
   - Restart or reuse the dedicated React Prototype SubAgent for the affected prototype scope; the worker owns `prototype/` and must repair the formal component-level frontend, not add hotspots over images.
   - Require the patched React route to basically replicate the approved image and pass primary interaction checks.
   - Rerun `react-worker-result.json`, `react-interaction-audit.json`, visual parity, and functional audits.
   - Do not regenerate approved images unless the user dislikes the design image itself.

7. Feishu or Figma delivery mismatch
   - Examples: Feishu doc lacks design narrative, Figma frame diverges from approved imagegen design or React/design package, Figma prototype links are missing.
   - Use the corresponding companion skill after the design package and React prototype are current.
   - Rerun the related delivery audit.
   - For Figma, restart or reuse the dedicated Figma Replica SubAgent. Require fully editable, frontend-handoff-ready frames that basically replicate approved AI page images; a generic reconstruction, pasted screenshot, or non-editable icon/asset treatment is not acceptable.
   - If assets are missing, use the crop-reference -> image-gen isolated asset -> background cleanup -> individual Figma layer/component -> asset manifest flow.

## Revision Plan

Write a short revision plan before modifying artifacts. Prefer a small JSON or Markdown artifact under `qa/`, for example `qa/revision-plan.json` or `qa/revision-log.md`.

Include:

- revision id, timestamp, and feedback source;
- classification;
- affected pages and delivery channels;
- artifacts to edit;
- whether style samples, page regeneration, React patching, Feishu sync, or Figma sync are required;
- gates that must be rerun;
- risks or clarifications.

Example:

```json
{
  "revision_id": "rev-002",
  "feedback": "Overall design is too playful; make it more enterprise and data-dense.",
  "classification": ["global_style_change"],
  "affected_pages": ["home", "analytics", "settings"],
  "requires_style_resampling": true,
  "requires_page_regeneration": true,
  "requires_react_update": true,
  "requires_figma_update": false,
  "gates_to_rerun": ["style-exploration", "main-audit", "design-completion", "visual-parity", "delivery"]
}
```

## Artifact Rules

- Preserve earlier approved worker directories and images when practical.
- Use a new worker output directory for regenerated pages, such as `workers/<page_id>-rev-002/`.
- Do not edit SubAgent worker artifacts to make an old result appear revised.
- Do not let a SubAgent edit `ui-run.json`.
- Register each new page result from the main thread with `scripts/record_ui_worker_result.py`.
- Expect validation gates to fail while revision work is in progress.
- Update the structured design document after regenerated images or React/Figma/Feishu changes are complete.

If a manifest does not have a dedicated revision field, keep revision metadata in `qa/revision-log.md` or `qa/revision-plan.json`. Avoid inventing unsupported page statuses unless the validation scripts have been updated to understand them.

## Execution Flow

1. Load current run state:
   - inspect `ui-run.json`;
   - run `scripts/ui_job_status.py --run-dir <run-dir>`;
   - inspect the latest validation and audit reports.

2. Classify the feedback and identify affected artifacts.

3. Write the revision plan.

4. Apply upstream changes:
   - update `app_requirements_summary` or page inventory only when requirements changed;
   - update `global_style_contract` for global visual direction changes;
   - update affected page briefs for page, element, copy, or interaction changes.

5. Regenerate design images when needed:
   - create one page-level SubAgent per affected source page;
   - pass the revision plan, updated style contract, updated page brief, and prior approved image as context;
   - require the worker to write `worker-result.json`, `review.md`, `prompt-history.md`, and a final image;
   - run `record_ui_worker_result.py` for each returned worker.

6. Re-run main-agent audit across all affected pages and cross-page consistency.

7. Update the structured design document:
   - add a revision summary;
   - update page specs, images, interaction notes, and audit notes;
   - mark downstream React/Feishu/Figma status as pending when affected.

8. Re-run `validate_design_run.py --phase design-completion`.

9. Update React if any approved design image, page brief, route, state, or interaction changed.

10. Re-run React visual parity and final functional audit.

11. Update Feishu and Figma only if requested or already part of the active delivery package, using their companion skills.

12. Run `validate_design_run.py --phase delivery` after all requested channels are current.

## SubAgent Regeneration Prompt Additions

When regenerating an affected page, add this context to the normal page worker prompt:

```text
Revision context:
- revision_id: <id>
- user feedback: <exact feedback>
- prior approved image: <path>
- specific issues to fix: <list>
- constraints to preserve: <what must remain from the prior approved design>
- updated style/page brief changes: <summary>

Generate a revised UI image for the same source page only. Preserve unaffected requirements and cross-page consistency. Do not redesign unrelated pages. Write new worker artifacts in the assigned revision output directory.
```

## When To Ask The User

Ask for clarification when:

- the feedback is subjective and could map to multiple visual directions;
- multiple generated style samples are viable and the choice changes product personality;
- feedback conflicts with source requirements or accessibility;
- a requested change would require deferring or removing a required page;
- the user asks for a partial revision while dependent pages or delivery channels would become inconsistent.

Do not ask for confirmation for routine SubAgent use, page regeneration, React visual parity checks, or standard gate reruns.

## Completion Criteria

A revision is complete only when:

- every affected page has updated briefs or a documented reason no brief change was needed;
- every affected design image is regenerated or explicitly kept with rationale;
- regenerated page workers have required artifacts and are registered in `ui-run.json`;
- main-agent audit passes for affected pages and cross-page consistency;
- structured design document reflects the revision;
- React visual parity passes when React is affected;
- Feishu/Figma audits pass when those channels are affected or requested;
- delivery validation passes, or remaining issues are explicitly blocked with reasons.

## Companion Skill Boundary

Keep this workflow in the main skill by default. It should become a separate companion skill only when users frequently start from an already completed design package and ask for standalone revision work, for example:

- "Use this existing ui-run.json and revise the dashboard style."
- "Apply these screenshot comments to the existing React/Figma design package."
- "Run only the post-review correction workflow on this previous delivery."

If split into a companion skill, the companion must still use the original `ui-run.json`, page briefs, worker registration script, main-audit rules, and delivery gates. It must not create a separate manifest or bypass SubAgent/image generation requirements.
