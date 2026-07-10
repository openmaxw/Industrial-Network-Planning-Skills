from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


def _windows_dot_candidates() -> list[Path]:
    candidates: list[Path] = []
    for env_name in ['ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA']:
        base = os.environ.get(env_name)
        if not base:
            continue
        root = Path(base)
        candidates.extend([
            root / 'Graphviz' / 'bin' / 'dot.exe',
            root / 'Graphviz' / 'bin' / 'dot',
        ])
        for child in root.glob('Graphviz*'):
            candidates.extend([
                child / 'bin' / 'dot.exe',
                child / 'bin' / 'dot',
            ])
    candidates.extend([
        Path(r'C:\Program Files\Graphviz\bin\dot.exe'),
        Path(r'C:\Program Files (x86)\Graphviz\bin\dot.exe'),
    ])
    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def resolve_graphviz_dot() -> Path | None:
    direct = shutil.which('dot') or shutil.which('dot.exe')
    if direct:
        return Path(direct)
    if platform.system().lower().startswith('win'):
        for path in _windows_dot_candidates():
            if path.exists():
                return path
    return None


def has_graphviz() -> bool:
    return resolve_graphviz_dot() is not None


def graphviz_install_hint() -> str:
    return '未检测到 Graphviz。Linux 请确认 `dot` 在 PATH 中；Windows 请确认 Graphviz 已安装，或 `dot.exe` 位于常见安装目录。'


def get_graphviz_workdir() -> Path:
    preferred = Path.cwd() / 'output' / '.graphviz-temp'
    preferred.mkdir(parents=True, exist_ok=True)
    return preferred
