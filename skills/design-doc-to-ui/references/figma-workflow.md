# Figma Replica Workflow

Use Figma only when the user provides a Figma file/link or explicitly asks to create/sync Figma output.

## Required Companion Skill

Before Figma work, load `design-doc-to-ui-figma-replica/SKILL.md`.

If the companion skill is unavailable, mark Figma delivery blocked. Do not create a simplified Figma file from the main skill alone.

## Prerequisites

Do not start Figma work until:

- the Design Completion Gate has passed;
- every non-deferred required page has an approved final design image;
- the main-agent audit has passed;
- no style-sampling, page-generation, or regeneration SubAgent is still running;
- the structured design document exists;
- the React prototype exists and has passed visual parity and interaction audit.

Figma output must be based on the approved AI page images, structured design document, and the passed React prototype. Do not create or sync Figma frames from requirements alone while page images are still pending. When React and the approved AI image disagree, treat the approved AI image and structured design document as the visual source of truth unless the React change is explicitly documented as an approved revision.

Start one page-level Figma Replica SubAgent per non-deferred required page using `design-doc-to-ui-figma-replica/references/figma-replica-worker-prompt.md`. Run page workers in batches with at most 6 active SubAgents across the whole design-doc-to-ui run.

Before starting page workers, the main agent must prepare the Figma scaffold and write `qa/figma-scaffold-audit.json`: target file/page, frame slots for every required page, shared styles/variables/components where practical, naming conventions, frame ownership map, and prototype target contract.

Each Figma page worker owns exactly one page frame and its page-local `figma-assets/<page_id>/` artifacts. The main agent owns the Figma file structure, shared styles/components/tokens, global prototype links, cross-frame navigation, aggregate `qa/figma-worker-result.json`, and final `qa/figma-replica-audit.json`. The main agent must not replace page workers with a quick main-thread Figma build.

## Process Management Files

Figma work must be managed through intermediate files, not only a final Figma URL. Treat these files as the Figma equivalent of page-image worker outputs in `ui-run.json`:

- `qa/figma-scaffold-audit.json`: main-agent Figma file scaffold, shared styles/components, frame slots, ownership map, and prototype target contract.
- `qa/figma-page-worker-registry.json`: main-thread registry of every Figma page worker result.
- `qa/figma-page-workers/<page_id>/worker-result.json`: page frame implementation result.
- `qa/figma-page-workers/<page_id>/frame-audit.json`: page-local Figma frame audit.
- `qa/figma-page-workers/<page_id>/review.md`: page worker self-review and repair notes.
- `figma-assets/<page_id>/asset-manifest.fragment.json`: page-local generated/processed asset records, when assets are needed.
- `figma-assets/asset-manifest.json`: merged asset manifest.
- `qa/figma-prototype-link-plan.json`: main-agent plan mapping page-worker outbound targets to Figma prototype links.
- `qa/figma-integration-audit.json`: main-agent audit for global prototype links, cross-frame jumps, shared styles, and handoff consistency.
- `qa/figma-worker-result.json`: aggregate Figma implementation result.
- `qa/figma-replica-audit.json`: final Figma delivery gate.

After each Figma page worker returns, register it from the main thread:

```bash
python scripts/record_figma_page_worker_result.py \
  --run-dir <output-run-dir> \
  --page-id <page_id> \
  --worker-result qa/figma-page-workers/<page_id>/worker-result.json \
  --frame-audit qa/figma-page-workers/<page_id>/frame-audit.json \
  --review qa/figma-page-workers/<page_id>/review.md
```

The registry must contain one passing page entry per non-deferred required page before the main agent writes aggregate Figma results.

## Replica Requirements

For each required page:

- create one corresponding editable Figma frame;
- basically replicate layout, information hierarchy, spacing, colors, type scale, component shapes, and major decorative resources from the AI page image and React screenshot;
- keep the approved image and React screenshot as references only, not as full-screen implementation layers;
- make all major UI elements editable or replaceable, including text, cards, controls, icons, illustrations, image assets, and state panels;
- recreate icons and repeated controls as vectors, components, or individual replaceable assets where practical;
- make the frame frontend-handoff ready with clear layers, reusable styles/variables/components where practical, and annotations for implementation-critical details;
- add prototype links for primary navigation, main buttons, modal/state flows, and recovery paths where Figma supports them;
- record page-local outbound prototype targets for the main agent to wire and verify globally;
- use SubAgent + imagegen to reconstruct missing local assets such as illustrations, icons, mascots, or decorative resources, then register them in `figma-assets/asset-manifest.json`.

Every page must score at least `visual_similarity_score >= 0.80`. Average score cannot hide a failed page.

Baseline Figma replication means:

- every non-deferred required page has a corresponding frame with the same route/page identity;
- major regions, section order, visual density, component shapes, and key imagery match the approved image closely enough to review the same design;
- Figma does not substitute a generic layout, component library default, pasted screenshot, or text-only wireframe for the image-generated design;
- editable element coverage is at least 0.95 and no primary UI region is flattened into a screenshot;
- icons and visual assets match the approved image language instead of using generic substitutes;
- primary navigation and main actions have prototype links or documented Figma limitations;
- global prototype links and cross-frame jumps are verified by the main agent after all page frames are complete;
- any intentional divergence is listed in `qa/figma-replica-audit.json` with a reason and repair plan if needed.

## Missing Asset Reconstruction

When an icon, illustration, mascot, decorative asset, or image element cannot be recreated directly:

1. crop the desired element from the approved AI design image or React screenshot as a local reference;
2. delegate an asset SubAgent to use `image_gen` to generate a clean, single isolated asset on a plain or transparent-friendly background;
3. process the generated asset locally to remove/crop the background where needed;
4. save source crop, generated image, processed asset, prompt, and usage notes under `figma-assets/`;
5. place the processed asset as an individual Figma layer/component;
6. record it in `figma-assets/asset-manifest.json`.

Do not solve missing assets by pasting a larger region or full-page screenshot into the Figma frame.

## Tooling

- Use Figma tools according to the available Figma skill instructions.
- Before every `use_figma` call, load the `figma-use` skill.
- Use `figma-generate-design` when capturing the local React prototype is the best route to preserve layout.
- Preserve existing Figma content unless the user asks to overwrite.
- Add frame notes that map Figma frames back to React routes and approved page images.

## Output Contract

Write `qa/figma-replica-audit.json` with:

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
      "notes": "Matches layout, color, cards, and primary actions."
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

Also require aggregate `qa/figma-worker-result.json`, with one passing `page_worker_results` entry per required page, `max_active_subagents <= 6`, and `global_prototype_links_passed: true`.

Also require `qa/figma-scaffold-audit.json`, `qa/figma-page-worker-registry.json`, `qa/figma-prototype-link-plan.json`, and `qa/figma-integration-audit.json` to pass. These files are mandatory process artifacts; a Figma URL without them is not a complete delivery.

## When No Figma Context Exists

Do not create a Figma file by default. In the final response say:

```text
Figma was not generated because no Figma link was provided and Figma output was not requested.
```

Figma is an optional design-delivery channel. The canonical outputs of this skill are the structured design document and local React prototype project.
