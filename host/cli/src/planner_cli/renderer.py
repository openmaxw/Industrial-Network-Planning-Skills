from planner_cli.core_loader import CoreAssets
from planner_cli.models import EvidenceItem
from planner_cli.planner import Chapter, PlanBundle




def _formalize_result_text(text: str) -> str:
    value = text.strip().rstrip('。')
    replacements = [
        ('建议采用', '采用'),
        ('建议按', '按'),
        ('建议以', '以'),
        ('建议围绕', '围绕'),
        ('建议在', '在'),
        ('建议将', '将'),
        ('建议对', '对'),
        ('建议通过', '通过'),
        ('建议保留', '保留'),
        ('建议划分', '划分'),
        ('建议设置', '设置'),
        ('建议组织', '组织'),
        ('建议延续', '延续'),
        ('建议强化', '强化'),
        ('建议', ''),
        ('宜先', '先'),
        ('宜对', '对'),
        ('宜按', '按'),
        ('宜围绕', '围绕'),
        ('宜以', '以'),
        ('宜在', '在'),
        ('宜通过', '通过'),
        ('宜保留', '保留'),
        ('宜采用', '采用'),
        ('宜', ''),
        ('VLAN 组织建议：', 'VLAN 组织：'),
        ('命名建议：', '命名规则：'),
        ('访问路径建议：', '访问路径：'),
        ('关键设备部署建议应以', '关键设备部署以'),
        ('实施路径应强调', '实施路径按'),
        ('不宜直接承诺', '暂不直接固化'),
        ('原则性冗余建议', '冗余控制要求'),
        ('规划原则', '区域级规划结果'),
        ('现有设备对象：', ''),
        ('现网层级：', ''),
        ('系统对象：', ''),
        ('角色对象：', ''),
        ('部署位置：', ''),
        ('主要连接：', ''),
        ('关键通信：', ''),
        ('协议线索：', ''),
        ('安全目标：', ''),
        ('候选分区：', ''),
        ('边界要求：', ''),
        ('审计要求：', ''),
        ('调研关注风险：', ''),
        ('项目约束：', ''),
        ('边界对象：', ''),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    value = ' '.join(value.split())
    return value + '。'


def _clean_table_cell(text: str) -> str:
    value = _formalize_result_text(text)
    value = value.replace('应优先', '优先').replace('应以', '以').replace('应按', '按').replace('应', '')
    value = value.replace('原则性冗余', '冗余要求')
    value = value.replace('当前设计以', '当前按').replace('默认', '按')
    return ' '.join(value.split())
def _append_evidence_list(lines: list[str], items: list[EvidenceItem], fallback: str, show_source: bool = True, limit: int | None = None) -> None:
    if items:
        rendered = items[:limit] if limit is not None else items
        for item in rendered:
            suffix = f"（来源：`{item.source}`）" if show_source and item.source else ""
            rendered_text = _formalize_result_text(item.text) if not show_source else item.text
            lines.append(f"- {rendered_text}{suffix}")
    else:
        lines.append(f"- {fallback}")
    lines.append("")


def _append_table(lines: list[str], headers: list[str], rows: list[list[str]]) -> None:
    if not rows:
        return
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        normalized = [cell.replace("\n", " ").strip() or "-" for cell in row]
        lines.append("| " + " | ".join(normalized) + " |")
    lines.append("")


def _build_topology_mermaid(plan: PlanBundle) -> str:
    delivery = plan.appendix_delivery or {}
    topology_zones = delivery.get("topologyZones") or []
    topology_nodes = delivery.get("topologyNodes") or []
    topology_links = delivery.get("topologyLinks") or []
    if topology_zones and topology_nodes:
        zone_map = {str(item.get("id", "")).strip(): str(item.get("title", item.get("id", "区域"))).strip() or "区域" for item in topology_zones}
        zone_nodes = {key: [] for key in zone_map.keys()}
        loose_nodes = []
        for item in topology_nodes:
            node_id = str(item.get("id", "节点")).strip() or "节点"
            label = str(item.get("label", node_id)).strip() or node_id
            zone = str(item.get("zone", "")).strip()
            if zone in zone_nodes:
                zone_nodes[zone].append((node_id, label))
            else:
                loose_nodes.append((node_id, label))
        lines = ["```mermaid", "flowchart LR"]
        for zone in topology_zones:
            zid = str(zone.get("id", "")).strip()
            title = zone_map.get(zid, zid or "区域")
            lines.append(f'    subgraph {zid}["{title}"]')
            for node_id, label in zone_nodes.get(zid, []):
                lines.append(f'        {node_id}["{label}"]')
            lines.append('    end')
        for node_id, label in loose_nodes:
            lines.append(f'    {node_id}["{label}"]')
        for item in topology_links:
            source = str(item.get("source", "")).strip()
            target = str(item.get("target", "")).strip()
            label = str(item.get("label", "")).strip()
            style = str(item.get("style", "solid")).strip()
            if not source or not target:
                continue
            if label:
                connector = '-."' + label.replace('"', '') + '".-' if style == 'dashed' else '-->|"' + label.replace('"', '') + '"|'
                lines.append(f'    {source} {connector} {target}')
            else:
                lines.append(f'    {source} --> {target}')
        lines.append("```")
        return "\n".join(lines)

    access_matrix = delivery.get("accessMatrix") or []

    if access_matrix:
        nodes: dict[str, str] = {}
        edges: list[tuple[str, str, str]] = []
        for item in access_matrix:
            source = str(item.get("source", "源区")).strip() or "源区"
            target = str(item.get("target", "目标区")).strip() or "目标区"
            service = str(item.get("service", "业务")).strip() or "业务"
            sid = source.replace("/", "_").replace(" ", "_")
            tid = target.replace("/", "_").replace(" ", "_")
            nodes[sid] = source
            nodes[tid] = target
            edges.append((sid, tid, service))

        left_nodes = {k: v for k, v in nodes.items() if any(word in v for word in ["接入", "业务", "运维", "办公"]) }
        center_nodes = {k: v for k, v in nodes.items() if any(word in v for word in ["服务边界", "DMZ", "监控"]) }
        right_nodes = {k: v for k, v in nodes.items() if any(word in v for word in ["高关键", "边界网关"]) }

        lines = ["```mermaid", "flowchart LR"]
        if left_nodes:
            lines.append('    subgraph LEFT["接入与外部访问域"]')
            for key, label in left_nodes.items():
                lines.append(f'        {key}["{label}"]')
            lines.append('    end')
        if center_nodes:
            lines.append('    subgraph CENTER["中心监控与服务域"]')
            for key, label in center_nodes.items():
                lines.append(f'        {key}["{label}"]')
            lines.append('    end')
        if right_nodes:
            lines.append('    subgraph RIGHT["关键控制与边界域"]')
            for key, label in right_nodes.items():
                lines.append(f'        {key}["{label}"]')
            lines.append('    end')
        for key, label in nodes.items():
            if key not in left_nodes and key not in center_nodes and key not in right_nodes:
                lines.append(f'    {key}["{label}"]')
        for sid, tid, label in edges:
            lines.append(f'    {sid} -->|"{label}"| {tid}')
        lines.append("```")
        return "\n".join(lines)

    topology = str(plan.appendix_design.get("targetArchitecture", "")).strip()
    fallback = [
        "```mermaid",
        "flowchart LR",
        '    CORE["中央监控核心层"]',
        '    AGG["厂房汇聚层"]',
        '    ACC["公辅对象接入层"]',
        '    BND["受控边界/服务层"]',
        '    CORE --> AGG',
        '    AGG --> ACC',
        '    BND --> CORE',
        "```",
    ]
    return "\n".join(fallback if not topology else fallback)


def _build_boundary_topology_mermaid(plan: PlanBundle) -> str:
    delivery = plan.appendix_delivery or {}
    access_matrix = delivery.get("accessMatrix") or []
    security = plan.appendix_security or {}

    lines = ["```mermaid", "flowchart LR"]
    lines.append('    subgraph OUTER["外部访问域"]')
    lines.append('        EXT["办公/业务/运维外部访问"]')
    lines.append('    end')
    lines.append('    subgraph MID["服务边界域"]')
    lines.append('        DMZ["服务边界/DMZ"]')
    lines.append('    end')
    lines.append('    subgraph INNER["生产与关键控制域"]')
    lines.append('        CORE["监控核心区"]')
    lines.append('        HC["高关键对象区"]')
    lines.append('    end')
    lines.append('    EXT -->|"受控访问"| DMZ')
    lines.append('    DMZ -->|"接口/服务转发"| CORE')
    lines.append('    CORE -->|"受控采集/运维"| HC')

    for req in security.get("boundaryRequirements", [])[:2]:
        label = str(req).strip().replace('"', '')
        if label:
            lines.append(f'    DMZ -."{label}".- CORE')

    if access_matrix:
        first = access_matrix[0]
        label = str(first.get("control", "白名单控制")).strip().replace('"', '')
        lines.append(f'    EXT -."{label}".- DMZ')

    lines.append("```")
    return "\n".join(lines)


def _rows_from_dicts(items: list[dict], keys: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in items:
        rows.append([str(item.get(key, "-")).strip() or "-" for key in keys])
    return rows


def _top_texts(items: list[EvidenceItem], limit: int = 3) -> list[str]:
    return [_clean_table_cell(item.text) for item in items[:limit]]


def _first(values: list[str], fallback: str) -> str:
    return values[0] if values else fallback


def _build_formal_tables(plan: PlanBundle, chapter: Chapter) -> list[tuple[str, list[str], list[list[str]]]]:
    facts = _top_texts(chapter.confirmed_facts, limit=4)
    recommendations = _top_texts(chapter.recommendations, limit=4)
    assumptions = _top_texts(chapter.assumptions, limit=3)
    pending = _top_texts(chapter.pending_items, limit=3)

    if chapter.title == "项目概述与建设目标":
        return [(
            "**项目目标与范围表**",
            ["项", "定版内容", "输出要求"],
            [
                ["建设对象", plan.project_name, "作为本次网络方案正式交付对象。"],
                ["建设范围", plan.scope, "覆盖中央监控、厂房接入、边界与运维路径。"],
                ["交付目标", plan.objective, "输出可评审、可实施、可移交的正式方案。"],
            ],
        )]

    if chapter.title == "现状网络与调研结论":
        return [(
            "**现状调研摘要表**",
            ["项", "现状结论", "对设计的影响"],
            [
                ["网络组织", facts[0] if facts else "现网以多厂房本地控制、中央统一纳管为主。", "决定采用分厂房汇聚、中心统一收口架构。"],
                ["现场部署", pending[1] if len(pending) > 1 else "部分汇聚交换机与协议网关位置待现场复核。", "设备落位和主干路径需在实施前锁定。"],
                ["主干条件", pending[2] if len(pending) > 2 else "中央监控机房与各厂房弱电间主干条件待复核。", "影响链路组织与冗余方式最终定版。"],
            ],
        )]

    if chapter.title == "需求与约束分析":
        return [(
            "**需求与约束分析表**",
            ["类别", "收敛结果", "设计响应"],
            [
                ["连续性", facts[0] if facts else "厂务系统连续运行，不允许长时间中断。", "采用分阶段接入与切换窗口控制。"],
                ["隔离要求", facts[1] if len(facts) > 1 else "高关键对象需独立边界与更严格访问控制。", "高关键对象单独成区并配置独立边界控制。"],
                ["存量兼容", facts[3] if len(facts) > 3 else "部分既有控制器与网关需保留接入。", "对既有地址和接口采用平滑纳入方案。"],
            ],
        )]

    if chapter.title == "技术选择与方案比较":
        return [(
            "**技术路线比较表**",
            ["设计主题", "定版选择", "未采用方式"],
            [
                ["总体架构", "中央监控核心 + 厂房汇聚 + 对象接入三级结构", "不采用全对象直连中心的扁平架构。"],
                ["跨域交互", "统一经服务边界/DMZ 收口", "不采用 MES/办公网直接访问现场对象。"],
                ["高关键对象", "独立边界、独立策略、独立审计", "不采用与普通公辅对象共享访问边界。"],
            ],
        )]

    if chapter.title == "总体网络架构方案":
        tables = [(
            "**总体架构说明表**",
            ["设计项", "定版结果", "实施控制"],
            [
                ["总体架构", "采用核心层、汇聚层、接入层三级承载结构，中央统一监控、区域分散接入。", assumptions[0] if assumptions else "按现场接口条件深化。"],
                ["分层组织", "监控与服务集中部署，厂房侧对象先本地汇聚后接入中心平台，高关键对象独立边界接入。", pending[0] if pending else "无新增待确认项。"],
                ["扩容控制", "地址、边界与设备容量按后续新增对象预留扩容空间。", pending[1] if len(pending) > 1 else "结合实施图纸锁定。"],
            ],
        )]
        structures = plan.appendix_delivery.get("topologyStructures") or []
        rows = []
        for item in structures[:6]:
            rows.append([str(item.get("name", "网络结构")).strip() or "网络结构", str(item.get("type", "结构类型")).strip() or "结构类型", str(item.get("description", "-")).strip() or "-"])
        if rows:
            tables.append((
                "**关键网络结构表**",
                ["结构名称", "结构类型", "结构说明"],
                rows,
            ))
        return tables

    if chapter.title == "IEC62443 分区分域与安全边界设计":
        return [(
            "**边界控制表**",
            ["区域/边界", "规划结果", "控制要求"],
            [
                ["监控核心区", "承载 FMCS 中央监控平台、核心交换与集中管理服务。", "跨区访问统一经边界控制点收口。"],
                ["公辅控制区", "普通公辅对象按厂房或对象类别组织接入，高关键对象独立成区。", "对象间最小化互通，高关键对象不得与普通对象共边界。"],
                ["运维/接口边界", "MES、办公网、运维终端及第三方访问统一经受控边界接入。", assumptions[0] if assumptions else "白名单、账号与审计策略随实施定版。"],
            ],
        )]

    if chapter.title == "关键设备与部署建议":
        key_devices = plan.appendix_delivery.get("keyNetworkDevices") or []
        if isinstance(key_devices, list) and key_devices:
            return [(
                "**关键网络设备表**",
                ["设备标识", "设备角色", "重要级别"],
                [[str(item.get("id", "-")).strip() or "-", str(item.get("role", "-")).strip() or "-", str(item.get("importance", "-")).strip() or "-"] for item in key_devices],
            )]

    if chapter.title == "网络拓扑与通信路径说明":
        access_matrix = plan.appendix_delivery.get("accessMatrix") or []
        if isinstance(access_matrix, list) and access_matrix:
            return [(
                "**访问控制矩阵摘要表**",
                ["编号", "业务场景", "源区", "目标区", "允许服务", "控制要求"],
                _rows_from_dicts(access_matrix, ["id", "scenario", "source", "target", "service", "control"]),
            )]
        flows = [str(item).strip() for item in plan.appendix_communications.get("flows", []) if str(item).strip()]
        access_paths = [str(item).strip() for item in plan.appendix_communications.get("accessPaths", []) if str(item).strip()]
        return [(
            "**访问控制矩阵摘要表**",
            ["编号", "业务场景", "源区", "目标区", "允许路径", "控制要求"],
            [
                ["AC-01", "监控采集", "现场对象区", "中心监控区", _first(flows[:2], "现场控制器、网关或子系统经汇聚后上联中心平台。"), "仅放通监控采集所需协议、方向与端口。"],
                ["AC-02", "跨系统交互", "业务接口区", "监控服务边界区", _first(flows[2:4] + access_paths[:1], "与上层业务交互经应用服务层、接口服务器或受控网关转发。"), _first(access_paths[:2], "跨域通信统一收口，不允许现场对象直接暴露。")],
                ["AC-03", "运维访问", "运维接入区", "监控区/边界网关", _first(flows[4:] + plan.appendix_communications.get("remoteMaintenance", []), "运维终端与第三方远程维护通过独立运维入口接入。"), pending[0] if pending else _first(access_paths[1:3], "实施前锁定访问白名单。")],
            ],
        )]

    if chapter.title == "IP 地址、VLAN 与子网规划":
        vlan_plan = plan.appendix_delivery.get("vlanPlan") or []
        if isinstance(vlan_plan, list) and vlan_plan:
            return [(
                "**地址与 VLAN 规划表**",
                ["编号", "区域", "VLAN", "子网", "编号/命名策略", "定版约束"],
                _rows_from_dicts(vlan_plan, ["id", "zone", "vlan", "subnet", "naming", "constraint"]),
            )]
        existing = [str(item).strip() for item in plan.appendix_addressing.get("existingNetworks", []) if str(item).strip()]
        reserved = [str(item).strip() for item in plan.appendix_addressing.get("reservedNetworks", []) if str(item).strip()]
        vlans = [str(item).strip() for item in plan.appendix_addressing.get("vlans", []) if str(item).strip()]
        naming = [str(item).strip() for item in plan.appendix_addressing.get("naming", []) if str(item).strip()]
        constraints = [str(item).strip() for item in plan.appendix_addressing.get("constraints", []) if str(item).strip()]
        return [(
            "**地址与 VLAN 规划表**",
            ["编号", "区域", "网络组织方式", "编号/命名策略", "定版约束"],
            [
                ["IP-01", "核心与监控服务区", "独立设置中心监控服务网段与管理 VLAN。", _first(naming[:1], "按中心服务与管理用途统一命名。"), "中心地址池统一管理。"],
                ["IP-02", "厂房汇聚与公辅接入区", _first(vlans[:1], "按厂房、系统类别或安全边界划分独立 VLAN 与子网。"), _first(naming[1:2] + naming[:1], "按厂房、系统与用途统一命名。"), pending[0] if pending else _first(constraints[:1], "网段号现场复核后锁定。")],
                ["IP-03", "保留与扩容区", _first(reserved[:2], "既有地址平滑纳入，并为新增对象、边界设备和后续扩容预留地址空间。"), "保留网段不提前占用，新增对象按区域顺延编号。", _first(existing[:1] + constraints[1:2], "既有地址尽量平滑纳入。")],
            ],
        )]

    if chapter.title == "关键设备与部署建议":
        device_plan = plan.appendix_delivery.get("devicePlan") or []
        if isinstance(device_plan, list) and device_plan:
            return [(
                "**关键设备部署表**",
                ["编号", "设备类别", "部署位置", "实施前置条件", "部署定版要求"],
                _rows_from_dicts(device_plan, ["id", "deviceType", "location", "prerequisite", "requirement"]),
            )]
        devices = [str(item).strip() for item in plan.appendix_assets_raw.get("devices", []) if str(item).strip()]
        locations = [str(item).strip() for item in plan.appendix_assets_raw.get("locations", []) if str(item).strip()]
        criticality = [str(item).strip() for item in plan.appendix_assets_raw.get("criticality", []) if str(item).strip()]
        return [(
            "**关键设备部署表**",
            ["编号", "设备类别", "部署位置", "实施前置条件", "部署定版要求"],
            [
                ["EQ-01", "核心交换与监控服务器", _first(locations[:1], "中央监控机房。"), "中心机房机柜、电源、上联链路条件明确。", f"集中部署、统一管理；{_first(criticality[2:3], '必要时按可用性目标配置冗余。')}"],
                ["EQ-02", "汇聚交换机/协议网关", _first(locations[1:3], "厂房弱电间、就近控制间或公辅机柜。"), pending[0] if pending else "现场机柜、电源和光纤条件核实完成。", f"部署对象包括{_first(devices[1:3], '汇聚交换机、协议网关')}，按区域汇聚与就近接入原则落位。"],
                ["EQ-03", "边界安全与远程运维设备", _first(locations[3:4], "监控核心区与外部网络交界边界位置独立部署。"), pending[1] if len(pending) > 1 else "边界位置、审计要求与运维入口方案明确。", f"部署对象包括{_first(devices[6:8], '边界防火墙、运维接入设备')}，统一认证、审计与白名单控制。"],
            ],
        )]

    if chapter.title == "实施步骤与迁移建议":
        return [(
            "**实施阶段表**",
            ["阶段", "实施内容", "交付结果"],
            [
                ["阶段一", "完成现场复核、对象梳理、接口核定与边界确认。", "形成实施边界、设备清单和接入对象清单。"],
                ["阶段二", "完成边界策略、地址规划、设备部署与施工图定版。", "形成施工图、地址表、VLAN 表和访问控制表。"],
                ["阶段三", "按窗口分批接入、联调验证、切换与验收移交。", pending[0] if pending else "完成联调验证与交付移交。"],
            ],
        )]

    if chapter.title == "结论与建议":
        return [(
            "**实施闭环表**",
            ["编号", "闭环事项", "当前状态", "后续动作"],
            [
                ["CL-01", "总体架构与边界方案", "已明确", "按正式版输出进入深化设计。"],
                ["CL-02", "地址、设备与访问细项", "待现场复核后锁定", pending[0] if pending else "完成复核后下发实施定稿。"],
                ["CL-03", "实施组织与验收边界", "可启动", pending[1] if len(pending) > 1 else "按阶段实施并组织验收。"],
            ],
        )]

    return []


def _render_formal_chapter(lines: list[str], plan: PlanBundle, chapter: Chapter) -> None:
    display_title = FORMAL_TITLE_MAP.get(chapter.title, chapter.title)
    lines.append(f"## {display_title}")
    lines.append("")

    if chapter.title == "网络拓扑与通信路径说明":
        lines.append("**总体拓扑图**")
        lines.append("")
        lines.append(_build_topology_mermaid(plan))
        lines.append("")
        lines.append("**重点边界拓扑图**")
        lines.append("")
        lines.append(_build_boundary_topology_mermaid(plan))
        lines.append("")

    for table_title, headers, rows in _build_formal_tables(plan, chapter):
        lines.append(table_title)
        lines.append("")
        _append_table(lines, headers, rows)

    result_titles = {
        "项目概述与建设目标": "**本节结论**",
        "现状网络与调研结论": "**调研结论摘要**",
        "设计依据与方法说明": "**设计说明**",
        "需求与约束分析": "**需求与约束结论**",
        "技术选择与方案比较": "**技术选择说明**",
        "总体网络架构方案": "**架构说明**",
        "IEC62443 分区分域与安全边界设计": "**边界控制说明**",
        "网络拓扑与通信路径说明": "**通信路径说明**",
        "IP 地址、VLAN 与子网规划": "**地址规划说明**",
        "关键设备与部署建议": "**设备部署说明**",
        "通信与运维接入方案": "**运维接入说明**",
        "实施步骤与迁移建议": "**实施安排**",
        "风险、假设与待确认项": "**风险说明**",
        "结论与建议": "**执行结论**",
    }

    if chapter.conclusion:
        lines.append(result_titles.get(chapter.title, "**本章结论**"))
        lines.append("")
        lines.append(_formalize_result_text(chapter.conclusion))
        lines.append("")
    elif chapter.narrative and chapter.title in {"项目概述与建设目标", "现状网络与调研结论", "需求与约束分析", "技术选择与方案比较"}:
        lines.append(result_titles.get(chapter.title, "**本章结论**"))
        lines.append("")
        lines.append(_formalize_result_text(chapter.narrative))
        lines.append("")

    if chapter.confirmed_facts:
        label = "**现状与已知条件**" if chapter.title in {"项目概述与建设目标", "现状网络与调研结论"} else "**设计依据**"
        lines.append(label)
        lines.append("")
        limit = 3 if chapter.title in {"网络拓扑与通信路径说明", "IP 地址、VLAN 与子网规划", "关键设备与部署建议"} else 4
        _append_evidence_list(lines, chapter.confirmed_facts, "当前未补充相关内容。", show_source=False, limit=limit)

    if chapter.recommendations and chapter.title not in {"结论与建议"}:
        label = "**方案说明**" if chapter.title != "实施步骤与迁移建议" else "**实施安排**"
        lines.append(label)
        lines.append("")
        limit = 3 if chapter.title in {"网络拓扑与通信路径说明", "IP 地址、VLAN 与子网规划", "关键设备与部署建议"} else 4
        _append_evidence_list(lines, chapter.recommendations, "当前未补充相关内容。", show_source=False, limit=limit)

    if chapter.pending_items:
        lines.append("**待确认项**")
        lines.append("")
        _append_evidence_list(lines, chapter.pending_items, "当前无新增待确认项。", show_source=False, limit=3)


def _render_draft_chapter(lines: list[str], chapter: Chapter) -> None:
    lines.append(f"## {chapter.title}")
    lines.append("")
    lines.append("**章节摘要**")
    lines.append("")
    lines.append(chapter.narrative if chapter.narrative else "当前未生成章节摘要。")
    lines.append("")
    lines.append("**章节结论**")
    lines.append("")
    lines.append(chapter.conclusion if chapter.conclusion else "当前未生成章节结论。")
    lines.append("")
    lines.append("**本章目标**")
    lines.append("")
    lines.append(f"- {chapter.objective}")
    lines.append("")
    lines.append("**输入来源**")
    lines.append("")
    for item in chapter.input_sources:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("**规则主题**")
    lines.append("")
    for item in chapter.rule_topics:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("**适用前提**")
    lines.append("")
    if chapter.applicability:
        for item in chapter.applicability:
            lines.append(f"- {item}")
    else:
        lines.append("- 本章未补充额外适用前提。")
    lines.append("")
    lines.append("**闭环条件**")
    lines.append("")
    if chapter.closure_conditions:
        for item in chapter.closure_conditions:
            lines.append(f"- {item}")
    else:
        lines.append("- 本章未补充额外闭环条件。")
    lines.append("")
    lines.append("**已确认事实**")
    lines.append("")
    _append_evidence_list(lines, chapter.confirmed_facts, "现阶段暂无进一步可确认事实。", limit=4)
    lines.append("**规划建议**")
    lines.append("")
    _append_evidence_list(lines, chapter.recommendations, "本章暂无补充规划建议。", limit=4)
    lines.append("**假设项**")
    lines.append("")
    _append_evidence_list(lines, chapter.assumptions, "本章暂无新增假设项。", limit=3)
    lines.append("**待确认项**")
    lines.append("")
    _append_evidence_list(lines, chapter.pending_items, "本章暂无新增待确认项。", limit=3)






FORMAL_TITLE_MAP = {
    "项目概述与建设目标": "项目概述",
    "现状网络与调研结论": "现场调研与现状结论",
    "设计依据与方法说明": "设计原则与技术路线",
    "总体网络架构方案": "总体网络架构方案",
    "IEC62443 分区分域与安全边界设计": "网络分区与边界控制方案",
    "网络拓扑与通信路径说明": "网络拓扑图",
    "IP 地址、VLAN 与子网规划": "地址、VLAN 与子网规划",
    "关键设备与部署建议": "关键设备部署方案",
    "通信与运维接入方案": "通信与运维接入方案",
    "实施步骤与迁移建议": "实施方案与切换策略",
    "风险、假设与待确认项": "风险分析与待确认事项",
    "结论与建议": "实施结论与定版条件",
}

HIDE_FORMAL_TITLES = {
    "ISA95 层级建模与系统协同结构",
}

def _chapter_map(chapters: list[Chapter]) -> dict[str, Chapter]:
    return {chapter.title: chapter for chapter in chapters}


def _formal_ordered_chapters(chapters: list[Chapter]) -> list[Chapter]:
    by_title = _chapter_map(chapters)
    ordered_titles = [
        "项目概述与建设目标",
        "现状网络与调研结论",
        "设计依据与方法说明",
        "需求与约束分析",
        "技术选择与方案比较",
        "总体网络架构方案",
        "IEC62443 分区分域与安全边界设计",
        "网络拓扑与通信路径说明",
        "IP 地址、VLAN 与子网规划",
        "关键设备与部署建议",
        "通信与运维接入方案",
        "实施步骤与迁移建议",
        "风险、假设与待确认项",
        "ISA95 层级建模与系统协同结构",
        "结论与建议",
    ]
    ordered = [by_title[title] for title in ordered_titles if title in by_title]
    extras = [chapter for chapter in chapters if chapter.title not in ordered_titles]
    return ordered + extras


def _build_executive_summary(plan: PlanBundle) -> list[str]:
    lines: list[str] = []
    scope = (plan.scope or '').strip()
    if scope.startswith('覆盖'):
        scope = scope[2:].strip('，。 ')
    lines.append("## 执行摘要")
    lines.append("")
    lines.append(f"- 本方案覆盖 {scope or plan.scope}，用于形成可评审、可定版、可实施的网络建设结果。")
    lines.append("- 总体架构已明确为核心汇聚、控制承载、业务接入与边界隔离分层组织，跨域通信统一通过受控边界收口。")
    lines.append("- 文档直接给出网络分区、拓扑路径、地址与 VLAN 组织、关键设备部署及实施安排，不再以原则性描述替代设计结果。")
    lines.append("- 当前已确定内容可直接作为深化设计基础；未闭合事项统一列入“待确认项”，用于后续定版控制。")
    lines.append("- 本文档用于业主评审、实施组织、采购边界确认及后续现场落地。")
    lines.append("")
    return lines

def render_markdown(plan: PlanBundle, assets: CoreAssets, style: str = "draft") -> str:
    lines: list[str] = []
    lines.append(f"# {plan.project_name} 工业网络方案")
    lines.append("")
    if style == "formal":
        lines.append("> 本文档为面向客户交付的综合性网络方案版本。")
    else:
        lines.append("> 本文档由 `industrial-network-planner` CLI 生成，定位为基于 ISA95 + IEC62443 方法体的客户交付级方案草案。")
    lines.append("")
    lines.append("## 文档说明")
    lines.append("")
    lines.append(f"- 客户名称：{plan.customer_name}")
    lines.append(f"- 项目地点：{plan.site_name}")
    lines.append(f"- 建设目标：{plan.objective}")
    lines.append(f"- 建设范围：{plan.scope}")
    if style != "formal":
        lines.append("- 输出宿主：`host/cli`")
        lines.append(f"- 输出风格：`{style}`")
        lines.append("- 方法依据：`core/SKILL.md` + ISA95 + IEC62443")
        lines.append("- 模板来源：`core/templates/customer-solution-template.md`")
    else:
        lines.append("- 设计依据：工业网络分层承载、边界隔离、受控访问与运维可管可控原则")
    lines.append("")

    if style == "formal":
        lines.extend(_build_executive_summary(plan))
        for chapter in _formal_ordered_chapters(plan.chapters):
            if chapter.title in HIDE_FORMAL_TITLES:
                continue
            _render_formal_chapter(lines, plan, chapter)
    else:
        for chapter in plan.chapters:
            _render_draft_chapter(lines, chapter)

    lines.append("## 附录")
    lines.append("")
    if style == "formal":
        lines.append("**对象清单摘要**")
        lines.append("")
        if plan.appendix_assets:
            asset_text = "、".join(item.text for item in plan.appendix_assets[:6])
            lines.append(f"- 方案涉及的主要对象包括：{asset_text}。")
        else:
            lines.append("- 当前未补充对象清单摘要。")
        lines.append("")

        lines.append("**网络规划摘要**")
        lines.append("")
        if plan.appendix_networks:
            lines.append(f"- 地址与分段规划按以下结果执行：{plan.appendix_networks[0].text}。")
        else:
            lines.append("- 当前未补充地址规划摘要。")
        if plan.appendix_links:
            communication_summary = "；".join(item.text for item in plan.appendix_links[:3])
            lines.append(f"- 关键连接关系包括：{communication_summary}。")
        else:
            lines.append("- 当前未补充关键连接摘要。")
        lines.append("")
    else:
        lines.append("**核心资产清单**")
        lines.append("")
        if plan.appendix_assets:
            for item in plan.appendix_assets:
                lines.append(f"- {item.text}（来源：`{item.source}`）")
        else:
            lines.append("- 当前未记录资产对象。")
        lines.append("")

        lines.append("**通信关系摘要**")
        lines.append("")
        if plan.appendix_links:
            for item in plan.appendix_links:
                lines.append(f"- {item.text}（来源：`{item.source}`）")
        else:
            lines.append("- 当前未记录通信关系。")
        lines.append("")

        lines.append("**地址规划摘要**")
        lines.append("")
        if plan.appendix_networks:
            for item in plan.appendix_networks:
                lines.append(f"- {item.text}（来源：`{item.source}`）")
        else:
            lines.append("- 当前未记录地址规划信息。")
        lines.append("")

        dedup_pending = []
        seen_pending = set()
        for chapter in plan.chapters:
            for item in chapter.pending_items:
                key = item.text.strip()
                if key and key not in seen_pending:
                    seen_pending.add(key)
                    dedup_pending.append(item)

        lines.append("## 输出前自检")
        lines.append("")
        lines.append("**通过项**")
        lines.append("")
        if plan.audit.checks:
            for item in plan.audit.checks:
                lines.append(f"- {item}")
        else:
            lines.append("- 当前未记录通过项。")
        lines.append("")
        lines.append("**警告项**")
        lines.append("")
        if plan.audit.warnings:
            for item in plan.audit.warnings:
                lines.append(f"- {item}")
        else:
            lines.append("- 当前未发现结构性装配问题。")
        lines.append("")

        lines.append("## 证据边界说明")
        lines.append("")
        lines.append("- 当高优先级事实与较低优先级设计结论存在冲突时，优先保留事实，并将设计内容降级为建议或待确认。")
        lines.append("- 涉及现场复核项与客户确认项的结论，不输出为实施定稿。")
        lines.append("")
        lines.append("## 装配注记")
        lines.append("")
        lines.append("- 文档按固定章节结构输出，优先装配事实，再装配建议，再单列假设与待确认项。")
        lines.append("- 若地址、边界或部署信息不足，当前版本仅输出规划原则与建议，不输出确定性定稿结论。")
        lines.append(f"- 模板加载字符数：{len(assets.template)}")
        lines.append(f"- 大纲加载字符数：{len(assets.report_outline)}")
        lines.append(f"- 装配规则加载字符数：{len(assets.document_rules)}")
        lines.append("")
    return "\n".join(lines)
