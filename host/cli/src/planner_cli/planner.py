from dataclasses import dataclass, field

from planner_cli.inference import infer_models
from planner_cli.phrasing import chapter_phrasing
from planner_cli.prose import build_conclusion_paragraph, build_narrative
from planner_cli.models import EvidenceItem


@dataclass(slots=True)
class Chapter:
    title: str
    objective: str
    narrative: str = ""
    conclusion: str = ""
    input_sources: list[str] = field(default_factory=list)
    rule_topics: list[str] = field(default_factory=list)
    applicability: list[str] = field(default_factory=list)
    closure_conditions: list[str] = field(default_factory=list)
    confirmed_facts: list[EvidenceItem] = field(default_factory=list)
    recommendations: list[EvidenceItem] = field(default_factory=list)
    assumptions: list[EvidenceItem] = field(default_factory=list)
    pending_items: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class DocumentAudit:
    checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PlanBundle:
    project_name: str
    customer_name: str
    site_name: str
    objective: str
    scope: str
    chapters: list[Chapter] = field(default_factory=list)
    appendix_assets: list[EvidenceItem] = field(default_factory=list)
    appendix_networks: list[EvidenceItem] = field(default_factory=list)
    appendix_links: list[EvidenceItem] = field(default_factory=list)
    appendix_addressing: dict = field(default_factory=dict)
    appendix_communications: dict = field(default_factory=dict)
    appendix_assets_raw: dict = field(default_factory=dict)
    appendix_security: dict = field(default_factory=dict)
    appendix_design: dict = field(default_factory=dict)
    appendix_open_items: dict = field(default_factory=dict)
    appendix_delivery: dict = field(default_factory=dict)
    glossary: list[str] = field(default_factory=list)
    audit: DocumentAudit = field(default_factory=DocumentAudit)


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _items(values: list[str], source: str, evidence_type: str) -> list[EvidenceItem]:
    return [EvidenceItem(text=value, source=source, evidence_type=evidence_type) for value in values if value]


def _single(value: str, source: str, evidence_type: str) -> list[EvidenceItem]:
    return [EvidenceItem(text=value, source=source, evidence_type=evidence_type)] if value else []


def _collect_audit(chapters: list[Chapter]) -> DocumentAudit:
    checks = [
        "每章均输出了本章目标与输入来源。",
        "每章均输出了规则主题。",
        "事实、建议、假设、待确认项已分栏表达。",
        "风险、假设与待确认项已单列章节。",
    ]
    warnings: list[str] = []

    for chapter in chapters:
        if not chapter.narrative:
            warnings.append(f"章节《{chapter.title}》缺少叙述性摘要。")
        if not chapter.conclusion:
            warnings.append(f"章节《{chapter.title}》缺少结论段。")
            warnings.append(f"章节《{chapter.title}》缺少叙述性摘要。")
        if not chapter.rule_topics:
            warnings.append(f"章节《{chapter.title}》缺少规则主题标注。")
        if not chapter.input_sources:
            warnings.append(f"章节《{chapter.title}》缺少输入来源标注。")
        if not chapter.applicability:
            warnings.append(f"章节《{chapter.title}》缺少适用前提说明。")
        if not chapter.closure_conditions:
            warnings.append(f"章节《{chapter.title}》缺少闭环条件说明。")
        if not any([chapter.confirmed_facts, chapter.recommendations, chapter.assumptions, chapter.pending_items]):
            warnings.append(f"章节《{chapter.title}》缺少可交付内容。")

        for bucket_name, items in [
            ("已确认事实", chapter.confirmed_facts),
            ("规划建议", chapter.recommendations),
            ("假设项", chapter.assumptions),
            ("待确认项", chapter.pending_items),
        ]:
            for item in items:
                if not item.source:
                    warnings.append(f"章节《{chapter.title}》中的{bucket_name}缺少来源：{item.text}")

    return DocumentAudit(checks=checks, warnings=warnings)


