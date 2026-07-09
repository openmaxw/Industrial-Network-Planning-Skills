# 标准输入合同

本文件定义 `industrial-network-planner` 使用的标准输入模型。

## 1. 设计原则

- 不直接绑定当前系统字段名
- 支持系统内导出数据与系统外整理输入两种模式
- 缺失信息允许存在，但必须被标记和传递

## 2. 输入域

### 2.1 项目域

- `project.name`
- `project.customer`
- `project.site`
- `project.objective`
- `project.scope`
- `project.constraints`

### 2.2 调研域

- `survey.timeline`
- `survey.participants`
- `survey.sources`
- `survey.observations`
- `survey.findings`
- `survey.concerns`
- `survey.environment`
- `survey.installation`
- `survey.emc`
- `survey.physicalDistances`
- `survey.powerAndGrounding`

### 2.3 现状网络域

- `currentNetwork.topology`
- `currentNetwork.layers`
- `currentNetwork.boundaries`
- `currentNetwork.links`
- `currentNetwork.resilience`

### 2.4 资产与系统域

- `assets.systems`
- `assets.devices`
- `assets.roles`
- `assets.locations`
- `assets.criticality`

### 2.5 通信与访问域

- `communications.flows`
- `communications.protocols`
- `communications.accessPaths`
- `communications.remoteMaintenance`
- `communications.performance`
- `communications.bandwidthDrivers`

### 2.6 地址规划域

- `addressing.existingNetworks`
- `addressing.reservedNetworks`
- `addressing.vlans`
- `addressing.naming`
- `addressing.constraints`
- `addressing.vlanTable`
- `addressing.subnetTable`

### 2.7 安全与合规域

- `security.objectives`
- `security.zones`
- `security.boundaryRequirements`
- `security.accessControl`
- `security.auditRequirements`

### 2.8 设计输出域

- `design.principles`
- `design.targetArchitecture`
- `design.segmentation`
- `design.addressPlan`
- `design.deployment`
- `design.implementation`
- `design.topologyRationale`
- `design.redundancyPolicy`
- `design.performancePlan`
- `design.environmentAdaptation`

### 2.10 施工级定版域（可选）

- `delivery.accessMatrix`
- `delivery.vlanPlan`
- `delivery.devicePlan`
- `delivery.topologyZones`
- `delivery.topologyNodes`
- `delivery.topologyLinks`
- `delivery.topologyStructures`
- `delivery.keyNetworkDevices`
- `delivery.redundancyPlan`
- `delivery.bandwidthPlan`
- `delivery.environmentRequirements`

### 2.9 假设与待确认项域

- `openItems.missingInformation`
- `openItems.siteVerification`
- `openItems.customerConfirmation`
- `openItems.designAssumptions`

## 3. 最小可运行输入

若要生成最小可用方案，至少应具备：

- 项目基本信息
- 现状网络基础描述
- 资产或系统对象基础信息
- 初步通信或访问关系
- 约束条件
- 已知待确认项

## 4. 缺失处理规则

- 缺少事实时，允许生成“建议版方案”，但必须标记为建议或待确认
- 缺少关键边界信息时，不得生成确定性的安全边界说明
- 缺少地址基础时，不得生成精确的 IP 定稿，只能给规划原则或建议方案
- 缺少环境、安装、供电、EMC 条件时，不得生成过度细化的设备等级、介质和安装定稿
- 缺少可靠性目标、物理路径或停机容忍度时，不得把冗余结构写成确定性定版
- 缺少流量、并发或关键业务性能约束时，不得给出过度确定的带宽定版值
- 若提供施工级定版域，可优先输出精确定版表；若未提供，则维持区域级规划与待确认表达
