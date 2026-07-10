from dataclasses import dataclass, field

from planner_cli.evidence_policy import EvidenceAudit, detect_conflicts
from planner_cli.models import EvidenceItem
from planner_cli.rule_topics import RuleDecisionBundle, derive_rule_decisions


@dataclass(slots=True)
class ISA95Model:
    levels: list[EvidenceItem] = field(default_factory=list)
    systems: list[EvidenceItem] = field(default_factory=list)
    roles: list[EvidenceItem] = field(default_factory=list)
    collaborations: list[EvidenceItem] = field(default_factory=list)
    placement: list[EvidenceItem] = field(default_factory=list)
    conclusions: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class BoundaryModel:
    boundary_issues: list[EvidenceItem] = field(default_factory=list)
    boundary_objects: list[EvidenceItem] = field(default_factory=list)
    remote_objects: list[EvidenceItem] = field(default_factory=list)
    conclusions: list[EvidenceItem] = field(default_factory=list)
    pending_items: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class IEC62443Model:
    zones: list[EvidenceItem] = field(default_factory=list)
    conduits: list[EvidenceItem] = field(default_factory=list)
    boundaries: list[EvidenceItem] = field(default_factory=list)
    access_controls: list[EvidenceItem] = field(default_factory=list)
    remote_access: list[EvidenceItem] = field(default_factory=list)
    conclusions: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class AccessPathModel:
    external_paths: list[EvidenceItem] = field(default_factory=list)
    cross_zone_paths: list[EvidenceItem] = field(default_factory=list)
    third_party_paths: list[EvidenceItem] = field(default_factory=list)
    whitelist_candidates: list[EvidenceItem] = field(default_factory=list)
    conclusions: list[EvidenceItem] = field(default_factory=list)
    pending_items: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class AddressingModel:
    existing: list[EvidenceItem] = field(default_factory=list)
    vlan_strategy: list[EvidenceItem] = field(default_factory=list)
    naming: list[EvidenceItem] = field(default_factory=list)
    reserve: list[EvidenceItem] = field(default_factory=list)
    constraints: list[EvidenceItem] = field(default_factory=list)
    conclusions: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class AvailabilityModel:
    current_state: list[EvidenceItem] = field(default_factory=list)
    constraints: list[EvidenceItem] = field(default_factory=list)
    recommendations: list[EvidenceItem] = field(default_factory=list)
    pending_items: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class DeploymentModel:
    asset_classes: list[EvidenceItem] = field(default_factory=list)
    placements: list[EvidenceItem] = field(default_factory=list)
    critical_objects: list[EvidenceItem] = field(default_factory=list)
    implementation_steps: list[EvidenceItem] = field(default_factory=list)
    migration_constraints: list[EvidenceItem] = field(default_factory=list)
    conclusions: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class InferenceBundle:
    isa95: ISA95Model
    boundary: BoundaryModel
    iec62443: IEC62443Model
    access_paths: AccessPathModel
    addressing: AddressingModel
    availability: AvailabilityModel
    deployment: DeploymentModel
    design_principles: list[EvidenceItem] = field(default_factory=list)
    architecture: list[EvidenceItem] = field(default_factory=list)
    assumptions: list[EvidenceItem] = field(default_factory=list)
    pending_items: list[EvidenceItem] = field(default_factory=list)
    audit_notes: list[str] = field(default_factory=list)
    rule_decisions: RuleDecisionBundle | None = None
    evidence_audit: EvidenceAudit | None = None





def _looks_structured_object(value: object) -> bool:
    if isinstance(value, (dict, list, tuple)):
        return True
    text = str(value).strip()
    if not text:
        return False
    if (text.startswith('{') and text.endswith('}')) or (text.startswith('[') and text.endswith(']')):
        return True
    return any(token in text for token in ["{'id':", '{"id":', "'source':", '"source":', "'target':", '"target":', "'members':", '"members":'])

