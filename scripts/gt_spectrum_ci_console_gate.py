#!/usr/bin/env python3
"""Fail-closed secondary GitHub Actions console gate for private Unity shader CI.

Unity 2021 may report successful AssetBundle and ShaderUtil.GetShaderMessages=0
even while its *internal shader variant* GLSL linker prints failures to the
Editor console. Therefore a successful C# receipt is NOT enough.
Run this ONLY in a separate job after the Unity job has finalized, using
authenticated GitHub Actions job logs. Never print source lines or filenames.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

# Intentionally broad enough to catch Unity Editor importer and worker errors.
# The input is ONLY the isolated private Spectrum job's finalized console.
_ERROR_CLASSES = {
    "glsl_link": re.compile(r"\bGLSL\s+link\s+error\b", re.IGNORECASE),
    "internal_variant_failed": re.compile(
        r"\bCreation of internal variant of shader\b[^\r\n]*\bfailed\b",
        re.IGNORECASE,
    ),
    "shader_import": re.compile(r"\bShader error in\b", re.IGNORECASE),
    "shader_compile": re.compile(r"\bshader\s+(?:compilation|compile)\s+failed\b",
                                 re.IGNORECASE),
}
# Match only actual timestamped program output, never the shell's echoed
# Python source where a print("MARKER") string may appear before execution.
_SUCCESS_MARKERS = (
    "GT_SPECTRUM_UNITY_ANDROID_VULKAN_PRIVATE realUnity2021=true",
    "GT_SPECTRUM_VARIANT1_UNITY_PRIVATE_OK editor2021=true",
)
_LOG_TS = r"(?m)^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?Z[ \\t]+"

MAX_LOG_BYTES = 64 * 1024 * 1024


def verify_console(content: bytes):
    if (type(content) is not bytes or not 0 < len(content) <= MAX_LOG_BYTES
            or b"\x00" in content):
        raise ValueError("private_Unity_final_console_log_missing_or_invalid")
    text = content.decode("utf-8", errors="replace")
    counts = {key: len(pattern.findall(text))
              for key,pattern in _ERROR_CLASSES.items()}
    completed = {
        k: re.search(_LOG_TS + re.escape(k) + r"(?:[ \\r\\n]|$)", text) is not None
        for k in _SUCCESS_MARKERS
    }
    if not all(completed.values()):
        raise ValueError("private_Unity_variant0_or_variant1_success_marker_missing")
    return {
        "schema":1,
        "status":"PRIVATE_SPECTRUM_UNITY_FINAL_LOG_CLEAN" if not any(counts.values())
                 else "PRIVATE_SPECTRUM_UNITY_FINAL_LOG_HAS_HIDDEN_ERRORS",
        "source_original_keyword_routing_or_material_parity_proven":False,
        "Android_Adreno_pixels_verified":False,
        "unity_variant0_success_marker_seen":completed[_SUCCESS_MARKERS[0]],
        "unity_variant1_success_marker_seen":completed[_SUCCESS_MARKERS[1]],
        "Unity_GL_link_errors":counts["glsl_link"],
        "Unity_hidden_internal_variant_failures":counts["internal_variant_failed"],
        "Unity_Shader_import_errors":counts["shader_import"],
        "Unity_shader_compilation_failures":counts["shader_compile"],
        "original_ShaderLab_text_or_keyword_names_published":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--console",type=Path,required=True)
    x=p.parse_args()
    file=x.console
    if not file.is_file() or file.is_symlink() or file.stat().st_size>MAX_LOG_BYTES:
        print("GT_SPECTRUM_FINAL_UNITY_CONSOLE_GATE_SAFE status=INCONCLUSIVE")
        return 2
    try:
        result=verify_console(file.read_bytes())
    except (ValueError,OSError):
        print("GT_SPECTRUM_FINAL_UNITY_CONSOLE_GATE_SAFE status=INCONCLUSIVE")
        return 2
    # Numeric classes only; no raw source, SHA, keyword, shader or asset names.
    print("GT_SPECTRUM_FINAL_UNITY_CONSOLE_GATE_SAFE " +
          " ".join(k+"="+str(v) for k,v in result.items()))
    return 0 if result["status"]=="PRIVATE_SPECTRUM_UNITY_FINAL_LOG_CLEAN" else 2


if __name__=="__main__":
    raise SystemExit(main())
