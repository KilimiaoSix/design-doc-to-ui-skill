window.PROTOTYPE_DATA = {
  lang: "zh-CN",
  title: "静态交互原型",
  kicker: "交互原型",
  summary: "请用基于页面 brief、逐页评审结果和结构化设计文档生成的数据替换此示例。React 模板是默认交付方式，本静态模板仅保留为兼容选项。",
  labels: {
    pages: "页面",
    status: "状态",
    actions: "操作",
    controls: "控件",
    states: "页面状态",
    reference: "视觉参考",
    close: "关闭",
    saved: "已保存",
    noPages: "没有页面数据",
    blocked: "阻断",
    approved: "已通过",
  },
  pages: [
    {
      id: "home",
      name: "首页",
      navLabel: "首页",
      endpoint: "mobile",
      status: "approved",
      headline: "请替换为真实页面",
      purpose: "展示真实组件、控件、状态和页面跳转；生成的 UI 图片只作为视觉参考。",
      controls: [
        {
          id: "target",
          type: "text",
          label: "目标",
          placeholder: "输入目标",
          value: "",
        },
        {
          id: "mode",
          type: "select",
          label: "模式",
          options: ["快速", "标准", "深入"],
          value: "标准",
        },
      ],
      sections: [
        {
          title: "任务入口",
          body: "这里应替换为来自 page brief 的真实页面内容。",
          items: [
            {
              title: "填写信息",
              description: "演示按钮跳转到表单页。",
              action: { label: "进入", target: "form" },
            },
            {
              title: "查看状态",
              description: "演示弹窗和状态反馈。",
              action: { label: "查看", dialog: "这里展示该页面的状态说明。" },
            },
          ],
        },
      ],
      states: [
        { name: "默认", description: "页面正常加载后的主要状态。" },
        { name: "空状态", description: "没有数据时应展示的说明和行动入口。" },
        { name: "错误", description: "请求失败或校验失败时的可恢复提示。" },
      ],
      actions: [
        { label: "继续", target: "form" },
        { label: "保存", toast: "已保存当前页面状态", variant: "secondary" },
      ],
      referenceImage: "",
    },
    {
      id: "form",
      name: "表单页",
      navLabel: "表单",
      endpoint: "mobile",
      status: "approved",
      headline: "完成信息填写",
      purpose: "演示输入、开关、保存反馈和返回路径。",
      controls: [
        { id: "name", type: "text", label: "名称", placeholder: "输入名称", value: "" },
        { id: "enabled", type: "checkbox", label: "启用提醒", value: true },
      ],
      sections: [
        {
          title: "表单内容",
          items: [
            { title: "字段校验", description: "根据真实需求补齐校验、错误态和成功态。" },
          ],
        },
      ],
      states: [
        { name: "默认", description: "等待用户填写。" },
        { name: "成功", description: "保存成功后显示结果反馈。" },
      ],
      actions: [
        { label: "返回首页", target: "home" },
        { label: "提交", dialog: "提交成功。", variant: "primary" },
      ],
      referenceImage: "",
    },
  ],
};
