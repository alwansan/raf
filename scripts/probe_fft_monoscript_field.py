"""Resolve original water MonoScript class via its SHA256 within private CSharp9.

Authenticated source class identity comes from serialized globalgamemanagers
MonoScript, not a guessed type name. No original class names or source emitted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ORIGINAL_MONOSCRIPT_NAME_SHA256 = "cb4d4c048bb81a9c6260539769f50e73b91b44ae5d6ccc048038d342154ed687"
NAMESPACE = re.compile(r"(?m)^\s*namespace\s+([A-Za-z_][\w.]*)\s*(?:\{|;)")
COMPUTE_FIELD = re.compile(
    r"\b(?:public|private|protected|internal)\s+"
    r"(?:(?:static|readonly|volatile|new|protected|internal)\s+)*"
    r"(?:UnityEngine\.)?ComputeShader\s+([A-Za-z_]\w*)\s*(?:[;=,])"
)
MAX_SOURCE = 800_000


def inspect(root: Path, expected_sha=ORIGINAL_MONOSCRIPT_NAME_SHA256):
    if not root.is_dir():
        raise ValueError("Private original CSharp9 decompilation missing")
    files = list(root.rglob("*.cs"))
    if len(files) > 10_000:
        raise ValueError("Unbounded original CSharp source file count")
    matches = []
    for file in files:
        if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_SOURCE:
            continue
        raw = file.read_text(encoding="utf-8-sig")
        namespaces = NAMESPACE.findall(raw)
        namespace = namespaces[0] if namespaces else ""
        # Original MonoScript asset SHA was computed on namespace + "." + class.
        identity = namespace + "." + file.stem
        if hashlib.sha256(identity.encode("utf8")).hexdigest() != expected_sha:
            continue
        compute_fields = COMPUTE_FIELD.findall(raw)
        matches.append({
            "original_monoscript_identity_sha256": expected_sha,
            "original_class_csharp_source_sha256": hashlib.sha256(raw.encode("utf8")).hexdigest(),
            "original_field_type_compute_shader_declarations": len(compute_fields),
            "compute_shader_field_name_sha256": [
                hashlib.sha256(name.encode("utf8")).hexdigest() for name in compute_fields
            ],
            "compute_shader_mentions": len(re.findall(r"\bComputeShader\b", raw)),
            "waves_renderer_fft_mentions": len(re.findall(r"\bWavesRendererFFT\b", raw)),
            "dx11_fft_mentions": len(re.findall(r"\bDx11FFT\b", raw)),
            "original_type_name_or_csharp_published": False,
        })
    if len(matches) > 1:
        raise ValueError("Ambiguous original class SHA256 identity")
    return {
        "original_monoscript_identity_sha256": expected_sha,
        "original_managed_type_matched": len(matches) == 1,
        "matches": matches,
        "serialized_compute_field_offset_verified": False,
        "android_water_shader_compiled": False,
        "original_sources_modified": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    a = p.parse_args()
    print("RAFT_FFT_MONOSCRIPT_CSHARP_FIELD_LINK " + json.dumps(inspect(a.source), sort_keys=True))


if __name__ == "__main__":
    main()
