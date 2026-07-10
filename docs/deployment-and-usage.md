# 部署与使用说明

## 1. 项目定位

本项目是一个独立的工业网络规划方案生成器，输入为标准化项目资料，输出为正式 HTML 方案。

其目标不是承接某个旧系统的导出结果，而是围绕真实项目调研、设计分析和正式交付形成稳定的方法与工具链。

## 2. 目录说明

- `industrial-network-planner/`：方法体系、规则、输入合同、文档装配规则与参考资料
- `host/cli/`：命令行宿主与生成实现
- `output/`：本地生成的 HTML 结果
- `docs/`：项目说明、架构说明与使用文档

## 3. 输入要求

输入必须是标准输入包，并直接描述当前项目本身的信息。

重点字段包括：

- 项目目标、范围界定、业务流程
- 设备归属、安全需求、安全场景与后果分析
- 暴露面、基线检查、安全约束与关键对象
- 环境条件、实施约束、设计原则与架构划分
- 技术选择、网络设计、工程设计、对象接入、设备选型、部署设计、连接关系
- 网络拓扑、分层设计、性能设计、稳定性设计、冗余设计、地址分段、时延分析

## 4. 生成方式

正式 HTML 生成命令：

```bash
PYTHONPATH=host/cli/src python3 -m planner_cli.main generate \
  --input host/cli/examples/dayawan-unit1-mes-input.json \
  --format html --style formal \
  --output output/dayawan-detailed.html
```

标准样例生成命令：

```bash
PYTHONPATH=host/cli/src python3 -m planner_cli.main generate \
  --input industrial-network-planner/examples/standard-input-example.json \
  --format html --style formal \
  --output output/standard-detailed.html
```

## 5. 输出特征

正式 HTML 应满足以下要求：

- 以真实项目方案正文口吻输出
- 先呈现业务与现场，再展开设计与实施
- 同时保留关键事实、设计依据、设计响应与必要待确认事项
- 拓扑图使用 Graphviz 生成；如本地未安装，则在 HTML 中提示安装信息

## 6. 当前交付口径

当前项目文档与输出已统一按“全新项目”维护：

- 不强调来源系统、历史迁移或导出链路
- 不使用内部系统中间态措辞
- 不把方案写成模板拼装说明
- 重点突出项目事实、规划逻辑与正式交付表达
