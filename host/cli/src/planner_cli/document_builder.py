from __future__ import annotations

from planner_cli.document_model import Appendix, BulletBlock, DiagramBlock, DocumentMeta, DocumentModel, ParagraphBlock, Section, TableBlock
from planner_cli.planner import PlanBundle
from planner_cli.renderer import FORMAL_TITLE_MAP, HIDE_FORMAL_TITLES, _build_boundary_topology_mermaid, _build_formal_tables, _build_topology_mermaid, _formal_ordered_chapters, _formalize_result_text

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
        return DiagramBlock(title=title, diagram_type=title, source_format='mermaid', content='\n'.join(lines))

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
    for chapter in chapters:
        if style == 'formal' and chapter.title in HIDE_FORMAL_TITLES:
            continue
        section = Section(title=FORMAL_TITLE_MAP.get(chapter.title, chapter.title))
        if chapter.title == '网络拓扑与通信路径说明':
            overall = DiagramBlock(title='总体拓扑图', diagram_type='overall-topology', source_format='mermaid', content=_build_topology_mermaid(plan))
            boundary = DiagramBlock(title='重点边界拓扑图', diagram_type='boundary-topology', source_format='mermaid', content=_build_boundary_topology_mermaid(plan))
            section.diagrams.extend([overall, boundary])
            appendix_topology.extend(_build_focus_diagrams(plan))
        for table_title, headers, rows in _build_formal_tables(plan, chapter):
            section.tables.append(TableBlock(title=table_title.replace('**', ''), headers=headers, rows=rows))
        if chapter.conclusion:
            section.paragraphs.append(ParagraphBlock(text=f'【{RESULT_TITLES.get(chapter.title, "本章结论")}】{_formalize_result_text(chapter.conclusion)}'))
        elif chapter.narrative and chapter.title in {'项目概述与建设目标', '现状网络与调研结论', '需求与约束分析', '技术选择与方案比较'}:
            section.paragraphs.append(ParagraphBlock(text=f'【{RESULT_TITLES.get(chapter.title, "本章结论")}】{_formalize_result_text(chapter.narrative)}'))
        if chapter.confirmed_facts:
            label = '现状与已知条件' if chapter.title in {'项目概述与建设目标', '现状网络与调研结论'} else '设计依据'
            limit = 3 if chapter.title in {'网络拓扑与通信路径说明', 'IP 地址、VLAN 与子网规划', '关键设备与部署建议'} else 4
            section.bullets.append(BulletBlock(title=label, items=_items(chapter.confirmed_facts, limit=limit)))
        if chapter.recommendations and chapter.title not in {'结论与建议'}:
            label = '方案说明' if chapter.title != '实施步骤与迁移建议' else '实施安排'
            limit = 3 if chapter.title in {'网络拓扑与通信路径说明', 'IP 地址、VLAN 与子网规划', '关键设备与部署建议'} else 4
            section.bullets.append(BulletBlock(title=label, items=_items(chapter.recommendations, limit=limit)))
        if chapter.pending_items:
            section.bullets.append(BulletBlock(title='待确认项', items=_items(chapter.pending_items, limit=3)))
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
