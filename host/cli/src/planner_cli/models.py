from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class CliOptions:
    input_path: Path
    output_path: Path | None
    strict: bool
    style: str = "draft"
    format: str = "html"


@dataclass(slots=True)
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


@dataclass(slots=True)
class EvidenceItem:
    text: str
    source: str
    evidence_type: str
