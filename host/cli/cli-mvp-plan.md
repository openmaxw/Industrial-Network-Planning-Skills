# CLI MVP 方案

## 1. 目标

为 `industrial-network-planner` 建立第一版可执行宿主，使仓库能够在不依赖旧系统的前提下，从标准输入包生成客户交付级 HTML 方案。

本方案追求的是“最小闭环成立”，而不是“一步到位做完整产品”。

## 2. MVP 范围

### 2.1 必做范围

CLI MVP 必须具备：

- 一个明确的 `generate` 主命令
- 从本地读取标准输入 JSON
- 对输入进行最小合同校验
- 基于 `industrial-network-planner/` 的模板与规则装配 HTML 文档
- 输出到本地文件
- 对失败场景提供清晰错误信息

### 2.2 暂不纳入范围

CLI MVP 暂不处理：

- 来源系统专用输入格式直连
- 自动执行 adapter 转换
- 富交互问答式补全输入
- Word / PDF 直接导出
- Web UI
- 远程 API 服务化
- 多项目批处理
- 持久化数据库

## 3. 用户视角下的最小体验

用户只需要完成三件事：

1. 准备标准输入 JSON
2. 执行一条命令
3. 在 `output/` 中拿到正式 HTML 方案

理想最小示例：

```bash
planner generate --input industrial-network-planner/examples/standard-input-example.json
```

理想结果：

- 命令成功退出
- 控制台打印输出路径与摘要
- `output/` 中生成一份可审阅的 HTML 方案

## 4. 推荐命令接口

### 4.1 主命令

```bash
planner generate --input <path> [--output <path>] [--strict]
```

### 4.2 参数说明

- `--input`：标准输入 JSON 文件路径，必填
- `--output`：输出 HTML 文件路径，选填
- `--strict`：严格模式；遇到非阻断缺口也直接失败，选填

### 4.3 行为约束

- `--input` 必须指向本地文件
- `--output` 缺省时自动落到 `output/`

## 5. 内部处理链路

CLI MVP 建议采用以下处理链路：

### Step 1：参数解析

输出：

- 命令意图
- 输入路径
- 输出策略
- 严格模式标记

### Step 2：输入读取

输出：

- 原始 JSON 对象

失败条件：

- 文件不存在
- 文件不可读
- JSON 非法

### Step 3：输入校验

输出：

- 校验后的标准输入对象
- 错误列表
- 警告列表
- 假设项候选列表

校验参考：

- `industrial-network-planner/references/input-contract.md`
- `industrial-network-planner/references/portable-input-package-spec.md`

### Step 4：核心资产加载

输出：

- 模板文本
- 报告大纲规则
- 文档装配规则
- 设计决策相关规则引用

### Step 5：中间结果构建

输出：

- 项目摘要
- 约束摘要
- 设计要点
- 假设项
- 待确认项
- 报告章节内容草案

这一层应成为后续 Web / API 宿主可复用的核心编排边界。

### Step 6：HTML 装配

输出：

- 完整 HTML 文本

### Step 7：结果输出

输出：

- 写入正式 HTML 文件
- 返回执行摘要

## 6. 模块划分建议

建议第一版实现时采用如下逻辑模块：

- `command`：CLI 参数解析与入口编排
- `input`：读取标准输入文件
- `validation`：输入合同校验
- `skill-loader`：加载模板和规则资产
- `planner`：构建中间规划结果
- `formal-support`：支撑正式 HTML 章节装配

即使第一版代码量不大，也建议按职责拆开，避免“全部逻辑都在 main 里”。

## 7. 文档生成原则

CLI 输出文档时应遵守以下原则：

### 7.1 明确区分事实与假设

凡输入未明确给出的内容，不应伪装为确定结论。

### 7.2 对缺失信息保留待确认项

不能因为信息不足而静默省略关键设计风险。

### 7.3 输出结构稳定

相同输入结构应尽量得到稳定的章节结构，便于评审与版本管理。

### 7.4 尽量面向交付物

输出不是调试日志，而是“客户方案草案”或“可交付版初稿”的骨架。

## 8. 第一版建议输入/输出样例链路

建议以现有样例作为 MVP 验证链路：

输入参考：

- `industrial-network-planner/examples/standard-input-example.json`

输出目标：

- `output/standard-input-example-solution.html`

评估标准：

- 是否能覆盖 `report-outline.md` 的主要章节
- 是否能把输入中的不确定项转成假设/待确认项
- 是否能形成一份结构完整、可读的 HTML

## 9. 实现语言建议

在未受宿主限制的前提下，第一版实现语言应优先考虑：

- 文件处理方便
- HTML 输出更贴近正式交付
- CLI 参数解析轻量
- 后续易扩展

语言选择本身不是当前阶段最关键问题。

当前更重要的是：

- 接口边界明确
- 输入输出清晰
- 模块职责不混乱

因此可先写清接口与流程，再决定使用何种具体技术栈。

## 10. 后续演进路径

CLI MVP 完成后，建议按以下方向逐步演进：

### 阶段 A：稳定 CLI 核心链路

- 完善校验规则
- 提升 HTML 交付质量
- 固化中间结果模型

### 阶段 B：引入 adapter 串接

- 支持从 adapter 输出直接生成标准输入包
- 但仍保持 adapter 与 host 分层

### 阶段 C：抽出宿主无关编排层

- 把可复用编排逻辑下沉为共享模块
- 为 Web / API 宿主复用做好准备

### 阶段 D：扩展输出形态

- HTML
- PDF
- 其他交付格式

## 11. 当前建议结论

如果下一步继续推进，最合理的顺序是：

1. 基于本方案补 `host/cli/` 文档骨架
2. 再增加一份实现前接口草案
3. 然后开始第一版 CLI 命令实现

换句话说，当前最重要的不是“马上写很多代码”，而是先把 CLI 作为第一宿主的边界定准。
