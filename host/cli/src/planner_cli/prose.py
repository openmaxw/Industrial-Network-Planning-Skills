from planner_cli.models import EvidenceItem


SECTION_SUMMARY_MAP = {
    "项目概述与建设目标": "明确项目背景、建设目标、覆盖范围及主要实施约束。",
    "现状网络与调研结论": "归纳现状网络结构、调研结果与主要限制条件。",
    "设计依据与方法说明": "明确方案形成依据、设计边界与方法路径。",
    "需求与约束分析": "归纳业务连续性、安全、运维、扩展与施工约束。",
    "技术选择与方案比较": "明确主要技术路线及选择理由。",
    "总体网络架构方案": "给出目标网络总体组织方式。",
    "ISA95 层级建模与系统协同结构": "明确层级划分、对象归属及跨层协同关系。",
    "IEC62443 分区分域与安全边界设计": "明确安全域划分、边界组织与访问控制原则。",
    "网络拓扑与通信路径说明": "明确主要连接结构、关键通信路径与跨域访问组织方式。",
    "IP 地址、VLAN 与子网规划": "明确地址规划、VLAN 组织方式及扩展预留。",
    "关键设备与部署建议": "明确关键设备类别、部署位置与实施条件。",
    "实施步骤与迁移建议": "明确实施前提、阶段划分与迁移控制重点。",
    "风险、假设与待确认项": "归纳风险项、假设项及待闭环事项。",
    "结论与建议": "汇总方案结论与下一步闭环事项。",
}

CHAPTER_RECOMMEND_KEYWORDS = {
    "项目概述与建设目标": ["项目目标", "总体策略", "建设", "范围"],
    "现状网络与调研结论": ["现状", "问题", "限制", "边界"],
    "设计依据与方法说明": ["方法体", "更新", "依据"],
    "需求与约束分析": ["连续运行", "约束", "边界", "运维", "扩展", "审计"],
    "技术选择与方案比较": ["技术路线", "边界组织", "地址规划", "部署方式", "收敛"],
    "总体网络架构方案": ["层级", "区域框架", "边界", "DMZ", "控制区"],
    "ISA95 层级建模与系统协同结构": ["层级", "协同", "ISA95"],
    "IEC62443 分区分域与安全边界设计": ["区域", "安全域", "受控", "边界", "DMZ", "收敛"],
    "网络拓扑与通信路径说明": ["访问路径", "跨域", "收敛", "白名单", "协议", "方向"],
    "IP 地址、VLAN 与子网规划": ["地址", "VLAN", "网段", "预留"],
    "关键设备与部署建议": ["部署", "设备", "落位", "位置"],
    "实施步骤与迁移建议": ["分阶段", "实施", "迁移", "节奏", "窗口"],
    "风险、假设与待确认项": ["风险", "假设", "待确认", "闭环"],
    "结论与建议": ["固化", "收口", "阶段实施", "定稿"],
}

GENERIC_FACT_KEYWORDS = ["现网", "安全目标", "项目名称", "项目约束", "主要连接", "候选分区"]
SUPPRESSED_NARRATIVE_PATTERNS = ["第三方/外部路径：", "跨域访问路径：", "关键对象："]
ARCHITECTURE_PRIORITY_KEYWORDS = ["层级", "区域框架", "办公区", "DMZ", "控制区", "边界"]


def _looks_structured_object_text(text: str) -> bool:
    value = text.strip()
    if not value:
        return False
    if (value.startswith('{') and value.endswith('}')) or (value.startswith('[') and value.endswith(']')):
        return True
    return any(token in value for token in ["{'id':", '{"id":', "'source':", '"source":', "'target':", '"target":', "'members':", '"members":'])


def _clean_text(text: str) -> str:
    value = text.strip().rstrip("。")
    for prefix in ["建议：", "待确认：", "前提假设："]:
        if value.startswith(prefix):
            value = value[len(prefix):].strip()
    return value


