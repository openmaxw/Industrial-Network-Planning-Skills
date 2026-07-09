from __future__ import annotations

import html
import re
from planner_cli.document_model import DiagramBlock

WIDTH = 1800
HEIGHT = 980


def _strip_mermaid(content: str) -> list[str]:
    return [raw.strip() for raw in content.splitlines() if raw.strip() and not raw.strip().startswith('```') and not raw.strip().startswith('flowchart')]


def _parse_mermaid(diagram: DiagramBlock):
    lines = _strip_mermaid(diagram.content)
    groups, ungrouped, edges = [], [], []
    current_group = None
    subgraph_re = re.compile(r'^subgraph\s+([A-Za-z0-9_\-]+)\["(.+?)"\]$')
    node_re = re.compile(r'^([A-Za-z0-9_\-/]+)\["(.+?)"\]$')
    patterns = [
        re.compile(r'^([A-Za-z0-9_\-/]+)\s+--\>\|"(.+?)"\|\s+([A-Za-z0-9_\-/]+)$'),
        re.compile(r'^([A-Za-z0-9_\-/]+)\s+-\."(.+?)"\.-\s+([A-Za-z0-9_\-/]+)$'),
        re.compile(r'^([A-Za-z0-9_\-/]+)\s+-->\s+([A-Za-z0-9_\-/]+)$'),
    ]
    for line in lines:
        if line == 'end':
            current_group = None
            continue
        m = subgraph_re.match(line)
        if m:
            current_group = {'title': m.group(2), 'nodes': []}
            groups.append(current_group)
            continue
        m = node_re.match(line)
        if m:
            pair = (m.group(1), m.group(2))
            if current_group is not None:
                current_group['nodes'].append(pair)
            else:
                ungrouped.append(pair)
            continue
        for idx, pattern in enumerate(patterns):
            m = pattern.match(line)
            if m:
                if idx < 2:
                    edges.append((m.group(1), m.group(3), m.group(2), idx == 1))
                else:
                    edges.append((m.group(1), m.group(2), '', False))
                break
    return groups, ungrouped, edges


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _node_style(label: str):
    if '防火墙' in label:
        return ('#fee2e2', '#dc2626', '#7f1d1d')
    if '核心交换机' in label:
        return ('#dbeafe', '#2563eb', '#1e3a8a')
    if '汇聚交换机' in label:
        return ('#e0f2fe', '#0284c7', '#0c4a6e')
    if '服务器' in label:
        return ('#ede9fe', '#7c3aed', '#4c1d95')
    return ('#ffffff', '#2563eb', '#1e293b')


def render_diagram_svg(diagram: DiagramBlock) -> str:
    groups, ungrouped, edges = _parse_mermaid(diagram)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">']
    parts.append('<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#334155"/></marker></defs>')
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>')
    parts.append(f'<text x="44" y="46" font-size="22" font-weight="700" fill="#0f172a">{_esc(diagram.title or "网络拓扑图")}</text>')
    positions = {}
    if groups:
        gap = 16
        usable = WIDTH - 88
        group_w = (usable - gap * (len(groups)-1)) // len(groups)
        for idx, group in enumerate(groups):
            x1 = 44 + idx * (group_w + gap)
            y1 = 72
            y2 = HEIGHT - 42
            parts.append(f'<rect x="{x1}" y="{y1}" width="{group_w}" height="{y2-y1}" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>')
            parts.append(f'<rect x="{x1+10}" y="{y1+10}" width="220" height="32" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>')
            parts.append(f'<text x="{x1+22}" y="{y1+31}" font-size="17" font-weight="700" fill="#1e40af">{_esc(group["title"])}</text>')
            node_w = group_w - 28
            node_h = 66
            node_gap = 14
            max_nodes = max(1, len(group['nodes']))
            total_h = max_nodes * node_h + (max_nodes - 1) * node_gap
            start_y = y1 + 58 + max(0, ((y2 - y1 - 70) - total_h) // 2)
            for n_idx, (node_id, label) in enumerate(group['nodes']):
                ny1 = start_y + n_idx * (node_h + node_gap)
                fill, stroke, text_color = _node_style(label)
                parts.append(f'<rect x="{x1+14}" y="{ny1}" width="{node_w}" height="{node_h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>')
                parts.append(f'<text x="{x1+28}" y="{ny1+40}" font-size="14" font-weight="600" fill="{text_color}">{_esc(label)}</text>')
                positions[node_id] = {'x1': x1+14, 'y1': ny1, 'x2': x1+14+node_w, 'y2': ny1+node_h, 'cx': x1+14+node_w//2, 'cy': ny1+node_h//2}
    for sid, tid, label, dashed in edges:
        if sid not in positions or tid not in positions:
            continue
        s, t = positions[sid], positions[tid]
        start = (s['x2'], s['cy']) if s['cx'] <= t['cx'] else (s['x1'], s['cy'])
        end = (t['x1'], t['cy']) if s['cx'] <= t['cx'] else (t['x2'], t['cy'])
        dash_attr = ' stroke-dasharray="8 5"' if dashed else ''
        parts.append(f'<line x1="{start[0]}" y1="{start[1]}" x2="{end[0]}" y2="{end[1]}" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"{dash_attr}/>')
        if label:
            short = label[:14]
            mid_x = (start[0]+end[0])//2
            mid_y = (start[1]+end[1])//2 - 12
            parts.append(f'<rect x="{mid_x-62}" y="{mid_y-12}" width="124" height="24" rx="6" fill="#fff" stroke="#cbd5e1" stroke-width="1"/>')
            parts.append(f'<text x="{mid_x}" y="{mid_y+5}" text-anchor="middle" font-size="12" fill="#1e293b">{_esc(short)}</text>')
    parts.append('</svg>')
    return ''.join(parts)
