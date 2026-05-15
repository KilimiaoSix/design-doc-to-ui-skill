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

Before generating samples, first inspect the original source document, source bundle, requirements summary, tables, screenshots, and brand notes for explicit expected style types.

Write `source_style_expectations` before proposing directions:

```json
{
  "has_explicit_style_expectation": true,
  "expected_style_types": ["企业级工作台", "AI Assistant Copilot"],
  "source_evidence": [
    {
      "quote_or_section": "",
      "interpretation": "",
      "strength": "explicit|strong|weak"
    }
  ],
  "weighting_rule": "high-priority source constraint; must influence candidate directions before catalog defaults",
  "conflicts_or_risks": []
}
```

Treat explicit source style expectations as high-priority constraints. They outrank catalog presets, generic "good taste", and the agent's preferred visual direction. At least one candidate direction must directly anchor on the expected style type, and no selected final style may contradict it unless the source expectation conflicts with accessibility, platform fit, or a later user instruction. If source style signals conflict, ask the user or generate contrasting samples that make the tradeoff explicit.

After extracting source style expectations, derive:

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

- A grounded/default direction that is highly usable and low-risk while respecting explicit source style expectations.
- A brand-forward direction that amplifies the source's strongest identity and expected style signals.
- A differentiated direction that explores a more distinctive but still usable visual system.

If the source document explicitly names a style type or benchmark, raise its weight in every candidate direction:

- include it in the direction rationale with source evidence;
- map it to relevant catalog references only as supporting ingredients;
- preserve its key visual traits in color, typography, component shape, icon/illustration rules, and density;
- add negative rules preventing accidental drift away from it;
- reject style samples that ignore or dilute it without a documented reason.

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
- source style expectation alignment and weighting

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
- Inputs passed to each SubAgent must include `source_style_expectations`. When `has_explicit_style_expectation` is true, the worker must treat it as a weighted constraint in the image-generation prompt and review.
- The main agent must not generate style samples with `image_gen`.
- Each SubAgent writes `style-sample-result.json`, `prompt-history.md`, `review.md`, and the final sample image.
- Main agent reviews samples for product fit, originality, scalability, endpoint fit, readability, and anti-template quality.

If a candidate direction deliberately deviates from an explicit source style expectation, label it as exploratory and lower priority. It cannot be selected unless the user chooses it or the main agent documents why the source expectation is infeasible.

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
  "source_style_expectations": {},
  "style_expectation_weighting": "explicit source style signals were treated as high-priority constraints",
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

Every page prompt, page review, React prototype, and final design document must reference this contract.

Do not lock `global_style_contract` if explicit source style expectations were ignored, omitted from the selected direction rationale, or contradicted without a recorded reason.

## Fast Path

Use the fast path only when the user explicitly requests speed over exploration or provides a complete visual style. In fast path:

- Still write `product_visual_principles`.
- Still state why style sampling was skipped.
- Still lock a `global_style_contract`.
- Do not pretend a preset was validated by image sampling.
