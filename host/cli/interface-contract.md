# CLI 接口合同

## 1. 目标

本文件定义 `host/cli` 作为 `industrial-network-planner` 第一宿主时的最小接口合同，确保：

- 宿主边界清晰
- 输入输出稳定
- 校验结果可预期
- 后续 Web / API 宿主可复用相同编排思想

## 2. 主命令合同

当前主命令：

```bash
planner generate --input <path> [--output <path>] [--strict]
```

### 2.1 参数语义

- `--input`：标准输入 JSON 文件路径，必填
- `--output`：输出 HTML 文件路径，选填
- `--strict`：严格模式；将警告提升为失败，选填

### 2.2 参数约束

- `--input` 必须是本地可读 JSON 文件
- 若不传 `--output`，默认输出到 `output/<project-slug>-solution.html`

## 3. 输入合同

CLI 当前只接受标准输入包，不直接接受来源系统运行时导出结构。

输入依据：

- `industrial-network-planner/references/input-contract.md`
- `industrial-network-planner/references/portable-input-package-spec.md`

### 3.1 当前最小必需域

- `project`
- `currentNetwork`
- `assets`
- `communications`
- `openItems`

### 3.2 当前推荐域

- `survey`
- `addressing`
- `security`
- `design`

### 3.3 当前项目必需字段

- `project.name`
- `project.customer`
- `project.objective`
- `project.scope`

## 4. 校验结果合同

CLI 当前把校验结果分为：

- 阻断错误 `errors`
- 非阻断警告 `warnings`

### 4.1 阻断错误示例

- 输入文件不存在
- JSON 非法
- 根结构不是对象
- 缺失最小必需域
- 缺失项目基本必填字段

### 4.2 非阻断警告示例

- 缺少推荐域
- 缺少现状基础描述
- 缺少通信/访问关系
- 缺少实施约束
- 缺少明确待确认项

### 4.3 严格模式规则

在 `--strict` 下：

- 任意 `warnings` 均提升为失败
- 命令返回输入校验失败退出码

## 5. 输出合同

CLI 当前输出统一为正式 HTML。

### 5.1 输出章节目标

输出应尽量覆盖：

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
12. 结论与建议
13. 附录

### 5.2 表达边界

正文中的关键内容必须归类为：

- 已确认事实
- 规划建议
- 假设项
- 待确认项

若证据不足，不应写成确定性定稿结论。

## 6. 退出码合同

- `0`：成功生成
- `1`：通用执行失败
- `2`：参数错误
- `3`：输入读取失败
- `4`：输入校验失败
- `5`：输出写入失败

## 7. 当前实现与合同的关系

当前实现已经满足：

- 单命令生成链路
- 标准输入读取
- 最小合同校验
- 章节化正式 HTML 输出
- 假设项与待确认项单列

当前实现尚未完全满足：

- 所有 `industrial-network-planner/references/` 规则的结构化执行
- 细粒度字段级证据追踪
- 深度章节推理与更强的客户交付表达

因此，本合同当前定义的是：

- 第一版可运行接口
- 而不是最终完整能力上限
