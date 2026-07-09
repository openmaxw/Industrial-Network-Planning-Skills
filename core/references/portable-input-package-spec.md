# 可移植输入包规范

本文件定义 `industrial-network-planner` 在脱离任何特定系统后使用的标准输入包规范。

## 1. 目标

可移植输入包是独立 skill 的第一入口。

它的作用是：

- 让 skill 不依赖当前系统页面结构运行
- 让不同来源系统都能通过 adapter 生成同一类输入
- 让人工整理输入、CLI 调用、API 调用都使用相同数据合同

## 2. 包结构建议

最小输入包可采用单文件 JSON：

- `standard-input.json`

后续如信息量较大，也可采用目录结构：

```text
input-package/
  project.json
  survey.json
  current-network.json
  assets.json
  communications.json
  addressing.json
  security.json
  design.json
  open-items.json
```

第一版建议优先支持单文件 JSON。

## 3. 顶层对象结构

顶层字段建议固定为：

- `project`
- `survey`
- `currentNetwork`
- `assets`
- `communications`
- `addressing`
- `security`
- `design`
- `openItems`

所有顶层键建议始终存在；如果某一域暂无数据，可使用空对象、空数组或空字符串。

## 4. 各域要求

### 4.1 `project`

至少建议包含：

- `name`
- `customer`
- `site`
- `objective`
- `scope`
- `constraints`

### 4.2 `survey`

建议包含：

- `timeline`
- `participants`
- `sources`
- `observations`
- `findings`
- `concerns`

### 4.3 `currentNetwork`

建议包含：

- `topology`
- `layers`
- `boundaries`
- `links`
- `resilience`

### 4.4 `assets`

建议包含：

- `systems`
- `devices`
- `roles`
- `locations`
- `criticality`

### 4.5 `communications`

建议包含：

- `flows`
- `protocols`
- `accessPaths`
- `remoteMaintenance`

### 4.6 `addressing`

建议包含：

- `existingNetworks`
- `reservedNetworks`
- `vlans`
- `naming`
- `constraints`
- `vlanTable`（可选，结构化 VLAN 明细）
- `subnetTable`（可选，结构化子网明细）

### 4.7 `security`

建议包含：

- `objectives`
- `zones`
- `boundaryRequirements`
- `accessControl`
- `auditRequirements`

### 4.8 `design`

建议包含：

- `principles`
- `targetArchitecture`
- `segmentation`
- `addressPlan`
- `deployment`
- `implementation`

### 4.9 `openItems`

建议包含：

- `missingInformation`
- `siteVerification`
- `customerConfirmation`
- `designAssumptions`

### 4.10 `delivery`

用于承载施工级或审批冻结级数据；若缺失，系统继续按规划级输出。

建议包含：

- `accessMatrix`
- `vlanPlan`
- `devicePlan`
- `topologyZones`（详细拓扑分区定义）
- `topologyNodes`（详细拓扑节点定义）
- `topologyLinks`（详细拓扑链路定义）
- `topologyStructures`（星型、环型、双上联、堆叠等网络结构定义）
- `keyNetworkDevices`（需重点突出的关键网络设备清单）

## 5. 必填与可缺失策略

### 必须具备的最小信息

若要生成一版最小可用客户方案，建议至少具备：

- `project.name`
- `project.objective`
- `project.scope`
- `currentNetwork.topology`
- `assets.systems` 或 `assets.devices`
- `communications.flows` 或 `communications.accessPaths`
- `openItems`（即便为空，也应存在）

### 可缺失但必须显式处理的信息

以下信息可以缺失，但缺失后必须转入 `openItems` 或在正文中按建议/待确认方式表达：

- 精确 IP 清单
- 设备品牌与型号
- 详细冗余策略
- 安全设备部署位置
- 审计粒度与实施窗口

## 6. 格式要求

- 优先使用 UTF-8 编码 JSON
- 数组字段优先使用字符串数组或结构化对象数组
- 不要在顶层混入来源系统专有字段
- 适配器来源信息如需保留，建议放入单独的 `meta` 对象，而不是污染核心域

## 7. 使用方式

独立 skill 在使用时应优先接受：

- 单文件标准输入 JSON
- 或 adapter 输出后的标准输入对象

不应默认要求：

- 当前系统页面结构
- `formData`
- `recordCollections`

## 8. 结论

可移植输入包规范是 `industrial-network-planner` 脱离当前系统后的最重要基础之一。

谁能生成符合该规范的输入包，谁就能调用该 skill。
