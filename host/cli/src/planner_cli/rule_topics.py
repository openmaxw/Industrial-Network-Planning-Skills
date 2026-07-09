from dataclasses import dataclass, field

from planner_cli.models import EvidenceItem


@dataclass(slots=True)
class RuleDecision:
    topic: str
    responsibility: str
    inputs: list[str] = field(default_factory=list)
    impacts: list[str] = field(default_factory=list)
    chapter_targets: list[str] = field(default_factory=list)
    conclusions: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class RuleDecisionBundle:
    decisions: list[RuleDecision] = field(default_factory=list)

    def by_topic(self, topic: str) -> RuleDecision | None:
        for decision in self.decisions:
            if decision.topic == topic:
                return decision
        return None



def derive_rule_decisions(payload: dict) -> RuleDecisionBundle:
    project = payload.get("project", {})
    current_network = payload.get("currentNetwork", {})
    assets = payload.get("assets", {})
    communications = payload.get("communications", {})
    addressing = payload.get("addressing", {})
    security = payload.get("security", {})
    design = payload.get("design", {})
    survey = payload.get("survey", {})

    decisions = [
        RuleDecision(
            topic="场景规则",
            responsibility="确定项目的总体规划场景与设计主线。",
            inputs=["project.objective", "project.scope", "project.constraints"],
            impacts=["总体架构定位", "设计原则选择", "实施边界"],
            chapter_targets=["项目概述与建设目标", "设计依据与方法说明", "总体网络架构方案"],
            conclusions=[
                EvidenceItem(
                    text="项目目标聚焦于分层分区优化、远程运维边界梳理与地址规划，适合采用结构治理与安全边界并行推进的总体策略。",
                    source="project.objective+project.scope+project.constraints",
                    evidence_type="recommendation",
                )
            ],
        ),
        RuleDecision(
            topic="分层规则",
            responsibility="确定核心、汇聚、接入及对象协同层级。",
            inputs=["currentNetwork.layers", "assets.systems", "communications.flows"],
            impacts=["网络层级结构", "ISA95 协同结构", "总体架构组织"],
            chapter_targets=["总体网络架构方案", "ISA95 层级建模与系统协同结构"],
            conclusions=[
                EvidenceItem(
                    text="依据现有厂级核心、车间汇聚、产线接入结构及系统协同流，建议延续三级层级并强化层间职责划分。",
                    source="currentNetwork.layers+communications.flows+assets.systems",
                    evidence_type="recommendation",
                )
            ],
        ),
        RuleDecision(
            topic="区域规则",
            responsibility="确定对象归属的区域或安全域。",
            inputs=["security.zones", "security.objectives", "communications.flows"],
            impacts=["zone 划分", "区域职责", "边界组织"],
            chapter_targets=["总体网络架构方案", "IEC62443 分区分域与安全边界设计"],
            conclusions=[
                EvidenceItem(
                    text="建议围绕办公访问、运维接入、受控交换与控制相关边界建立清晰区域框架。",
                    source="security.zones+security.objectives+communications.flows",
                    evidence_type="recommendation",
                )
            ],
        ),
        RuleDecision(
            topic="通道规则",
            responsibility="确定跨区域访问如何受控收敛。",
            inputs=["communications.accessPaths", "communications.remoteMaintenance", "security.boundaryRequirements"],
            impacts=["conduit 设计", "跨域访问路径", "远程维护收口"],
            chapter_targets=["IEC62443 分区分域与安全边界设计", "网络拓扑与通信路径说明"],
            conclusions=[
                EvidenceItem(
                    text="办公到生产、运维到控制及第三方远程维护访问均应通过受控路径与边界控制点收敛。",
                    source="communications.accessPaths+communications.remoteMaintenance+security.boundaryRequirements",
                    evidence_type="recommendation",
                ),
                EvidenceItem(
                    text="跨域访问路径宜在完成必要性梳理后按对象、方向、协议和时间窗进行白名单化控制。",
                    source="communications.accessPaths+communications.flows+security.accessControl",
                    evidence_type="recommendation",
                )
            ],
        ),
        RuleDecision(
            topic="地址规划规则",
            responsibility="确定地址边界、VLAN 与扩展策略。",
            inputs=["addressing.existingNetworks", "addressing.vlans", "addressing.reservedNetworks", "design.addressPlan"],
            impacts=["IP 规划", "VLAN 划分", "地址预留"],
            chapter_targets=["IP 地址、VLAN 与子网规划", "总体网络架构方案"],
            conclusions=[
                EvidenceItem(
                    text="在现网存在地址复用的前提下，应优先保证边界清晰、VLAN 分段明确，并为新增产线预留地址空间。",
                    source="addressing.existingNetworks+addressing.vlans+addressing.reservedNetworks+design.addressPlan",
                    evidence_type="recommendation",
                )
            ],
        ),
        RuleDecision(
            topic="冗余规则",
            responsibility="确定关键链路、关键边界与关键节点的高可用建议边界。",
            inputs=["currentNetwork.resilience", "project.constraints", "survey.concerns", "openItems.customerConfirmation"],
            impacts=["冗余建议", "高可用边界", "实施节奏"],
            chapter_targets=["总体网络架构方案", "关键设备与部署建议", "实施步骤与迁移建议"],
            conclusions=[
                EvidenceItem(
                    text="在可靠性目标尚未量化前，宜对关键链路与关键边界控制节点提出原则性冗余建议，而不直接承诺具体冗余架构。",
                    source="currentNetwork.resilience+project.constraints+survey.concerns+openItems.customerConfirmation",
                    evidence_type="recommendation",
                )
            ],
        ),
        RuleDecision(
            topic="部署规则",
            responsibility="确定关键设备部署位置与实施条件。",
            inputs=["assets.locations", "assets.devices", "design.deployment", "openItems.siteVerification"],
            impacts=["部署位置", "设备能力边界", "现场复核要求"],
            chapter_targets=["关键设备与部署建议", "实施步骤与迁移建议"],
            conclusions=[
                EvidenceItem(
                    text="关键设备部署建议应以厂级机房、车间弱电间和产线控制柜为主，同时保留安全边界设备位置待现场复核。",
                    source="assets.locations+assets.devices+design.deployment+openItems.siteVerification",
                    evidence_type="recommendation",
                )
            ],
        ),
        RuleDecision(
            topic="实施规则",
            responsibility="确定阶段划分、迁移路径与风险控制重点。",
            inputs=["project.constraints", "survey.concerns", "design.implementation"],
            impacts=["阶段实施", "迁移控制", "风险提示"],
            chapter_targets=["实施步骤与迁移建议", "风险、假设与待确认项"],
            conclusions=[
                EvidenceItem(
                    text="结合分阶段迁移和有限停机窗口约束，实施路径应强调先边界治理、后结构优化、再地址规范化。",
                    source="project.constraints+survey.concerns+design.implementation",
                    evidence_type="recommendation",
                )
            ],
        ),
    ]

    return RuleDecisionBundle(decisions=decisions)
