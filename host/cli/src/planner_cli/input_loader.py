import json
from pathlib import Path


class InputLoadError(Exception):
    pass


def load_json_file(path: Path) -> dict:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputLoadError(f"Input file not found: {path}") from exc
    except OSError as exc:
        raise InputLoadError(f"Failed to read input file: {path}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise InputLoadError(f"Invalid JSON in input file: {path} ({exc})") from exc

    if not isinstance(payload, dict):
        raise InputLoadError("Input root must be a JSON object.")

    return payload
