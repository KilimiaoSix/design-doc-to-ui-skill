# Design Doc To UI Skill

这是一个可安装的 Codex Skill 包，用于把 PRD、产品设计文档、飞书/Lark 文档、Markdown 规格、线框图、截图和品牌素材，转换成经过阶段确认的 UI 设计包。

当前仓库包含 1 个主 skill 和 3 个 companion skill：

```text
skills/
  design-doc-to-ui/                 # 主编排 skill
  design-doc-to-ui-feishu-doc/      # 飞书/Lark 干净设计文档上传与远端复查
  design-doc-to-ui-figma-replica/   # Figma 可编辑复刻
  design-doc-to-ui-visual-audit/    # React/Figma 视觉一致性审计
```

## 这个 Skill 做什么

`design-doc-to-ui` 会把源文档拆成可审查、可实现、可验证的 UI 设计工作流：

- 读取源文档、图片、表格、飞书内容和页面线索；
- 生成 `app_requirements_summary`、`page_inventory` 和 `ui-run.json`；
- 先做风格探索，等待用户确认；
- 再做交互设计、页面 brief、路由和状态模型，等待用户确认；
- 使用页面级 SubAgent 为每个 required 页面生成 imagegen UI 图；
- 主 Agent 审查全部页面图，再等待用户确认；
- 生成干净的结构化设计文档，等待用户确认；
- 用户要求飞书时，只上传干净设计文档，并从远端重新 fetch 校验内容；
- 通过设计阶段门禁后，再生成 React 原型；
- 用户要求 Figma 时，再创建可编辑 Figma 复刻。

这个 skill 的目标不是一口气交付最终产物，而是把长任务拆成可以中途修正的阶段。

## 重要原则

### 1. 飞书只放干净设计文档

飞书文档必须是产品/交互/视觉设计文档，不是交付报告。禁止上传：

- 交付结论、交付索引、最终验收；
- 审计结果、audit matrix、page evidence matrix；
- worker 证据、SubAgent 状态、`qa/` 路径；
- React/Figma/Feishu 验证结果；
- run command、prototype 路径、本地文件路径；
- visual parity 分数、上传校验细节。

这些交付材料只保存在本地 `qa/` 或单独的本地交付索引中，例如 `qa/delivery-index.md`、`qa/final-delivery-audit.json`。

### 2. 设计文档必须像设计文档

结构化设计文档必须包含：

- 产品定位、目标用户、核心问题和设计主张；
- 来源依据、需求追踪、假设边界；
- 用户故事、核心场景、验收标准；
- 信息架构、页面地图、主任务流和恢复路径；
- 设计决策、取舍、风险；
- 视觉系统、设计 token、组件和模式矩阵；
- 交互、状态、异常、内容和数据模型；
- 每个页面的详细规格、可见文案、状态覆盖和设计验收标准；
- 可访问性、响应式、内容和本地化说明。

如果文档主要是截图目录、页面清单、交付链接、审计表或 worker 记录，门禁会失败。

### 3. 阶段必须让用户确认

长任务必须分阶段停止并等待用户确认：

1. 风格方向确认；
2. 交互设计和页面 brief 确认；
3. AI 页面设计图确认；
4. 本地结构化设计文档确认；
5. 飞书远端文档确认，仅在用户要求飞书时；
6. React/Figma 生成和最终审计。

## 安装

需要安装 4 个 skill。推荐在 Codex 中使用 `skill-installer`：

```text
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-feishu-doc
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-figma-replica
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-visual-audit
```

也可以在 Windows PowerShell 中运行安装脚本：

```powershell
$skills = @(
  "design-doc-to-ui",
  "design-doc-to-ui-feishu-doc",
  "design-doc-to-ui-figma-replica",
  "design-doc-to-ui-visual-audit"
)

foreach ($skill in $skills) {
  python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
    --repo KilimiaoSix/design-doc-to-ui-skill `
    --path "skills/$skill"
}
```

安装完成后，重启 Codex，让 skill 元数据重新加载。

## 更新已有安装

如果本机已经安装过旧版本，先删除旧目录再重新安装：

```powershell
$skills = @(
  "design-doc-to-ui",
  "design-doc-to-ui-feishu-doc",
  "design-doc-to-ui-figma-replica",
  "design-doc-to-ui-visual-audit"
)

