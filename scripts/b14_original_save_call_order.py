"""B14 LOCAL-005: authentic original save call order vs Android stats-only boundary.

Read pinned private ILSpy original C# locally in source-only CI. Report counts,
call ordering, and booleans only; never raw game source or original save bytes.
This is not a .rgd roundtrip, Unity import, or Android runtime proof.
"""
import argparse
import json
from pathlib import Path
import re

from scripts.b07_probe_original_world_callbacks import (
    PINS, assert_original_dll, _source, method_body, fingerprint,
    _executable_positions,
)
from scripts.instrument_android_runtime_operations import guard_android_local_savegame_stats

METHODS = ("SaveGame", "SaveUser", "SaveWorld", "Save")
CALLS = {
    "save_user": re.compile(r"\bSaveUser\s*\("),
    "save_world": re.compile(r"\bSaveWorld\s*\("),
    "steam_store_stats": re.compile(r"\bSteamUserStats\s*\.\s*StoreStats\s*\(\s*\)"),
}
SERIALIZE = re.compile(r"(?<!\w)Save\s*\(")
FILE_CREATE = re.compile(r"\bFileManager\s*\.\s*CreateFile\s*\(")
EXTERNAL_CALL = re.compile(r"\b(?:Steam[A-Za-z0-9_]*|PlayFab[A-Za-z0-9_]*)\s*\.\s*[A-Za-z_]\w*\s*\(")
CONDITIONAL = re.compile(r"(?m)^\s*#\s*(?:if|elif|else|endif)\b")
LOCAL_GUARD = re.compile(r"\bif\s*\(\s*!\s*RaftAndroid\s*\.\s*Platform\s*\.\s*LocalPlayerIdentity\s*\.\s*Enabled\s*\)")


def _masked(text):
    return _executable_positions(text)


def _bodies(source):
    result = {}
    for name in METHODS:
        ret, body = method_body(source, name)
        if ret != "void" or CONDITIONAL.search(_masked(body)):
            raise ValueError("Unsupported original SaveAndLoad method contract: " + name)
        result[name] = body
    return result


def _events(code):
    events = [(m.start(), label) for label, pattern in CALLS.items()
              for m in pattern.finditer(code)]
    events.sort()
    return [label for _, label in events]


def inspect_original_text(source, expected_sha=None):
    """Accept synthetic fixtures only with an explicitly supplied test SHA."""
    pinned = PINS["SaveAndLoad"] if expected_sha is None else expected_sha
    if fingerprint(source) != pinned:
        raise ValueError("Unrecognized original SaveAndLoad SHA")
    bodies = _bodies(source)
    raw_calls = _events(_masked(bodies["SaveGame"]))
    if raw_calls.count("steam_store_stats") != 1:
        raise ValueError("Original SaveGame must have one stats call")
    if raw_calls.count("save_world") < 1 or raw_calls.count("save_user") < 1:
        raise ValueError("Original SaveGame user/world persistence calls missing")
    original_nonstats = [e for e in raw_calls if e != "steam_store_stats"]
    guarded = guard_android_local_savegame_stats(source)
    adapted_bodies = _bodies(guarded)
    adapted_events = _events(_masked(adapted_bodies["SaveGame"]))
    if adapted_events != raw_calls or not LOCAL_GUARD.search(_masked(adapted_bodies["SaveGame"])):
        raise ValueError("Android stats isolation lost original save call order")
    if any(adapted_bodies[name] != bodies[name] for name in ("SaveUser", "SaveWorld", "Save")):
        raise ValueError("Android stats isolation modified original persistence path")
    # This ensures the new guard is the ONLY source-text change, rather than
    # merely seeing one guard somewhere in a modified SaveGame.
    if guarded.count("if (!RaftAndroid.Platform.LocalPlayerIdentity.Enabled)") != 1:
        raise ValueError("Android local stats guard was not unique")
    other_native = {}
    for name in ("SaveGame", "SaveUser", "SaveWorld"):
        code = _masked(bodies[name])
        count = len(EXTERNAL_CALL.findall(code))
        if name == "SaveGame":
            count -= raw_calls.count("steam_store_stats")
        other_native[name] = count
    if any(c < 0 for c in other_native.values()):
        raise ValueError("Invalid platform-call classification")
    # Counts deliberately do not claim their branches execute on the phone.
    return {
        "original_source_sha256": fingerprint(source),
        "savegame_direct_order": raw_calls,
        "savegame_user_save_calls": raw_calls.count("save_user"),
        "savegame_world_save_calls": raw_calls.count("save_world"),
        "savegame_steam_stats_calls": 1,
        "original_user_method_save_calls": len(SERIALIZE.findall(_masked(bodies["SaveUser"]))),
        "original_world_method_save_calls": len(SERIALIZE.findall(_masked(bodies["SaveWorld"]))),
        "original_save_uses_file_manager": bool(FILE_CREATE.search(_masked(bodies["Save"]))),
        "other_direct_platform_calls": other_native,
        "android_save_calls_preserved_in_order": original_nonstats ==
            [e for e in adapted_events if e != "steam_store_stats"],
        "android_stats_guard_source_preserved": True,
        "android_unity_compiled": False,
        "rgd_written_or_reloaded": False,
        "device_confirmed": False,
    }


def probe(dll: Path, original_source: Path):
    assert_original_dll(dll)
    if original_source.is_symlink() or not original_source.is_dir():
        raise ValueError("Unsafe private source directory")
    source, _ = _source(original_source, "SaveAndLoad", PINS["SaveAndLoad"])
    report = inspect_original_text(source)
    return {"authenticated_original_managed_dll": True, **report}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-managed-dll", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    try:
        report, code = probe(args.original_managed_dll, args.source), 0
    except Exception as exc:
        report, code = {"status": "incomplete", "error_type": type(exc).__name__,
                        "device_confirmed": False, "original_source_published": False}, 2
    print("B14_ORIGINAL_LOCAL_SAVE_ORDER " + json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
