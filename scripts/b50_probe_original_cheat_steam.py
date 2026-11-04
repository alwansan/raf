"""B50 LOCAL-005: authenticated, read-only original Cheat Steam identity boundary probe.

Runs in isolated private CI after ILSpy CSharp9 extraction of pinned game DLL.
Only structural counts/SHA and booleans may leave the runner; never original C#.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_scene_audio import method_body, _executable_positions

ORIGINAL_DLL_BYTES = 3211776
ORIGINAL_DLL_SHA256 = "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e"
STEAM_ID = re.compile(r"\bSteamUser\s*\.\s*GetSteamID\s*\(\s*\)")
CONDITIONAL = re.compile(r"(?m)^\s*#\s*(?:if|elif|else|endif)\b")


def authenticated(dll, *, expected_bytes=ORIGINAL_DLL_BYTES, expected_sha=ORIGINAL_DLL_SHA256):
    if dll.is_symlink() or not dll.is_file() or dll.stat().st_size != expected_bytes:
        raise ValueError("Original managed provider missing, linked, or not exact bytes")
    h = hashlib.sha256()
    with dll.open("rb") as stream:
        while data := stream.read(1024 * 1024):
            h.update(data)
    if h.hexdigest() != expected_sha:
        raise ValueError("Original managed provider digest mismatch")
    return h.hexdigest()


def probe(source_root, dll, *, expected_bytes=ORIGINAL_DLL_BYTES, expected_sha=ORIGINAL_DLL_SHA256):
    provider_sha = authenticated(dll, expected_bytes=expected_bytes, expected_sha=expected_sha)
    if source_root.is_symlink() or not source_root.is_dir():
        raise ValueError("Unsafe original extracted source root")
    candidates = list(source_root.rglob("Cheat.cs"))
    if len(candidates) != 1:
        raise ValueError("Require unique original Cheat source")
    selected = candidates[0]
    if selected.is_symlink() or not selected.is_file():
        raise ValueError("Unsafe original Cheat source")
    # No linked parent between authenticated extracted root and selected source.
    for part in [selected, *list(selected.parents)]:
        if part == source_root:
            break
        if part.is_symlink():
            raise ValueError("Linked parent in extracted source")
    text = selected.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    ret, body = method_body(text, "AllowCheatsForLocalPlayer")
    executable = _executable_positions(body)
    # If the method uses preprocessor branches, a lexical call count cannot
    # establish what Android will run. Report only branch presence, not success.
    call_count = len(STEAM_ID.findall(executable))
    return {
        "provider_sha256": provider_sha,
        "cheat_source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "cheat_method_sha256": hashlib.sha256(body.encode()).hexdigest(),
        "method_returns_bool": ret == "bool",
        "direct_steam_getid_calls": call_count,
        "has_preprocessor_branches": bool(CONDITIONAL.search(executable)),
        "other_steam_named_tokens": len(re.findall(r"\bSteam[A-Za-z0-9_]*\s*\.", executable)),
        "source_changed": False,
        "unity_or_android_executed": False,
        "world_load_verified": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original-managed-dll", required=True, type=Path)
    p.add_argument("--source", required=True, type=Path)
    a = p.parse_args()
    print("B50_ORIGINAL_CHEAT_STEAM_PROBE " +
          json.dumps(probe(a.source, a.original_managed_dll), sort_keys=True))


if __name__ == "__main__":
    main()
