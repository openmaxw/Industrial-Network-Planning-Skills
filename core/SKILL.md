---
name: industrial-network-planner
description: 基于 ISA95 + IEC62443 方法体，从项目资料、现状网络、调研结果与设计依据中生成客户交付级工业网络方案。
---

# industrial-network-planner

## 用途

该 skill 用于生成面向客户交付的完整工业网络方案。

它不是单纯的资料整理器，也不是自由发挥的写作器。它必须在既有方法体约束下工作，把项目输入整理为一份结构稳定、语言专业、边界清晰的客户方案文档。

## 适用场景

适用于以下任务：

- 根据项目输入生成完整工业网络方案
- 根据现状网络、调研结果和设计结论生成方案文档草稿
- 基于 ISA95 + IEC62443 方法体整理网络架构、分区分域、地址规划与实施建议
- 将当前系统中的项目运行时数据映射为客户交付文档

## 不适用场景

以下任务不应直接由本 skill 假定完成：

- 没有项目事实依据时直接编造网络方案
- 把未核实信息写成确定性设计结论
- 把建议版方案写成已实施或已验收状态
- 替代正式现场勘查、容量校核、品牌选型确认或实施验收

## 读取顺序

执行任务时按以下顺序读取引用材料：

1. `references/methodology-core.md`
2. `references/input-contract.md`
3. `references/design-decision-rules.md`
4. `references/report-outline.md`
5. `references/evidence-and-assumption-rules.md`
6. `references/experience-absorption-spec.md`
7. `references/research-analysis-design-flow.md`
8. `references/experience-page-classification.md`
9. `references/page-to-input-mapping.md`
10. `references/rule-topic-to-design-mapping.md`
11. `references/document-assembly-rules.md`
12. `references/system-mapping.md`（仅在输入来自当前系统时读取）
13. `templates/customer-solution-template.md`

## 工作要求

### 输入要求

优先使用标准输入模型组织项目资料，输入类别包括：

- 项目概况
- 调研信息
- 现状网络与拓扑
- 资产与系统对象
- 通信与访问关系
- IP/网段/VLAN 相关信息
- 环境与实施约束
- 安全与边界要求
- 已有设计判断或推演结论
- 假设与待确认项

若输入来自当前系统，应先依据 `references/system-mapping.md` 进行归一。

### 执行阶段

1. 读取输入并完成标准化
2. 识别缺失信息、冲突信息与待确认项
3. 按 ISA95 组织层级、对象归属与系统协同关系
4. 按 IEC62443 识别 zone、conduit、边界与安全控制需求
5. 形成目标网络架构、地址规划与部署建议
6. 按模板输出客户交付级方案文档

### 输出要求

输出必须满足以下要求：

- 使用专业、克制、可交付的方案语气
- 章节结构稳定，不随意改变主顺序
- 事实、建议、假设、待确认项明确区分
- 不伪造现场信息，不补造客户未提供的已确认条件
- 附录清单完整，至少包含资产、IP、连接和待确认项

## 强制规则

- 对已核实事实使用事实表述
- 对规划建议使用建议表述
- 对未核实内容标记为“待确认”或“建议”
- 对品牌、容量、冗余方式、链路数量、边界位置等未确定内容，不得写成最终定稿
- 对缺失信息，不得隐去，必须纳入风险、假设或待确认项章节
- 必须完整吸收经验体中的采集、判断、推演和结果落地链路，不能只抽取输出页结论

## 产出物

首选产出为 Markdown 方案文档。文档面向客户交付，建议包含以下章节：

1. 项目概述与建设目标
2. 现状网络与调研结论
3. 设计依据与方法说明
4. 总体网络架构方案
5. ISA95 层级建模与系统协同结构
6. IEC62443 分区分域与安全边界设计
7. 网络拓扑与通信路径说明
8. IP 地址、VLAN 与子网规划
9. 关键设备与部署建议
10. 实施步骤与迁移建议
11. 风险、假设与待确认项
12. 附录

## 使用提示

当用户要求：

- “生成客户网络方案”
- “根据项目资料输出完整工业网络设计方案”
- “把调研、拓扑、IP、分区分域整理成客户文档”

应使用本 skill。

若用户仅要求查看当前系统字段或页面，不必调用整个方案文档模板，可只引用相关 `references/` 文件完成局部分析。
