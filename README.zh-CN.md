# Design Doc To UI Skill 中文文档

这是一个可安装的 Codex Skill 包，用于把产品需求文档、设计文档、飞书文档、Markdown 规格、线框图、截图和品牌素材转换成完整、经过评审的 UI 设计交付物。

仓库采用“1 个主 skill + 3 个 companion skill”的结构：

```text
skills/
  design-doc-to-ui/                 # 主编排 skill
  design-doc-to-ui-feishu-doc/      # 飞书富文档交付
  design-doc-to-ui-figma-replica/   # Figma 可编辑复刻交付
  design-doc-to-ui-visual-audit/    # React/Figma 视觉复刻审计
```

## 能做什么

`design-doc-to-ui` 会生成：

- 基于源文档的 `page_inventory` 和需求摘要；
- 脚本化 `ui-run.json` manifest 与门禁校验；
- 由 SubAgent 生成的产品专属风格打样；
- 每个 required 页面各 1 张由 imagegen 生成并评审的 UI 图；
- 每页独立 SubAgent 的评审记录；
- 与请求语言一致的结构化设计文档，包含设计思想、页面联动和所有页面生成图；
- 可本地运行的 React 小前端项目，由主 agent 先创建框架、路由、共享样式和页面槽位，再由页面级 SubAgent 细化页面并自审，使用真实组件复刻已批准 AI 页面图并实现交互；
- 用户明确要求时，交付飞书/Lark 富文档；
- 用户明确要求时，交付 Figma 可编辑复刻原型，使用页面级 frame worker 和主 agent 全局 prototype link 验证。

这个 skill 的策略是宁可阻断，也不静默缩水。页面缺失、SubAgent 证据缺失、审计缺失、React/Figma 提前开始，都会被视为 blocker。

## Companion Skills

主 skill 只负责编排，不把专业交付降级成简化实现：

- `design-doc-to-ui-visual-audit`：React 与 Figma 的视觉复刻审计。每个 required 页面都必须达到 `0.80`，平均分不能掩盖单页失败。
- `design-doc-to-ui-feishu-doc`：飞书/Lark 富文档交付。要求设计叙事、页面联动、callout、grid、whiteboard/diagram、表格和 `qa/feishu-doc-audit.json`。
- `design-doc-to-ui-figma-replica`：Figma 可编辑复刻交付。必须以已批准 AI 页面图和 React 截图为基准，不允许整屏贴图冒充可编辑原型。

如果对应 companion skill 缺失、不可读或 frontmatter 不合法，对应阶段必须 blocked，不降级执行。

## 核心保证

- 源文档中的每个 required 页面都必须有独立 page brief。
- 每个 required 页面图都必须由页面级 SubAgent 生成和评审。
- 同时最多 6 个活跃 SubAgent；页面多时必须分批。
- 源文档里明确写出的风格类型、参考产品、品牌形容词、视觉 do/don't 规则，必须先被提取，并在风格打样中获得高于 catalog 默认预设的权重。
- React 和 Figma 只能在设计图、主审计和结构化设计文档完成后开始。
- React 默认输出 Vite 小前端项目，不能只是整页图片浏览器；主 agent 必须先创建 app shell、route registry、style system、page slots 和 worker ownership map。
- React 页面 worker 必须先产出 `visual-decomposition.json`、`dom-element-inventory.json`、`visual-replica-audit.json`，再登记到 `prototype/qa/react-page-worker-registry.json`；主 agent 必须通过 `react-navigation-audit.json` 验证全局路由、跨页状态和完整跳转流。
- React demo 可用性由 `prototype/qa/react-usability-audit.json` 强制门禁：内容超过视口的页面必须可滚动，底部内容必须可达，并且右侧页面快捷菜单必须能跳转到每个 required route，同时不影响视觉复刻截图。
- Figma 必须先通过 `qa/figma-scaffold-audit.json`，页面 worker 必须登记到 `qa/figma-page-worker-registry.json`，并通过 `qa/figma-prototype-link-plan.json` 与 `qa/figma-integration-audit.json`。每个 Figma 页面 worker 还必须产出 `visual-decomposition.json`、`figma-layer-inventory.json`、`figma-visual-replica-audit.json`。
- 重做/返工必须写 `qa/revision-plan.json`，按 affected 页面/渠道启动预期 SubAgent，并登记到 `qa/revision-subagent-registry.json`；受影响的页面图、React 页面、Figma 页面或飞书交付物不能由主线程直接重做。
- React/Figma 复刻按逐页分数判断，单页低于 `0.80` 即失败。
- 最终文档、React 元数据、飞书/Figma 输出都跟随用户请求语言。

