# 施工级输入包模板说明

本模板用于在正式交付件引擎中触发“施工级实数表”输出能力。

## 适用场景

当项目已具备以下条件时，建议使用本模板补充输入：

- 已明确 VLAN 编号或编号策略
- 已明确子网规划或网关信息
- 已明确访问控制矩阵
- 已明确关键设备部署位置与前置条件

## 关键新增输入域

### `delivery.accessMatrix`

用于输出正式版中的 `访问控制矩阵摘要表`。

字段建议：

- `id`
- `scenario`
- `source`
- `target`
- `service`
- `control`

### `delivery.vlanPlan`

用于输出正式版中的 `地址与 VLAN 定版摘要表`。

字段建议：

- `id`
- `zone`
- `vlan`
- `subnet`
- `naming`
- `constraint`

### `delivery.devicePlan`

用于输出正式版中的 `关键设备部署定版表`。

字段建议：

- `id`
- `deviceType`
- `location`
- `prerequisite`
- `requirement`

## 输出行为

- 若存在 `delivery.*` 数据，正式版优先输出施工级实数表。
- 若不存在 `delivery.*` 数据，正式版回退为区域级审批摘要表。

## 推荐使用方式

- 方案初版：先使用标准输入模型生成审批级正式版
- 方案深化：补充 `delivery.*` 字段，生成施工级冻结表版本
- 项目定版：基于现场复核和客户确认持续修订 `delivery.*` 数据
