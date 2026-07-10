from __future__ import annotations

from planner_cli.document_model import Appendix, BulletBlock, DiagramBlock, DocumentMeta, DocumentModel, ParagraphBlock, Section, TableBlock
from planner_cli.graphviz_renderer import build_diagram_dot
from planner_cli.planner import PlanBundle
from planner_cli.formal_support import COMPACT_SECTION_GROUPS, FORMAL_TITLE_MAP, HIDE_FORMAL_TITLES, _build_boundary_topology_mermaid, _build_formal_tables, _build_topology_mermaid, _formal_ordered_chapters, _formalize_result_text

RESULT_TITLES = {
    '项目概述与建设目标': '本节结论',
    '现状网络与调研结论': '调研结论摘要',
    '设计依据与方法说明': '设计说明',
    '需求与约束分析': '需求与约束结论',
    '技术选择与方案比较': '技术选择说明',
    '总体网络架构方案': '架构说明',
    'IEC62443 分区分域与安全边界设计': '边界控制说明',
    '网络拓扑与通信路径说明': '通信路径说明',
    'IP 地址、VLAN 与子网规划': '地址规划说明',
    '关键设备与部署建议': '设备部署说明',
    '通信与运维接入方案': '运维接入说明',
    '实施步骤与迁移建议': '实施安排',
    '风险、假设与待确认项': '风险说明',
    '结论与建议': '执行结论',
}


def _items(items, limit=None):
    values = items[:limit] if limit is not None else items
    return [_formalize_result_text(item.text) for item in values]


def _raw_items(items, limit=None):
    values = items[:limit] if limit is not None else items
    return [item.text.strip() for item in values if item.text.strip()]


def _normalize_raw_text(text: str) -> str:
    value = text.strip()
    prefixes = [
        '边界问题：', '关键链路：', '调研观察：', '调研发现：', '调研关注：', '业务通信：', '访问路径：',
        '系统对象：', '角色对象：', '部署位置：', '环境约束：', '现场关注：', '拓扑结构：', '冗余线索：',
        '性能线索：', '通信流：', '拓扑链路：', '现网地址现状：', '地址约束：', '调研关注风险：'
    ]
    for prefix in prefixes:
        if value.startswith(prefix):
            value = value[len(prefix):].strip()
            break
    return value


def _numbered(items: list[str]) -> list[str]:
    return [f'{index + 1}. {_normalize_raw_text(item)}' for index, item in enumerate(items)]


def _constraint_items(items, limit=None):
    values = items[:limit] if limit is not None else items
    return [_formalize_result_text(item.text) for item in values if item.text.strip()]


def _response_items(items, limit=None):
    values = items[:limit] if limit is not None else items
    return [_formalize_result_text(item.text) for item in values if item.text.strip()]


def _response_blocks(chapter_title: str, chapter) -> list[BulletBlock]:
    recs = chapter.recommendations
    blocks: list[BulletBlock] = []

    def pick(title: str, keywords: list[str], limit: int = 4):
        matched = []
        for item in recs:
            text = item.text.strip()
            if any(keyword in text for keyword in keywords):
                matched.append(_formalize_result_text(text))
        if matched:
            blocks.append(BulletBlock(title=title, items=matched[:limit]))

    if chapter_title == '总体网络架构方案':
        pick('架构响应', ['核心', '汇聚', '分层', '架构', '边界收口'], 4)
        pick('边界响应', ['边界', '分区', '独立', '受控'], 4)
        return blocks

    if chapter_title == '拓扑结构与冗余设计说明':
        pick('拓扑响应', ['星型', '环网', '双上联', '拓扑'], 4)
        pick('冗余响应', ['冗余', '高可用', '关键链路', '设备冗余'], 4)
        return blocks

    if chapter_title == '带宽与性能设计说明':
        pick('性能与时延响应', ['带宽', '时延', '广播域', '视频', '流量'], 4)
        return blocks

    if chapter_title == 'IP 地址、VLAN 与子网规划':
        pick('地址分段响应', ['地址', 'VLAN', '子网', '命名', '预留'], 4)
        return blocks

    if chapter_title == '关键设备与部署建议':
        pick('设备与部署响应', ['部署', '设备', '机房', '汇聚交换机', '边界'], 4)
        return blocks

    if chapter_title == '通信与运维接入方案':
        pick('通信与运维响应', ['运维', '访问', '审计', '白名单', '远程'], 4)
        return blocks

    if recs:
        blocks.append(BulletBlock(title='设计响应', items=_response_items(recs, limit=4)))
    return blocks


