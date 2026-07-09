# Industrial-Network-Planning-Skills 部署与使用说明

## 1. 目标

本说明用于解释新独立仓库如何被使用，而不依赖原有工业网络规划框架页面系统。

## 2. 当前仓库结构

当前仓库已按三层组织：

- `core/`：独立 skill 核心
- `adapters/`：不同来源系统适配资料
- `docs/`：架构、迁移与使用说明
- `output/`：输出目录，当前建议优先输出 HTML 交付预览

## 3. 最小使用方式

第一版建议采用最简单的使用方式：

1. 准备一个标准输入包
2. 基于 `core/` 中的方法与模板生成客户方案
3. 输出 HTML 文档到 `output/`

## 4. 如何准备输入

### 方式一：手工准备标准输入包

直接参照：

- `core/references/portable-input-package-spec.md`
- `core/examples/standard-input-example.json`

手工整理项目输入，生成标准输入 JSON。

### 方式二：通过 adapter 生成标准输入包

例如当前系统：

- `adapters/current-industrial-network-planning-framework/runtime-to-standard-input-spec.md`
- `adapters/current-industrial-network-planning-framework/runtime-export-example.json`

先从来源系统导出数据，再按 adapter 规范转换为标准输入包。

## 5. 如何组织 skill 运行

在没有实现代码的阶段，当前仓库中的运行逻辑应理解为：

- 按 `core/SKILL.md` 规定读取核心规则
- 使用 `core/references/` 中的方法与装配规则
- 以 `core/templates/customer-solution-template.md` 作为输出骨架
- 生成客户方案 Markdown

## 6. 当前阶段推荐的运行形态

最推荐的第一宿主是 CLI。

原因：

- 最轻量
- 不依赖先做 Web 前端
- 最适合验证标准输入包与核心输出是否合理

## 7. CLI MVP 建议行为

未来若进入实现阶段，CLI 第一版建议提供以下能力：

- 指定输入文件
- 指定输出文件
- 读取标准输入 JSON
- 调用核心规则生成 Markdown 方案
- 在生成前进行输入完整性检查
- 在输出中保留待确认项和假设项

## 8. 输出建议

第一版输出建议统一为 Markdown：

- 易于版本管理
- 易于人工审阅
- 易于后续转换为 HTML / Word / PDF

输出目录建议为：

- `output/`（如 `output/dayawan-detailed.html`）

## 正式 HTML 的表达原则

当前正式 HTML 输出不应只保留收敛结论，而应尽量保留规划逻辑链条。核心章节建议按以下层次组织：

1. 本章结论摘要
2. 基础事实记录
3. 关键设计约束
4. 结构化表格 / 图示
5. 设计响应
6. 待确认项

其中：

- “基础事实记录”用于保留业务描述、调研记录、环境条件、地址继承条件等原始素材
- “关键设计约束”用于说明这些原始输入如何转化为规划边界
- “设计响应”用于说明网络架构、冗余、性能、地址、部署等设计如何回应这些约束

## 9. 当前系统的定位

当前工业网络规划框架不再被定义为 skill 的唯一宿主，而是：

- 一个已知来源系统
- 一个首个 adapter 样例

这意味着：

- skill 可以脱离它使用
- 但也可以继续通过 adapter 接入它

## 10. 推荐使用路径

### 路径 A：完全脱离当前系统

- 手工或通过其他来源准备标准输入包
- 用独立 skill 生成客户方案

### 路径 B：当前系统作为来源

- 在当前系统完成采集与推演
- 导出运行时数据
- 经 adapter 转换为标准输入包
- 用独立 skill 生成客户方案

## 11. 当前阶段结论

当前仓库已经具备：

- 核心 skill 资产
- 当前系统 adapter 样例
- 独立化迁移与系统骨架说明

下一步若要真正运行，只需补一层宿主实现（优先 CLI）。
