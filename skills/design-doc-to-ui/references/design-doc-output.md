# Structured Design Document Output

Generate the structured design document after the main-agent audit passes and before React/Figma implementation begins. This document is the source of truth for React, optional Feishu rich documents, and optional Figma replica implementation.

In a scripted run, write the document to the `structured_design_doc` path recorded in `ui-run.json` unless the user requests another path. The document must exist before `validate_design_run.py --phase design-completion` can allow React/Figma.

Also read `references/design-doc-quality-gate.md`. After writing the document, audit it and write `qa/structured-design-doc-audit.json` before running the Design Completion Gate.

## Language Rules

- Use `requested_output_language` for the document title, headings, table headers, body text, review summaries, and risk labels.
- If the user request is Chinese or the source document is Chinese and the user gives no other preference, write the whole structured document in Chinese.
- Do not default to English section names such as "Product Summary" or "Review Summary" when `requested_output_language` is not English.
- Keep product claims tied to the source document and separate confirmed requirements from agent assumptions.

## Design Narrative Gate

A page-by-page catalog is not enough. The document must explain why the design is shaped this way and how pages work together.

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
- accessibility, content, localization, responsive, and handoff acceptance rules;
- evidence: approved UI images, page briefs, worker reviews, and main-agent audit results.

Write or update `design_thinking_map` when the run manifest provides that artifact path. It may be Markdown, Mermaid, or another source file that supports the final rich document.

## Recommended Markdown Structure

Use equivalent headings in `requested_output_language`. For Chinese output, use:

```markdown
# <产品名称> UI 设计文档

## 1. 执行摘要、设计主张与交付结论

## 2. 来源依据、需求追踪与假设边界

## 3. 目标用户、用户故事与验收标准

## 4. 核心场景、用户旅程与体验断点

## 5. 页面地图、信息架构与路由关系

## 6. 关键任务流、页面联动与恢复路径

## 7. 设计决策、取舍与风险

## 8. 视觉系统、设计 Token 与组件/模式矩阵

## 9. 交互、状态、异常与商业化策略

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
- React/Figma 复刻验收：
- 可访问性与响应式注意事项：
- 单页评审状态：

![UI 页面](relative/path.png)

## 11. 可访问性、内容与本地化

## 12. React/Figma/Feishu 交付与 QA 验收

## 13. 逐页评审结果与主 Agent 审计

## 14. 用户反馈与变更记录

## 15. 开放问题、阻塞项与后续建议

```

For other languages, translate the same structure rather than reusing Chinese or English labels.

## Required Coverage

- Include every `page_inventory` page.
- Mark each page as `approved`, `blocked`, `infeasible`, or `user-approved deferred`.
- Embed approved UI images with relative links when writing Markdown.
- Include blocked, infeasible, and deferred pages in the page map and review summary; do not hide them as approved.
- Include worker evidence paths for each generated page when useful for auditability.
- Include a source-to-page traceability matrix.
- Include user stories with acceptance criteria for every core scenario.
- Include a detailed interaction/state/error matrix.
- Include a component/token matrix with state and accessibility rules.
- Include per-page implementation acceptance criteria for React and Figma replication.
- Include accessibility, responsive behavior, content tone, and localization notes.
- Include React prototype implementation requirements derived from page briefs, route targets, interaction notes, and approved images.
- Include user feedback revisions when any revision has occurred: revision id, feedback summary, affected pages, regenerated artifacts, gates rerun, and residual risks.
- Before React/Figma/Feishu generation, mark prototype paths, Figma links, and Feishu links as `pending`.
- After React/Figma/Feishu generation, update the same design document with the final React project path, run command, Feishu link if any, Figma link if any, visual parity result, and final audit notes.
- Mention Figma and Feishu only if generated/uploaded or requested.

## Document Quality Audit

After writing the document, create `qa/structured-design-doc-audit.json` using the schema in `references/design-doc-quality-gate.md`.

Do not mark the audit passed when:

- the document is mostly screenshots and shallow callouts;
- any required page lacks a detailed spec;
- source traceability, user stories, acceptance criteria, journey/IA, interaction states, component tokens, accessibility, or handoff acceptance criteria are missing;
- `quality_score` is below `0.85`;
- blockers are present.