def build_plan_bundle(payload: dict) -> PlanBundle:
    project = payload.get("project", {})
    survey = payload.get("survey", {})
    current_network = payload.get("currentNetwork", {})
    assets = payload.get("assets", {})
    communications = payload.get("communications", {})
    addressing = payload.get("addressing", {})
    security = payload.get("security", {})
    design = payload.get("design", {})
    open_items = payload.get("openItems", {})
    delivery = payload.get("delivery", {})
    inferred = infer_models(payload)

    assumptions = inferred.assumptions or _items(
        _as_list(open_items.get("designAssumptions")) + _as_list(open_items.get("missingInformation")),
        "openItems",
        "assumption",
    )
    pending_items = inferred.pending_items or _items(
        _as_list(open_items.get("siteVerification")) + _as_list(open_items.get("customerConfirmation")),
        "openItems",
        "pending",
    )

    rule_decisions = inferred.rule_decisions

    def rule_texts(*topics: str) -> list[str]:
        if not rule_decisions:
            return []
        resolved: list[str] = []
        for topic in topics:
            if rule_decisions.by_topic(topic):
                resolved.append(topic)
        return resolved

    def rule_conclusions(*topics: str) -> list[EvidenceItem]:
        if not rule_decisions:
            return []
        items: list[EvidenceItem] = []
        for topic in topics:
            decision = rule_decisions.by_topic(topic)
            if decision:
                items.extend(decision.conclusions)
        return items

    evidence_conflicts = inferred.evidence_audit.conflicts if inferred.evidence_audit else []

    def apply_phrasing(title: str, recommendations: list[EvidenceItem], pending: list[EvidenceItem]):
        return chapter_phrasing(title, recommendations, evidence_conflicts, pending)

    chapters = [
        Chapter(
            title="项目概述与建设目标",
            objective="说明项目背景、建设目标、范围和主要约束，不夸大项目边界。",
            input_sources=["project"],
            rule_topics=rule_texts("场景规则"),
            applicability=apply_phrasing("项目概述与建设目标", rule_conclusions("场景规则"), []).applicability,
            closure_conditions=apply_phrasing("项目概述与建设目标", rule_conclusions("场景规则"), []).closure_conditions,
            confirmed_facts=[
                *_single(f"项目名称：{project.get('name', '未提供')}", "project.name", "fact"),
                *_single(f"客户名称：{project.get('customer', '未提供')}", "project.customer", "fact"),
                *_single(f"建设地点：{project.get('site', '未提供')}", "project.site", "fact"),
                *_single(f"建设目标：{project.get('objective', '未提供')}", "project.objective", "fact"),
                *_single(f"建设范围：{project.get('scope', '未提供')}", "project.scope", "fact"),
                *_items([f"实施约束：{item}" for item in _as_list(project.get('constraints'))], "project.constraints", "fact"),
            ],
            recommendations=rule_conclusions("场景规则"),
        ),
        Chapter(
            title="现状网络与调研结论",
            objective="总结现网结构、已识别问题、调研发现与关键限制。",
            input_sources=["survey", "currentNetwork"],
            applicability=["当前章节建议基于现有输入成立，若现场信息变化需同步调整。"],
            closure_conditions=["闭环条件：当前章节未新增强制闭环项。"],
            rule_topics=rule_texts("场景规则"),
            confirmed_facts=[
                *_single(current_network.get("topology", "暂无现状拓扑描述。"), "currentNetwork.topology", "fact"),
                *_items([f"现网层级：{item}" for item in _as_list(current_network.get("layers"))], "currentNetwork.layers", "fact"),
                *_items([f"边界问题：{item}" for item in _as_list(current_network.get("boundaries"))], "currentNetwork.boundaries", "fact"),
                *_items([f"关键链路：{item}" for item in _as_list(current_network.get("links"))], "currentNetwork.links", "fact"),
                *_items([f"调研观察：{item}" for item in _as_list(survey.get("observations"))], "survey.observations", "fact"),
                *_items([f"调研发现：{item}" for item in _as_list(survey.get("findings"))], "survey.findings", "fact"),
                *_items([f"调研关注：{item}" for item in _as_list(survey.get("concerns"))], "survey.concerns", "fact"),
            ],
            pending_items=_items(_as_list(open_items.get("siteVerification")), "openItems.siteVerification", "pending"),
        ),
        Chapter(
            title="设计依据与方法说明",
            objective="说明方案形成依据、设计边界与定版控制原则。",
            input_sources=["project", "survey", "design", "security"],
            applicability=["当前章节建议基于现有输入成立，若现场信息变化需同步调整。"],
            closure_conditions=["闭环条件：当前章节未新增强制闭环项。"],
            rule_topics=rule_texts("场景规则", "分层规则", "区域规则", "通道规则", "地址规划规则", "部署规则", "实施规则"),
            confirmed_facts=[
                *_single("本方案基于项目输入资料、调研信息、现状网络信息与已知约束形成。", "project+survey+currentNetwork", "fact"),
                *_single("设计过程综合考虑网络分层承载、业务隔离、边界控制、运维可管可控及实施连续性要求。", "methodology-core", "fact"),
            ],
            recommendations=_items(
                ["后续若补充现场核实信息，应据此更新边界、地址与实施细节。"],
                "research-analysis-design-flow",
                "recommendation",
            ),
        ),
        Chapter(
            title="需求与约束分析",
            objective="归纳业务连续性、安全、运维、扩展与施工方面的关键约束，形成后续设计输入。",
            input_sources=["project", "survey", "security", "communications", "openItems"],
            applicability=["当前章节基于现有输入形成，若现场条件更新需同步调整约束分析结论。"],
            closure_conditions=["闭环条件：关键约束已纳入后续章节设计与实施控制。"],
            rule_topics=rule_texts("场景规则", "区域规则", "通道规则", "实施规则"),
            confirmed_facts=[
                *_items([f"业务连续性要求：{item}" for item in _as_list(project.get("constraints"))], "project.constraints", "fact"),
                *_items([f"调研约束：{item}" for item in _as_list(survey.get("concerns"))], "survey.concerns", "fact"),
                *_items([f"安全要求：{item}" for item in _as_list(security.get("boundaryRequirements"))], "security.boundaryRequirements", "fact"),
                *_items([f"运维要求：{item}" for item in _as_list(communications.get("remoteMaintenance"))], "communications.remoteMaintenance", "fact"),
            ],
            recommendations=[
                *rule_conclusions("场景规则", "区域规则", "通道规则", "实施规则"),
                *_items(["后续设计需同时满足连续运行、边界受控、运维审计和分阶段实施要求。"], "project+security+communications", "recommendation"),
            ],
            pending_items=pending_items,
        ),
        Chapter(
            title="技术选择与方案比较",
            objective="说明总体架构、边界组织、地址规划和运维接入的主要技术选择及收敛原因。",
            input_sources=["design", "security", "communications", "addressing"],
            applicability=["当前章节用于说明方案收敛逻辑，后续若输入变化需同步调整技术选择。"],
            closure_conditions=["闭环条件：最终技术路线已在后续总体方案、边界、地址与实施章节落实。"],
            rule_topics=rule_texts("分层规则", "区域规则", "通道规则", "地址规划规则", "部署规则"),
            confirmed_facts=[
                *_single(f"总体技术路线：{design.get('targetArchitecture', '暂无目标架构描述。')}", "design.targetArchitecture", "fact"),
                *_single(f"边界组织方式：{design.get('segmentation', '暂无边界组织描述。')}", "design.segmentation", "fact"),
                *_single(f"地址规划方式：{design.get('addressPlan', '暂无地址规划描述。')}", "design.addressPlan", "fact"),
                *_single(f"部署方式：{design.get('deployment', '暂无部署方式描述。')}", "design.deployment", "fact"),
            ],
            recommendations=[
                *rule_conclusions("分层规则", "区域规则", "通道规则", "地址规划规则", "部署规则"),
                *_items(["总体方案优先选择便于集中纳管、边界收口、后续扩展和分阶段实施的技术路线。"], "design+rule-topics", "recommendation"),
                *_items(["跨域访问、远程运维和高关键对象接入均按受控边界优先收敛，而不采用开放式互联。"], "security+communications", "recommendation"),
            ],
            pending_items=_items(_as_list(open_items.get("customerConfirmation")), "openItems.customerConfirmation", "pending"),
        ),
        Chapter(
            title="总体网络架构方案",
            objective="说明目标网络总体结构、核心组织方式和边界思路。",
            input_sources=["design", "currentNetwork", "security"],
            rule_topics=rule_texts("场景规则", "分层规则", "区域规则", "地址规划规则", "冗余规则", "边界对象规则"),
            applicability=apply_phrasing("总体网络架构方案", rule_conclusions("场景规则", "分层规则", "区域规则", "地址规划规则"), pending_items).applicability,
            closure_conditions=apply_phrasing("总体网络架构方案", rule_conclusions("场景规则", "分层规则", "区域规则", "地址规划规则"), pending_items).closure_conditions,
            recommendations=apply_phrasing("总体网络架构方案", [*rule_conclusions("场景规则", "分层规则", "区域规则", "地址规划规则", "冗余规则", "边界对象规则"), *_single(design.get("targetArchitecture", "暂无目标架构描述。"), "design.targetArchitecture", "recommendation"), *_items([f"设计原则：{item}" for item in _as_list(design.get("principles"))], "design.principles", "recommendation"), *_items([f"边界要求：{item}" for item in _as_list(security.get("boundaryRequirements"))], "security.boundaryRequirements", "recommendation"), *_items([item.text for item in inferred.boundary.conclusions], "inference.boundary", "recommendation")], pending_items).adjusted_recommendations,
            assumptions=assumptions + apply_phrasing("总体网络架构方案", [*rule_conclusions("场景规则", "分层规则", "区域规则", "地址规划规则", "冗余规则", "边界对象规则"), *_single(design.get("targetArchitecture", "暂无目标架构描述。"), "design.targetArchitecture", "recommendation")], pending_items).adjusted_assumptions,
            pending_items=pending_items + apply_phrasing("总体网络架构方案", [*rule_conclusions("场景规则", "分层规则", "区域规则", "地址规划规则", "冗余规则", "边界对象规则"), *_single(design.get("targetArchitecture", "暂无目标架构描述。"), "design.targetArchitecture", "recommendation")], pending_items).adjusted_pending,
        ),
        Chapter(
            title="ISA95 层级建模与系统协同结构",
            objective="说明层级划分、对象归属和跨层协同关系。",
            input_sources=["assets", "currentNetwork", "communications"],
            applicability=["当前章节建议基于现有输入成立，若现场信息变化需同步调整。"],
            closure_conditions=["闭环条件：当前章节未新增强制闭环项。"],
            rule_topics=rule_texts("分层规则"),
            confirmed_facts=[
                *_items([f"现网层级：{item.text}" for item in inferred.isa95.levels], "currentNetwork.layers", "fact"),
                *_items([f"系统对象：{item.text}" for item in inferred.isa95.systems], "assets.systems", "fact"),
                *_items([f"角色对象：{item.text}" for item in inferred.isa95.roles], "assets.roles", "fact"),
                *_items([f"部署位置：{item.text}" for item in inferred.isa95.placement], "assets.locations", "fact"),
            ],
            recommendations=[
                *rule_conclusions("分层规则"),
                *_items([item.text for item in inferred.isa95.conclusions], "inference.isa95", "recommendation"),
                *_items([f"跨层协同：{item.text}" for item in inferred.isa95.collaborations], "communications.flows", "recommendation"),
            ],
        ),
        Chapter(
            title="IEC62443 分区分域与安全边界设计",
            objective="说明 zone、conduit、边界与访问控制原则。",
            input_sources=["security", "communications", "design"],
            rule_topics=rule_texts("区域规则", "通道规则", "边界对象规则"),
            applicability=apply_phrasing("IEC62443 分区分域与安全边界设计", rule_conclusions("区域规则", "通道规则"), pending_items).applicability,
            closure_conditions=apply_phrasing("IEC62443 分区分域与安全边界设计", rule_conclusions("区域规则", "通道规则"), pending_items).closure_conditions,
            confirmed_facts=[
                *_items([f"安全目标：{item}" for item in _as_list(security.get("objectives"))], "security.objectives", "fact"),
                *_items([f"候选分区：{item.text}" for item in inferred.iec62443.zones], "security.zones", "fact"),
                *_items([f"边界要求：{item}" for item in _as_list(security.get("boundaryRequirements"))], "security.boundaryRequirements", "fact"),
                *_items([f"审计要求：{item}" for item in _as_list(security.get("auditRequirements"))], "security.auditRequirements", "fact"),
            ],
            recommendations=apply_phrasing("IEC62443 分区分域与安全边界设计", [*rule_conclusions("区域规则", "通道规则", "边界对象规则"), *_items([item.text for item in inferred.boundary.conclusions], "inference.boundary", "recommendation"), *_items([item.text for item in inferred.access_paths.conclusions], "inference.access_paths", "recommendation"), *_single(design.get("segmentation", "暂无分区分域建议。"), "design.segmentation", "recommendation"), *_items([item.text for item in inferred.iec62443.conclusions], "inference.iec62443", "recommendation"), *_items([f"边界控制原则：{item.text}" for item in inferred.iec62443.access_controls], "security.accessControl", "recommendation"), *_items([f"远程运维要求：{item.text}" for item in inferred.iec62443.remote_access], "communications.remoteMaintenance", "recommendation")], pending_items).adjusted_recommendations,
            assumptions=apply_phrasing("IEC62443 分区分域与安全边界设计", [*rule_conclusions("区域规则", "通道规则", "边界对象规则"), *_single(design.get("segmentation", "暂无分区分域建议。"), "design.segmentation", "recommendation")], pending_items).adjusted_assumptions,
            pending_items=pending_items + apply_phrasing("IEC62443 分区分域与安全边界设计", [*rule_conclusions("区域规则", "通道规则", "边界对象规则"), *_single(design.get("segmentation", "暂无分区分域建议。"), "design.segmentation", "recommendation")], pending_items).adjusted_pending,
        ),
        Chapter(
            title="网络拓扑与通信路径说明",
            objective="说明主要连接结构、关键通信路径和跨域访问路径。",
            input_sources=["currentNetwork", "communications"],
            rule_topics=rule_texts("通道规则"),
            applicability=apply_phrasing("网络拓扑与通信路径说明", rule_conclusions("通道规则"), []).applicability,
            closure_conditions=apply_phrasing("网络拓扑与通信路径说明", rule_conclusions("通道规则"), []).closure_conditions,
            confirmed_facts=[
                *_items([f"主要连接：{item}" for item in _as_list(current_network.get("links"))], "currentNetwork.links", "fact"),
                *_items([f"关键通信：{item}" for item in _as_list(communications.get("flows"))], "communications.flows", "fact"),
                *_items([f"协议线索：{item}" for item in _as_list(communications.get("protocols"))], "communications.protocols", "fact"),
                *_items([f"跨域访问路径：{item.text}" for item in inferred.access_paths.cross_zone_paths], "inference.access_paths", "fact"),
                *_items([f"第三方/外部路径：{item.text}" for item in inferred.access_paths.third_party_paths], "inference.access_paths", "fact"),
            ],
            recommendations=apply_phrasing("网络拓扑与通信路径说明", [
                *rule_conclusions("通道规则"),
                *_items([f"访问路径建议：{item}" for item in _as_list(communications.get("accessPaths"))], "communications.accessPaths", "recommendation"),
                *_items([item.text for item in inferred.access_paths.conclusions], "inference.access_paths", "recommendation"),
                *_items([f"访问控制收敛点：{item.text}" for item in inferred.access_paths.whitelist_candidates], "inference.access_paths", "recommendation"),
            ], inferred.access_paths.pending_items).adjusted_recommendations,
            assumptions=apply_phrasing("网络拓扑与通信路径说明", [
                *rule_conclusions("通道规则"),
                *_items([item.text for item in inferred.access_paths.conclusions], "inference.access_paths", "recommendation"),
            ], inferred.access_paths.pending_items).adjusted_assumptions,
            pending_items=inferred.access_paths.pending_items + apply_phrasing("网络拓扑与通信路径说明", [
                *rule_conclusions("通道规则"),
                *_items([item.text for item in inferred.access_paths.conclusions], "inference.access_paths", "recommendation"),
            ], inferred.access_paths.pending_items).adjusted_pending,
        ),
        Chapter(
            title="IP 地址、VLAN 与子网规划",
            objective="在信息充分时给出规划结果，信息不足时给规划原则与预留建议。",
            input_sources=["addressing", "design"],
            rule_topics=rule_texts("地址规划规则"),
            applicability=apply_phrasing("IP 地址、VLAN 与子网规划", rule_conclusions("地址规划规则"), []).applicability,
            closure_conditions=apply_phrasing("IP 地址、VLAN 与子网规划", rule_conclusions("地址规划规则"), []).closure_conditions,
            confirmed_facts=[
                *_items([f"现网地址现状：{item.text}" for item in inferred.addressing.existing], "addressing.existingNetworks", "fact"),
                *_items([f"地址约束：{item.text}" for item in inferred.addressing.constraints], "addressing.constraints", "fact"),
            ],
            recommendations=apply_phrasing("IP 地址、VLAN 与子网规划", [*rule_conclusions("地址规划规则"), *_single(design.get("addressPlan", "暂无地址规划建议。"), "design.addressPlan", "recommendation"), *_items([item.text for item in inferred.addressing.conclusions], "inference.addressing", "recommendation"), *_items([f"VLAN 组织建议：{item.text}" for item in inferred.addressing.vlan_strategy], "addressing.vlans", "recommendation"), *_items([f"命名建议：{item.text}" for item in inferred.addressing.naming], "addressing.naming", "recommendation"), *_items([f"预留策略：{item.text}" for item in inferred.addressing.reserve], "addressing.reservedNetworks", "recommendation")], []).adjusted_recommendations,
            assumptions=_items(
                ["若现网地址基础信息不足，本章仅输出规划原则与预留建议，不形成精确定稿地址表。"],
                "input-contract+design-decision-rules",
                "assumption",
            ) + apply_phrasing("IP 地址、VLAN 与子网规划", [*_single(design.get("addressPlan", "暂无地址规划建议。"), "design.addressPlan", "recommendation")], []).adjusted_assumptions,
            pending_items=apply_phrasing("IP 地址、VLAN 与子网规划", [*_single(design.get("addressPlan", "暂无地址规划建议。"), "design.addressPlan", "recommendation")], []).adjusted_pending,
        ),
        Chapter(
            title="关键设备与部署建议",
            objective="说明设备类别需求、部署原则与实施条件。",
            input_sources=["assets", "design"],
            rule_topics=rule_texts("部署规则", "冗余规则", "边界对象规则"),
            applicability=apply_phrasing("关键设备与部署建议", rule_conclusions("部署规则"), pending_items).applicability,
            closure_conditions=apply_phrasing("关键设备与部署建议", rule_conclusions("部署规则"), pending_items).closure_conditions,
            confirmed_facts=[
                *_items([f"现有设备对象：{item.text}" for item in inferred.deployment.asset_classes], "assets.devices", "fact"),
                *_items([f"部署位置：{item.text}" for item in inferred.deployment.placements], "assets.locations", "fact"),
                *_items([f"关键性说明：{item}" for item in _as_list(assets.get("criticality"))], "assets.criticality", "fact"),
            ],
            recommendations=[
                *rule_conclusions("部署规则", "冗余规则", "边界对象规则"),
                *_items([f"边界对象：{item.text}" for item in inferred.boundary.boundary_objects], "inference.boundary", "fact"),
                *_items([item.text for item in inferred.availability.recommendations], "inference.availability", "recommendation"),
                *_single(design.get("deployment", "暂无部署建议。"), "design.deployment", "recommendation"),
                *_items([item.text for item in inferred.deployment.conclusions], "inference.deployment", "recommendation"),
                *_items([f"关键对象：{item.text}" for item in inferred.deployment.critical_objects], "assets.criticality", "recommendation"),
            ],
            pending_items=_items(_as_list(open_items.get("siteVerification")), "openItems.siteVerification", "pending"),
        ),
        Chapter(
            title="通信与运维接入方案",
            objective="说明业务通信路径、跨域访问控制、远程运维方式及审计要求。",
            input_sources=["communications", "security", "openItems"],
            rule_topics=rule_texts("通道规则", "边界对象规则", "实施规则"),
            applicability=apply_phrasing("网络拓扑与通信路径说明", rule_conclusions("通道规则"), pending_items).applicability,
            closure_conditions=apply_phrasing("网络拓扑与通信路径说明", rule_conclusions("通道规则"), pending_items).closure_conditions,
            confirmed_facts=[
                *_items([f"业务通信：{item}" for item in _as_list(communications.get("flows"))], "communications.flows", "fact"),
                *_items([f"访问路径：{item}" for item in _as_list(communications.get("accessPaths"))], "communications.accessPaths", "fact"),
                *_items([f"远程运维：{item}" for item in _as_list(communications.get("remoteMaintenance"))], "communications.remoteMaintenance", "fact"),
                *_items([f"审计要求：{item}" for item in _as_list(security.get("auditRequirements"))], "security.auditRequirements", "fact"),
            ],
            recommendations=[
                *rule_conclusions("通道规则", "边界对象规则", "实施规则"),
                *_items([item.text for item in inferred.access_paths.conclusions], "inference.access_paths", "recommendation"),
                *_items([f"访问控制收敛点：{item.text}" for item in inferred.access_paths.whitelist_candidates], "inference.access_paths", "recommendation"),
                *_items([f"远程运维要求：{item}" for item in _as_list(communications.get("remoteMaintenance"))], "communications.remoteMaintenance", "recommendation"),
            ],
            pending_items=_items(_as_list(open_items.get("customerConfirmation")), "openItems.customerConfirmation", "pending"),
        ),
        Chapter(
            title="实施步骤与迁移建议",
            objective="强调前置条件、阶段划分、风险控制与迁移路径。",
            input_sources=["project", "design", "survey"],
            rule_topics=rule_texts("实施规则", "冗余规则"),
            applicability=apply_phrasing("实施步骤与迁移建议", rule_conclusions("实施规则"), pending_items).applicability,
            closure_conditions=apply_phrasing("实施步骤与迁移建议", rule_conclusions("实施规则"), pending_items).closure_conditions,
            confirmed_facts=[
                *_items([f"项目约束：{item}" for item in _as_list(project.get("constraints"))], "project.constraints", "fact"),
                *_items([f"实施关注：{item}" for item in _as_list(survey.get("concerns"))], "survey.concerns", "fact"),
            ],
            recommendations=[
                *rule_conclusions("实施规则", "冗余规则"),
                *_items([item.text for item in inferred.availability.recommendations], "inference.availability", "recommendation"),
                *_single(design.get("implementation", "暂无实施建议。"), "design.implementation", "recommendation"),
                *_items([item.text for item in inferred.deployment.conclusions if "分阶段" in item.text or "迁移" in item.text or "核实顺序" in item.text], "inference.deployment", "recommendation"),
            ],
            pending_items=_items(_as_list(open_items.get("customerConfirmation")), "openItems.customerConfirmation", "pending") + inferred.availability.pending_items,
        ),
        Chapter(
            title="风险、假设与待确认项",
            objective="单列风险、假设、待现场复核项和待客户确认项。",
            input_sources=["openItems", "survey", "project"],
            rule_topics=rule_texts("实施规则", "部署规则"),
            applicability=apply_phrasing("风险、假设与待确认项", rule_conclusions("实施规则", "部署规则"), pending_items).applicability,
            closure_conditions=apply_phrasing("风险、假设与待确认项", rule_conclusions("实施规则", "部署规则"), pending_items).closure_conditions,
            confirmed_facts=_items(
                [f"调研关注风险：{item}" for item in _as_list(survey.get("concerns"))],
                "survey.concerns",
                "fact",
            ),
            assumptions=assumptions,
            pending_items=pending_items,
        ),
        Chapter(
            title="结论与建议",
            objective="总结方案主结论与后续建议，保持建议语气与边界清晰。",
            input_sources=["design", "security", "openItems"],
            applicability=["当前章节建议基于现有输入成立，若现场信息变化需同步调整。"],
            closure_conditions=["闭环条件：当前章节未新增强制闭环项。"],
            rule_topics=rule_texts("场景规则", "分层规则", "区域规则", "通道规则", "地址规划规则", "部署规则", "实施规则"),
            recommendations=[
                *_single(design.get("targetArchitecture", "暂无目标架构描述。"), "design.targetArchitecture", "recommendation"),
                *_single(design.get("implementation", "暂无实施建议。"), "design.implementation", "recommendation"),
                *_items(["建议在完成现场复核与客户确认后，再固化精细地址、设备部署、访问白名单与实施窗口。"], "openItems+design-decision-rules", "recommendation"),
            ],
            pending_items=pending_items,
        ),
    ]

    chapters = [
        Chapter(
            title=chapter.title,
            objective=chapter.objective,
            narrative=build_narrative(chapter.title, chapter.confirmed_facts, chapter.recommendations, chapter.pending_items, chapter.assumptions),
            conclusion=build_conclusion_paragraph(chapter.title, chapter.confirmed_facts, chapter.recommendations, chapter.assumptions, chapter.pending_items),
            input_sources=chapter.input_sources,
            rule_topics=chapter.rule_topics,
            applicability=chapter.applicability,
            closure_conditions=chapter.closure_conditions,
            confirmed_facts=chapter.confirmed_facts,
            recommendations=chapter.recommendations,
            assumptions=chapter.assumptions,
            pending_items=chapter.pending_items,
        )
        for chapter in chapters
    ]

    audit = _collect_audit(chapters)
    audit.warnings.extend(inferred.audit_notes)
    if inferred.evidence_audit:
        audit.warnings.extend(item.resolution for item in inferred.evidence_audit.conflicts)
        audit.warnings.extend(inferred.evidence_audit.downgrade_notes)

    glossary = [
        "DMZ：用于受控隔离、转发与安全检查的边界区域。",
        "VLAN：基于逻辑划分的二层广播域。",
        "白名单：仅允许已核定对象、协议、端口和方向通过的访问控制方式。",
    ]

    return PlanBundle(
        project_name=project.get("name", "unnamed-project"),
        customer_name=project.get("customer", "未提供"),
        site_name=project.get("site", "未提供"),
        objective=project.get("objective", "未提供"),
        scope=project.get("scope", "未提供"),
        chapters=chapters,
        appendix_assets=_items(_as_list(assets.get("systems")) + _as_list(assets.get("devices")), "assets", "fact"),
        appendix_networks=_items(_as_list(addressing.get("existingNetworks")) + _as_list(addressing.get("vlans")) + _as_list(addressing.get("reservedNetworks")) + _as_list(addressing.get("naming")), "addressing", "fact"),
        appendix_links=_items(_as_list(current_network.get("links")) + _as_list(communications.get("flows")) + _as_list(communications.get("accessPaths")), "currentNetwork+communications", "fact"),
        appendix_addressing=addressing,
        appendix_communications=communications,
        appendix_assets_raw=assets,
        appendix_security=security,
        appendix_design=design,
        appendix_open_items=open_items,
        appendix_delivery=delivery,
        glossary=glossary,
        audit=audit,
    )
