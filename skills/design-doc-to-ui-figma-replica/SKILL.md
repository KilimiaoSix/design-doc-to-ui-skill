---
name: design-doc-to-ui-figma-replica
description: "Create or update Figma replicas for design-doc-to-ui runs through page-level SubAgents, with at most 6 active workers. Use when a user requests Figma output that must basically replicate approved AI UI images and React screenshots as fully editable, frontend-handoff-ready frames with at least 80 percent per-page visual similarity and globally verified prototype links. Requires Figma skills, figma-use before use_figma, optional figma-generate-design for React capture, SubAgent imagegen asset reconstruction for missing illustrations/icons, and audit evidence that major elements are editable. Blocks if frames are missing, pasted full-screen images are used as implementation, major UI elements/icons/assets are not editable or replaceable, page scores are below 0.80, prototype links or cross-frame jumps for primary flows are absent, or Figma materially diverges from approved imagegen designs."
---

# Design Doc To UI Figma Replica

Use this companion skill only from `$design-doc-to-ui` when the user provides a Figma file/link or explicitly requests Figma output.

All Figma implementation work must run through page-level Figma Replica SubAgents using `references/figma-replica-worker-prompt.md`. Start one worker per non-deferred required page and keep at most 6 active SubAgents across the run. Before workers start, the main agent must prepare the Figma scaffold and write `qa/figma-scaffold-audit.json` with the target file/page, frame slots, shared styles/variables/components where practical, naming conventions, ownership map, and prototype target contract. Each worker owns exactly one frame and its page-local assets. The main agent prepares inputs, manages batches, registers page worker results, integrates shared styles/components, wires global prototype links and cross-frame jumps, and runs gates; it must not replace page workers with a quick main-thread Figma build.

## Required External Skills

Before Figma write operations:

- read and follow `figma-use`;
- call `figma-use` before every `use_figma` tool call;
- use `figma-generate-design` when capturing the local React prototype is the best way to preserve layout;
- use other Figma skills only when their trigger matches the task.

If Figma tools, SubAgent delegation, image generation, local asset processing, or required companion instructions are unavailable, mark Figma delivery blocked.

## Source Of Truth

Use only completed design artifacts:

- approved AI page images;
- rendered React route screenshots;
- `qa/structured-design-doc.md`;
- page briefs, worker reviews, main audit, and React visual audit.

Do not recreate screens from the original requirements alone. When the React screenshot and approved AI page image differ, prefer the approved AI page image and structured design document unless the React difference is recorded as an approved revision.

## Replica Requirements

For every non-deferred required page:

- create one editable Figma frame with the same route/page name;
- basically replicate layout, hierarchy, spacing, colors, type scale, components, cards, controls, and states;
- keep AI images and React screenshots as locked references outside the implementation frame or clearly separated reference layers, not as full-screen implementation layers;
- make all major UI elements editable or replaceable: text, containers, cards, buttons, form controls, tabs, chips, dividers, icons, illustrations, images, and state panels;
- recreate icons as vectors or individual reusable assets/components where practical; do not substitute generic icons when the approved design has a specific icon language;
- componentize repeated controls and name layers for frontend handoff;
- add prototype links for primary navigation, main buttons, modal/state flows, and recovery paths where Figma supports them;
- record outbound prototype targets for the main agent to wire and verify globally;
- add notes for interactions that React demonstrates better than Figma.

If illustrations, icons, mascots, or decorative assets are missing, the Figma worker must follow the asset reconstruction flow:

1. crop the needed element from the approved AI design image or React screenshot as a local reference;
2. start a SubAgent with `image_gen` to generate a clean single isolated asset on a plain or transparent-friendly background;
3. cut out/remove the background locally when needed;
4. save the processed asset under `figma-assets/`;
5. record source crop, image-gen prompt, processed asset, and Figma usage in `figma-assets/asset-manifest.json`;
6. place the isolated asset as its own Figma layer/component.

