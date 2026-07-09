from dataclasses import dataclass, field

from planner_cli.models import EvidenceItem


PRIORITY_BY_SOURCE_PREFIX = {
    "project": 1,
    "survey": 1,
    "currentNetwork": 1,
    "assets": 1,
    "communications": 1,
    "addressing": 1,
    "security": 1,
    "design": 2,
    "inference": 3,
    "methodology-core": 3,
    "research-analysis-design-flow": 3,
    "openItems": 1,
}


@dataclass(slots=True)
class ConflictRecord:
    domain: str
    high_priority: EvidenceItem
    low_priority: EvidenceItem
    resolution: str
    downgrade_to: str = "recommendation"
    affected_terms: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceAudit:
    conflicts: list[ConflictRecord] = field(default_factory=list)
    downgrade_notes: list[str] = field(default_factory=list)



def _priority(source: str) -> int:
    for prefix, value in PRIORITY_BY_SOURCE_PREFIX.items():
        if source.startswith(prefix):
            return value
    return 99



def detect_conflicts(payload: dict) -> EvidenceAudit:
    audit = EvidenceAudit()

    security = payload.get("security", {})
    design = payload.get("design", {})
    open_items = payload.get("openItems", {})
    current_network = payload.get("currentNetwork", {})
    addressing = payload.get("addressing", {})
    communications = payload.get("communications", {})
    assets = payload.get("assets", {})
    project = payload.get("project", {})

    if security.get("zones") and design.get("segmentation"):
        zone_text = " ".join(str(x) for x in security.get("zones", []))
        segmentation = str(design.get("segmentation", ""))
        if "DMZ" not in zone_text and "DMZ" in segmentation:
            high = EvidenceItem(text=zone_text, source="security.zones", evidence_type="fact")
            low = EvidenceItem(text=segmentation, source="design.segmentation", evidence_type="recommendation")
            audit.conflicts.append(
                ConflictRecord(
                    domain="security-zones",
                    high_priority=high,
                    low_priority=low,
                    resolution="设计分区结论与已确认 zone 不一致，分区内容应降级为建议并保留待确认。",
                    downgrade_to="pending",
                    affected_terms=["DMZ", "分区", "区域"],
                )
            )

    if addressing.get("existingNetworks") and design.get("addressPlan"):
        existing = " ".join(str(x) for x in addressing.get("existingNetworks", []))
        plan = str(design.get("addressPlan", ""))
        if "复用" in existing and ("定稿" in plan or "精确" in plan):
            high = EvidenceItem(text=existing, source="addressing.existingNetworks", evidence_type="fact")
            low = EvidenceItem(text=plan, source="design.addressPlan", evidence_type="recommendation")
            audit.conflicts.append(
                ConflictRecord(
                    domain="addressing-precision",
                    high_priority=high,
                    low_priority=low,
                    resolution="现网地址存在复用，地址设计不能保持精确定稿表达，应降级为规划原则。",
                    downgrade_to="assumption",
                    affected_terms=["定稿", "精确", "地址规划"],
                )
            )

    if current_network.get("boundaries") and design.get("targetArchitecture"):
        boundaries = " ".join(str(x) for x in current_network.get("boundaries", []))
        architecture = str(design.get("targetArchitecture", ""))
        if "不清晰" in boundaries and "已" in architecture and "边界" in architecture:
            high = EvidenceItem(text=boundaries, source="currentNetwork.boundaries", evidence_type="fact")
            low = EvidenceItem(text=architecture, source="design.targetArchitecture", evidence_type="recommendation")
            audit.conflicts.append(
                ConflictRecord(
                    domain="boundary-certainty",
                    high_priority=high,
                    low_priority=low,
                    resolution="现状边界仍不清晰，目标架构不得表述为已落地边界结果。",
                    downgrade_to="recommendation",
                    affected_terms=["已", "落地", "完成", "边界"],
                )
            )

    remote_requirements = " ".join(str(x) for x in communications.get("remoteMaintenance", []))
    segmentation = str(design.get("segmentation", ""))
    if remote_requirements and segmentation:
        if ("DMZ" in remote_requirements or "统一" in remote_requirements) and ("DMZ" not in segmentation):
            high = EvidenceItem(text=remote_requirements, source="communications.remoteMaintenance", evidence_type="fact")
            low = EvidenceItem(text=segmentation, source="design.segmentation", evidence_type="recommendation")
            audit.conflicts.append(
                ConflictRecord(
                    domain="remote-maintenance-boundary",
                    high_priority=high,
                    low_priority=low,
                    resolution="远程维护已提出统一收敛或 DMZ 要求，分区建议不得忽略该受控边界。",
                    downgrade_to="pending",
                    affected_terms=["远程", "维护", "边界", "收敛", "DMZ"],
                )
            )

    deployment = str(design.get("deployment", ""))
    criticality = " ".join(str(x) for x in assets.get("criticality", []))
    site_verification = " ".join(str(x) for x in open_items.get("siteVerification", []))
    if deployment and (criticality or site_verification):
        if ("位置" in criticality or "位置" in site_verification) and ("已" in deployment or "完成" in deployment or "确定" in deployment):
            high = EvidenceItem(
                text=criticality or site_verification,
                source="assets.criticality/openItems.siteVerification",
                evidence_type="fact",
            )
            low = EvidenceItem(text=deployment, source="design.deployment", evidence_type="recommendation")
            audit.conflicts.append(
                ConflictRecord(
                    domain="deployment-certainty",
                    high_priority=high,
                    low_priority=low,
                    resolution="关键设备部署位置仍受现场复核约束，部署结论不得按已确定或已完成表述输出。",
                    downgrade_to="assumption",
                    affected_terms=["部署", "位置", "已", "完成", "确定"],
                )
            )

    resilience = str(current_network.get("resilience", ""))
    constraints = " ".join(str(x) for x in project.get("constraints", []))
    missing_information = " ".join(str(x) for x in open_items.get("missingInformation", []))
    implementation = str(design.get("implementation", ""))
    if implementation and (resilience or constraints or missing_information):
        if (("不明" in resilience) or ("缺少统一目标" in resilience) or ("待进一步量化" in constraints) or ("未量化" in missing_information)) and ("分阶段" not in implementation and "明确" not in implementation):
            high = EvidenceItem(
                text="；".join(item for item in [resilience, constraints, missing_information] if item),
                source="currentNetwork.resilience/project.constraints/openItems.missingInformation",
                evidence_type="fact",
            )
            low = EvidenceItem(text=implementation, source="design.implementation", evidence_type="recommendation")
            audit.conflicts.append(
                ConflictRecord(
                    domain="availability-target-uncertain",
                    high_priority=high,
                    low_priority=low,
                    resolution="可靠性目标或现网冗余现状尚未闭环时，实施建议应保留为阶段性路径，不应形成确定性交付节奏。",
                    downgrade_to="assumption",
                    affected_terms=["实施", "冗余", "高可用", "一次", "直接", "完成"],
                )
            )

    if open_items.get("siteVerification"):
        for item in open_items.get("siteVerification", []):
            audit.downgrade_notes.append(f"涉及现场复核项的结论需保持待确认表达：{item}")
    if open_items.get("customerConfirmation"):
        for item in open_items.get("customerConfirmation", []):
            audit.downgrade_notes.append(f"涉及客户确认项的结论需保持待确认表达：{item}")

    return audit
