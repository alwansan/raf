"""Read-only privacy-safe probe for the original Raft scene-audio handoff.

Run ONLY on privately decompiled Assembly-CSharp source in the existing
no-Unity/no-LFS CI lane. Print structural counters/digests, never the original
method bodies. No production source is modified by this probe.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def method_body(source: str, method: str):
    # ILSpy's CSharp9 class methods have a regular method declaration here.
    declaration = re.compile(
        r"(?m)^\s*(?:public|private|protected|internal)\s+"
        r"(?:(?:static|virtual|override|sealed|new|async)\s+)*"
        r"(?P<return>[\w<>\[\],.?]+)\s+" + re.escape(method)
        + r"\s*\([^;{}]*\)\s*\{"
    )
    matches = list(declaration.finditer(source))
    if len(matches) != 1:
        raise ValueError("Expected one original " + method + " declaration; found " + str(len(matches)))
    match = matches[0]
    start = match.end()
    depth = 1
    for i in range(start, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return match["return"], source[start:i]
    raise ValueError("Unclosed original " + method + " body")


def inspect(source_root: Path) -> dict:
    matches = sorted(source_root.rglob("SoundManager.cs"))
    if len(matches) != 1 or not matches[0].is_file() or matches[0].is_symlink():
        raise ValueError("Expected one regular original SoundManager source")
    source = matches[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    result = {
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_chars": len(source),
        "methods": {},
        "modified_source": False,
        "unity_compiled": False,
    }
    # Do not require every method; old Raft changed the naming of callbacks.
    for name in ("OnSceneEvent", "Awake", "Start"):
        if re.search(r"\b" + name + r"\s*\(", source) is None:
            continue
        try:
            return_type, body = method_body(source, name)
        except ValueError:
            if name == "OnSceneEvent":
                raise
            continue
        result["methods"][name] = {
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
            "return_void": return_type == "void",
            "has_fmod_runtime_manager": "RuntimeManager" in body,
            "has_studio_event_emitter": "StudioEventEmitter" in body,
            "has_event_reference": "EventReference" in body,
            "event_creation_calls": len(re.findall(r"\b(?:CreateInstance|GetEventDescription|Play|Start)\s*\(", body)),
            "broadcast_calls": len(re.findall(r"\b(?:BroadcastMessage|BroadCastToScene)\s*\(", body)),
            "explicit_return_count": len(re.findall(r"\breturn\b", body)),
            "catch_count": len(re.findall(r"\bcatch\s*\(", body)),
        }
    if "OnSceneEvent" not in result["methods"]:
        raise ValueError("Missing original scene-event callback")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_SCENE_AUDIO_SOURCE_PROBE " + json.dumps(inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