Baseline replication requires the Figma frame to preserve the approved image's major regions, section order, visual density, component shape language, key imagery, icon language, and primary action placement. A generic UI kit frame, text-only wireframe, pasted screenshot, or visually plausible but different redesign is non-compliant even when it covers the same requirements.

## Process Management

Figma delivery must produce intermediate process files, not only a final Figma URL:

- `qa/figma-scaffold-audit.json`
- `qa/figma-page-worker-registry.json`
- `qa/figma-page-workers/<page_id>/worker-result.json`
- `qa/figma-page-workers/<page_id>/frame-audit.json`
- `qa/figma-page-workers/<page_id>/review.md`
- `figma-assets/<page_id>/asset-manifest.fragment.json` when page-local assets are generated
- `figma-assets/asset-manifest.json` when any assets are generated or processed
- `qa/figma-prototype-link-plan.json`
- `qa/figma-integration-audit.json`
- `qa/figma-worker-result.json`
- `qa/figma-replica-audit.json`

After every page worker returns, the main agent must run:

```bash
python scripts/record_figma_page_worker_result.py \
  --run-dir <output-run-dir> \
  --page-id <page_id> \
  --worker-result qa/figma-page-workers/<page_id>/worker-result.json \
  --frame-audit qa/figma-page-workers/<page_id>/frame-audit.json \
  --review qa/figma-page-workers/<page_id>/review.md
```

The registry must pass before aggregate Figma audits can pass.

## 80% Replica Gate

Every page must have `visual_similarity_score >= 0.80`.

Hard failures:

- missing required page frame;
- full-screen screenshot pasted as the implementation;
- major UI elements are flattened into a page image instead of editable layers;
- editable element coverage is below 0.95;
- missing primary navigation or main action;
- missing prototype links for primary navigation, main actions, modal/state flows, or recovery paths where Figma supports them;
- missing or failed global cross-frame jumps after main-agent integration;
- wrong output language;
- material layout/style mismatch;
- generic reinterpretation instead of baseline replication of the approved imagegen design;
- missing or generic-substituted icons/assets when the approved design shows specific icons/assets;
- generated assets are not isolated, processed, registered, or traceable in `figma-assets/asset-manifest.json`;
- unresolved missing assets.

Average score is advisory only and cannot hide a failed page.

## Audit Output

Write `qa/figma-replica-audit.json`:

```json
{
  "passed": true,
  "figma_url": "https://www.figma.com/design/...",
  "frame_count": 7,
  "editable_frame_count": 7,
  "full_screen_image_layer_count": 0,
  "prototype_link_count": 20,
  "editable_element_coverage": 0.98,
  "frontend_handoff_ready": true,
  "global_prototype_links_passed": true,
  "asset_manifest": "figma-assets/asset-manifest.json",
  "page_scores": [
    {
      "page_id": "home",
      "visual_similarity_score": 0.86,
      "baseline_replica_passed": true,
      "editable_elements_passed": true,
      "icon_replication_passed": true,
      "asset_reconstruction_passed": true,
      "prototype_links_passed": true,
      "frontend_handoff_ready": true,
      "notes": "Matches layout, colors, cards, and primary actions."
    }
  ],
  "hard_failures": [],
  "cross_frame_navigation_results": [
    {
      "flow": "primary flow",
      "passed": true,
      "notes": ""
    }
  ],
  "missing_assets": [],
  "repair_required": []
}
```

Also write aggregate `qa/figma-worker-result.json` using the schema in `references/figma-replica-worker-prompt.md`. It must include one passing `page_worker_results` entry per required page, `max_active_subagents <= 6`, and `global_prototype_links_passed: true`. `qa/figma-scaffold-audit.json`, `qa/figma-page-worker-registry.json`, `qa/figma-prototype-link-plan.json`, and `qa/figma-integration-audit.json` must also pass.

Do not mark `passed: true` unless every required page passes the 80% gate, baseline replication check, editability check, icon/asset reconstruction check, frontend handoff readiness check, and primary prototype-link check.
