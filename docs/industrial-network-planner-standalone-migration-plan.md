# industrial-network-planner 独立化迁移方案

## 1. 目标

本方案用于将当前仓库中的 `industrial-network-planner` 从“附着在现有系统中的 skill 设计包”提升为“可独立存在、可迁移、可复用的核心能力体”。

独立化后的目标不是简单复制一个文件夹，而是完成以下转变：

- 从“当前系统内的一个 skill 目录”转为“可独立运行的核心能力包”
- 从“依赖当前系统页面结构理解输入”转为“以标准输入包为主、系统适配器为辅”
- 从“当前系统是默认宿主”转为“当前系统只是一个 adapter 来源”

## 2. 总体判断

结论：适合独立出去，而且越早按“独立核心 + 适配器 + 宿主”的结构收口，后续越省成本。

原因如下：

1. 当前 skill 的核心价值已经不再只是服务当前系统页面，而是服务“ISA95 + IEC62443 总经验体”的方法执行与客户方案生成。
2. 未来若要接多个系统、多种输入形式或做产品化，继续强绑当前系统会增加维护成本。
3. 当前已形成的方法、规则、模板、输入合同、装配规则，天然适合作为独立核心保存。

## 3. 独立化后的三层结构

建议把未来的新系统或新仓库设计为三层：

### 3.1 核心层（Core）

职责：

- 保存 skill 的方法体执行规则
- 保存标准输入合同
- 保存输出模板与装配规则
- 保存端到端运行说明

这一层不依赖当前系统。

建议结构：

```text
industrial-network-planner/
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
    deployment-and-usage.md
  templates/
    customer-solution-template.md
  examples/
    standard-input-example.json
    expected-output-outline.md
    end-to-end-runbook.md
    standalone-workflow-example.md
```

### 3.2 适配层（Adapters）

职责：

- 负责把不同来源系统的数据转换为核心层的标准输入包
- 不改变核心方法体，只做输入对接

建议结构：

```text
adapters/
  current-industrial-network-planning-framework/
    adapter-overview.md
    runtime-to-standard-input-spec.md
    runtime-export-example.json
    field-level-mapping-example.md
```

未来可扩展为：

```text
adapters/
  current-industrial-network-planning-framework/
  future-survey-system/
  excel-input-package/
  api-ingestion/
```

### 3.3 宿主层（Hosts）

职责：

- 承载 skill 的运行方式
- 可以是当前系统、未来新系统、CLI、Web 页面或 API 服务

可选宿主包括：

- 当前工业网络规划框架
- 一个新的独立系统
- 一个命令行工具
- 一个 Web 端导入/导出工具
- 一个后端 API 服务

## 4. 当前仓库内容如何拆分

### 4.1 应保留为核心层的内容

以下内容应视为独立 skill 的核心资产：

- `skills/industrial-network-planner/SKILL.md`
- `skills/industrial-network-planner/references/methodology-core.md`
- `skills/industrial-network-planner/references/input-contract.md`
- `skills/industrial-network-planner/references/design-decision-rules.md`
- `skills/industrial-network-planner/references/report-outline.md`
- `skills/industrial-network-planner/references/evidence-and-assumption-rules.md`
- `skills/industrial-network-planner/references/experience-absorption-spec.md`
- `skills/industrial-network-planner/references/research-analysis-design-flow.md`
- `skills/industrial-network-planner/references/experience-page-classification.md`
- `skills/industrial-network-planner/references/page-to-input-mapping.md`
- `skills/industrial-network-planner/references/rule-topic-to-design-mapping.md`
- `skills/industrial-network-planner/references/document-assembly-rules.md`
- `skills/industrial-network-planner/templates/customer-solution-template.md`
- `skills/industrial-network-planner/examples/standard-input-example.json`
- `skills/industrial-network-planner/examples/expected-output-outline.md`
- `skills/industrial-network-planner/examples/end-to-end-runbook.md`

这些文件的特点是：

- 不依赖当前系统运行
- 面向总经验体本身
- 可在其他环境下直接复用

### 4.2 应降级为当前系统适配器的内容

以下内容不应再被视为核心 skill 主体，而应视为当前系统的 adapter 文档：

- `skills/industrial-network-planner/references/system-mapping.md`
- `skills/industrial-network-planner/references/runtime-to-standard-input-spec.md`
- `skills/industrial-network-planner/examples/runtime-export-example.json`
- `skills/industrial-network-planner/examples/field-level-mapping-example.md`

这些文件的特点是：

- 明显依赖当前系统的页面、运行时结构或导出形态
- 只是在说明“当前系统如何接入 skill”
- 不应成为 skill 脱离系统后的主入口

### 4.3 当前系统代码在独立化后的定位

