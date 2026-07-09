# 字段级映射示例

本文件演示，当前系统中的具体页面记录如何逐步落入标准输入模型。

## 示例 1：`enterprise-basic` → `project`

### 原始记录

```json
{
  "enterprise.name": "某新能源制造企业",
  "enterprise.scope": "华东生产基地一期工业网络升级",
  "enterprise.level": "集团-基地-车间",
  "enterprise.goal": "形成清晰层级、边界和可实施的工业网络方案"
}
```

### 映射结果

```json
{
  "project": {
    "customer": "某新能源制造企业",
    "scope": "华东生产基地一期工业网络升级",
    "objective": "形成清晰层级、边界和可实施的工业网络方案"
  }
}
```

### 说明

- `enterprise.name` 优先进入 `project.customer`
- `enterprise.scope` 进入 `project.scope`
- `enterprise.goal` 进入 `project.objective`
- `enterprise.level` 可作为补充信息进入项目概述或 ISA95 层级建模说明

## 示例 2：`site-structure` → `project` / `assets` / `currentNetwork`

### 原始记录

```json
{
  "site.nodeName": "车间汇聚",
  "site.nodeType": "车间级",
  "site.parentNode": "厂级核心",
  "site.responsibility": "车间网络汇聚与边界承接"
}
```

### 映射结果

```json
{
  "project": {
    "site": "华东生产基地一期"
  },
  "assets": {
    "locations": ["车间汇聚"]
  },
  "currentNetwork": {
    "layers": ["厂级核心", "车间汇聚"]
  }
}
```

### 说明

- `site.nodeName` 与 `site.parentNode` 支撑层级关系识别
- `site.responsibility` 支撑结构职责说明
- 同类记录应合并后形成完整层级图景

## 示例 3：`isa95-design` → `design`

### 原始记录

```json
{
  "isa95.designPrinciple": "按层级、角色和协同路径组织网络结构。",
  "isa95.integrationPath": "MES 经受控路径与车间控制系统协同。",
  "isa95.boundary": "厂级与车间级之间形成清晰结构边界。"
}
```

### 映射结果

```json
{
  "design": {
    "principles": ["按层级、角色和协同路径组织网络结构。"],
    "targetArchitecture": "MES 经受控路径与车间控制系统协同，厂级与车间级之间形成清晰结构边界。"
  }
}
```

### 说明

- `isa95.designPrinciple` 进入 `design.principles`
- `isa95.integrationPath` 与 `isa95.boundary` 共同支撑 `design.targetArchitecture`
- 若存在多条推演记录，应先归并再出正式表述

## 示例 4：`security-design` → `security` / `design`

### 原始记录

```json
{
  "security.designPrinciple": "按区域、通道、边界和访问关系逐步收敛安全暴露面。",
  "security.remoteControl": "统一经 DMZ、堡垒机与受控维护链路接入控制区。",
  "security.measure": "执行白名单、双因素认证、时间窗控制和日志审计。"
}
```

### 映射结果

```json
{
  "security": {
    "boundaryRequirements": ["统一经 DMZ 和受控维护链路接入控制区"],
    "accessControl": ["白名单", "双因素认证", "时间窗控制"],
    "auditRequirements": ["关键维护操作日志审计"]
  },
  "design": {
    "segmentation": "按区域、通道、边界和访问关系逐步收敛安全暴露面。"
  }
}
```

### 说明

- 安全设计类字段通常同时影响 `security` 和 `design`
- 它们既是安全边界依据，也是总体方案的一部分

## 示例 5：`special-judgements` → `openItems`

### 原始记录

```json
{
  "iteration.name": "远程维护边界先行治理",
  "iteration.reason": "当前远程入口风险高于内部结构优化优先级。",
  "iteration.action": "建议先完成 DMZ 与远维受控路径治理。"
}
```

### 映射结果

```json
{
  "openItems": {
    "designAssumptions": ["远程维护边界治理优先于内部结构优化。"],
    "customerConfirmation": ["是否接受先完成 DMZ 与远维受控路径治理的实施顺序。"]
  }
}
```

### 说明

- 特殊判断不直接进入客户定稿正文
- 通常转入假设、待确认项或实施顺序说明

## 总结

字段级映射的核心不是逐字复制字段，而是：

- 识别字段语义
- 归入稳定的标准输入域
- 为最终客户方案提供结构化输入
