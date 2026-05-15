# Structured Design Document Output

Generate the structured design document after the main-agent audit passes, after the AI design images have user approval, and before Feishu/React/Figma implementation begins. This document is the product design source of truth for Feishu rich documents, React, and optional Figma replica implementation.

The document's primary job is to explain the product design: user problem, design proposition, user stories, information architecture, task flows, design decisions, state behavior, component system, content/data model, page specs, and review risks. It must be a clean design document. Do not include delivery conclusions, worker status, audit results, link indexes, React/Figma/Feishu acceptance reports, or other delivery materials in this document.

In a scripted run, write the document to the `structured_design_doc` path recorded in `ui-run.json` unless the user requests another path. The document must exist before `validate_design_run.py --phase design-completion` can allow React/Figma.

Also read `references/design-doc-quality-gate.md`. After writing the document, audit it and write `qa/structured-design-doc-audit.json` before running the Design Completion Gate.

## Language Rules

- Use `requested_output_language` for the document title, headings, table headers, body text, review summaries, and risk labels.
- If the user request is Chinese or the source document is Chinese and the user gives no other preference, write the whole structured document in Chinese.
- Do not default to English section names such as "Product Summary" or "Review Summary" when `requested_output_language` is not English.
- Do not use English delivery/process headings such as "Encoding repair", "Delivery index", "Delivery evidence", "Page evidence matrix", "Audit matrix", "Structured design document", "Page images and acceptance", or "Final acceptance" in a Chinese document.
- Keep product claims tied to the source document and separate confirmed requirements from agent assumptions.

## Design Document Quality Bar

A page-by-page catalog is not enough. The document must be a review-ready product design document, not a delivery status report. A product manager should be able to evaluate scope and risks, a designer should be able to critique rationale and system consistency, an engineer should be able to implement from it, and QA should be able to test from it.

Do not pass the document when it contains delivery bookkeeping, encoding repair notes, worker/audit status, link indexes, React/Figma/Feishu delivery acceptance, or generic status rows such as "React worker passed". Also fail placeholder serialization such as `[object Object]`, mojibake/question-mark replacement runs, shallow one-line page descriptions, or section headings with no concrete content.

Delivery evidence is not part of the design document. Keep worker evidence, audit paths, run commands, Feishu links, Figma links, React project paths, visual parity scores, and upload verification in local `qa/` artifacts or a separate local delivery index. Do not upload those materials to Feishu as part of the design document.

Include:

- design proposition / design thinking: the product-level UI idea and the user problem it answers;
- source traceability: how source requirements map to pages, user stories, approved images, routes, and open assumptions;
- user stories and acceptance criteria: actor, need, goal, done criteria, and evidence for each core scenario;
- user mindset and core tension: what the user feels, wants, fears, and needs at key moments;
- page linkage: how pages form task loops, conversion paths, recovery paths, and state transitions;
- information architecture: top-level sections, hierarchy, and navigation logic;
- user journey: entry, activation, core task, success, monetization, failure/recovery;
- state strategy: default, loading, empty, success, error, quota, blocked, and modal states;
- component system: repeated components, design tokens, visual semantics, interaction rules, states, accessibility, and reuse;
- accessibility, content, localization, responsive, and design acceptance rules;
- decision log: concrete design decisions, alternatives considered, rationale, risk, and implementation consequence;
- content/data model: visible copy examples, generated data examples, input/output rules, validation, backend/external dependencies, and privacy/compliance boundaries;
- review annotations: product/design risks, unresolved requirements, and decisions needing user confirmation.

Write or update `design_thinking_map` when the run manifest provides that artifact path. It may be Markdown, Mermaid, or another source file that supports the final rich document.

## Recommended Markdown Structure

Use equivalent headings in `requested_output_language`. For Chinese output, use:

