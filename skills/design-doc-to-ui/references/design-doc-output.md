# Structured Design Document Output

Generate the structured design document after the main-agent audit passes and before React/Figma implementation begins. This document is the source of truth for React, optional Feishu rich documents, and optional Figma replica implementation.

In a scripted run, write the document to the `structured_design_doc` path recorded in `ui-run.json` unless the user requests another path. The document must exist before `validate_design_run.py --phase design-completion` can allow React/Figma.

## Language Rules

- Use `requested_output_language` for the document title, headings, table headers, body text, review summaries, and risk labels.
- If the user request is Chinese or the source document is Chinese and the user gives no other preference, write the whole structured document in Chinese.
- Do not default to English section names such as "Product Summary" or "Review Summary" when `requested_output_language` is not English.
- Keep product claims tied to the source document and separate confirmed requirements from agent assumptions.

## Design Narrative Gate

A page-by-page catalog is not enough. The document must explain why the design is shaped this way and how pages work together.

Include:

- design proposition / design thinking: the product-level UI idea and the user problem it answers;
- user mindset and core tension: what the user feels, wants, fears, and needs at key moments;
- page linkage: how pages form task loops, conversion paths, recovery paths, and state transitions;
- information architecture: top-level sections, hierarchy, and navigation logic;
- user journey: entry, activation, core task, success, monetization, failure/recovery;
- state strategy: default, loading, empty, success, error, quota, blocked, and modal states;
- component system: repeated components, visual semantics, interaction rules, and reuse;
- evidence: approved UI images, page briefs, worker reviews, and main-agent audit results.

Write or update `design_thinking_map` when the run manifest provides that artifact path. It may be Markdown, Mermaid, or another source file that supports the final rich document.

## Recommended Markdown Structure

Use equivalent headings in `requested_output_language`. For Chinese output, use:

```markdown
# <产品名称> UI 设计文档

## 1. 设计主张与产品概要

## 2. 目标用户、心智与核心矛盾

## 3. 核心场景与用户旅程

## 4. 页面地图与信息架构

## 5. 关键任务流与页面联动

## 6. 视觉风格与组件系统

## 7. 状态、异常与商业化策略

## 8. 页面规格

### <页面名称>

- 页面目的：
- 终端：
- 来源依据：
- 关键组件：
- 可见文案：
- 交互说明：
- 与其他页面的关系：
- 单页评审状态：

![UI 页面](relative/path.png)

## 9. 逐页评审结果

## 10. 主 Agent 整体功能评审

## 11. React 原型与视觉复刻审计

## 12. 飞书富文档交付

## 13. Figma 复刻

## 14. 开放问题与风险
```

For other languages, translate the same structure rather than reusing Chinese or English labels.

## Required Coverage

- Include every `page_inventory` page.
- Mark each page as `approved`, `blocked`, `infeasible`, or `user-approved deferred`.
- Embed approved UI images with relative links when writing Markdown.
- Include blocked, infeasible, and deferred pages in the page map and review summary; do not hide them as approved.
- Include worker evidence paths for each generated page when useful for auditability.
- Include React prototype implementation requirements derived from page briefs, route targets, interaction notes, and approved images.
- Before React/Figma/Feishu generation, mark prototype paths, Figma links, and Feishu links as `pending`.
- After React/Figma/Feishu generation, update the same design document with the final React project path, run command, Feishu link if any, Figma link if any, visual parity result, and final audit notes.
- Mention Figma and Feishu only if generated/uploaded or requested.
