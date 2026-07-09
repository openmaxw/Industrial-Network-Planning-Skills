# host/cli

## 1. 定位

`host/cli/` 是 `industrial-network-planner` 的命令行宿主，用于从标准输入包生成客户交付级工业网络方案。

CLI 的职责保持清晰、稳定、可扩展：

- 接收标准输入包
- 执行基础校验与生成流程
- 调用核心规则、设计逻辑与渲染器
- 输出正式 HTML 方案

CLI 不承担：

- 来源系统专用页面逻辑
- 非标准输入的临时字段适配
- 与具体业务系统耦合的运行时状态管理

## 2. 当前输出目标

当前项目以正式 HTML 作为主交付物。

标准执行结果：

1. 读取标准输入 JSON
2. 校验项目、业务、环境、网络与实施信息
3. 装配业务分析、调研依据、架构、安全、工程与实施内容
4. 生成正式 HTML 方案
5. 输出到 `output/`

## 3. 最小命令形态

```bash
planner generate --input <input.json> --format html --output <output.html>
```

示例：

```bash
PYTHONPATH=host/cli/src python3 -m planner_cli.main generate \
  --input host/cli/examples/dayawan-unit1-mes-input.json \
  --format html --style formal \
  --output output/dayawan-detailed.html
```

## 4. 输入约定

CLI 只接受标准输入包。

输入合同来源：

- `core/references/input-contract.md`
- `core/references/portable-input-package-spec.md`

输入应直接表达项目本身的信息，包括：

- 项目目标、范围与实施约束
- 业务流程、对象归属与安全需求
- 环境条件、干扰因素与工程约束
- 网络结构、冗余诉求、带宽与时延要求
- 设备选型、部署条件与连接关系

## 5. 输出约定

当前输出统一为正式 HTML。

输出内容应覆盖：

- 项目概况与建设范围
- 业务需求与系统协同
- 现场调研与设计依据
- 总体架构与安全方案
- 工程实施设计
- 通信关系与实施方案
- 风险分析与待确认事项
- 结论与实施建议

## 6. 模块边界

建议保持以下模块边界：

- 入口层：参数解析与执行组织
- 输入层：读取与基础校验
- 规划层：业务、环境、网络、安全与实施推理
- 文档层：章节装配与结构建模
- 渲染层：正式 HTML 输出

## 7. 执行原则

- 优先生成面向客户交付的正式文档
- 保留关键调研事实，不只输出抽象总结
- 把业务、环境、冗余、拓扑、性能与实施逻辑完整落到方案中
- 对缺失信息保留少量必要的待确认事项，不制造大量伪缺口

## 8. 当前建议

对于当前仓库，建议统一按“独立项目、独立输入、正式交付”口径维护，不再保留容易让人误解为旧系统迁移物的叙事。
