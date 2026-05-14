# Style Exploration Gate

Run the Style Exploration Gate after requirements summary and before page image generation. The goal is to design a product-specific visual direction, not to pick a fixed catalog preset by default.

## Assets

Use these bundled assets as references and guardrails:

- `assets/style-catalog/catalog.md`: human-readable style catalog.
- `assets/style-catalog/style-presets.json`: structured presets.
- `assets/style-catalog/style-board-contact-sheet.png`: visual overview.
- `assets/style-catalog/generated-samples/*.png`: approved four-endpoint sample boards.
- `assets/style-catalog/endpoints/*.md`: endpoint-specific style guidance.

The 20 preset styles are a vocabulary and quality baseline. They are not the final answer unless the user explicitly asks for a preset or the source has strict matching brand/style guidance.

## Product Visual Principles

Before generating samples, derive:

- product category and credibility needs
- user emotional state and desired feeling
- interaction model and information density
- brand/IP assets and visual signals
- source prototype or screenshot signals
- platform and endpoint priorities
- accessibility and readability constraints
- anti-template risks

Write these into `product_visual_principles`.

## Custom Style Directions

Create 2-3 custom style directions for complete design packages:

- A grounded/default direction that is highly usable and low-risk.
- A brand-forward direction that amplifies the source's strongest identity signals.
- A differentiated direction that explores a more distinctive but still usable visual system.

Each direction must define:

- style direction name
- rationale tied to source evidence
- color system
- typography direction
- component shape language
- icon and illustration/IP rules
- motion/interaction tone when relevant
- endpoint adaptation notes
- negative rules
- risks

Do not reuse catalog preset names as the final direction name unless deliberately selecting that preset. It is fine to cite presets as ingredients, for example "uses the calm surfaces of Health Calm and the task orchestration of AI Assistant Copilot".

## Style Sampling With SubAgents

Read `references/style-sampling-worker-prompt.md`.

Generate style samples before locking `global_style_contract` unless:

- the user explicitly requests a known style/preset and waives style exploration, or
- strict brand guidelines already provide a complete visual system, or
- SubAgents are unavailable, in which case style sampling is blocked.

Rules:

- Use one SubAgent per candidate style direction.
- Keep at most 6 SubAgents active at the same time across the whole run. Style sampling is usually 2-3 workers, but it still counts toward the same limit as page-generation and regeneration workers.
- If style exploration is combined with other active workers, wait until active worker count is below 6 before spawning more.
- Each SubAgent uses `image_gen` to create either a style board or the same representative page in that direction.
- The main agent must not generate style samples with `image_gen`.
- Each SubAgent writes `style-sample-result.json`, `prompt-history.md`, `review.md`, and the final sample image.
- Main agent reviews samples for product fit, originality, scalability, endpoint fit, readability, and anti-template quality.

## When To Ask The User

Ask the user to choose or confirm a style when:

- Multiple generated samples are viable and the choice materially changes the product personality.
- Requirements contain conflicting style signals.
- The source document says only vague words such as "高级", "好看", "年轻", or "科技感".
- The target platform or endpoint priority is unclear.
- Repeated image-generation attempts fail the style review.

Do not ask when:

- The user explicitly asks for autonomous execution.
- The source includes strict brand guidelines or asks to replicate a provided screenshot/prototype style.
- Only one style sample passes review and the rationale is clear.

## `global_style_contract`

After review or user confirmation, lock the style:

```json
{
  "style_direction_id": "",
  "style_name": "",
  "confirmed_by_user": true,
  "source_evidence": [],
  "catalog_references": [],
  "platforms": ["web", "pc", "mobile", "tablet"],
  "visual_keywords": [],
  "color_rules": {},
  "typography": "",
  "component_rules": [],
  "layout_density": "",
  "interaction_tone": "",
  "endpoint_rules": {
    "web": "",
    "pc": "",
    "mobile": "",
    "tablet": ""
  },
  "brand_assets": [],
  "mascot_or_ip_rules": [],
  "negative_rules": [],
  "accessibility_risks": [],
  "selected_sample_image": "",
  "rejected_directions": []
}
```

Every page prompt, page review, HTML prototype, and final design document must reference this contract.

## Fast Path

Use the fast path only when the user explicitly requests speed over exploration or provides a complete visual style. In fast path:

- Still write `product_visual_principles`.
- Still state why style sampling was skipped.
- Still lock a `global_style_contract`.
- Do not pretend a preset was validated by image sampling.