def _group_raw_inputs(chapter_title: str, chapter) -> list[BulletBlock]:
    facts = chapter.confirmed_facts
    grouped: list[BulletBlock] = []

    def pick(title: str, keywords: list[str], limit: int = 4):
        matched = []
        for item in facts:
            text = item.text.strip()
            if any(keyword in text for keyword in keywords):
                matched.append(text)
        if matched:
            grouped.append(BulletBlock(title=title, items=_numbered(matched[:limit])))

    if chapter_title == '业务分析与系统协同':
        pick('业务场景与通信记录', ['业务通信', '访问路径'], 6)
        pick('系统对象与角色归属', ['系统对象', '角色对象'], 6)
        pick('部署位置与协同界面', ['部署位置'], 4)
        return grouped

    if chapter_title == '现状网络与调研结论':
        pick('现场观察记录', ['调研观察'], 4)
        pick('调研发现记录', ['调研发现'], 4)
        pick('调研关注记录', ['调研关注', '边界问题', '关键链路'], 5)
        return grouped

    if chapter_title == '现场环境与工程约束':
        pick('环境与安装条件', ['环境约束', '现场关注'], 6)
        return grouped

    if chapter_title == '总体网络架构方案':
        pick('架构与分层原始依据', ['设计原则', '边界要求'], 6)
        pick('现网层级与边界线索', ['现网层级', '边界问题'], 5)
        return grouped

    if chapter_title == '拓扑结构与冗余设计说明':
        pick('拓扑结构原始记录', ['拓扑结构'], 6)
        pick('冗余诉求原始记录', ['冗余线索'], 5)
        return grouped

    if chapter_title == '带宽与性能设计说明':
        pick('性能与流量线索', ['性能线索', '通信流'], 6)
        pick('访问路径与链路线索', ['访问路径', '拓扑链路'], 6)
        return grouped

    if chapter_title == 'IP 地址、VLAN 与子网规划':
        pick('地址继承与保留条件', ['现网地址现状', '地址约束', '保留网段', '命名规则', 'VLAN 组织'], 6)
        return grouped

    if chapter_title == '关键设备与部署建议':
        pick('设备与部署原始条件', ['设备对象', '部署位置', '关键等级'], 6)
        return grouped

    if chapter_title == '风险、假设与待确认项':
        pick('原始风险触发点', ['调研关注风险'], 5)
        return grouped

    if facts:
        grouped.append(BulletBlock(title='基础事实记录', items=_numbered(_raw_items(facts, limit=4))))
    return grouped


def _to_graphviz_diagram(title: str, diagram_type: str, mermaid_content: str) -> DiagramBlock:
    dot, error = build_diagram_dot(DiagramBlock(title=title, diagram_type=diagram_type, source_format='mermaid', content=mermaid_content))
    content = dot if not error and dot else mermaid_content
    source_format = 'graphviz' if not error and dot else 'mermaid'
    return DiagramBlock(title=title, diagram_type=diagram_type, source_format=source_format, content=content)


def _build_focus_diagrams(plan: PlanBundle) -> list[DiagramBlock]:
    delivery = plan.appendix_delivery or {}
    nodes = delivery.get('topologyNodes') or []
    links = delivery.get('topologyLinks') or []
    if not nodes or not links:
        return []

    def make_diagram(title: str, zone_ids: list[str], node_ids: set[str] | None = None) -> DiagramBlock:
        zone_map = {str(item.get('id', '')).strip(): str(item.get('title', item.get('id', '区域'))).strip() or '区域' for item in delivery.get('topologyZones', [])}
        lines = ['```mermaid', 'flowchart LR']
        selected = []
        if node_ids is None:
            for item in nodes:
                if str(item.get('zone', '')).strip() in zone_ids:
                    selected.append(item)
        else:
            for item in nodes:
                if str(item.get('id', '')).strip() in node_ids:
                    selected.append(item)
        selected_ids = {str(item.get('id', '')).strip() for item in selected}
        for zid in zone_ids:
            title_text = zone_map.get(zid, zid)
            lines.append(f'    subgraph {zid}["{title_text}"]')
            for item in selected:
                if str(item.get('zone', '')).strip() == zid:
                    nid = str(item.get('id', '')).strip()
                    label = str(item.get('label', nid)).strip() or nid
                    lines.append(f'        {nid}["{label}"]')
            lines.append('    end')
        for item in links:
            source = str(item.get('source', '')).strip()
            target = str(item.get('target', '')).strip()
            label = str(item.get('label', '')).strip()
            style = str(item.get('style', 'solid')).strip()
            if source not in selected_ids or target not in selected_ids:
                continue
            connector = '-."' + label.replace('"', '') + '".-' if style == 'dashed' and label else ('-->|"' + label.replace('"', '') + '"|' if label else '-->')
            lines.append(f'    {source} {connector} {target}' if connector != '-->' else f'    {source} --> {target}')
        lines.append('```')
        return _to_graphviz_diagram(title, title, '\n'.join(lines))

    return [
        make_diagram('核心区设备拓扑图', ['ZONE-CORE']),
        make_diagram('边界与接口拓扑图', ['ZONE-DMZ', 'ZONE-CORE']),
        make_diagram('关键系统独立边界图', ['ZONE-CRITICAL', 'ZONE-CORE']),
        make_diagram('生产支撑接入拓扑图', ['ZONE-FIELD', 'ZONE-CORE']),
    ]


