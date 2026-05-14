window.PROTOTYPE_DATA = {
  lang: "zh-CN",
  title: "产品交互原型",
  kicker: "Interactive Prototype",
  summary: "用需求页面、单页评审结果和 HTML 交互规格替换这里的示例数据。",
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
      headline: "今天先完成一个核心任务",
      purpose: "展示真实 HTML 组件、控件、状态和页面跳转；生成的 UI 图片只作为视觉参考。",
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
        {
          id: "name",
          type: "text",
          label: "名称",
          placeholder: "请输入名称",
          value: "",
        },
        {
          id: "enabled",
          type: "toggle",
          label: "启用提醒",
          value: true,
        },
      ],
      sections: [
        {
          title: "下一步",
          items: [
            {
              title: "返回首页",
              description: "验证主路径可达。",
              action: { label: "返回", target: "home" },
            },
          ],
        },
      ],
      states: [
        { name: "成功", description: "保存成功后的提示。" },
        { name: "校验错误", description: "必填字段为空时的错误提示。" },
      ],
      actions: [
        { label: "提交", toast: "提交成功" },
        { label: "返回", target: "home", variant: "secondary" },
      ],
      referenceImage: "",
    },
  ],
};
