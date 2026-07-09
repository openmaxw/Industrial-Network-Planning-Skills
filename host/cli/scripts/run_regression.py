from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLI_ENV = os.environ.copy()
CLI_ENV["PYTHONPATH"] = str(ROOT / "host/cli/src")
CASES = [
    (ROOT / "core/examples/standard-input-example.json", "standard", "draft"),
    (ROOT / "host/cli/examples/minimal-viable-input.json", "minimal", "draft"),
    (ROOT / "host/cli/examples/high-completeness-input.json", "complete", "draft"),
    (ROOT / "host/cli/examples/remote-maintenance-heavy-input.json", "remote-maintenance", "draft"),
    (ROOT / "host/cli/examples/address-constrained-input.json", "address-constrained", "draft"),
    (ROOT / "host/cli/examples/multi-workshop-input.json", "multi-workshop", "draft"),
    (ROOT / "host/cli/examples/redundancy-demand-input.json", "redundancy-demand", "draft"),
    (ROOT / "host/cli/examples/compound-conflict-input.json", "compound-conflict", "draft"),
    (Path("/tmp/conflict-input.json"), "conflict", "draft"),
    (Path("/tmp/dayawan-mes-input.json"), "dayawan-mes", "formal"),
    (ROOT / "host/cli/examples/high-completeness-input.json", "formal-complete", "formal"),
    (ROOT / "host/cli/examples/remote-maintenance-heavy-input.json", "formal-remote-maintenance", "formal"),
    (ROOT / "host/cli/examples/address-constrained-input.json", "formal-address-constrained", "formal"),
    (ROOT / "host/cli/examples/multi-workshop-input.json", "formal-multi-workshop", "formal"),
    (ROOT / "host/cli/examples/fmcs-from-framework-input.json", "formal-fmcs-from-framework", "formal"),
]

REQUIRED_MARKERS_DRAFT = [
    "## 输出前自检",
    "## 证据边界说明",
    "**章节摘要**",
    "**章节结论**",
    "**规则主题**",
    "**适用前提**",
    "**闭环条件**",
]

REQUIRED_MARKERS_FORMAL = [
    "## 文档说明",
    "## 实施结论与定版条件",
    "**待确认项**",
    "**总体拓扑图**",
    "**重点边界拓扑图**",
    "```mermaid",
    "源区",
    "目标区",
    "编号/命名策略",
    "**地址与 VLAN 定版摘要表**",
    "**项目定版结论**",
    "**对象清单摘要**",
]


def run_case(input_path: Path, label: str, style: str) -> dict:
    output_path = Path("/tmp") / f"regression-{label}.md"
    cmd = [
        "python3",
        "-m",
        "planner_cli.main",
        "generate",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--style",
        style,
    ]
    proc = subprocess.run(cmd, cwd=ROOT, env=CLI_ENV, capture_output=True, text=True)
    result = {
        "label": label,
        "input": str(input_path),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "output": str(output_path),
        "missing_markers": [],
        "skipped": False,
    }
    if not input_path.exists():
        result["skipped"] = True
        result["stderr"] = f"Skipped missing input: {input_path}\n"
        return result
    if proc.returncode == 0 and output_path.exists():
        text = output_path.read_text(encoding="utf-8")
        required_markers = REQUIRED_MARKERS_FORMAL if style == "formal" else REQUIRED_MARKERS_DRAFT
        result["missing_markers"] = [marker for marker in required_markers if marker not in text]
    return result


def main() -> int:
    results = [run_case(path, label, style) for path, label, style in CASES]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(item["skipped"] or (item["returncode"] == 0 and not item["missing_markers"]) for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