def build_document_model(plan: PlanBundle, style: str = 'formal') -> DocumentModel:
    meta = DocumentMeta(project_name=plan.project_name, customer_name=plan.customer_name, site_name=plan.site_name, objective=plan.objective, scope=plan.scope)
    model = DocumentModel(meta=meta)
    chapters = _formal_ordered_chapters(plan.chapters) if style == 'formal' else plan.chapters
    appendix_topology = []
    raw_sections = []
    for chapter in chapters:
        if style == 'formal' and chapter.title in HIDE_FORMAL_TITLES:
            continue
        section = Section(title=FORMAL_TITLE_MAP.get(chapter.title, chapter.title))
        if chapter.title == '网络拓扑与通信路径说明':
            overall = _to_graphviz_diagram('总体拓扑图', 'overall-topology', _build_topology_mermaid(plan))
            boundary = _to_graphviz_diagram('重点边界拓扑图', 'boundary-topology', _build_boundary_topology_mermaid(plan))
            section.diagrams.extend([overall, boundary])
            appendix_topology.extend(_build_focus_diagrams(plan))
        for table_title, headers, rows in _build_formal_tables(plan, chapter):
            section.tables.append(TableBlock(title=table_title.replace('**', ''), headers=headers, rows=rows))
        if chapter.conclusion:
            section.paragraphs.append(ParagraphBlock(text=_formalize_result_text(chapter.conclusion)))
        elif chapter.narrative and chapter.title in {'项目概述与建设目标', '现状网络与调研结论', '需求与约束分析', '技术选择与方案比较'}:
            section.paragraphs.append(ParagraphBlock(text=_formalize_result_text(chapter.narrative)))
        section.raw_inputs.extend(_group_raw_inputs(chapter.title, chapter))
        if chapter.recommendations and chapter.title in {'业务分析与系统协同', '现状网络与调研结论', '现场环境与工程约束', '总体网络架构方案', '拓扑结构与冗余设计说明', '带宽与性能设计说明', 'IP 地址、VLAN 与子网规划', '关键设备与部署建议'}:
            section.derived_constraints.append(BulletBlock(title='关键设计约束', items=_constraint_items(chapter.recommendations, limit=4)))
        section.design_responses.extend(_response_blocks(chapter.title, chapter))
        if chapter.confirmed_facts and chapter.title not in {'业务分析与系统协同', '现状网络与调研结论', '现场环境与工程约束'}:
            label = '现状与已知条件' if chapter.title in {'项目概述与建设目标', '现状网络与调研结论'} else '设计依据'
            limit = 3 if chapter.title in {'网络拓扑与通信路径说明', 'IP 地址、VLAN 与子网规划', '关键设备与部署建议'} else 4
            section.bullets.append(BulletBlock(title=label, items=_items(chapter.confirmed_facts, limit=limit)))
        if chapter.recommendations and chapter.title not in {'结论与建议', '总体网络架构方案', '拓扑结构与冗余设计说明', '带宽与性能设计说明', 'IP 地址、VLAN 与子网规划', '关键设备与部署建议', '通信与运维接入方案'}:
            label = '方案说明' if chapter.title != '实施步骤与迁移建议' else '实施安排'
            limit = 3 if chapter.title in {'网络拓扑与通信路径说明', 'IP 地址、VLAN 与子网规划', '关键设备与部署建议'} else 4
            section.bullets.append(BulletBlock(title=label, items=_items(chapter.recommendations, limit=limit)))
        if chapter.pending_items:
            section.bullets.append(BulletBlock(title='待确认项', items=_items(chapter.pending_items, limit=3)))
        raw_sections.append((chapter.title, section))

    if style == 'formal':
        section_map = {title: section for title, section in raw_sections}
        for group_title, chapter_titles in COMPACT_SECTION_GROUPS:
            merged = Section(title=group_title)
            for chapter_title in chapter_titles:
                section = section_map.get(chapter_title)
                if not section:
                    continue
                merged.paragraphs.extend(section.paragraphs)
                merged.raw_inputs.extend(section.raw_inputs)
                merged.derived_constraints.extend(section.derived_constraints)
                merged.design_responses.extend(section.design_responses)
                merged.tables.extend(section.tables)
                merged.diagrams.extend(section.diagrams)
                merged.bullets.extend(section.bullets)
            if any([merged.paragraphs, merged.tables, merged.diagrams, merged.bullets]):
                model.sections.append(merged)
    else:
        for _, section in raw_sections:
            model.sections.append(section)
    appendix = Appendix(title='附录')
    if plan.appendix_assets:
        appendix.paragraphs.append(ParagraphBlock(text='方案涉及对象摘要：' + '、'.join(item.text for item in plan.appendix_assets[:6]) + '。'))
    if plan.appendix_networks:
        appendix.paragraphs.append(ParagraphBlock(text='网络规划摘要：' + plan.appendix_networks[0].text + '。'))
    if plan.appendix_links:
        appendix.paragraphs.append(ParagraphBlock(text='关键连接摘要：' + '；'.join(item.text for item in plan.appendix_links[:3]) + '。'))
    appendix.diagrams.extend(appendix_topology)
    model.appendices.append(appendix)
    return model
