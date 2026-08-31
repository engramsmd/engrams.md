#!/usr/bin/env python3
"""Validate ENGRAMS.md files and registry indexes against the v0.1 schema.

    python tools/validate.py ENGRAMS.md [more files...]
    python tools/validate.py registry/index.json

Requires: pip install pyyaml jsonschema
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "schema" / "engrams.schema.json").read_text())
BLOCK = re.compile(r"^```engram[ \t]*\n(.*?)^```", re.M | re.S)


def blocks_in_markdown(text: str) -> list[dict]:
    return [yaml.safe_load(m.group(1)) for m in BLOCK.finditer(text)]


def main() -> int:
    validator = jsonschema.Draft202012Validator(SCHEMA)
    failures = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.suffix == ".json":
            doc = json.loads(path.read_text())
            entries = doc.get("cartridges", [])
        else:
            entries = blocks_in_markdown(path.read_text())
        if not entries:
            print(f"{path}: no engram declarations found")
            failures += 1
            continue
        for entry in entries:
            errors = sorted(validator.iter_errors(entry), key=lambda e: list(e.path))
            name = entry.get("name", "<unnamed>") if isinstance(entry, dict) else "<invalid>"
            if errors:
                failures += 1
                for err in errors:
                    where = "/".join(str(p) for p in err.path) or "<root>"
                    print(f"{path}: {name}: {where}: {err.message}")
            else:
                print(f"{path}: {name}: ok")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
