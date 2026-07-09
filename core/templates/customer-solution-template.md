# {{project.name}} 工业网络方案

## 1. 项目概述与建设目标

### 1.1 项目背景
- 客户名称：{{project.customer}}
- 项目名称：{{project.name}}
- 站点/厂区：{{project.site}}

### 1.2 建设目标
{{project.objective}}

### 1.3 项目范围与约束
{{project.scope}}
{{project.constraints}}

## 2. 现状网络与调研结论

### 2.1 调研概况
{{survey.timeline}}
{{survey.participants}}
{{survey.sources}}

### 2.2 现状网络概述
{{currentNetwork.topology}}
{{currentNetwork.layers}}
{{currentNetwork.boundaries}}

### 2.3 关键问题与发现
{{survey.findings}}
{{survey.concerns}}

## 3. 设计依据与方法说明

### 3.1 设计依据
{{design.principles}}

### 3.2 方法说明
基于 ISA95 的层级建模与系统协同分析方法，以及 IEC62443 的分区分域与边界控制方法，结合项目实际输入形成本方案。

## 4. 总体网络架构方案
{{design.targetArchitecture}}

## 5. ISA95 层级建模与系统协同结构
{{assets.systems}}
{{assets.roles}}
{{assets.locations}}

## 6. IEC62443 分区分域与安全边界设计
{{design.segmentation}}
{{security.boundaryRequirements}}
{{security.accessControl}}

## 7. 网络拓扑与通信路径说明
{{communications.flows}}
{{communications.accessPaths}}
{{communications.remoteMaintenance}}

## 8. IP 地址、VLAN 与子网规划
{{addressing.existingNetworks}}
{{addressing.reservedNetworks}}
{{addressing.vlans}}
{{design.addressPlan}}

## 9. 关键设备与部署建议
{{design.deployment}}

## 10. 实施步骤与迁移建议
{{design.implementation}}

## 11. 风险、假设与待确认项
{{openItems.designAssumptions}}
{{openItems.siteVerification}}
{{openItems.customerConfirmation}}
{{openItems.missingInformation}}

## 12. 结论与建议
请基于项目确认结果对方案中的待确认项进行闭合，并据此进入详细实施设计阶段。

## 附录

### 附录 A 资产清单摘要
{{assets.devices}}

### 附录 B IP/VLAN/子网清单
{{addressing.naming}}

### 附录 C 连接关系清单
{{currentNetwork.links}}

### 附录 D 术语与说明
- ISA95：企业控制系统集成层级建模方法
- IEC62443：工业自动化与控制系统安全系列标准
