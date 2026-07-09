# 正式交付件中间文档模型迁移设计

本文件说明如何将当前 `planner -> renderer -> markdown` 的流程，逐步迁移为：

`planner -> document model -> markdown/docx renderer`

## 当前现状

当前系统已经具备：

- 强论证型正式交付章节结构
- 表格输出
- Mermaid 拓扑图输出
- 审批级 / 施工级两层正式版内容

但当前问题是：

- renderer 直接拼接 Markdown
- 图、表、段落没有统一中间表达
- 后续 `docx` 输出无法直接复用现有内容结构

## 迁移目标

将当前正式版内容统一映射为 `DocumentModel`：

- 元数据 → `DocumentMeta`
- 章节 → `Section`
- 正文段落 → `ParagraphBlock`
- 要点清单 → `BulletBlock`
- 图 → `DiagramBlock`
- 表 → `TableBlock`
- 附录 → `Appendix`

## 推荐迁移顺序

### 第一步：保留现有 Markdown 输出
现有 `render_markdown(...)` 继续保留，避免影响已有交付能力。

### 第二步：新增正式版模型构建函数
建议新增：

- `build_document_model(plan, style="formal") -> DocumentModel`

作用：

- 不直接输出字符串
- 只负责组装章节、段落、图、表、附录对象

当前已落地原型实现：

- `host/cli/src/planner_cli/document_model.py`
- `host/cli/src/planner_cli/document_builder.py`

### 第三步：将 Markdown renderer 改为消费模型
由：

- `PlanBundle -> markdown`

改为：

- `DocumentModel -> markdown`

### 第四步：新增 DOCX renderer
在中间模型稳定后，增加：

- `DocumentModel -> docx`

## 当前模型需要覆盖的正式交付对象

### 章节
- 项目概述
- 现场调研与现状结论
- 设计原则与技术路线
- 需求与约束分析
- 技术选择与方案比较
- 总体网络架构方案
- 网络拓扑图
- 网络分区与边界控制方案
- 地址、VLAN 与子网规划
- 关键设备部署方案
- 通信与运维接入方案
- 实施方案与切换策略
- 风险分析与待确认事项
- 实施结论与定版条件

### 图
- 总体拓扑图
- 重点边界拓扑图

### 表
- 访问控制矩阵摘要表
- 地址与 VLAN 定版摘要表
- 关键设备部署定版表
- 定版闭环表

### 附录
- 对象清单摘要
- 网络规划摘要
- 后续可扩展为细化拓扑图集、地址表、设备表、访问矩阵明细表

## 当前判断

当前是进入 DOCX 输出前的最佳时机：

- 章节结构已经稳定
- 图表种类已经稳定
- 门禁已经可以保护现有正式版结构

因此下一步最合理的工程动作是：

1. 让正式版先能构建 `DocumentModel`
2. 再让 Markdown renderer 消费模型
3. 最后增加 DOCX renderer
