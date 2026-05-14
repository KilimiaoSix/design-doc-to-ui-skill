---
name: design-doc-to-ui-figma-replica
description: "Create or update Figma replicas for design-doc-to-ui runs. Use when a user requests Figma output that must recreate approved AI UI images and React screenshots with at least 80 percent per-page visual similarity. Requires Figma skills, figma-use before use_figma, optional figma-generate-design for React capture, and SubAgent imagegen asset generation for missing illustrations/icons. Blocks if frames are missing, pasted full-screen images are used as implementation, or page scores are below 0.80."
---

# Design Doc To UI Figma Replica

Use this companion skill only from `$design-doc-to-ui` when the user provides a Figma file/link or explicitly requests Figma output.

## Required External Skills

Before Figma write operations:

- read and follow `figma-use`;
- call `figma-use` before every `use_figma` tool call;
- use `figma-generate-design` when capturing the local React prototype is the best way to preserve layout;
- use other Figma skills only when their trigger matches the task.

If Figma tools or required companion instructions are unavailable, mark Figma delivery blocked.

## Source Of Truth

Use only completed design artifacts:

- approved AI page images;
- rendered React route screenshots;
- `qa/structured-design-doc.md`;
- page briefs, worker reviews, main audit, and React visual audit.

Do not recreate screens from the original requirements alone.

## Replica Requirements

For every non-deferred required page:

- create one editable Figma frame with the same route/page name;
- match layout, hierarchy, spacing, colors, type scale, components, cards, controls, and states;
- keep AI images and React screenshots as references, not as full-screen implementation layers;
- add prototype links for primary navigation, main buttons, modal/state flows, and recovery paths where Figma supports them;
- add notes for interactions that React demonstrates better than Figma.

If illustrations, icons, mascots, or decorative assets are missing, request a SubAgent to generate local assets with `image_gen`, place them under `figma-assets/`, and record source/prompt notes.

## 80% Replica Gate

Every page must have `visual_similarity_score >= 0.80`.

Hard failures:

- missing required page frame;
- full-screen screenshot pasted as the implementation;
- missing primary navigation or main action;
- wrong output language;
- material layout/style mismatch;
- unresolved missing assets.

Average score is advisory only and cannot hide a failed page.

## Audit Output

Write `qa/figma-replica-audit.json`:

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
      "notes": "Matches layout, colors, cards, and primary actions."
    }
  ],
  "missing_assets": [],
  "repair_required": []
}
```

Do not mark `passed: true` unless every required page passes the 80% gate.
