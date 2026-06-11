from __future__ import annotations

import csv
import json
from pathlib import Path


SUPPORTED_FORMATS = {"md", "txt", "json", "csv"}


def read_supported_text(path: Path, file_format: str) -> str:
    if file_format in {"md", "txt"}:
        return path.read_text(encoding="utf-8")
    if file_format == "json":
        loaded = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(loaded, ensure_ascii=False, indent=2)
    if file_format == "csv":
        return read_csv_text(path)
    raise ValueError(f"Unsupported format: {file_format}")


def read_csv_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    rendered_rows: list[str] = []
    for index, row in enumerate(rows, start=1):
        values = [f"{key}={value}" for key, value in row.items()]
        rendered_rows.append(f"row {index}: {' | '.join(values)}")
    return "\n".join(rendered_rows)
