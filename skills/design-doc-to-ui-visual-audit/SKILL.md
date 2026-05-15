---
name: design-doc-to-ui-visual-audit
description: "Audit visual parity and baseline replication for design-doc-to-ui React and Figma outputs. Use when comparing rendered React route screenshots or Figma frames against approved AI UI images. Scores every required page across layout, components, visual style, typography, assets, and interaction state coverage. Requires each page to reach visual_similarity_score at least 0.80 and fails hard for missing pages, screenshot-only implementations, missing primary navigation/actions, broken interactions/prototype links, wrong language, generic reinterpretations, or material visual drift from approved imagegen designs."
---

# Design Doc To UI Visual Audit

Use this companion skill from `$design-doc-to-ui` for React and Figma visual parity gates.

## Inputs

Required:

- `ui-run.json`;
- approved AI page images;
- rendered React route screenshots or Figma frame screenshots;
- structured design document;
- page briefs and worker reviews.

Do not score from descriptions alone. If screenshots are unavailable, mark the audit blocked.

## Scoring Rubric

Score each page out of 100:

- layout and information hierarchy: 25;
- component completeness: 20;
- color, material, and visual style: 20;
- typography, copy language, and density: 15;
- key images, icons, and decorative assets: 10;
- interaction states and prototype links: 10.

Convert the page score to `visual_similarity_score` by dividing by 100.

Baseline replication is a separate qualitative check. A page passes this check only when the implementation preserves the approved AI image's major regions, section order, visual density, component shape language, key imagery, primary actions, and state presentation. A generic redesign that covers the same requirements but does not look like the approved image fails even if individual rubric categories seem partially satisfied.

For React, also check interaction fidelity:

- primary navigation targets load the intended route;
- primary buttons produce the declared route, modal, toast, or state change;
- controls that look interactive actually update state or are explicitly disabled/blocked;
- declared success, error, empty, loading, modal, blocked, and quota states are reachable or documented as unavailable.

For Figma, also check prototype-link fidelity:

- primary navigation and main actions have prototype links where Figma supports them;
- modal/state/recovery flows are linked or clearly annotated;
- frames are editable reconstructions, not pasted full-screen images.

## Pass/Fail Rules

- Every required page must have `visual_similarity_score >= 0.80`.
- Global average is advisory only.
- Do not allow the average score to hide a failed page.
- Hard fail when a required page is missing, the implementation is a full-screen screenshot/image browser, baseline replication fails, primary navigation/main actions are absent, React interactions are broken, Figma primary prototype links are missing, language is wrong, or material visual drift is obvious.

## Repair Guidance

For each failed page, produce concise repair prompts:

- name the missing/mismatched sections;
- identify style drift;
- call out missing controls/states/assets;
- state whether repair belongs in React, Figma, or asset generation.

## Audit Output

Write `qa/visual-parity-audit.json`:

```json
{
  "passed": true,
  "target": "react",
  "page_scores": [
    {
      "page_id": "home",
      "visual_similarity_score": 0.84,
      "baseline_replica_passed": true,
      "interaction_or_prototype_links_passed": true,
      "layout": 22,
      "components": 18,
      "style": 17,
      "typography": 13,
      "assets": 7,
      "interactions": 7,
      "notes": "Main structure and actions match; minor card spacing drift."
    }
  ],
  "global_average": 0.84,
  "hard_failures": [],
  "repair_prompts": []
}
```

Set `target` to `react` or `figma`. Do not mark `passed: true` unless every required page passes.