def _compress_delivery_text(text: str) -> str:
    value = _clean_text(text)
    replacements = [
        ("依据现有", "基于"),
        ("可进一步收敛为", "统一为"),
        ("受控路径与边界控制点收敛", "受控边界收敛"),
        ("对象访问关系", "访问关系"),
        ("并强化", "，同时强化"),
        ("并通过", "，并通过"),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    return " ".join(value.split())


def _dedupe_texts(items: list[EvidenceItem], limit: int | None = None) -> list[str]:
    results: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = _compress_delivery_text(item.text)
        if not text or text in seen or _looks_structured_object_text(text):
            continue
        if any(pattern in text for pattern in SUPPRESSED_NARRATIVE_PATTERNS):
            continue
        seen.add(text)
        results.append(text)
        if limit is not None and len(results) >= limit:
            break
    return results


def _pick_text(title: str, items: list[EvidenceItem], limit: int, keyword_map: dict[str, list[str]]) -> list[str]:
    keywords = keyword_map.get(title, [])
    matched: list[str] = []
    fallback: list[str] = []
    for text in _dedupe_texts(items, limit=None):
        if any(keyword in text for keyword in keywords):
            matched.append(text)
        elif any(keyword in text for keyword in GENERIC_FACT_KEYWORDS):
            fallback.append(text)
    values = matched[:limit]
    if len(values) < limit:
        for item in fallback:
            if item not in values:
                values.append(item)
            if len(values) >= limit:
                break
    return values[:limit]


def _pick_architecture_text(recommendations: list[EvidenceItem]) -> str | None:
    texts = _dedupe_texts(recommendations, limit=8)
    for text in texts:
        if any(keyword in text for keyword in ARCHITECTURE_PRIORITY_KEYWORDS):
            return text
    return texts[0] if texts else None


def _normalize_fact_fragment(text: str) -> str:
    value = _compress_delivery_text(text)
    for prefix in ["项目名称：", "客户名称：", "建设地点：", "现网层级：", "项目约束：", "安全目标：", "候选分区：", "调研关注风险：", "现网地址现状：", "地址约束："]:
        if value.startswith(prefix):
            return value[len(prefix):].strip()
    return value


def _topic_phrase(title: str, recommendations: list[EvidenceItem]) -> str | None:
    texts = _dedupe_texts(recommendations, limit=8)
    joined = " ".join(texts)
    if title == "项目概述与建设目标":
        return "分层分区治理、边界收敛与地址规划协同推进"
    if title == "总体网络架构方案":
        return "分层承载、分区治理与受控边界收敛"
    if title == "IEC62443 分区分域与安全边界设计":
        return "分区分域、边界隔离与受控访问"
    if title == "网络拓扑与通信路径说明":
        return "关键业务链路梳理与跨域访问统一收口"
    if title == "IP 地址、VLAN 与子网规划":
        return "分区对应编址、VLAN 分层组织与扩容预留"
    if title == "关键设备与部署建议":
        return "边界控制设备、汇聚交换设备与运维接入节点统筹部署"
    if title == "实施步骤与迁移建议":
        return "先边界治理、后结构优化、再分阶段迁移验证"
    if title == "结论与建议":
        return "完成复核确认后固化实施定稿"
    if title == "ISA95 层级建模与系统协同结构" and joined:
        return "层级职责划分与系统协同界面收敛"
    return None


def _default_narrative(title: str, confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], pending_items: list[EvidenceItem], assumptions: list[EvidenceItem]) -> str:
    fact = _pick_text(title, confirmed_facts, 1, {title: GENERIC_FACT_KEYWORDS})
    pending = _dedupe_texts(pending_items, limit=1)
    assumption = _dedupe_texts(assumptions, limit=1)
    topic = _topic_phrase(title, recommendations)

    if title == "项目概述与建设目标":
        parts = []
        if fact:
            parts.append(f"本项目以{_normalize_fact_fragment(fact[0])}为项目基础。")
        if topic:
            parts.append(f"项目建设围绕{topic}展开，并同步明确范围边界与实施路径。")
        if pending:
            parts.append(f"涉及{pending[0]}的内容在项目启动阶段完成确认。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "现状网络与调研结论":
        parts = []
        if fact:
            parts.append(f"根据现阶段调研资料，{_normalize_fact_fragment(fact[0])}构成现状判断依据。")
        if topic:
            parts.append(f"网络深化工作围绕{topic}组织开展。")
        if pending:
            parts.append(f"{pending[0]}仍需结合现场核实结果进一步明确。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "设计依据与方法说明":
        parts = ["本方案以项目输入资料、现状调研信息及既有网络条件为基础，按工业控制网络分层承载、分区隔离、边界受控和实施可落地原则组织。"]
        if pending:
            parts.append(f"如{pending[0]}后续补充，相关边界、地址与实施细节同步更新。")
        return "".join(parts)

    if title == "需求与约束分析":
        parts = []
        if fact:
            parts.append(f"结合现阶段输入，{_normalize_fact_fragment(fact[0])}构成本项目设计约束的直接依据。")
        if topic:
            parts.append(f"后续方案需围绕{topic}同步落实业务连续性、边界控制与实施可行性要求。")
        if pending:
            parts.append(f"{pending[0]}完成确认后，相关约束边界进一步细化。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "技术选择与方案比较":
        parts = []
        if fact:
            parts.append(f"结合{_normalize_fact_fragment(fact[0])}，本方案优先选择便于集中纳管、边界收口和分阶段实施的技术路线。")
        if topic:
            parts.append(f"技术收敛围绕{topic}展开，并以可实施性、可维护性和后续扩展性作为主要取舍依据。")
        if pending:
            parts.append(f"{pending[0]}在最终定版前继续作为技术选择边界条件。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "ISA95 层级建模与系统协同结构":
        parts = []
        if fact:
            parts.append(f"结合现有系统对象与部署位置，{_normalize_fact_fragment(fact[0])}构成系统职责划分与接口归属分析基础。")
        if topic:
            parts.append(f"在此基础上，进一步明确系统归属、跨系统协同关系及接口边界，形成{topic}。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "网络拓扑与通信路径说明":
        parts = []
        if fact:
            parts.append(f"网络拓扑按{_normalize_fact_fragment(fact[0])}组织总体连接关系。")
        else:
            parts.append("网络拓扑按中央承载、区域汇聚与对象接入三级结构组织。")
        if topic:
            parts.append(f"图中跨域通信路径按{topic}统一收口，业务访问、监控采集与运维访问分别通过对应边界实施控制。")
        if pending:
            parts.append(f"涉及{pending[0]}的链路落位在实施前完成复核后纳入最终施工图。")
        return "".join(parts)

    if title == "IP 地址、VLAN 与子网规划":
        parts = []
        if fact:
            parts.append(f"地址规划在保留{_normalize_fact_fragment(fact[0])}的基础上实施分区对应编址。")
        else:
            parts.append("地址规划按分区对应编址、VLAN 分层组织和扩容预留执行。")
        if topic:
            parts.append(f"各区域网络按{topic}组织，并同步满足扩容与运维识别要求。")
        if pending:
            parts.append(f"涉及{pending[0]}的精细网段号与 VLAN 编号在现场复核后纳入最终地址表。")
        return "".join(parts)

    if title == "关键设备与部署建议":
        parts = []
        if fact:
            parts.append(f"依据现有对象分布与部署条件，{_normalize_fact_fragment(fact[0])}。")
        if topic:
            parts.append(f"设备部署按{topic}实施，以支撑网络边界、运维收口与业务连续性要求。")
        if pending:
            parts.append(f"涉及{pending[0]}的设备落位在实施前完成核实。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "实施步骤与迁移建议":
        parts = []
        if fact:
            parts.append(f"考虑到{_normalize_fact_fragment(fact[0])}，实施组织坚持受控变更、分阶段切换和逐步验证。")
        if topic:
            parts.append(f"实施路径按{topic}执行，以控制对既有生产业务的影响。")
        if pending:
            parts.append(f"{pending[0]}完成确认后，进一步细化施工窗口、变更节奏与验收边界。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "风险、假设与待确认项":
        parts = []
        if fact:
            parts.append(f"当前主要风险集中在{_normalize_fact_fragment(fact[0])}。")
        if assumption:
            parts.append(f"在相关信息尚未完整前，实施按{assumption[0]}作为边界前提组织。")
        if pending:
            parts.append(f"{pending[0]}列为下一阶段优先闭环事项。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    if title == "结论与建议":
        parts = []
        parts.append("本方案的网络结构、边界组织、访问收口方式和实施路径已明确，可据此进入实施定版审批。")
        if pending:
            parts.append(f"在正式下发实施定稿前，{pending[0]}仍需完成闭环确认。")
        return "".join(parts) or SECTION_SUMMARY_MAP[title]

    parts = []
    if fact:
        parts.append(f"当前已确认{fact[0]}。")
    if topic:
        parts.append(f"后续工作按{topic}推进。")
    if pending:
        parts.append(f"其中，{pending[0]}需进一步确认。")
    return "".join(parts) or SECTION_SUMMARY_MAP.get(title, "归纳相关规划内容。")


def _default_conclusion(title: str, confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], assumptions: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    pending = _dedupe_texts(pending_items, limit=1)
    assumption = _dedupe_texts(assumptions, limit=1)
    topic = _topic_phrase(title, recommendations)

    if title == "项目概述与建设目标":
        parts = []
        if topic:
            parts.append(f"本项目建设以{topic}为总体方向。")
        if pending:
            parts.append(f"{pending[0]}在方案深化阶段进一步明确。")
        return "".join(parts)

    if title == "现状网络与调研结论":
        parts = []
        if topic:
            parts.append(f"后续方案深化围绕{topic}执行。")
        if pending:
            parts.append(f"{pending[0]}的复核结果将直接影响后续边界设计。")
        return "".join(parts)

    if title == "设计依据与方法说明":
        return "后续若输入条件发生变化，应同步修订相关章节结论，并重新核定网络边界、地址组织、设备部署及实施安排。"

    if title == "需求与约束分析":
        parts = []
        if topic:
            parts.append(f"后续设计与实施需统一满足{topic}。")
        if pending:
            parts.append(f"在{pending[0]}完成确认前，相关章节按保守边界组织定版。")
        return "".join(parts)

    if title == "技术选择与方案比较":
        parts = []
        parts.append("当前技术路线已收敛到便于集中纳管、边界受控、分阶段实施和后续扩展的方案。")
        if pending:
            parts.append(f"在{pending[0]}完成确认前，最终技术细项继续保留定版弹性。")
        return "".join(parts)

    if title == "ISA95 层级建模与系统协同结构":
        return f"系统职责划分、对象归属与协同界面按{_topic_phrase(title, recommendations) or '既定层级与协同边界'}组织。"

    if title == "网络拓扑与通信路径说明":
        parts = []
        if topic:
            parts.append(f"最终拓扑与通信路径按{topic}执行。")
        if pending:
            parts.append(f"{pending[0]}完成后，同步下发最终链路清单与访问白名单。")
        return "".join(parts)

    if title == "IP 地址、VLAN 与子网规划":
        parts = []
        if topic:
            parts.append(f"地址与 VLAN 规划按{topic}统一执行，并预留后续扩容余量。")
        if pending:
            parts.append(f"在{pending[0]}完成前，最终地址表与 VLAN 编号表锁定至区域级。")
        return "".join(parts)

    if title == "关键设备与部署建议":
        parts = []
        if topic:
            parts.append(f"关键设备部署按{topic}实施，并与现场机房条件及维护路径同步校核。")
        if pending:
            parts.append(f"{pending[0]}的确认将直接影响设备最终落位。")
        return "".join(parts)

    if title == "实施步骤与迁移建议":
        parts = []
        if topic:
            parts.append(f"后续实施按{topic}组织详细计划、施工窗口与验证步骤。")
        if pending:
            parts.append(f"在{pending[0]}完成确认前，最终实施定版暂不下发。")
        return "".join(parts)

    if title == "风险、假设与待确认项":
        parts = []
        if assumption:
            parts.append(f"当前方案暂按{assumption[0]}组织实施边界。")
        if pending:
            parts.append(f"{pending[0]}优先纳入实施前闭环事项。")
        return "".join(parts)

    if title == "结论与建议":
        parts = []
        parts.append("后续工作按现场复核、接口确认、实施定版和分阶段落地四项任务组织执行。")
        if pending:
            parts.append(f"其中，{pending[0]}作为实施定稿下发前的优先闭环事项。")
        return "".join(parts)

    return ""


def _tailored_architecture_narrative(recommendations: list[EvidenceItem], pending_items: list[EvidenceItem], assumptions: list[EvidenceItem]) -> str:
    topic = _topic_phrase("总体网络架构方案", recommendations)
    pending = _dedupe_texts(pending_items, limit=1)
    assumption = _dedupe_texts(assumptions, limit=1)
    parts = []
    parts.append(f"总体网络架构按{topic or '分层承载、分区治理与受控边界收敛'}组织，形成清晰的业务承载层次与边界控制层次。")
    parts.append("在架构组织上，兼顾业务连续性、跨域访问受控以及后续扩展实施的可管理性。")
    if assumption:
        parts.append(f"当前设计以{assumption[0]}为实施边界前提，相关接口方式在实施前结合现场条件完成核实。")
    if pending:
        parts.append(f"{pending[0]}将直接影响边界设备部署与网络收口方式。")
    return "".join(parts)


def _tailored_security_narrative(confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    target = _pick_text("IEC62443 分区分域与安全边界设计", confirmed_facts, 1, {"IEC62443 分区分域与安全边界设计": ["安全目标", "候选分区", "边界要求"]})
    pending = _dedupe_texts(pending_items, limit=1)
    parts = []
    if target:
        parts.append(f"结合{_normalize_fact_fragment(target[0])}，安全边界设计按分区分域、边界隔离与访问审计组织。")
    else:
        parts.append("安全边界设计按分区分域、边界隔离与访问审计组织。")
    parts.append("跨域访问、远程运维和高关键对象访问统一纳入受控边界管理。")
    if pending:
        parts.append(f"{pending[0]}确认后，受控通道与控制策略同步定版。")
    return "".join(parts)


def _tailored_implementation_narrative(confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    constraint = _pick_text("实施步骤与迁移建议", confirmed_facts, 1, {"实施步骤与迁移建议": ["项目约束", "实施关注"]})
    topic = _topic_phrase("实施步骤与迁移建议", recommendations)
    pending = _dedupe_texts(pending_items, limit=1)
    parts = []
    if constraint:
        parts.append(f"考虑到{_normalize_fact_fragment(constraint[0])}，实施组织坚持受控变更、分阶段切换和逐步验证。")
    else:
        parts.append("实施组织坚持受控变更、分阶段切换和逐步验证。")
    if topic:
        parts.append(f"实施路径按{topic}执行，以控制对既有生产业务的影响。")
    if pending:
        parts.append(f"{pending[0]}完成确认后，进一步细化施工窗口、变更节奏与验收边界。")
    return "".join(parts)


def _tailored_summary_narrative(recommendations: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    pending = _dedupe_texts(pending_items, limit=1)
    parts = []
    parts.append("本方案已具备实施定版审批基础，已明确内容可据此转入深化设计与实施组织。")
    if pending:
        parts.append(f"在正式下发实施定稿前，{pending[0]}仍需完成闭环确认。")
    return "".join(parts)


def _tailored_architecture_conclusion(recommendations: list[EvidenceItem], assumptions: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    topic = _topic_phrase("总体网络架构方案", recommendations)
    pending = _dedupe_texts(pending_items, limit=1)
    assumption = _dedupe_texts(assumptions, limit=1)
    parts = [f"目标架构按{topic or '分层承载、分区治理与受控边界收敛'}组织。"]
    if assumption:
        parts.append(f"{assumption[0]}作为后续详细设计基础。")
    if pending:
        parts.append(f"{pending[0]}完成后，边界设备、接口方式及部署细节同步细化。")
    return "".join(parts)


def _tailored_security_conclusion(confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    target = _pick_text("IEC62443 分区分域与安全边界设计", confirmed_facts, 1, {"IEC62443 分区分域与安全边界设计": ["安全目标", "候选分区", "边界要求"]})
    pending = _dedupe_texts(pending_items, limit=1)
    parts = []
    if target:
        parts.append(f"结合{_normalize_fact_fragment(target[0])}，安全边界设计按分区分域、统一边界控制、白名单放行和审计留痕组织定版。")
    else:
        parts.append("安全边界设计按分区分域、统一边界控制、白名单放行和审计留痕组织定版。")
    if pending:
        parts.append(f"{pending[0]}的确认结果将决定受控通道与控制策略最终落地方式。")
    return "".join(parts)


def _tailored_implementation_conclusion(confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    constraint = _pick_text("实施步骤与迁移建议", confirmed_facts, 1, {"实施步骤与迁移建议": ["项目约束", "实施关注"]})
    topic = _topic_phrase("实施步骤与迁移建议", recommendations)
    pending = _dedupe_texts(pending_items, limit=1)
    parts = []
    if constraint:
        parts.append(f"基于{_normalize_fact_fragment(constraint[0])}这一实施约束，")
    parts.append(f"后续实施按{topic or '边界治理、结构优化和逐步验证'}组织详细计划、施工窗口与验证步骤。")
    if pending:
        parts.append(f"在{pending[0]}完成确认前，最终实施定版暂不下发。")
    return "".join(parts)


def _tailored_summary_conclusion(recommendations: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    pending = _dedupe_texts(pending_items, limit=1)
    parts = ["后续工作按现场复核、接口确认、实施定版和分阶段落地四项任务组织执行。"]
    if pending:
        parts.append(f"其中，{pending[0]}作为实施定稿下发前的优先闭环事项。")
    return "".join(parts)


def build_narrative(title: str, confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], pending_items: list[EvidenceItem], assumptions: list[EvidenceItem]) -> str:
    if title == "总体网络架构方案":
        return _tailored_architecture_narrative(recommendations, pending_items, assumptions)
    if title == "IEC62443 分区分域与安全边界设计":
        return _tailored_security_narrative(confirmed_facts, recommendations, pending_items)
    if title == "实施步骤与迁移建议":
        return _tailored_implementation_narrative(confirmed_facts, recommendations, pending_items)
    if title == "结论与建议":
        return _tailored_summary_narrative(recommendations, pending_items)
    return _default_narrative(title, confirmed_facts, recommendations, pending_items, assumptions)


def build_conclusion_paragraph(title: str, confirmed_facts: list[EvidenceItem], recommendations: list[EvidenceItem], assumptions: list[EvidenceItem], pending_items: list[EvidenceItem]) -> str:
    if title == "总体网络架构方案":
        return _tailored_architecture_conclusion(recommendations, assumptions, pending_items)
    if title == "IEC62443 分区分域与安全边界设计":
        return _tailored_security_conclusion(confirmed_facts, recommendations, pending_items)
    if title == "实施步骤与迁移建议":
        return _tailored_implementation_conclusion(confirmed_facts, recommendations, pending_items)
    if title == "结论与建议":
        return _tailored_summary_conclusion(recommendations, pending_items)
    return _default_conclusion(title, confirmed_facts, recommendations, assumptions, pending_items)
