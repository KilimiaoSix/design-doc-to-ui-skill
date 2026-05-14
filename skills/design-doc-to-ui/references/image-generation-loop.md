# Image Generation Loop

All final UI screen images must be generated with `image_gen` inside page-level SubAgents. The main agent must not call `image_gen` for final UI screen generation and must not perform the final page-calibration loop itself.

## SubAgent Requirement

Before generating any UI screen image:

- Start exactly one page-level SubAgent for the assigned source page.
- Keep at most 6 SubAgents active at the same time across the whole run, including style-sampling workers, page-generation workers, and regeneration workers.
- If more than 6 pages need generation, start page workers in batches and wait for an active worker to finish before spawning the next worker.
- Assign a disjoint output directory to that SubAgent.
- Pass the `app_requirements_summary`, `global_style_contract`, assigned page brief, relevant style assets, source evidence, and output directory.
- Do not ask the user to confirm normal SubAgent use; create the required SubAgent directly when the tool is available.
- If SubAgents are unavailable or unable to access `image_gen`, stop the image-generation phase and report it as blocked. Do not generate the screen image in the main thread.

Do not batch multiple source pages into one worker. A worker may cover important states of its assigned page only when those states are listed in the page brief.

## Prompt Construction

Build prompts from:

- `app_requirements_summary`
- `requested_output_language`
- `global_style_contract`
- assigned page brief
- page source evidence
- relevant reference images
- endpoint guidance
- product domain constraints
- accessibility and quality constraints

Prompt skeleton:

```text
Use case: ui-mockup
Asset type: APP UI screen image draft
Product: <product name>
Output language: <requested_output_language>
Endpoint: <web|pc|mobile|tablet>, target resolution <size>
Source page: <source_page_ref>
Page: <page name>
Purpose: <page purpose>
Style: <selected style name and visual keywords>
Layout: <navigation, content regions, hierarchy>
Required components: <list>
Visible text: "<short exact labels in requested_output_language>"
Brand/IP assets: <how to use them>
Interaction/state shown: <default/success/error/etc>
Constraints: Real usable product UI, not a poster. Text must be minimal, legible, and in requested_output_language. Preserve the selected style contract.
Avoid: <negative constraints>
```

For UI restoration from reference images, include:

```text
Deeply understand the reference interface style and recreate the component effects, layout rhythm, hierarchy, and interaction affordances at high fidelity. The result must look like a real usable APP interface. If mascot/IP cutouts are not provided, generate a matching mascot/IP image element while preserving pose, perspective, material, and brand consistency. Use Hugeicons-like simple line icons unless the selected style requires another icon language.
```

## Iteration Policy

Do not use a fixed 2-3 round limit. Iterate while the result is improving.

Stop when:

- The screen passes the acceptance criteria.
- Additional iterations no longer improve the result.
- The brief is ambiguous or contradictory.
- The requested design cannot be reliably generated with `image_gen`.
- SubAgent delegation or SubAgent `image_gen` access is unavailable.

Each iteration must record:

- prompt used
- generated image path
- review failures
- prompt changes for the next attempt
- approval/blocking decision

## Required Worker Artifacts

Each SubAgent must write these files in its assigned output directory:

- `prompt-history.md`
- `review.md`
- `worker-result.json`
- the selected final image file referenced by `worker-result.json`

The main agent must treat missing worker artifacts as a page failure, not as approval.

## Review Criteria

Check:

- Requirement fit
- Source-page fit
- Output language fit
- Style-contract fit
- Endpoint fit
- Copy and data accuracy
- Brand/IP consistency
- Component realism
- Navigation and hierarchy
- Text legibility
- Absence of obvious AI artifacts, broken layout, fake words, or impossible UI

If a screen fails, revise the prompt with concrete corrections, not generic "make it better" language.