foreach ($skill in $skills) {
  Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\$skill"
}
```

然后重新执行安装命令并重启 Codex。

## 如何开始

给 Codex 一个源文档，并明确使用主 skill：

```text
请使用 $design-doc-to-ui，把这个产品需求文档转换成完整的移动端 UI 设计包。先做风格设计，等我确认后再做交互设计和页面图，最后生成干净的设计文档和 React 原型。
```

如果源文档是飞书链接：

```text
请使用 $design-doc-to-ui，读取这个飞书产品文档并生成 UI 设计包。输出语言使用中文。需要飞书设计文档，但飞书里只放干净设计文档，交付审计材料保留在本地。
```

如果还需要 Figma：

```text
请使用 $design-doc-to-ui，从这份 PRD 生成 UI 设计包、React 原型，并在设计文档确认后创建可编辑 Figma 复刻。
```

## 标准流程

主流程如下：

1. 读取源文档和素材。
2. 提取页面清单、源语言、输出语言和需求摘要。
3. 初始化 `ui-run.json`。
4. 进行风格探索，生成 2-3 个风格方向和样例，等待用户确认。
5. 为每个 required 页面写 page brief，并生成中间交互设计文件，等待用户确认。
6. 每个 required 页面启动一个页面级 SubAgent 生成 UI 图。
7. 主 Agent 审查页面图，必要时返工，再等待用户确认。
8. 生成干净结构化设计文档，并写 `qa/structured-design-doc-audit.json`。
9. 用户确认设计文档后，如果要求飞书，则上传干净飞书文档。
10. 上传飞书后，必须重新 fetch 远端链接，校验内容已更新、无乱码、无交付/审计材料泄漏。
11. 设计阶段门禁通过后，生成 React 原型。
12. React 通过交互和视觉审计后，按需生成 Figma 可编辑复刻。
13. 所有交付审计结果保存在本地 `qa/`。

## 主要输出

典型运行目录会包含：

```text
ui-run.json
app-requirements-summary.json
page-briefs/
design-images/
qa/
  structured-design-doc.md
  structured-design-doc-audit.json
  stage-approval-style.json
  stage-approval-interaction-design.json
  stage-approval-ai-design-images.json
  stage-approval-design-doc.json
  feishu-doc-audit.json
  feishu-doc-content-audit.json
  delivery-index.md
prototype/
  package.json
  src/
```

其中 `qa/structured-design-doc.md` 是干净设计文档。其它审计、链接、运行命令和交付结果保存在本地 `qa/`，不写入飞书设计文档。

## 脚本化门禁

主 skill 提供一组确定性脚本，用来避免漏页、伪完成和提前进入实现阶段：

```bash
python skills/design-doc-to-ui/scripts/prepare_ui_run.py --source prd.md --run-dir out/app --requested-output-language zh-CN
python skills/design-doc-to-ui/scripts/ui_job_status.py --run-dir out/app
python skills/design-doc-to-ui/scripts/record_ui_worker_result.py --run-dir out/app --page-id home
python skills/design-doc-to-ui/scripts/validate_companion_skills.py --run-dir out/app --require-all
python skills/design-doc-to-ui/scripts/validate_design_run.py --run-dir out/app --phase design-completion
python skills/design-doc-to-ui/scripts/build_prototype_data.py --run-dir out/app --template react --copy-template
python skills/design-doc-to-ui/scripts/validate_design_run.py --run-dir out/app --phase delivery
```

`validate_design_run.py` 会检查：

- required 页面是否都有 brief、worker result、review、prompt history 和 final image；
- 风格、交互设计、页面图、设计文档是否有用户确认；
- 结构化设计文档是否是干净设计文档；
- 飞书远端内容是否真正更新成功；
- 飞书远端内容是否无乱码、无 stale 内容、无交付/审计材料泄漏；
- React/Figma 是否满足对应审计和视觉一致性门槛。

## Companion Skill 说明

### design-doc-to-ui-feishu-doc

只负责把已批准的干净设计文档上传为飞书/Lark 富文档，并重新 fetch 远端链接做内容复查。它会写本地：

```text
qa/feishu-doc-audit.json
qa/feishu-doc-content-audit.json
qa/stage-approval-feishu-doc.json
```

飞书文档本身不包含这些审计材料。

### design-doc-to-ui-visual-audit

负责 React/Figma 与已批准 AI 页面图的视觉一致性审计。每页都要达到 `0.80`，不能用平均分掩盖单页失败。

### design-doc-to-ui-figma-replica

负责创建或更新可编辑 Figma 复刻。Figma 不能用整屏截图冒充实现，需要可编辑图层、组件、样式和原型连线。

## 校验 Skill

可以用 Codex 内置的 skill 校验脚本检查结构：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-feishu-doc
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-figma-replica
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-visual-audit
```

Windows PowerShell：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" skills/design-doc-to-ui
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" skills/design-doc-to-ui-feishu-doc
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" skills/design-doc-to-ui-figma-replica
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" skills/design-doc-to-ui-visual-audit
```

## 仓库说明

- 仓库根目录的 `README.md` 是中文主文档。
- 单个 skill 目录内不要放 README、CHANGELOG 等额外说明文件。
- Skill 目录只保留 Codex 执行能力所需的 `SKILL.md`、`agents/`、`references/`、`scripts/` 和 `assets/`。
- 飞书/Figma 是可选输出；一旦用户要求，就必须通过对应 companion skill 和本地审计 JSON。

仓库地址：[https://github.com/KilimiaoSix/design-doc-to-ui-skill](https://github.com/KilimiaoSix/design-doc-to-ui-skill)
