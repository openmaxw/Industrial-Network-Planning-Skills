from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DocumentMeta:
    project_name: str
    customer_name: str
    site_name: str
    objective: str
    scope: str
    version: str = "v1.0"
    document_title: str = "工业网络方案"


@dataclass(slots=True)
class DiagramBlock:
    title: str
    diagram_type: str
    source_format: str
    content: str
    caption: str = ""


@dataclass(slots=True)
class TableBlock:
    title: str
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    caption: str = ""


@dataclass(slots=True)
class BulletBlock:
    title: str
    items: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParagraphBlock:
    text: str


@dataclass(slots=True)
class Section:
    title: str
    number: str = ""
    summary: str = ""
    paragraphs: list[ParagraphBlock] = field(default_factory=list)
    bullets: list[BulletBlock] = field(default_factory=list)
    diagrams: list[DiagramBlock] = field(default_factory=list)
    tables: list[TableBlock] = field(default_factory=list)


@dataclass(slots=True)
class Appendix:
    title: str
    tables: list[TableBlock] = field(default_factory=list)
    diagrams: list[DiagramBlock] = field(default_factory=list)
    paragraphs: list[ParagraphBlock] = field(default_factory=list)


@dataclass(slots=True)
class DocumentModel:
    meta: DocumentMeta
    sections: list[Section] = field(default_factory=list)
    appendices: list[Appendix] = field(default_factory=list)
