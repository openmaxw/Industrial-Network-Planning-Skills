# HANDOFF

## 1. 当前目标

将 `industrial-network-planner` 打造成一个**脱离当前 Industrial-Network-Planning-Framework 系统也可独立使用**的 skill / 能力仓库。

当前仓库：

- `/home/max/Industrial-Network-Planning-Skills`

其定位已经明确为：

- `core/`：独立核心能力
- `adapters/`：来源系统适配层
- `docs/`：独立化设计、迁移与使用说明
- `output/`：输出目录预留

## 2. 已完成内容

### 2.1 核心层已迁入 `core/`

已存在：

- `core/SKILL.md`
- `core/references/`
  - `methodology-core.md`
  - `input-contract.md`
  - `design-decision-rules.md`
  - `report-outline.md`
  - `evidence-and-assumption-rules.md`
  - `experience-absorption-spec.md`
  - `research-analysis-design-flow.md`
  - `experience-page-classification.md`
  - `page-to-input-mapping.md`
  - `rule-topic-to-design-mapping.md`
  - `document-assembly-rules.md`
  - `portable-input-package-spec.md`
- `core/templates/customer-solution-template.md`
- `core/examples/`
  - `standard-input-example.json`
  - `expected-output-outline.md`
  - `minimal-input-example.md`
  - `end-to-end-runbook.md`

### 2.2 当前系统 adapter 已迁入 `adapters/current-industrial-network-planning-framework/`

已存在：

- `system-mapping.md`
- `runtime-to-standard-input-spec.md`
- `runtime-export-example.json`
- `field-level-mapping-example.md`

### 2.3 文档层已建立

已存在：

- `docs/industrial-network-planner-standalone-migration-plan.md`
- `docs/industrial-network-planner-standalone-system-skeleton.md`
- `docs/deployment-and-usage.md`

## 3. 当前明确结论

### 3.1 不再以旧系统为主宿主

旧仓库：

- `/home/max/Industrial-Network-Planning-Framework`

以后只应被视为：

- 方法来源系统
- 当前系统 adapter 来源
- 参考宿主

而不是主开发场所。

### 3.2 主线工作已切换到本仓库

接下来所有主线设计与实现，应优先在：

- `/home/max/Industrial-Network-Planning-Skills`

继续进行。

## 4. 下一步最推荐工作

优先顺序建议如下：

### Step 1：补 `host/cli/` 骨架

目标：明确第一宿主为 CLI。

建议补：

- `host/cli/README.md`
- `host/cli/cli-mvp-plan.md`

内容应说明：

- CLI 接收什么输入
- CLI 输出什么结果
- CLI 最小命令形态
- 输入校验与输出流程

### Step 2：设计 CLI MVP 的模块边界

建议先不急着写完整代码，而是先定清：

- 输入读取模块
- 标准输入校验模块
- 核心规则加载模块
- 文档装配模块
- Markdown 输出模块

### Step 3：再决定是否写第一版 CLI 实现

如果前两步清晰，再进入实现。

## 5. 对后续对话的建议上下文

在新对话中，可直接把下面这段作为开场说明：

> 当前工作目录是 `/home/max/Industrial-Network-Planning-Skills`。这是一个独立的 industrial-network-planner skill 仓库，不再以旧系统为主宿主。请基于现有 `core/`、`adapters/` 和 `docs/`，继续推进 `host/cli/` 的最小骨架和 CLI MVP 方案，优先保持独立可移植性，不回到旧系统中心化思路。

## 6. 注意事项

- 不要再把当前系统相关文档当成核心层继续扩写
- 当前系统相关内容统一放在 `adapters/current-industrial-network-planning-framework/`
- 后续任何新增设计，优先考虑是否属于：
  - `core`
  - `adapter`
  - `host`
- 若不属于 `core`，不要放进 `core/references/`

## 7. 最终方向

最终目标不是“把旧系统搬过来”，而是：

- 形成一个独立的 `industrial-network-planner` 核心仓库
- 当前系统只是首个 adapter
- 第一宿主优先 CLI
- 后续再考虑 Web / API 扩展