## 安装

需要安装 4 个 skill。可以在 Codex 中分别请求：

```text
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-feishu-doc
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-figma-replica
$skill-installer install https://github.com/KilimiaoSix/design-doc-to-ui-skill/tree/main/skills/design-doc-to-ui-visual-audit
```

也可以直接运行安装脚本：

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

安装后重启 Codex，让技能元数据重新加载。

## 更新已有安装

官方安装脚本在目标目录已存在时会中止。更新前先删除或备份旧目录：

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

## 使用方式

给 Codex 一个源文档，并明确使用主 skill：

```text
请使用 $design-doc-to-ui，把这个产品需求文档转换成完整的移动端 APP UI 设计稿、结构化设计文档和可运行 React 原型。
```

主流程会按顺序执行：

1. 读取源文档和素材。
2. 生成完整 `page_inventory` 并初始化 `ui-run.json`。
3. 使用 SubAgent 探索产品专属视觉方向。
4. 每个 required 页面使用一个页面级 SubAgent 生图和评审。
5. 主线程用脚本登记每个 worker 结果。
6. 生成包含设计思想、页面联动和页面图的结构化设计文档。
7. 运行 design-completion 门禁。
8. 先生成 React 框架，再登记页面级 React worker，并完成全局导航审计。
9. 使用视觉审计 companion 检查并修复，直到每页达到 `0.80`。
10. 用户要求时，使用飞书 companion 上传富文档。
11. 用户要求时，使用 Figma companion 创建或更新可编辑复刻原型。
12. 运行最终 delivery gate。

## 脚本化门禁

主 skill 内置确定性的 helper 脚本：

```bash
python skills/design-doc-to-ui/scripts/prepare_ui_run.py --source prd.md --run-dir out/minihire --requested-output-language zh-CN
python skills/design-doc-to-ui/scripts/ui_job_status.py --run-dir out/minihire
python skills/design-doc-to-ui/scripts/record_ui_worker_result.py --run-dir out/minihire --page-id home
python skills/design-doc-to-ui/scripts/validate_companion_skills.py --run-dir out/minihire --require-all
python skills/design-doc-to-ui/scripts/validate_design_run.py --run-dir out/minihire --phase design-completion
python skills/design-doc-to-ui/scripts/build_prototype_data.py --run-dir out/minihire --template react --copy-template
python skills/design-doc-to-ui/scripts/record_react_page_worker_result.py --run-dir out/minihire --page-id home --worker-result prototype/qa/react-page-workers/home/worker-result.json --interaction-audit prototype/qa/react-page-workers/home/interaction-audit.json --visual-decomposition prototype/qa/react-page-workers/home/visual-decomposition.json --dom-inventory prototype/qa/react-page-workers/home/dom-element-inventory.json --visual-replica-audit prototype/qa/react-page-workers/home/visual-replica-audit.json --review prototype/qa/react-page-workers/home/review.md
python skills/design-doc-to-ui/scripts/record_figma_page_worker_result.py --run-dir out/minihire --page-id home --worker-result qa/figma-page-workers/home/worker-result.json --frame-audit qa/figma-page-workers/home/frame-audit.json --visual-decomposition qa/figma-page-workers/home/visual-decomposition.json --layer-inventory qa/figma-page-workers/home/figma-layer-inventory.json --visual-replica-audit qa/figma-page-workers/home/figma-visual-replica-audit.json --review qa/figma-page-workers/home/review.md
python skills/design-doc-to-ui/scripts/record_revision_subagent_result.py --run-dir out/minihire --revision-id rev-002 --scope react-page --page-id home --channel react --subagent-id <spawn_agent_id> --worker-result prototype/qa/react-page-workers/home/worker-result.json --review prototype/qa/react-page-workers/home/review.md
python skills/design-doc-to-ui/scripts/validate_design_run.py --run-dir out/minihire --phase delivery
```

