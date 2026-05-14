# Design Doc To UI Skill 中文文档

这是一个可安装的 Codex Skill，用于把产品需求文档、设计文档和原型资料转换成完整、经过评审的 UI 设计交付包。

仓库采用通用 Codex Skill 发布结构：

```text
skills/
  design-doc-to-ui/
    SKILL.md
    agents/
    references/
    assets/
```

## 能做什么

`design-doc-to-ui` 可处理 PRD、设计文档、飞书/Lark 文档、Markdown 规格、线框图、截图和品牌素材，并生成：

- 基于源文档的页面清单和需求摘要；
- 定制化视觉风格探索与 SubAgent 生图打样；
- 每个必需页面一张通过评审的 UI 设计图；
- 每页独立的 SubAgent 评审记录；
- 与请求语言一致的结构化设计文档；
- 真实可交互的本地 HTML 原型；
- 用户明确要求时生成或同步 Figma 原型。

这个 skill 的策略比较严格：如果页面不完整、评审证据缺失、设计图未完成，它会阻断交付，而不是静默缩小为一个简单 pilot 流程。

## 核心保证

- 源文档中的每个 required 页面都必须有独立 page brief。
- 每个 required 页面设计图都必须由页面级 SubAgent 生成并评审。
- 同一时间最多 6 个活跃 SubAgent；页面较多时必须分批执行。
- HTML 和 Figma 原型只能在全部必需设计图和结构化设计文档完成后开始。
- HTML 原型必须使用真实组件和交互，不能只是整页截图切换器。
- 最终文档、HTML 元数据和原型说明必须跟随用户请求语言。

## 安装

在 Codex 中可以直接请求内置 skill installer：

```text
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui
```

也可以直接运行安装脚本：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo KilimiaoSix/design-doc-to-ui-skill \
  --path skills/design-doc-to-ui
```

Windows PowerShell 示例：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo KilimiaoSix/design-doc-to-ui-skill `
  --path skills/design-doc-to-ui
```

安装后需要重启 Codex，让 Codex 重新加载 skill 元数据。

## 更新已有安装

官方安装脚本在目标目录已存在时会中止。若要更新，请先删除或备份旧版本：

```bash
rm -rf ~/.codex/skills/design-doc-to-ui
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo KilimiaoSix/design-doc-to-ui-skill \
  --path skills/design-doc-to-ui
```

Windows PowerShell：

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\design-doc-to-ui"
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo KilimiaoSix/design-doc-to-ui-skill `
  --path skills/design-doc-to-ui
```

更新后同样需要重启 Codex。

## 使用方式

给 Codex 一个源文档，并明确使用该 skill，例如：

```text
Use $design-doc-to-ui to convert this PRD into a full reviewed mobile app UI package and interactive HTML prototype.
```

中文也可以：

```text
请使用 $design-doc-to-ui，把这个产品需求文档转换成完整的移动端 APP UI 设计稿、结构化设计文档和可交互 HTML 原型。
```

skill 会按以下顺序执行：

1. 读取源文档和素材；
2. 生成需求摘要和完整页面清单；
3. 探索 2-3 个定制视觉方向，并用 SubAgent 生图打样；
4. 锁定全局视觉风格约定；
5. 为每个 required 页面生成独立 page brief；
6. 每个页面使用独立 SubAgent 生图和评审；
7. 主线程做整体功能与一致性审查；
8. 生成结构化设计文档；
9. 基于已批准设计图和结构化文档生成 HTML 原型；
10. 用户要求时再生成或同步 Figma 原型。

## 关键流程约束

### 页面覆盖

源文档页面清单是交付范围的来源。不能把完整需求静默缩小成“核心流程”“pilot”“trial”。

如果需要延期某些页面，必须由用户明确批准，并在文档中标记为 `user-approved deferred`。

### SubAgent 生图与评审

风格打样、页面生图和校准都必须使用 SubAgent。

- 每个风格方向一个 SubAgent。
- 每个页面一个 SubAgent。
- 同一时间最多 6 个活跃 SubAgent。
- 主线程不能替代 SubAgent 调用 `image_gen` 生成最终 UI 图。

### HTML/Figma 顺序

HTML 和 Figma 不能在设计图完成前启动。

必须先满足：

- 全局风格约定已锁定；
- 每个 required 页面有已批准设计图；
- 每页有 SubAgent 产物和评审记录；
- 主线程整体审查通过；
- 结构化设计文档已生成。

之后才能基于“已批准设计图 + 结构化设计文档”实现 HTML 或 Figma 原型。

## 校验

可以使用官方 skill creator validator 校验 skill 结构：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui
```

期望输出：

```text
Skill is valid!
```

## 仓库说明

- README 放在仓库根目录，方便 GitHub 用户阅读。
- 不要把 README、CHANGELOG 等额外文档放入 `skills/design-doc-to-ui/` 内部；skill 目录应只保留 Codex 执行该能力所需的说明、引用资料和资产。
- `assets/style-catalog/` 中包含较大的风格样张图片，这是该 skill 的风格参考和质量基线资产。

## 仓库地址

https://github.com/KilimiaoSix/design-doc-to-ui-skill
