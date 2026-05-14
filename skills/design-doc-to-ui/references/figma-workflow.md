# Figma Workflow

Use Figma only when the user provides a Figma file/link or explicitly asks to create/sync Figma output.

## Prerequisites

Do not start Figma work until:

- the Design Completion Gate has passed;
- every non-deferred required page has an approved final design image;
- the main-agent audit has passed;
- no style-sampling, page-generation, or regeneration SubAgent is still running;
- the structured design document exists.

Figma output must be based on the approved design images, structured design document, and the passed React prototype. Do not create or sync Figma frames from requirements alone while page images are still pending.

When React has been generated, Figma must recreate the same style and interaction mechanism as the React prototype:

- same page routes/screens and naming;
- same visual hierarchy, spacing, colors, components, and states;
- same primary navigation and prototype links;
- same modal/toast/state flows where Figma supports them;
- same notes for interactions that are easier to demonstrate in React than in Figma.

After Figma generation or sync, update the structured design document with the Figma link and any Figma-specific audit notes.

## When User Provides A Figma Link

1. Extract file key and node ID when present.
2. Use Figma tools according to the available Figma skill instructions.
3. Add frames for approved screens, page map, interaction notes, and structured design documentation summaries.
4. Preserve existing content unless the user asks to overwrite.
5. Add links/notes that map Figma frames back to React routes.

## When User Asks To Convert React To Figma

- Generate the local React prototype first, but only after the Design Completion Gate passes and the structured design document exists.
- If capture tooling is available, capture the local page into Figma.
- If capture tooling is unavailable, provide the React prototype and explain the Figma limitation.

## When User Asks For A Figma Prototype

- Use approved design images, the structured design document, and the React prototype as the source of truth.
- Create or update frames for each approved page.
- Add prototype links according to the user flow and route/action definitions in the structured design document.
- Match the React prototype's component style and interaction map rather than creating an unrelated Figma-only visual direction.
- Do not create Figma prototype links for pages whose design image is missing or unapproved, unless the user explicitly approves a partial prototype.

## When No Figma Context Exists

Do not create a Figma file by default. In the final response say:

```text
Figma was not generated because no Figma link was provided and Figma output was not requested.
```

## Figma Output Notes

Figma is an optional design-delivery channel. The canonical outputs of this skill are the structured design document and local React prototype project.