页面数量不写死，由源文档解析出的 `page_inventory` 决定。后续 page brief、SubAgent worker、设计图、设计文档、React route、飞书/Figma 准入和最终门禁都以它为唯一事实来源。

## 飞书富文档标准

飞书交付不是把 Markdown 贴进文档。`design-doc-to-ui-feishu-doc` 要求：

- 开头使用 callout 总结设计主张；
- 包含设计命题、用户心智、核心矛盾、任务联动、信息架构、状态策略、组件原则和风险；
- 至少 3 个 whiteboard/diagram：页面地图、用户主流程、状态/异常流；
- 至少 4 个结构化表格：页面矩阵、交互矩阵、组件矩阵、风险/开放问题矩阵；
- 使用 grid 做对比或原则分栏，避免连续纯段落；
- 输出 `qa/feishu-doc-audit.json`。

## Figma 复刻标准

Figma 交付必须基于已批准 AI 页面图、React 截图和结构化设计文档：

- 每个 required 页面必须有对应 Figma frame；
- frame 必须是可编辑结构，不能用整屏图片冒充；
- 每个页面 worker 必须先拆解 approved AI 图，再把所有可见元素映射到可编辑 Figma 图层/组件/素材，并输出页面级视觉复刻审计；
- 布局、层级、颜色、字体、组件形态和主要状态要尽量复刻；
- 原型连线覆盖主流程、主按钮、弹窗和状态流；
- 缺少插画/图标/局部资源时，使用 SubAgent + imagegen 生成局部素材；
- 输出 `qa/figma-replica-audit.json`，每页 `visual_similarity_score` 必须大于等于 `0.80`。

## 校验

校验 4 个 skill 结构：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-feishu-doc
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-figma-replica
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/design-doc-to-ui-visual-audit
```

本次回归覆盖：

- MiniHire fixture 可解析为 7 个 required 页面；
- `ui_job_status.py --batch-size 12` 会把下一批 worker 限制为最多 6 个；
- 设计图、worker 结果、主审计和结构化文档不完整时，`validate_design_run.py --phase design-completion` 返回 `react_allowed=false`；
- 补齐 mock worker 产物、锁定风格、主审计和结构化设计文档后，design-completion gate 通过；
- `build_prototype_data.py --template react --copy-template` 生成包含全部 required route 的 React 项目；
- 缺 React scaffold audit、React 页面视觉拆解、React DOM 映射、React 页面视觉复刻审计、React 页面 worker registry、React navigation audit、React usability audit、Figma scaffold audit、Figma 页面视觉拆解、Figma 图层清单、Figma 页面视觉复刻审计、Figma 页面 worker registry、Figma prototype link plan、Figma integration audit、存在 revision plan 时缺 revision SubAgent registry、companion、视觉审计、飞书审计、route、page brief、worker-result、final image、结构化文档都会输出明确 blocker code。

## 仓库说明

- README 放在仓库根目录，方便 GitHub 用户阅读。
- 不要把 README、CHANGELOG 等额外文档放进单个 skill 目录；skill 目录应只保留 Codex 执行该能力所需的说明、引用资料、脚本和资产。
- 飞书/Figma 是可选交付，但一旦用户要求，就必须通过对应 companion skill 和审计 JSON。

仓库地址：[https://github.com/KilimiaoSix/design-doc-to-ui-skill](https://github.com/KilimiaoSix/design-doc-to-ui-skill)
