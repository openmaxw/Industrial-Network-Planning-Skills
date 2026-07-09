from dataclasses import dataclass, field

from planner_cli.evidence_policy import ConflictRecord
from planner_cli.models import EvidenceItem


@dataclass(slots=True)
class ChapterPhrasing:
    applicability: list[str] = field(default_factory=list)
    closure_conditions: list[str] = field(default_factory=list)
    adjusted_recommendations: list[EvidenceItem] = field(default_factory=list)
    adjusted_assumptions: list[EvidenceItem] = field(default_factory=list)
    adjusted_pending: list[EvidenceItem] = field(default_factory=list)


CONFLICT_DOMAIN_TO_CHAPTERS = {
    "security-zones": ["IEC62443 分区分域与安全边界设计", "总体网络架构方案"],
    "addressing-precision": ["IP 地址、VLAN 与子网规划"],
    "boundary-certainty": ["总体网络架构方案", "网络拓扑与通信路径说明"],
    "remote-maintenance-boundary": ["IEC62443 分区分域与安全边界设计", "网络拓扑与通信路径说明"],
    "deployment-certainty": ["关键设备与部署建议", "实施步骤与迁移建议"],
    "availability-target-uncertain": ["实施步骤与迁移建议", "结论与建议"],
}



def _matches_conflict(text: str, conflict: ConflictRecord) -> bool:
    if not conflict.affected_terms:
        return True
    if not any(term in text for term in conflict.affected_terms):
        return False
    if any(term in text for term in ["项目目标", "项目名称", "客户名称", "建设目标", "建设范围"]):
        return False
    return True



def chapter_phrasing(chapter_title: str, recommendations: list[EvidenceItem], conflicts: list[ConflictRecord], pending_items: list[EvidenceItem]) -> ChapterPhrasing:
    applicability: list[str] = []
    closure_conditions: list[str] = []
    adjusted_recommendations: list[EvidenceItem] = []
    adjusted_assumptions: list[EvidenceItem] = []
    adjusted_pending: list[EvidenceItem] = []

    matched_conflicts = [item for item in conflicts if chapter_title in CONFLICT_DOMAIN_TO_CHAPTERS.get(item.domain, [])]

    for item in recommendations:
        text = item.text
        source = item.source
        evidence_type = item.evidence_type
        moved = False
        for conflict in matched_conflicts:
            if _matches_conflict(text, conflict):
                if conflict.downgrade_to == "pending":
                    adjusted_pending.append(EvidenceItem(text=f"待确认：{text}", source=source, evidence_type="pending"))
                    moved = True
                    break
                if conflict.downgrade_to == "assumption":
                    adjusted_assumptions.append(EvidenceItem(text=f"前提假设：{text}", source=source, evidence_type="assumption"))
                    moved = True
                    break
                if not text.startswith("建议") and not text.startswith("可") and not text.startswith("宜"):
                    text = f"建议：{text}"
        if not moved:
            adjusted_recommendations.append(EvidenceItem(text=text, source=source, evidence_type=evidence_type))

    for conflict in matched_conflicts:
        applicability.append(conflict.resolution)

    for pending in pending_items:
        closure_conditions.append(f"闭环条件：{pending.text}")

    if not applicability:
        applicability.append("当前章节建议基于现有输入成立，若现场信息变化需同步调整。")
    if not closure_conditions:
        closure_conditions.append("闭环条件：当前章节未新增强制闭环项。")

    return ChapterPhrasing(
        applicability=applicability,
        closure_conditions=closure_conditions,
        adjusted_recommendations=adjusted_recommendations,
        adjusted_assumptions=adjusted_assumptions,
        adjusted_pending=adjusted_pending,
    )
