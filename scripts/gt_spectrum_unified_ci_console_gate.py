#!/usr/bin/env python3
"""Second-job finalized console gate for source-provisional unified Spectrum.

ShaderUtil.GetShaderMessages=0 is NOT sufficient: real Unity 2021 can emit
hidden GLSL link failures after an otherwise 'successful' ShaderBundle.
Read finalized first-job logs with actions:read in a separate job.
Never emit shader source/keywords, only numeric counts.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re

from scripts.gt_spectrum_ci_console_gate import (
    _ERROR_CLASSES, _LOG_TS, MAX_LOG_BYTES
)

RUNTIME_MARKER = "GT_SPECTRUM_UNIFIED_KEYWORD_PRIVATE_UNITY_PROVISIONAL "


def verify(data:bytes):
    if type(data) is not bytes or not 0<len(data)<=MAX_LOG_BYTES or b"\x00" in data:
        raise ValueError("unity_unified_final_console_not_proven")
    text=data.decode("utf-8",errors="replace")
    marker=re.search(_LOG_TS+re.escape(RUNTIME_MARKER),text) is not None
    errors={k:len(v.findall(text)) for k,v in _ERROR_CLASSES.items()}
    return {
        "status":"PRIVATE_SPECTRUM_UNIFIED_KEYWORD_FINAL_CONSOLE_CLEAN"
                 if marker and not any(errors.values()) else "REJECTED",
        "unified_private_runtime_marker_confirmed":marker,
        "GLSL_link_errors":errors["glsl_link"],
        "internal_shader_variant_creation_errors":errors["internal_variant_failed"],
        "Shader_import_errors":errors["shader_import"],
        "Shader_compilation_errors":errors["shader_compile"],
        "original_keyword_scope_flags_parity_proven":False,
        "original_material_variant_runtime_parity_proven":False,
        "original_Adreno_pixels_verified":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--console",type=Path,required=True)
    x=p.parse_args()
    f=x.console
    if not f.is_file() or f.is_symlink() or f.stat().st_size>MAX_LOG_BYTES:
        print("GT_SPECTRUM_UNIFIED_FINAL_CONSOLE_SAFE status=INCONCLUSIVE")
        return 2
    try:
        result=verify(f.read_bytes())
    except (OSError,ValueError):
        print("GT_SPECTRUM_UNIFIED_FINAL_CONSOLE_SAFE status=INCONCLUSIVE")
        return 2
    print("GT_SPECTRUM_UNIFIED_FINAL_CONSOLE_SAFE "+" ".join(
        key+"="+str(value) for key,value in result.items()))
    return 0 if result["status"]=="PRIVATE_SPECTRUM_UNIFIED_KEYWORD_FINAL_CONSOLE_CLEAN" else 2


if __name__=="__main__":
    raise SystemExit(main())
