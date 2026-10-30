#!/usr/bin/env python3
"""Prevent accidental runner-image migrations and unbounded LFS transfers."""
from pathlib import Path
import re
import sys

root = Path(".github/workflows")
paths = sorted(root.glob("*.yml")) + sorted(root.glob("*.yaml"))
errors = []
for path in paths:
    text = path.read_text(encoding="utf8")
    for n, line in enumerate(text.splitlines(), start=1):
        if re.search(r"^\s*runs-on:\s*ubuntu-latest\s*(?:#.*)?$", line):
            errors.append(f"{path}:{n}: Ubuntu runner must use a pinned ubuntu-24.04 label")
        if re.search(r"^\s*lfs:\s*true\s*(?:#.*)?$", line):
            errors.append(f"{path}:{n}: checkout LFS must not download all game data")
        if re.search(r"^\s*git\s+lfs\s+pull\s*$", line):
            errors.append(f"{path}:{n}: unbounded git lfs pull forbidden")
print(f"Audited workflow files: {len(paths)}")
for issue in errors:
    print("ERROR:", issue)
if errors:
    raise SystemExit(1)
print("PASS: No ubuntu-latest runner labels or unbounded Git LFS checkout")
