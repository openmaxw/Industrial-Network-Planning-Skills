from __future__ import annotations

import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from planner_cli.document_model import DiagramBlock

WIDTH = 2200
HEIGHT = 1400
BG = (255, 255, 255)
FRAME = (203, 213, 225)
TITLE = (15, 23, 42)
SUBTITLE = (71, 85, 105)
TEXT = (30, 41, 59)
BLUE = (37, 99, 235)
BLUE_LIGHT = (219, 234, 254)
GRAY = (100, 116, 139)
ZONE_FILL = (248, 250, 252)
NODE_FILL = (255, 255, 255)
LINE = (51, 65, 85)


def _font(size: int, bold: bool = False):
    candidates = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if bold else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _strip_mermaid(content: str) -> list[str]:
    return [raw.strip() for raw in content.splitlines() if raw.strip() and not raw.strip().startswith('```') and not raw.strip().startswith('flowchart')]


def _parse_mermaid(diagram: DiagramBlock):
    lines = _strip_mermaid(diagram.content)
    groups = []
    ungrouped = []
    edges = []
    current_group = None
    subgraph_re = re.compile(r'^subgraph\s+([A-Za-z0-9_]+)\["(.+?)"\]$')
    node_re = re.compile(r'^([A-Za-z0-9_一-龥/]+)\["(.+?)"\]$')
    edge_patterns = [
        re.compile(r'^([A-Za-z0-9_一-龥/]+)\s+[-.]*-+>\|"(.+?)"\|\s+([A-Za-z0-9_一-龥/]+)$'),
        re.compile(r'^([A-Za-z0-9_一-龥/]+)\s+[-.]*-+\."(.+?)"\.-\s+([A-Za-z0-9_一-龥/]+)$'),
        re.compile(r'^([A-Za-z0-9_一-龥/]+)\s+[-.]*-+>\s+([A-Za-z0-9_一-龥/]+)$'),
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
        for idx, pattern in enumerate(edge_patterns):
            m = pattern.match(line)
            if m:
                if idx < 2:
                    edges.append((m.group(1), m.group(3), m.group(2)))
                else:
                    edges.append((m.group(1), m.group(2), ''))
                break
    return groups, ungrouped, edges


def _wrap(draw, text, font, max_width):
    lines, current = [], ''
    for ch in text:
        trial = current + ch
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines or [text]


def _draw_centered_text(draw, text, box, font, fill=TEXT, line_gap=6):
    x1, y1, x2, y2 = box
    lines = _wrap(draw, text, font, x2 - x1 - 20)
    line_h = max(26, draw.textbbox((0, 0), '测', font=font)[3] + line_gap)
    total_h = line_h * len(lines)
    y = y1 + max(10, ((y2 - y1) - total_h) // 2)
    for line in lines:
        w = draw.textbbox((0, 0), line, font=font)[2]
        x = x1 + ((x2 - x1) - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h


def _draw_arrow(draw, start, end, color=LINE, width=4, dashed=False):
    if dashed:
        total = math.dist(start, end)
        if total == 0:
            return
        dash, gap = 18, 10
        dx = (end[0] - start[0]) / total
        dy = (end[1] - start[1]) / total
        pos = 0
        while pos < total:
            seg_end = min(total, pos + dash)
            p1 = (start[0] + dx * pos, start[1] + dy * pos)
            p2 = (start[0] + dx * seg_end, start[1] + dy * seg_end)
            draw.line([p1, p2], fill=color, width=width)
            pos += dash + gap
    else:
        draw.line([start, end], fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 14
    p1 = (end[0] - size * math.cos(angle - math.pi / 7), end[1] - size * math.sin(angle - math.pi / 7))
    p2 = (end[0] - size * math.cos(angle + math.pi / 7), end[1] - size * math.sin(angle + math.pi / 7))
    draw.polygon([end, p1, p2], fill=color)


def _draw_title_block(draw, diagram_title, page_title_font, meta_font):
    draw.rounded_rectangle([40, 30, WIDTH - 40, 120], radius=14, outline=FRAME, width=2, fill=(255, 255, 255))
    draw.text((70, 48), diagram_title or '网络拓扑图', font=page_title_font, fill=TITLE)
    draw.text((WIDTH - 620, 52), '图纸类型：网络方案拓扑图', font=meta_font, fill=SUBTITLE)
    draw.text((WIDTH - 620, 80), '输出方式：自动生成工程示意图', font=meta_font, fill=SUBTITLE)


def _draw_footer(draw, meta_font):
    y1 = HEIGHT - 90
    draw.rounded_rectangle([40, y1, WIDTH - 40, HEIGHT - 30], radius=10, outline=FRAME, width=2, fill=(255, 255, 255))
    draw.text((70, y1 + 18), '说明：本图用于方案交付阶段展示网络分区、边界与主要通信路径。', font=meta_font, fill=SUBTITLE)
    draw.text((WIDTH - 430, y1 + 18), 'Industrial Network Planner', font=meta_font, fill=SUBTITLE)


def render_diagram_png(diagram: DiagramBlock, output_path: Path) -> Path:
    groups, ungrouped, edges = _parse_mermaid(diagram)
    image = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    title_font = _font(36, True)
    meta_font = _font(18, False)
    zone_font = _font(24, True)
    node_font = _font(22, False)
    edge_font = _font(18, False)

    _draw_title_block(draw, diagram.title or '网络拓扑图', title_font, meta_font)
    _draw_footer(draw, meta_font)

    positions = {}
    body_top = 150
    body_bottom = HEIGHT - 120
    body_h = body_bottom - body_top

    if groups:
        gap = 24
        group_w = (WIDTH - 80 - 80 - gap * (len(groups) - 1)) // len(groups)
        for idx, group in enumerate(groups):
            x1 = 80 + idx * (group_w + gap)
            x2 = x1 + group_w
            y1 = body_top
            y2 = body_top + body_h - 170
            draw.rounded_rectangle([x1, y1, x2, y2], radius=18, outline=FRAME, width=2, fill=ZONE_FILL)
            draw.rounded_rectangle([x1 + 12, y1 + 12, x1 + 220, y1 + 56], radius=10, outline=BLUE, width=2, fill=BLUE_LIGHT)
            draw.text((x1 + 26, y1 + 20), group['title'], font=zone_font, fill=ACCENT if 'ACCENT' in globals() else BLUE)

            node_x1, node_x2 = x1 + 20, x2 - 20
            node_top = y1 + 80
            node_h = 108
            node_gap = 24
            for n_idx, (node_id, label) in enumerate(group['nodes']):
                ny1 = node_top + n_idx * (node_h + node_gap)
                ny2 = ny1 + node_h
                draw.rounded_rectangle([node_x1, ny1, node_x2, ny2], radius=14, outline=BLUE, width=2, fill=NODE_FILL)
                draw.rectangle([node_x1 + 10, ny1 + 10, node_x1 + 28, ny1 + 28], outline=BLUE, width=2, fill=BLUE_LIGHT)
                _draw_centered_text(draw, label, (node_x1 + 38, ny1 + 8, node_x2 - 8, ny2 - 8), node_font)
                positions[node_id] = {'x1': node_x1, 'y1': ny1, 'x2': node_x2, 'y2': ny2, 'cx': (node_x1 + node_x2)//2, 'cy': (ny1 + ny2)//2}

    if ungrouped:
        base_y = HEIGHT - 240
        start_x = 150
        node_w = 280
        node_h = 96
        gap_x = 100
        for idx, (node_id, label) in enumerate(ungrouped):
            x1 = start_x + idx * (node_w + gap_x)
            x2 = x1 + node_w
            y1 = base_y
            y2 = y1 + node_h
            draw.rounded_rectangle([x1, y1, x2, y2], radius=14, outline=BLUE, width=2, fill=NODE_FILL)
            _draw_centered_text(draw, label, (x1 + 10, y1 + 10, x2 - 10, y2 - 10), node_font)
            positions[node_id] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'cx': (x1 + x2)//2, 'cy': (y1 + y2)//2}

    for sid, tid, label in edges:
        if sid not in positions or tid not in positions:
            continue
        s, t = positions[sid], positions[tid]
        horizontal = abs(s['cx'] - t['cx']) >= abs(s['cy'] - t['cy'])
        if horizontal:
            start = (s['x2'], s['cy']) if s['cx'] <= t['cx'] else (s['x1'], s['cy'])
            end = (t['x1'], t['cy']) if s['cx'] <= t['cx'] else (t['x2'], t['cy'])
        else:
            start = (s['cx'], s['y2']) if s['cy'] <= t['cy'] else (s['cx'], s['y1'])
            end = (t['cx'], t['y1']) if s['cy'] <= t['cy'] else (t['cx'], t['y2'])
        dashed = ('受控' not in label and len(label) > 0 and '访问' not in label and '服务' not in label)
        _draw_arrow(draw, start, end, color=LINE, width=4, dashed=dashed)
        if label:
            shown = label[:36]
            mid_x = (start[0] + end[0]) // 2
            mid_y = (start[1] + end[1]) // 2 - 24
            bbox = draw.textbbox((0, 0), shown, font=edge_font)
            pad = 10
            draw.rounded_rectangle([mid_x - bbox[2]//2 - pad, mid_y - pad, mid_x + bbox[2]//2 + pad, mid_y + 30], radius=8, outline=FRAME, width=1, fill=(255,255,255))
            draw.text((mid_x - bbox[2]//2, mid_y), shown, font=edge_font, fill=TEXT)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format='PNG')
    return output_path
