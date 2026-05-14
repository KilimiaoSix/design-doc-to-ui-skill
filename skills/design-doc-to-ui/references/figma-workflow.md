# Figma Workflow

Use Figma only when the user provides a Figma file/link or explicitly asks to create/sync Figma output.

## Prerequisites

Do not start Figma work until:

- the Design Completion Gate has passed;
- every non-deferred required page has an approved final design image;
- the main-agent audit has passed;
- no style-sampling, page-generation, or regeneration SubAgent is still running;
- the structured design document exists.

Figma output must be based on the approved design images and structured design document. Do not create or sync Figma frames from requirements alone while page images are still pending.

After Figma generation or sync, update the structured design document with the Figma link and any Figma-specific audit notes.

## When User Provides A Figma Link

1. Extract file key and node ID when present.
2. Use Figma tools according to the available Figma skill instructions.
3. Add frames for approved screens, page map, interaction notes, and structured design documentation summaries.
4. Preserve existing content unless the user asks to overwrite.

## When User Asks To Convert HTML To Figma

- Generate the local HTML prototype first, but only after the Design Completion Gate passes and the structured design document exists.
- If capture tooling is available, capture the local page into Figma.
- If capture tooling is unavailable, provide the HTML prototype and explain the Figma limitation.

## When User Asks For A Figma Prototype

- Use approved design images and the structured design document as the source of truth.
- Create or update frames for each approved page.
- Add prototype links according to the user flow and route/action definitions in the structured design document.
- Do not create Figma prototype links for pages whose design image is missing or unapproved, unless the user explicitly approves a partial prototype.

## When No Figma Context Exists

Do not create a Figma file by default. In the final response say:

```text
Figma was not generated because no Figma link was provided and Figma output was not requested.
```

## Figma Output Notes

Figma is an optional design-delivery channel. The canonical outputs of this skill are the structured design document and local HTML prototype folder.
