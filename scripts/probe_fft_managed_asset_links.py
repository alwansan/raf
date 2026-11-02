"""Compare SHA-pinned original managed FFT callers with one real serialized FFT name.

Read original private CSharp9 ILSpy files. No source text, literal values,
shader bytecode or decompiled game code is ever printed or committed. A lack
of direct Resources.Load literal is not proof the Unity PPtr is absent.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256

SERIALIZED_FFT_NAME_SHA256 = "60c1b5ee2352bd6e303aa5fc68c88f61031cf21234f524d54ec02334a8e142d1"
CALL = re.compile(r"\b(?:\w+\s*\.\s*)?(Dispatch|SetTexture|SetBuffer)\s*\(\s*([A-Za-z_]\w*)")
LITERAL = re.compile(r'"([^"\\\r\n]{1,160})"')
DECL = re.compile(r"\bComputeShader\s+([A-Za-z_]\w*)")
KERNEL_ASSIGN = re.compile(r"\b([A-Za-z_]\w*KernelIndex)\s*=\s*(\d+)\s*;")
MAX_SOURCE_BYTES = 600_000


def analyze_text(text: str, expected_sha: str):
    if len(text.encode("utf8")) > MAX_SOURCE_BYTES:
        raise ValueError("Original managed source outside bounded scan")
    digest = hashlib.sha256(text.encode("utf8")).hexdigest()
    if digest != expected_sha:
        raise ValueError("Managed FFT caller original source SHA256 mismatch")
    literals = LITERAL.findall(text)
    # Do not print any original literal string, source expression or field name.
    asset_name_matches = sum(
        hashlib.sha256(x.encode("utf8")).hexdigest() == SERIALIZED_FFT_NAME_SHA256
        for x in literals
    )
    if asset_name_matches > 2:
        raise ValueError("Original asset name literal occurrences unexpectedly repeated")
    calls = {"Dispatch": [], "SetTexture": [], "SetBuffer": []}
    for op, arg in CALL.findall(text):
        calls[op].append(hashlib.sha256(arg.encode("utf8")).hexdigest())
    fields = DECL.findall(text)
    assigns = KERNEL_ASSIGN.findall(text)
    return {
        "original_source_sha256_verified": True,
        "declared_compute_shader_identifier_count": len(fields),
        "distinct_compute_shader_identifier_count": len(set(fields)),
        "dispatch_callsites": len(calls["Dispatch"]),
        "texture_bind_callsites": len(calls["SetTexture"]),
        "buffer_bind_callsites": len(calls["SetBuffer"]),
        "dispatch_argument_identifiers_sha256": calls["Dispatch"],
        "texture_argument_identifiers_sha256": calls["SetTexture"],
        "dispatch_identifiers_also_used_for_settexture":
            sorted(set(calls["Dispatch"]) & set(calls["SetTexture"])),
        "constant_kernel_index_assignments": len(assigns),
        "original_literal_matches_serialized_fft_asset_name": asset_name_matches,
        "literal_match_proves_unity_asset_reference": False,
        "decompiled_csharp_published": False,
    }


def inspect(root: Path):
    result = {}
    for stem, expected in ORIGINAL_SOURCE_SHA256.items():
        paths = list(root.rglob(stem + ".cs"))
        if len(paths) != 1 or paths[0].is_symlink() or not paths[0].is_file():
            raise ValueError("Exactly one original SHA-pinned " + stem + " required")
        content = paths[0].read_text(encoding="utf8-sig").replace("\r\n", "\n")
        result[stem] = analyze_text(content, expected)
    return {"callers": result, "original_serialized_fft_name_sha256":
            SERIALIZED_FFT_NAME_SHA256, "original_assets_modified": False,
            "direct_asset_pptr_connection_verified": False, "unity_or_android_executed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_AUTHENTIC_FFT_MANAGED_LINKS " + json.dumps(inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
