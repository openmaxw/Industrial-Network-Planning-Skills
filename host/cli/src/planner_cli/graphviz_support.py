from __future__ import annotations

import shutil


def has_graphviz() -> bool:
    return shutil.which('dot') is not None


def graphviz_install_hint() -> str:
    return '未检测到 Graphviz，安装后可显示此图。'
