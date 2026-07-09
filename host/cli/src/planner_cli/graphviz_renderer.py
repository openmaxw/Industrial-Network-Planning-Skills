from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from planner_cli.document_model import DiagramBlock
from planner_cli.graphviz_support import has_graphviz


def _dot_id(value: str) -> str:
    return 'n_' + ''.join(ch if ch.isalnum() else '_' for ch in value)


def _dot_label(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"')


def _wrap_label(value: str, max_chars: int = 10) -> str:
    text = value.strip()
    if len(text) <= max_chars:
        return text
    parts = []
    while text:
        parts.append(text[:max_chars])
        text = text[max_chars:]
    return '\n'.join(parts)


def _strip_mermaid(content: str) -> list[str]:
    return [raw.strip() for raw in content.splitlines() if raw.strip() and not raw.strip().startswith('```') and not raw.strip().startswith('flowchart')]


def _parse_mermaid(diagram: DiagramBlock):
    import re
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
            current_group = {'id': m.group(1), 'title': m.group(2), 'nodes': []}
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


def _cluster_style(group_id: str, title: str) -> tuple[str, str, str]:
    text = f'{group_id} {title}'
    if 'DMZ' in text or '边界' in title or '接口' in title:
        return '#eef5ff', '#6aa7ff', '#1d4ed8'
    if 'CORE' in text or '核心' in title:
        return '#eef2ff', '#8b9cf6', '#4338ca'
    if 'FIELD' in text or '接入' in title or '汇聚' in title:
        return '#ecfeff', '#67d7ef', '#0f766e'
    if 'CRITICAL' in text or '关键' in title:
        return '#fff7ed', '#fdba74', '#c2410c'
    return '#f8fafc', '#cbd5e1', '#334155'


def _node_style(node_id: str, label: str) -> tuple[str, str, str]:
    text = f'{node_id} {label}'
    if 'FW' in text or '防火墙' in label:
        return '#fff1f2', '#fb7185', '#9f1239'
    if 'SW' in text or '交换机' in label:
        return '#eff6ff', '#60a5fa', '#1d4ed8'
    if 'SRV' in text or '服务器' in label or 'APP' in text or 'DB' in text or 'HIS' in text:
        return '#f5f3ff', '#a78bfa', '#6d28d9'
    if 'AUDIT' in text or '审计' in label or '堡垒机' in label:
        return '#ecfdf5', '#34d399', '#047857'
    if 'WS' in text or '工作站' in label or '终端' in label:
        return '#f8fafc', '#94a3b8', '#334155'
    if 'GW' in text or '网关' in label:
        return '#fff7ed', '#fdba74', '#c2410c'
    return '#ffffff', '#94a3b8', '#1f2937'


def build_diagram_dot(diagram: DiagramBlock) -> tuple[str, str | None]:
    if diagram.source_format == 'graphviz':
        return diagram.content, None
    if diagram.source_format != 'mermaid':
        return '', f'unsupported:{diagram.source_format}'

    try:
        groups, ungrouped, edges = _parse_mermaid(diagram)
        lines = [
            'digraph G {',
            'graph [rankdir=LR, bgcolor="white", splines=ortho, nodesep=1.1, ranksep=1.4, pad=0.55, margin=0.25, fontname="Arial", labelloc="t", labeljust="l"];',
            'node [shape=box, style="rounded,filled", fillcolor="#ffffff", color="#94a3b8", penwidth=1.7, fontname="Arial", fontsize=13, margin="0.24,0.16"];',
            'edge [color="#475569", penwidth=1.9, arrowsize=0.85, fontname="Arial", fontsize=10, labelfontsize=10, labeldistance=2.0, labelangle=20];',
            f'label="{_dot_label(diagram.title)}";',
            'fontsize=22;',
            'fontcolor="#0f172a";',
            'compound=true;',
            'newrank=true;',
        ]

        for group in groups:
            fill, border, font = _cluster_style(group['id'], group['title'])
            lines.append(f'subgraph cluster_{_dot_id(group["id"])} {{')
            lines.append(f'label="{_dot_label(group["title"])}"; color="{border}"; fontcolor="{font}"; pencolor="{border}"; penwidth=1.8; style="rounded,filled"; fillcolor="{fill}"; margin=30; labeljust="l";')
            for node_id, label in group['nodes']:
                node_fill, node_border, node_font = _node_style(node_id, label)
                lines.append(f'"{_dot_id(node_id)}" [label="{_dot_label(_wrap_label(label, 10))}", width=1.7, height=0.78, fillcolor="{node_fill}", color="{node_border}", fontcolor="{node_font}"];')
            lines.append('}')

        for node_id, label in ungrouped:
            node_fill, node_border, node_font = _node_style(node_id, label)
            lines.append(f'"{_dot_id(node_id)}" [label="{_dot_label(_wrap_label(label, 10))}", width=1.7, height=0.78, fillcolor="{node_fill}", color="{node_border}", fontcolor="{node_font}"];')

        lines.append('legend [shape=plain, margin=0, label=<')
        lines.append('<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="7" COLOR="#cbd5e1">')
        lines.append('<TR><TD COLSPAN="2" BGCOLOR="#f8fafc"><B>图例</B></TD></TR>')
        lines.append('<TR><TD BGCOLOR="#fff1f2">边界防护</TD><TD>防火墙 / 安全边界</TD></TR>')
        lines.append('<TR><TD BGCOLOR="#eff6ff">交换网络</TD><TD>核心 / 汇聚 / 接入交换机</TD></TR>')
        lines.append('<TR><TD BGCOLOR="#f5f3ff">平台服务</TD><TD>应用 / 数据 / 接口服务器</TD></TR>')
        lines.append('<TR><TD BGCOLOR="#ecfdf5">运维审计</TD><TD>堡垒机 / 审计访问</TD></TR>')
        lines.append('<TR><TD BGCOLOR="#fff7ed">接口设备</TD><TD>网关 / 协议接入</TD></TR>')
        lines.append('<TR><TD COLSPAN="2" ALIGN="LEFT">实线：主业务/主干链路；虚线：受控访问/运维/数据交互</TD></TR>')
        lines.append('</TABLE>>];')

        for sid, tid, label, dashed in edges:
            attrs = []
            if label:
                attrs.append(f'label="{_dot_label(label)}"')
            if dashed:
                attrs.extend(['style="dashed"', 'color="#f59e0b"', 'fontcolor="#b45309"'])
            else:
                attrs.extend(['color="#475569"', 'fontcolor="#475569"'])
            attr_text = ' [' + ', '.join(attrs) + ']' if attrs else ''
            lines.append(f'"{_dot_id(sid)}" -> "{_dot_id(tid)}"{attr_text};')

        if groups and groups[-1]['nodes']:
            lines.append(f'"{_dot_id(groups[-1]["nodes"][-1][0])}" -> legend [style="invis", weight=0, minlen=2];')

        lines.append('}')
        return '\n'.join(lines), None
    except Exception as exc:
        return '', f'error:{exc}'


def render_diagram_svg_graphviz(diagram: DiagramBlock) -> str:
    if not has_graphviz():
        return ''
    dot, error = build_diagram_dot(diagram)
    if error:
        raise RuntimeError(error)
    with tempfile.TemporaryDirectory(prefix='planner-dot-') as tmpdir:
        dot_path = Path(tmpdir) / 'graph.dot'
        svg_path = Path(tmpdir) / 'graph.svg'
        dot_path.write_text(dot, encoding='utf-8')
        subprocess.run(['dot', '-Tsvg', str(dot_path), '-o', str(svg_path)], check=True, capture_output=True)
        return svg_path.read_text(encoding='utf-8')


def render_diagram_svg_auto(diagram: DiagramBlock) -> tuple[str, str | None]:
    if not has_graphviz():
        return '', 'missing'
    try:
        return render_diagram_svg_graphviz(diagram), None
    except Exception as exc:
        return '', f'error:{exc}'
