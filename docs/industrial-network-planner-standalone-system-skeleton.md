# industrial-network-planner 新独立系统最小目录骨架方案

## 1. 目标

本方案用于定义一个围绕 `industrial-network-planner` 构建的新独立系统最小骨架。

该系统的目标不是复刻当前仓库的完整页面驱动框架，而是优先支撑以下能力：

1. 接收标准输入包
2. 调用 `industrial-network-planner` 核心能力
3. 生成客户交付级网络方案
4. 保持对多 adapter 和多宿主形态的扩展能力

## 2. 设计原则

### 2.1 核心优先

新系统应围绕独立核心能力构建，而不是围绕当前系统页面结构构建。

### 2.2 输入标准化优先

系统主入口应是标准输入包，而不是某一种固定页面结构。

### 2.3 Adapter 外置

不同来源系统的数据接入应通过 adapter 处理，不应污染核心层。

### 2.4 宿主轻量化

第一版宿主只做必要的输入、调用、输出，不提前做重型复杂前端。

## 3. 最小目录骨架

建议新系统或新仓库采用以下结构：

```text
industrial-network-planner-standalone/
  README.md
  docs/
    architecture-overview.md
    deployment-and-usage.md
    roadmap.md
  core/
    SKILL.md
    references/
      methodology-core.md
      input-contract.md
      design-decision-rules.md
      report-outline.md
      evidence-and-assumption-rules.md
      experience-absorption-spec.md
      research-analysis-design-flow.md
      experience-page-classification.md
      page-to-input-mapping.md
      rule-topic-to-design-mapping.md
      document-assembly-rules.md
      portable-input-package-spec.md
    templates/
      customer-solution-template.md
    examples/
      standard-input-example.json
      expected-output-outline.md
      end-to-end-runbook.md
      standalone-workflow-example.md
  adapters/
    current-industrial-network-planning-framework/
      adapter-overview.md
      runtime-to-standard-input-spec.md
      runtime-export-example.json
      field-level-mapping-example.md
  host/
    cli/
      README.md
    web/
      README.md
    api/
      README.md
  output/
    .gitkeep
```

## 4. 每层职责说明

### 4.1 `core/`

这是整个系统最重要的目录。

职责：

- 保存 skill 主说明
- 保存总经验体方法规则
- 保存标准输入合同
- 保存文档模板和装配规则
- 保存示例输入与运行说明

要求：

- 不依赖某个具体宿主
- 不依赖某个具体 adapter
- 可以被 CLI、Web、API 等多种宿主复用

### 4.2 `adapters/`

职责：

- 描述如何从特定来源系统提取或转换输入
- 生成符合 `core/` 标准输入合同的数据包

要求：

- 每个 adapter 自己维护来源说明和转换规范
- 不修改核心方法和模板

第一版只需一个 adapter：

- `current-industrial-network-planning-framework/`

### 4.3 `host/`

职责：

- 提供用户交互方式
- 承接输入、调用核心、输出结果

第一版可不全部实现，但目录上应预留三类宿主：

- `cli/`
- `web/`
- `api/`

建议优先顺序：

1. CLI
2. Web
3. API

因为 CLI 最轻、最利于验证核心能力。

### 4.4 `docs/`

职责：

- 说明独立系统的架构
- 说明部署与使用方式
- 说明阶段性路线图

### 4.5 `output/`

职责：

- 用于放生成的方案文档
- 不参与核心逻辑设计，但作为运行输出目录预留

## 5. 第一版最小可用系统（MVP）建议

建议第一版只实现一个最小闭环：

### 输入
- 读取一个标准输入 JSON

### 处理
- 按 `core/` 中的规则组织生成逻辑

### 输出
- 生成一份 Markdown 客户方案到 `output/`

### 交互方式
- 命令行触发

也就是说，MVP 不要求：

- 可视化编辑界面
- 拖拽式页面配置
- 多租户或复杂账号体系
- 实时协作

MVP 只要求验证：

- 核心方法能独立工作
- 不依赖当前系统也能生成方案

## 6. 新系统中的关键文件建议

### 6.1 `README.md`

说明：

- 系统定位
- 核心目录说明
- 如何运行最小示例
- 如何添加新 adapter

### 6.2 `docs/architecture-overview.md`

说明：

- Core / Adapters / Hosts 三层结构
- 数据流向
- 为什么当前系统只是 adapter

### 6.3 `docs/deployment-and-usage.md`

说明：

- 本地部署方式
- 如何准备标准输入包
- 如何生成输出文档

### 6.4 `docs/roadmap.md`

说明：

- MVP 阶段
- Adapter 扩展阶段
- Web/API 化阶段

## 7. 数据流建议

新独立系统中的最小数据流建议如下：

```text
标准输入包 / adapter 输出
  -> 核心输入校验
  -> 方法体执行
  -> 章节装配
  -> Markdown 方案输出
```

如果输入来自当前系统，则数据流为：

```text
当前系统运行时导出 JSON
  -> current adapter
  -> 标准输入包
  -> 核心方法执行
  -> 客户方案输出
```

## 8. 为什么推荐 CLI 作为第一宿主

CLI 最适合第一版独立系统，原因是：

1. 最轻量
2. 不依赖先做复杂前端
3. 最便于验证标准输入包是否合理
4. 最适合先验证核心方法和输出结构

Web 和 API 可以在核心稳定后再逐步增加。

## 9. 当前仓库与新系统的关系

建议关系如下：

- 当前仓库：经验来源 + 首个 adapter 来源 + 参考宿主
- 新独立系统：以 `industrial-network-planner` 为核心的正式独立宿主

不要再把当前仓库当作唯一母体，而应把它看作“首个已知来源系统”。

## 10. 推荐实施顺序

### Phase 1：建立新系统骨架

只建立目录与核心文档，不急于写代码。

### Phase 2：迁移核心层文件

把当前仓库中属于核心层的内容迁移到 `core/`。

### Phase 3：迁移当前系统 adapter

把当前系统相关映射和示例迁移到 `adapters/current-industrial-network-planning-framework/`。

### Phase 4：补 CLI MVP

增加最小命令行入口：

- 读取输入包
- 输出 Markdown

### Phase 5：再决定是否做 Web/API

只有在 CLI 验证稳定后，再决定扩展宿主层。

## 11. 建议结论

如果你的目标是让 `industrial-network-planner` 成为真正独立的个体，那么最合理的新系统骨架应该是：

- Core 为中心
- Adapter 为输入桥接
- Host 为可替换宿主

而不是继续以当前页面系统为中心做二次生长。
