# Feishu/Lark Delivery

Use this reference only when the user explicitly asks to upload, publish, or sync the final design package to Feishu/Lark.

## Preconditions

Do not upload partial work unless the user explicitly approves partial delivery.

Required before Feishu upload:

- structured design document exists and uses `requested_output_language`;
- every non-deferred required page image exists and is referenced in the document;
- React prototype exists and has passed the Final Functional Audit;
- blocked, infeasible, and deferred pages are clearly marked.

## Tooling

- Use the relevant `lark-*` skill or `lark-cli` workflow available in the environment.
- Prefer creating or updating a Feishu docx/wiki document for the structured design document.
- Upload page images as document images/attachments and insert them near each page spec.
- If the React project is too large to embed, upload a ZIP or provide the local project path and include run instructions in the Feishu document.

## Output Contract

The Feishu document must contain:

- 产品概要 / product summary;
- 页面地图 / page inventory;
- every required page section with its imagegen-generated UI image;
- visual style contract;
- React prototype path or uploaded artifact link;
- Final Functional Audit result;
- open questions, risks, blocked pages, infeasible pages, and user-approved deferred pages.

After upload, update the local structured design document with the Feishu link and upload notes.
