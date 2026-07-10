# 快速上手

本文档面向第一次接触 `Industrial-Network-Planning-Skills` 的使用者，帮助你用最少步骤生成第一份正式 HTML 方案。

## 1. 这是什么

这是一个工业网络规划方案生成项目。

你提供标准化项目资料，系统输出正式 HTML 方案，内容覆盖：

- 项目概况与建设范围
- 业务需求与系统协同
- 现场调研与设计依据
- 总体架构与安全方案
- 工程实施设计
- 通信关系与实施方案
- 风险分析与待确认事项
- 结论与实施建议

## 2. 运行前提

建议本地具备：

- `python3`
- Graphviz（可选，但建议安装）

说明补充：

- 仅生成 HTML 时，不需要安装 `python-docx`
- 只有在输出 DOCX 时，才需要额外安装相关依赖

说明：

- 未安装 Graphviz 时，HTML 仍可生成
- 但拓扑图位置会显示安装提示，而不是实际图形

## 3. 第一次运行

请优先使用以下命令生成正式 HTML。这个结果就是当前项目推荐的标准交付样式。

在仓库根目录执行：

```bash
PYTHONPATH=host/cli/src python3 -m planner_cli.main generate \
  --input host/cli/examples/dayawan-unit1-mes-input.json \
  --format html --style formal \
  --output output/dayawan-detailed.html
```

生成完成后，打开：

- `output/dayawan-detailed.html`

如果你只想先看一个较小样例，也可以执行：

```bash
PYTHONPATH=host/cli/src python3 -m planner_cli.main generate \
  --input industrial-network-planner/examples/standard-input-example.json \
  --format html --style formal \
  --output output/standard-detailed.html
```

注意：

- 不建议跳过 CLI、直接让模型自由拼写 HTML
- 那样得到的通常是普通单栏页面，不是当前仓库的正式交付版式

## 4. 输入文件从哪里开始

推荐从这几个文件开始理解输入：

- `industrial-network-planner/references/input-contract.md`
- `docs/deployment-and-usage.md`
- `host/cli/examples/dayawan-unit1-mes-input.json`
- `industrial-network-planner/examples/standard-input-example.json`

如果你要替换成自己的项目资料，优先补齐以下内容：

- 项目目标与范围
- 业务流程与设备归属
- 安全需求与关键对象
- 环境条件与实施约束
- 拓扑、冗余、性能、地址与时延要求
- 设备选型、部署设计与连接关系

## 5. 输出怎么看

正式 HTML 不是简单模板拼接，而是按项目规划逻辑展开。

建议重点查看这些章节：

1. `业务需求与系统协同`
2. `现场调研与设计依据`
3. `总体架构与安全方案`
4. `工程实施设计`
5. `通信关系与实施方案`
6. `风险分析与待确认事项`

## 6. 常见问题

### 6.1 为什么没有拓扑图

通常是因为本地没有安装 Graphviz。

安装后重新生成即可。

### 6.2 为什么有待确认事项

待确认事项用于承接输入中确实缺失、但又会影响实施定版的关键信息。

当前输出已尽量控制数量，只保留必要项。

### 6.3 怎么换成自己的项目

最简单做法：

1. 复制一个现有样例 JSON
2. 按自己的项目资料替换字段
3. 重新执行生成命令
4. 打开 `output/*.html` 查看结果

## 7. 推荐阅读顺序

如果你要正式接入或二次使用，推荐按以下顺序阅读：

1. `README.md`
2. `docs/public-quickstart.md`
3. `docs/deployment-and-usage.md`
4. `industrial-network-planner/references/input-contract.md`
5. `host/cli/examples/dayawan-unit1-mes-input.json`