def _list_items(values: object, source: str, evidence_type: str) -> list[EvidenceItem]:
    if isinstance(values, list):
        return [EvidenceItem(text=str(item), source=source, evidence_type=evidence_type) for item in values if str(item).strip() and not _looks_structured_object(item)]
    if isinstance(values, str) and values.strip():
        return [EvidenceItem(text=values, source=source, evidence_type=evidence_type)]
    return []



def infer_models(payload: dict) -> InferenceBundle:
    project = payload.get("project", {})
    current_network = payload.get("currentNetwork", {})
    assets = payload.get("assets", {})
    communications = payload.get("communications", {})
    addressing = payload.get("addressing", {})
    security = payload.get("security", {})
    design = payload.get("design", {})
    open_items = payload.get("openItems", {})
    survey = payload.get("survey", {})

    isa95 = ISA95Model(
        levels=_list_items(current_network.get("layers"), "currentNetwork.layers", "fact"),
        systems=_list_items(assets.get("systems"), "assets.systems", "fact"),
        roles=_list_items(assets.get("roles"), "assets.roles", "fact"),
        collaborations=_list_items(communications.get("flows"), "communications.flows", "fact"),
        placement=_list_items(assets.get("locations"), "assets.locations", "fact"),
        conclusions=[
            EvidenceItem(
                text="建议依据厂级、车间级、产线级结构及系统协同关系组织 ISA95 层级建模。",
                source="currentNetwork.layers+assets.systems+communications.flows",
                evidence_type="recommendation",
            )
        ],
    )

    boundary_issues = _list_items(current_network.get("boundaries"), "currentNetwork.boundaries", "fact")
    boundary_objects = [
        item for item in _list_items(assets.get("devices"), "assets.devices", "fact")
        if any(keyword in item.text for keyword in ["防火墙", "网关", "边界", "远程接入"])
    ]
    remote_objects = [
        item for item in _list_items(assets.get("systems"), "assets.systems", "fact") + _list_items(assets.get("roles"), "assets.roles", "fact")
        if any(keyword in item.text for keyword in ["远程", "运维", "维护"])
    ]
    boundary_pending = [
        item for item in _list_items(open_items.get("siteVerification"), "openItems.siteVerification", "pending") + _list_items(open_items.get("customerConfirmation"), "openItems.customerConfirmation", "pending")
        if any(keyword in item.text for keyword in ["边界", "防火墙", "网关", "访问", "白名单"])
    ]
    boundary_conclusions: list[EvidenceItem] = []
    if boundary_issues or boundary_objects or remote_objects:
        boundary_conclusions.append(
            EvidenceItem(
                text="对于边界对象复杂或远程维护对象参与度较高的场景，宜优先识别边界控制对象、统一边界收口位置，并明确跨域访问职责后，再细化部署与策略。",
                source="currentNetwork.boundaries+assets.devices+assets.systems+assets.roles+communications.remoteMaintenance",
                evidence_type="recommendation",
            )
        )
    boundary = BoundaryModel(
        boundary_issues=boundary_issues,
        boundary_objects=boundary_objects,
        remote_objects=remote_objects,
        conclusions=boundary_conclusions,
        pending_items=boundary_pending,
    )

    iec62443 = IEC62443Model(
        zones=_list_items(security.get("zones"), "security.zones", "fact"),
        conduits=_list_items(communications.get("accessPaths"), "communications.accessPaths", "recommendation"),
        boundaries=_list_items(security.get("boundaryRequirements"), "security.boundaryRequirements", "recommendation"),
        access_controls=_list_items(security.get("accessControl"), "security.accessControl", "recommendation"),
        remote_access=_list_items(communications.get("remoteMaintenance"), "communications.remoteMaintenance", "recommendation"),
        conclusions=[
            EvidenceItem(
                text="建议以办公访问区、运维接入区、受控交换区和控制相关边界区构成主要安全域，并通过受控通道收敛跨域访问。",
                source="security.zones+design.segmentation+communications.accessPaths",
                evidence_type="recommendation",
            )
        ],
    )

    access_path_facts = _list_items(communications.get("accessPaths"), "communications.accessPaths", "fact")
    external_paths = [
        item for item in access_path_facts
        if any(keyword in item.text for keyword in ["外部", "远程", "第三方", "办公到生产", "办公到控制"])
    ]
    cross_zone_paths = [
        item for item in access_path_facts + _list_items(communications.get("flows"), "communications.flows", "fact")
        if any(keyword in item.text for keyword in ["到控制", "跨域", "办公到生产", "办公到控制", "协同"])
    ]
    third_party_paths = [
        item for item in _list_items(communications.get("remoteMaintenance"), "communications.remoteMaintenance", "fact") + access_path_facts
        if any(keyword in item.text for keyword in ["第三方", "远程维护", "远维"])
    ]
    whitelist_candidates = [
        item for item in _list_items(security.get("accessControl"), "security.accessControl", "recommendation") + _list_items(open_items.get("customerConfirmation"), "openItems.customerConfirmation", "pending")
        if any(keyword in item.text for keyword in ["最小权限", "白名单", "时间窗", "账号", "访问粒度"])
    ]
    access_path_pending = [
        item for item in _list_items(open_items.get("customerConfirmation"), "openItems.customerConfirmation", "pending") + _list_items(open_items.get("siteVerification"), "openItems.siteVerification", "pending")
        if any(keyword in item.text for keyword in ["访问", "白名单", "时间窗", "网关", "账号"])
    ]
    access_path_conclusions: list[EvidenceItem] = []
    if external_paths or third_party_paths:
        access_path_conclusions.append(
            EvidenceItem(
                text="涉及外部或第三方进入控制相关区域的访问，宜统一收敛到受控入口，并以身份鉴别、时间窗、最小权限和会话审计作为基础控制。",
                source="communications.accessPaths+communications.remoteMaintenance+security.accessControl+security.auditRequirements",
                evidence_type="recommendation",
            )
        )
    if cross_zone_paths:
        access_path_conclusions.append(
            EvidenceItem(
                text="对办公到生产、运维到控制及业务协同跨域路径，宜先梳理必要通信清单，再以白名单化方式固化允许方向、对象和协议范围。",
                source="communications.accessPaths+communications.flows+security.accessControl",
                evidence_type="recommendation",
            )
        )
    access_paths = AccessPathModel(
        external_paths=external_paths,
        cross_zone_paths=cross_zone_paths,
        third_party_paths=third_party_paths,
        whitelist_candidates=whitelist_candidates,
        conclusions=access_path_conclusions,
        pending_items=access_path_pending,
    )

    addressing_model = AddressingModel(
        existing=_list_items(addressing.get("existingNetworks"), "addressing.existingNetworks", "fact"),
        vlan_strategy=_list_items(addressing.get("vlans"), "addressing.vlans", "recommendation"),
        naming=_list_items(addressing.get("naming"), "addressing.naming", "recommendation"),
        reserve=_list_items(addressing.get("reservedNetworks"), "addressing.reservedNetworks", "recommendation"),
        constraints=_list_items(addressing.get("constraints"), "addressing.constraints", "fact"),
        conclusions=[
            EvidenceItem(
                text="建议按区域、安全边界与用途组织网段与 VLAN，并为后续新增产线预留地址空间。",
                source="addressing.vlans+addressing.reservedNetworks+design.addressPlan",
                evidence_type="recommendation",
            )
        ],
    )

    availability_current = _list_items([current_network.get("resilience")] if current_network.get("resilience") else [], "currentNetwork.resilience", "fact")
    availability_constraints = _list_items(project.get("constraints"), "project.constraints", "fact") + _list_items(survey.get("concerns"), "survey.concerns", "fact")
    availability_pending = [
        item for item in _list_items(open_items.get("customerConfirmation"), "openItems.customerConfirmation", "pending")
        if "冗余" in item.text or "可靠" in item.text
    ]
    availability_recommendations: list[EvidenceItem] = []
    if availability_constraints:
        availability_recommendations.append(
            EvidenceItem(
                text="在可靠性目标未量化前，宜先对关键链路、关键边界控制节点和关键业务路径提出原则性冗余建议，不宜直接承诺具体冗余架构。",
                source="project.constraints+survey.concerns+design-decision-rules",
                evidence_type="recommendation",
            )
        )
        availability_recommendations.append(
            EvidenceItem(
                text="若停机容忍度低但目标等级仍未确认，实施节奏宜先完成目标量化、关键对象分级和物理路径核实，再进入设备与链路级冗余落地。",
                source="project.constraints+openItems.customerConfirmation+openItems.siteVerification",
                evidence_type="recommendation",
            )
        )
    if current_network.get("resilience"):
        availability_recommendations.append(
            EvidenceItem(
                text="建议优先统一关键链路和关键边界控制路径的高可用目标，再分阶段细化设备级与链路级冗余实施。",
                source="currentNetwork.resilience+project.constraints+survey.concerns",
                evidence_type="recommendation",
            )
        )
    availability = AvailabilityModel(
        current_state=availability_current,
        constraints=availability_constraints,
        recommendations=availability_recommendations,
        pending_items=availability_pending,
    )

    deployment = DeploymentModel(
        asset_classes=_list_items(assets.get("devices"), "assets.devices", "fact"),
        placements=_list_items(assets.get("locations"), "assets.locations", "fact"),
        critical_objects=_list_items(assets.get("criticality"), "assets.criticality", "fact"),
        implementation_steps=_list_items([design.get("implementation")] if design.get("implementation") else [], "design.implementation", "recommendation"),
        migration_constraints=_list_items(project.get("constraints"), "project.constraints", "fact") + _list_items(survey.get("concerns"), "survey.concerns", "fact"),
        conclusions=[
            EvidenceItem(
                text="建议围绕边界治理、结构优化、地址规范化分阶段实施，并结合停机窗口控制迁移风险。",
                source="design.implementation+project.constraints+survey.concerns",
                evidence_type="recommendation",
            ),
            EvidenceItem(
                text="对部署位置、边界设备能力或关键链路物理路径尚未核实的对象，现阶段宜输出部署原则与核实顺序，不宜输出落位定稿结论。",
                source="openItems.siteVerification+openItems.missingInformation+assets.criticality",
                evidence_type="recommendation",
            )
        ],
    )

    assumptions = _list_items(open_items.get("designAssumptions"), "openItems.designAssumptions", "assumption") + _list_items(open_items.get("missingInformation"), "openItems.missingInformation", "assumption")
    pending_items = _list_items(open_items.get("siteVerification"), "openItems.siteVerification", "pending") + _list_items(open_items.get("customerConfirmation"), "openItems.customerConfirmation", "pending")

    audit_notes = []
    if not isa95.levels:
        audit_notes.append("ISA95 层级模型缺少明确层级输入，只能保持原则级表达。")
    if not iec62443.zones:
        audit_notes.append("IEC62443 模型缺少明确 zone 输入，只能保持边界原则表达。")
    if not boundary_conclusions:
        audit_notes.append("边界对象模型缺少复杂边界线索，只能保持通用边界表达。")
    if not addressing_model.existing:
        audit_notes.append("地址模型缺少现网地址事实，不能输出精确地址定稿。")
    if not deployment.migration_constraints:
        audit_notes.append("实施模型缺少迁移约束输入，实施建议需要更多待确认项支撑。")
    if not availability_current:
        audit_notes.append("高可用模型缺少现网韧性输入，只能输出原则性冗余建议。")
    if not availability_pending:
        audit_notes.append("高可用模型缺少明确冗余确认项，相关建议需保持边界性表达。")

    rule_decisions = derive_rule_decisions(payload)
    evidence_audit = detect_conflicts(payload)

    return InferenceBundle(
        isa95=isa95,
        boundary=boundary,
        iec62443=iec62443,
        access_paths=access_paths,
        addressing=addressing_model,
        availability=availability,
        deployment=deployment,
        design_principles=_list_items(design.get("principles"), "design.principles", "recommendation"),
        architecture=_list_items([design.get("targetArchitecture")] if design.get("targetArchitecture") else [], "design.targetArchitecture", "recommendation"),
        assumptions=assumptions,
        pending_items=pending_items,
        audit_notes=audit_notes,
        rule_decisions=rule_decisions,
        evidence_audit=evidence_audit,
    )
