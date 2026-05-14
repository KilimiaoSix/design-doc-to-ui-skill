# Style Board Review Rubric

Use this rubric to decide whether a generated style board can enter the final catalog.

## Required Structure

- The board contains exactly four clearly separated endpoint examples: Web, PC, Mobile, Tablet.
- Endpoint examples should adapt layout density rather than duplicating the same screen at different sizes.
- The style name must be inferable from visual traits, not only from labels.

## Product Realism

- Looks like a usable application interface, not a poster, ad, abstract moodboard, or landing-page hero only.
- Includes real app structures: navigation, content areas, controls, cards/lists, forms, charts, feed items, or task surfaces as appropriate.
- Avoids impossible UI, unreadable microtext, excessive decorative elements, and hallucinated controls.

## Style Fidelity

- Color, typography, spacing, radius, shadows/material, icons, imagery, and hierarchy match the intended style.
- The four endpoints share the same visual language.
- Platform conventions are respected where the style is platform-native.

## Accessibility and Usability

- Text contrast appears sufficient.
- Tap targets look large enough on mobile and tablet.
- Risky styles such as glassmorphism, neumorphism, brutalism, dark mode, and dense dashboards include explicit mitigation notes.
- Controls are visually distinguishable from content.

## Approval States

- `approved`: Meets all required structure and style criteria, with only minor residual risks.
- `needs_iteration`: Promising but has fixable issues; prompt should be revised and regenerated.
- `blocked`: image generation unavailable, file could not be located, or repeated generation cannot satisfy the core criteria.

Do not mark a style as approved without an actual generated sample path.
