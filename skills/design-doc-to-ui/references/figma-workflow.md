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

Figma output must be based on the approved AI page images, structured design document, and the passed React prototype. Do not create or sync Figma frames from requirements alone while page images are still pending.

## Replica Requirements

For each required page:

- create one corresponding editable Figma frame;
- recreate layout, information hierarchy, spacing, colors, type scale, component shapes, and major decorative resources from the AI page image and React screenshot;
- keep the approved image and React screenshot as references only, not as full-screen implementation layers;
- add prototype links for primary navigation, main buttons, modal/state flows, and recovery paths where Figma supports them;
- use SubAgent + imagegen to generate missing local assets such as illustrations, icons, mascots, or decorative resources, then register them in `figma-assets/`.

Every page must score at least `visual_similarity_score >= 0.80`. Average score cannot hide a failed page.

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
  "prototype_link_count": 20,
  "page_scores": [
    {
      "page_id": "home",
      "visual_similarity_score": 0.86,
      "notes": "Matches layout, color, cards, and primary actions."
    }
  ],
  "missing_assets": [],
  "repair_required": []
}
```

## When No Figma Context Exists

Do not create a Figma file by default. In the final response say:

```text
Figma was not generated because no Figma link was provided and Figma output was not requested.
```

Figma is an optional design-delivery channel. The canonical outputs of this skill are the structured design document and local React prototype project.
