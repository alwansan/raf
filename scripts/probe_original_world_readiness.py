"""Redacted, fail-closed inspection of the original local-world readiness chain.

The original decompiled Raft_Network source is processed only in the existing
private no-Unity/no-LFS CI runner. Never print a method body or literal.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.adapt_android_offline_startup import PINS, fingerprint
from scripts.probe_original_scene_audio import method_body


RECEIVED = re.compile(r"\bWorldHasBeenRecieved\s*=\s*true\s*;")
BROADCAST = re.compile(r"\bHelper\s*\.\s*BroadCastToScene\s*\(")

# Only executable C# tokens count toward this source-level contract. Mask
# comments and literals without shifting the original character offsets.
# Interpolated string expressions are conservatively not counted.
_CSHARP_NON_CODE = re.compile(
    r'''//[^\r\n]*|/\*[\s\S]*?\*/|@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' '''
    .strip()
)


def _executable_only(body: str) -> str:
    return _CSHARP_NON_CODE.sub(
        lambda match: re.sub(r"[^\r\n]", " ", match.group()), body
    )



def inspect(source_root: Path) -> dict:
    matches = sorted(source_root.rglob("Raft_Network.cs"))
    if len(matches) != 1 or not matches[0].is_file() or matches[0].is_symlink():
        raise ValueError("Expected exactly one regular original Raft_Network source")
    source = matches[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    digest = fingerprint(source)
    if digest != PINS["Raft_Network"]:
        raise ValueError("Unknown original Raft_Network revision")
    return_type, body = method_body(source, "WorldHasBeenLoaded")
    executable = _executable_only(body)
    broadcasts = list(BROADCAST.finditer(executable))
    received = list(RECEIVED.finditer(executable))
    if len(received) != 1 or not broadcasts:
        raise ValueError("Original world readiness/broadcast contract changed")
    before = sum(event.start() < received[0].start() for event in broadcasts)
    if before < 1:
        raise ValueError("Original world readiness no longer follows scene broadcast")
    # A thrown listener before the completion assignment can interrupt this
    # coroutine. This is structural evidence, NOT proof that FMOD alone caused
    # the observed device failure or that the world has actually loaded.
    return {
        "original_source_sha256": digest,
        "world_coroutine_sha256": hashlib.sha256(body.encode()).hexdigest(),
        "coroutine_returns_enumerator": "IEnumerator" in return_type,
        "scene_broadcast_calls": len(broadcasts),
        "broadcasts_before_received_assignment": before,
        "received_true_assignments": len(received),
        "wait_or_yield_references": len(re.findall(r"\b(?:yield|WaitUntil|WaitForSeconds)\b", executable)),
        "game_manager_start_references": len(re.findall(r"\bgameManagerStartCalled\b", executable)),
        "modified_original_source": False,
        "unity_or_device_executed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_WORLD_READINESS_SOURCE_PROBE " + json.dumps(inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
