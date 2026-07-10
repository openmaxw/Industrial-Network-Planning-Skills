from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CoreAssets:
    template: str
    report_outline: str
    document_rules: str


class CoreAssetLoadError(Exception):
    pass


ROOT_MARKERS = ["industrial-network-planner", "docs", "adapters", "output"]


def discover_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if all((candidate / marker).exists() for marker in ROOT_MARKERS):
            return candidate
    raise CoreAssetLoadError("Unable to locate repository root from current working directory.")


def load_core_assets(repo_root: Path) -> CoreAssets:
    try:
        template = (repo_root / "industrial-network-planner/templates/customer-solution-template.md").read_text(encoding="utf-8")
        report_outline = (repo_root / "industrial-network-planner/references/report-outline.md").read_text(encoding="utf-8")
        document_rules = (repo_root / "industrial-network-planner/references/document-assembly-rules.md").read_text(encoding="utf-8")
    except OSError as exc:
        raise CoreAssetLoadError(f"Failed to load core assets: {exc}") from exc

    return CoreAssets(
        template=template,
        report_outline=report_outline,
        document_rules=document_rules,
    )
