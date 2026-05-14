# Structured Design Document Output

Generate a structured design document after the main-agent audit passes and before HTML/Figma implementation begins. This document is the source of truth for HTML and Figma prototype implementation.

In a scripted run, write the document to the `structured_design_doc` path recorded in `ui-run.json` unless the user requests another path. The document must exist before `validate_design_run.py --phase design-completion` can allow HTML/Figma.

## Language Rules

- Use `requested_output_language` for the document title, headings, table headers, body text, review summaries, and risk labels.
- If the user request is Chinese or the source document is Chinese and the user gives no other preference, write the whole structured document in Chinese.
- Do not default to English section names such as "Product Summary" or "Review Summary" when `requested_output_language` is not English.
- Keep product claims tied to the source document and separate confirmed requirements from agent assumptions.

## Recommended Markdown Structure

Use equivalent headings in `requested_output_language`. For Chinese output, use:

```markdown
# <产品名称> UI 设计文档

## 1. 产品概要

## 2. 目标用户

## 3. 核心场景

## 4. 页面地图

## 5. 用户流程

## 6. 视觉风格约定

## 7. 页面规格

### <页面名称>

- 页面目的：
- 终端：
- 来源依据：
- 关键组件：
- 可见文案：
- 交互说明：
- 单页评审状态：

![UI 页面](relative/path.png)

## 8. 组件与交互说明

## 9. 逐页评审结果

## 10. 主 Agent 整体功能评审

## 11. HTML 原型

## 12. Figma

## 13. 开放问题与风险
```

For other languages, translate the same structure rather than reusing Chinese or English labels.

## Required Coverage

- Include every `page_inventory` page.
- Mark each page as `approved`, `blocked`, `infeasible`, or `user-approved deferred`.
- Embed approved UI images with relative links when writing Markdown.
- Include blocked, infeasible, and deferred pages in the page map and review summary; do not hide them as approved.
- Include worker evidence paths for each generated page when useful for auditability.
- Include prototype implementation requirements derived from page briefs, route targets, interaction notes, and approved images.
- Before HTML/Figma generation, mark prototype paths and Figma links as `pending`.
- After HTML/Figma generation, update the same design document with the final prototype path, Figma link if any, and final audit notes.
- Mention Figma only if generated or requested.
