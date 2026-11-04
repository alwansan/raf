#!/usr/bin/env python3
"""Source-level regression checks; not a substitute for Android device tests."""
from pathlib import Path
src = (Path(__file__).resolve().parents[1] /
       "app/src/main/java/com/alwansan/lograf/ErrorCategorySummary.java").read_text()
for token in (
    '"fmod_initialization_failed"',
    '"fmod_event_not_found"',
    'line.contains("[FMOD] Initialization failed")',
    'line.contains("SystemNotInitializedException")',
    'line.contains("EventNotFoundException")',
):
    assert token in src, f"Missing FMOD diagnostic classification: {token}"
assert 'if(category!=null)groups.get(category).add();' in src
print("FMOD classification structural regression checks passed")
