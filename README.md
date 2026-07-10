# Industrial-Network-Planning-Skills

面向工业场景的网络规划方案生成项目。

本项目围绕真实工程调研、网络设计分析与正式交付组织能力，输入标准化项目资料，输出客户可阅读的正式 HTML 方案。

## 项目目标

- 组织工业网络规划所需的项目基础信息
- 形成覆盖业务、环境、安全、网络与工程实施的设计分析
- 输出正式、专业、可交付的工业网络方案文档

## 当前输出

当前主输出为正式 HTML 方案，重点覆盖：

- 项目概况与建设范围
- 业务需求与系统协同
- 现场调研与设计依据
- 总体架构与安全方案
- 工程实施设计
- 通信关系与实施方案
- 风险分析与待确认事项
- 结论与实施建议

说明：

- 当前仓库对外推荐的标准结果就是正式 HTML
- CLI 默认输出已设为 `html + formal`
- 如需得到左侧目录、结构化章节、图表块与正式版式，应使用 CLI 的 `--format html --style formal`
- 不建议直接让模型自由生成 HTML，否则可能得到简化单栏文稿，而不是正式交付版式

## 目录

- `industrial-network-planner/`：方法体系、规则、输入合同、文档装配规范与参考资料
- `host/cli/`：命令行宿主与生成实现
- `docs/`：项目说明、使用文档与交接文档
- `output/`：本地生成的 HTML 结果

## 使用方式

**标准使用方式**

- 使用 CLI 直接生成正式 HTML
- 使用仓库默认正式渲染链路
- 生成结果应包含目录、结构化章节、拓扑图或 Graphviz 缺失提示

**非标准使用方式**

- 先生成中间文稿，再转换成 HTML
- 直接让模型自由拼写 HTML 页面
- 结果缺少拓扑图，且也没有 Graphviz 缺失提示

以上非标准方式生成的结果，不视为正式交付件。

首次使用建议先阅读：

- `docs/public-quickstart.md`

示例命令：

```bash
PYTHONPATH=host/cli/src python3 -m planner_cli.main generate \
  --input host/cli/examples/dayawan-unit1-mes-input.json \
  --format html --style formal \
  --output output/dayawan-detailed.html
```

## 当前维护原则

- 以当前项目为中心表达，不强调历史来源背景
- 优先呈现真实业务、环境、设计与实施逻辑
- 输出文风面向正式方案交付，而不是内部系统记录
- 对缺失信息仅保留必要且有限的待确认事项
