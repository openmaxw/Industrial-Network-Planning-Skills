from __future__ import annotations

import html
from pathlib import Path

from planner_cli.document_model import Appendix, BulletBlock, DiagramBlock, DocumentModel, ParagraphBlock, Section, TableBlock
from planner_cli.graphviz_support import graphviz_install_hint
from planner_cli.graphviz_renderer import render_diagram_svg_auto


def _esc(text: str) -> str:
    return html.escape(text or '')


def _render_paragraph(block: ParagraphBlock) -> str:
    return f'<p class="para">{_esc(block.text)}</p>'


def _render_bullets(block: BulletBlock) -> str:
    items = ''.join(f'<li>{_esc(item)}</li>' for item in block.items)
    return f'<section class="block"><h4>{_esc(block.title)}</h4><ul>{items}</ul></section>'


def _render_table(block: TableBlock) -> str:
    head = ''.join(f'<th>{_esc(h)}</th>' for h in block.headers)
    rows = ''.join('<tr>' + ''.join(f'<td>{_esc(c)}</td>' for c in row) + '</tr>' for row in block.rows)
    return f'<section class="block"><h4>{_esc(block.title)}</h4><div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div></section>'


def _render_diagram(block: DiagramBlock, large: bool = False) -> str:
    svg, status = render_diagram_svg_auto(block)
    klass = 'diagram large-diagram' if large else 'diagram'
    if not svg:
        hint = graphviz_install_hint() if status == 'missing' else 'Graphviz 渲染失败，此图未显示。'
        return f'<section class="block"><h4>{_esc(block.title)}</h4><div class="{klass}"><p class="diagram-hint">{_esc(hint)}</p></div></section>'
    return f'<section class="block"><h4>{_esc(block.title)}</h4><div class="{klass}">{svg}</div></section>'


def _render_section(section: Section) -> str:
    parts = [f'<section class="chapter"><h2>{_esc(section.title)}</h2>']
    for block in section.paragraphs:
        parts.append(_render_paragraph(block))
    for block in section.tables:
        parts.append(_render_table(block))
    for block in section.diagrams:
        parts.append(_render_diagram(block, large=False))
    for block in section.bullets:
        parts.append(_render_bullets(block))
    parts.append('</section>')
    return ''.join(parts)


def _render_appendix(appendix: Appendix) -> str:
    parts = [f'<section class="chapter appendix"><h2>{_esc(appendix.title)}</h2>']
    for block in appendix.paragraphs:
        parts.append(_render_paragraph(block))
    for block in appendix.tables:
        parts.append(_render_table(block))
    for block in appendix.diagrams:
        parts.append(_render_diagram(block, large=True))
    parts.append('</section>')
    return ''.join(parts)


def render_html(model: DocumentModel, output_path: Path) -> None:
    toc = ''.join(f'<li><a href="#sec-{idx}">{_esc(section.title)}</a></li>' for idx, section in enumerate(model.sections, start=1))
    sections = ''.join(f'<div id="sec-{idx}">{_render_section(section)}</div>' for idx, section in enumerate(model.sections, start=1))
    appendices = ''.join(_render_appendix(app) for app in model.appendices)
    html_text = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>{_esc(model.meta.project_name)}</title><style>
:root{{--bg:#f8fafc;--panel:#ffffff;--line:#e2e8f0;--text:#1e293b;--muted:#64748b;--blue:#2563eb;--blue2:#1d4ed8;}}*{{box-sizing:border-box;}}html{{scroll-behavior:smooth;}}body{{font-family:"Noto Sans CJK SC","Microsoft YaHei",Arial,sans-serif;margin:0;background:var(--bg);color:var(--text);}}.layout{{display:grid;grid-template-columns:280px minmax(0,1fr);gap:20px;max-width:1540px;margin:0 auto;padding:20px;}}.sidebar{{position:sticky;top:16px;align-self:start;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 8px 20px rgba(15,23,42,.05);max-height:calc(100vh - 32px);overflow:auto;}}.brand{{font-size:13px;color:var(--muted);margin-bottom:6px;}}.project{{font-size:22px;font-weight:700;color:#0f172a;line-height:1.4;margin-bottom:14px;}}.meta{{font-size:13px;line-height:1.75;color:var(--muted);margin-bottom:16px;}}.nav-title{{font-size:14px;font-weight:700;color:#0f172a;margin:12px 0 8px;}}.nav{{list-style:none;padding:0;margin:0;}}.nav li{{margin:5px 0;}}.nav a{{display:block;padding:7px 9px;border-radius:9px;color:var(--blue);text-decoration:none;font-size:13px;line-height:1.45;}}.nav a:hover{{background:#eff6ff;color:var(--blue2);}}.main{{min-width:0;}}.cover,.chapter{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:24px 28px;margin-bottom:20px;box-shadow:0 8px 22px rgba(15,23,42,.05);}}.notice{{border-left:4px solid #f59e0b;}}.cover h1{{margin:0 0 14px;font-size:34px;line-height:1.3;color:#0f172a;}}.cover-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px 20px;}}.cover p{{margin:0;line-height:1.75;font-size:14px;}}h2{{font-size:26px;margin:0 0 14px;color:#0f172a;padding-bottom:8px;border-bottom:1px solid var(--line);}}h4{{font-size:18px;margin:18px 0 10px;color:var(--blue2);}}.para{{line-height:1.85;margin:10px 0;font-size:14px;}}.block{{margin:14px 0 18px;}}.diagram{{overflow:auto;border:1px solid #cbd5e1;border-radius:12px;background:#fff;padding:8px;max-width:100%;}}.diagram-hint{{margin:0;padding:18px 14px;text-align:center;color:var(--muted);font-size:13px;line-height:1.7;}}.diagram svg{{display:block;width:100%;height:auto;max-height:640px;}}.large-diagram svg{{max-height:none;min-height:760px;}}.table-wrap{{overflow:auto;}}table{{width:100%;border-collapse:collapse;font-size:13px;background:#fff;}}th,td{{border:1px solid #cbd5e1;padding:8px 10px;text-align:left;vertical-align:top;line-height:1.65;}}th{{background:#eff6ff;}}ul{{padding-left:20px;line-height:1.8;font-size:14px;}}.appendix{{border-style:dashed;}}@media (max-width: 1200px){{.layout{{grid-template-columns:1fr;}}.sidebar{{position:relative;top:auto;max-height:none;}}.cover-grid{{grid-template-columns:1fr;}}}}</style></head><body><div class="layout"><aside class="sidebar"><div class="brand">正式交付件 / HTML 阅读版</div><div class="project">{_esc(model.meta.project_name)}</div><div class="meta"><div><strong>建设单位：</strong>{_esc(model.meta.customer_name)}</div><div><strong>项目地点：</strong>{_esc(model.meta.site_name)}</div><div><strong>版本：</strong>{_esc(model.meta.version)}</div></div><div class="nav-title">章节导航</div><ul class="nav">{toc}</ul></aside><main class="main"><section class="cover"><h1>{_esc(model.meta.project_name)}</h1><div class="cover-grid"><p><strong>建设单位：</strong>{_esc(model.meta.customer_name)}</p><p><strong>项目地点：</strong>{_esc(model.meta.site_name)}</p><p><strong>项目目标：</strong>{_esc(model.meta.objective)}</p><p><strong>建设范围：</strong>{_esc(model.meta.scope)}</p></div></section>{sections}{appendices}</main></div></body></html>'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding='utf-8')