```markdown
# <产品名称> UI 设计文档

## 1. 执行摘要、设计主张与范围边界

## 2. 来源依据、需求追踪与假设边界

## 3. 目标用户、用户故事与验收标准

## 4. 核心场景、用户旅程与体验断点

## 5. 页面地图、信息架构与路由关系

## 6. 关键任务流、页面联动与恢复路径

## 7. 设计决策、取舍与风险

## 8. 视觉系统、设计 Token 与组件/模式矩阵

## 9. 交互、状态、异常、内容与数据模型

## 10. 逐页规格

### <页面名称>

- 页面 ID / 路由 / 终端：
- 页面目的：
- 来源依据：
- 关联用户故事：
- 信息层级：
- 关键组件：
- 可见文案：
- 输入/输出/校验：
- 状态覆盖：
- 交互说明：
- 与其他页面的关系：
- 设计验收要点：
- 可访问性与响应式注意事项：
- 单页评审状态：

![UI 页面](relative/path.png)

## 11. 可访问性、内容与本地化

## 12. 设计验收标准与可访问性检查

## 13. 用户反馈与变更记录

## 14. 开放问题、阻塞项与后续建议

```

For other languages, translate the same structure rather than reusing Chinese or English labels.

Hard structure rules:

- The first substantive section after the title must be a design summary/proposition section, not a delivery index, audit matrix, encoding repair note, or link table.
- Do not include sections whose purpose is delivery reporting, audit reporting, upload verification, worker evidence, React/Figma/Feishu links, run commands, or final acceptance.
- Do not wrap the real design document under a heading named "Structured design document"; the whole artifact is already the design document.
- Page images support the page specs; they must not replace specs or become the main organizing principle.

## Required Coverage

- Include every `page_inventory` page.
- Mark each page as `approved`, `blocked`, `infeasible`, or `user-approved deferred`.
- Embed approved UI images with relative links when writing Markdown.
- Include blocked, infeasible, and deferred pages in the page map and review summary; do not hide them as approved.
- Include a source-to-page traceability matrix.
- Include user stories with acceptance criteria for every core scenario.
- Include a detailed interaction/state/error matrix.
- Include a component/token matrix with state and accessibility rules.
- Include a concrete design decision log with tradeoffs; generic adjectives like "modern", "clean", or "friendly" are insufficient without source evidence and implementation consequence.
- Include visible copy examples, data examples, validation rules, empty/loading/error/quota states, and privacy/compliance notes for each relevant page.
- Include an information architecture and route graph that names entry points, branch decisions, loops, recovery paths, and dead ends.
- Include per-page design acceptance criteria that describe expected user-visible behavior and states, not React/Figma delivery verification.
- Include accessibility, responsive behavior, content tone, and localization notes.
- Include prototype-relevant design constraints derived from page briefs, route targets, interaction notes, and approved images, without local run commands or delivery links.
- Include user feedback revisions when any revision has occurred: revision id, feedback summary, affected pages, design artifacts changed, and residual risks.
- Do not mention prototype paths, Figma links, Feishu links, run commands, worker evidence, visual parity scores, or delivery audit notes in the design document. Track them only in local delivery artifacts.
- The local structured design document must pass user review before Feishu/React/Figma work starts. Record that approval in `qa/stage-approval-design-doc.json`.

## Document Quality Audit

After writing the document, create `qa/structured-design-doc-audit.json` using the schema in `references/design-doc-quality-gate.md`.

Do not mark the audit passed when:

- the document is mostly screenshots and shallow callouts;
- the document reads primarily as an implementation/delivery checklist rather than a design artifact;
- the document contains delivery/link/audit sections, React/Figma/Feishu verification results, worker evidence, run commands, or final acceptance material;
- product/design decisions are not concrete, evidenced, and testable;
- data/content model, visible copy, validation, and state behavior are missing;
- it contains `[object Object]`, `???` replacement runs, replacement characters, stale placeholders, or untranslated/generic section filler;
- any required page lacks a detailed spec;
- source traceability, user stories, acceptance criteria, journey/IA, interaction states, component tokens, accessibility, or design acceptance criteria are missing;
- `quality_score` is below `0.90`;
- blockers are present.