当前仓库中的以下部分应继续保留在宿主或 adapter 侧，而不是带入核心层：

- `src/app/`
- `src/components/`
- `src/store/`
- `src/methodologies/`
- `src/rules/`
- `src/engine/` 中与现有前端状态管理直接耦合的部分

原因：

- 这些内容服务的是当前系统的页面驱动和交互逻辑
- 它们不是独立 skill 本身

## 5. 新系统的建议形态

如果决定新建一个独立系统，建议不要复刻当前系统的整套页面驱动模式，而应围绕“独立输入包 + 方案生成”设计。

### 5.1 最小可用新系统（推荐）

建议先做一个轻量宿主：

- 导入标准输入包
- 选择模板和输出偏好
- 生成 Markdown 方案
- 导出结果

这类系统的核心能力应是：

1. 上传/编辑标准输入包
2. 调用 `industrial-network-planner` 核心层
3. 输出客户方案
4. 保存运行记录

### 5.2 后续增强能力

等独立核心稳定后，再逐步增加：

- 多 adapter 接入
- 可视化输入编辑
- 文档预览和二次修订
- API 服务化
- Word/PDF 导出

## 6. 推荐迁移路径

### Phase 1：概念独立化

目标：先在结构上把“核心层”和“当前系统 adapter”分开。

动作：

- 重定义现有文档角色
- 把当前系统相关文档标记为 adapter 级内容
- 在新文档中明确三层结构

### Phase 2：目录独立化

目标：把独立 skill 的核心目录从当前仓库中抽出。

动作：

- 建立新的独立目录或新仓库
- 迁移核心文件
- 单独建立 `adapters/current-industrial-network-planning-framework/`

### Phase 3：运行独立化

目标：让 skill 在没有当前系统页面的情况下也能使用。

动作：

- 以标准输入 JSON 为主入口
- 用模板生成客户方案
- 验证无需当前系统也可完成完整输出

### Phase 4：宿主扩展化

目标：根据需要接入新系统或新前端。

动作：

- 为新系统实现 adapter 或输入编辑器
- 为当前系统保留 adapter 支持

## 7. 为什么不建议继续把当前系统当主宿主

如果继续默认当前系统是主宿主，会出现以下问题：

- 核心能力与现有页面结构耦合越来越深
- 后续迁移时需要反向拆耦
- 任何新接入源都要模仿当前系统结构
- skill 容易退化成“当前系统的一个导出功能”

这与你想要的“独立个体”方向不一致。

## 8. 推荐结论

推荐你把 `industrial-network-planner` 定义为：

- 一个独立核心能力包
- 一个以标准输入包为主入口的客户方案生成 skill
- 当前工业网络规划框架只是它的首个 adapter 来源

这是当前最符合你长期目标的方案。

## 9. 当前阶段建议动作

如果你准备往独立化推进，建议下一步优先做以下三件事：

1. 在文档层明确“核心层 / adapter 层 / 宿主层”的边界
2. 把现有文件按这三层重新归档或至少重新命名归类
3. 设计一个新系统的最小目录骨架，而不是继续在当前系统里深化实现

## 10. 迁移清单

### 核心层拟迁出清单

- `skills/industrial-network-planner/SKILL.md`
- `skills/industrial-network-planner/references/methodology-core.md`
- `skills/industrial-network-planner/references/input-contract.md`
- `skills/industrial-network-planner/references/design-decision-rules.md`
- `skills/industrial-network-planner/references/report-outline.md`
- `skills/industrial-network-planner/references/evidence-and-assumption-rules.md`
- `skills/industrial-network-planner/references/experience-absorption-spec.md`
- `skills/industrial-network-planner/references/research-analysis-design-flow.md`
- `skills/industrial-network-planner/references/experience-page-classification.md`
- `skills/industrial-network-planner/references/page-to-input-mapping.md`
- `skills/industrial-network-planner/references/rule-topic-to-design-mapping.md`
- `skills/industrial-network-planner/references/document-assembly-rules.md`
- `skills/industrial-network-planner/templates/customer-solution-template.md`
- `skills/industrial-network-planner/examples/standard-input-example.json`
- `skills/industrial-network-planner/examples/expected-output-outline.md`
- `skills/industrial-network-planner/examples/end-to-end-runbook.md`

### 当前系统 adapter 拟保留/迁移为 adapter 清单

- `skills/industrial-network-planner/references/system-mapping.md`
- `skills/industrial-network-planner/references/runtime-to-standard-input-spec.md`
- `skills/industrial-network-planner/examples/runtime-export-example.json`
- `skills/industrial-network-planner/examples/field-level-mapping-example.md`

### 当前宿主系统保留清单

- `src/` 下现有前端、store、methodology、rules 等系统实现

