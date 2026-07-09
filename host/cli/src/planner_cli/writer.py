from pathlib import Path


class OutputWriteError(Exception):
    pass


def write_output(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise OutputWriteError(f"Failed to write output file: {path}") from exc
