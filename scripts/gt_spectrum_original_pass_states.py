#!/usr/bin/env python3
"""GT: recover original seven Spectrum RenderState blocks *privately* from ZIP2.

Read SHA-authenticated original Unity Shader object (B09), not dummy ShaderLab.
Do not publish proprietary state text, shader names, GUIDs or input source bytes.
This DOES NOT author the seven-pass ShaderLab, prove variants/material/RT upload,
import in Unity 2021.3, or execute Android Vulkan/Adreno pixels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from scripts.b09_spectrum_topology_contract import (
    PASSES, TARGET, OWNER,
)
from scripts.b09_stage_original_spectrum import _selected_original
from scripts.verify_targeted_lfs_compute_sources import (
    EXPECTED, verify_sources,
)
from scripts.w1_depth_shaderlab import render_state

MAX_STATE_BYTES = 65536
MAX_PROPS = 512


def _safe(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("linked_original_or_private_path")
    return path


def validate(parsed, *, serializer=render_state):
    if (not isinstance(parsed, dict)
            or parsed.get("m_Name") != TARGET
            or not isinstance(parsed.get("m_SubShaders"), list)
            or len(parsed["m_SubShaders"]) != 1):
        raise ValueError("original_spectrum_shader_identity_or_subshader_changed")
    sub = parsed["m_SubShaders"][0]
    if not isinstance(sub, dict) or not isinstance(sub.get("m_Passes"), list):
        raise ValueError("original_spectrum_pass_rows_invalid")
    passes = sub["m_Passes"]
    if len(passes) != PASSES:
        raise ValueError("original_Spectrum_requires_all_seven_passes")
    prop_info = parsed.get("m_PropInfo")
    props = prop_info.get("m_Props") if isinstance(prop_info, dict) else None
    if (not isinstance(props, list) or len(props) > MAX_PROPS or
            any(not isinstance(p, dict) or type(p.get("m_Type")) is not int
                for p in props)):
        raise ValueError("original_Spectrum_property_schema_unproven")
    rows = []
    texts = []
    for index, p in enumerate(passes):
        if (not isinstance(p, dict) or p.get("m_Type") != 0
                or not isinstance(p.get("m_State"), dict)):
            raise ValueError("original_Spectrum_pass_or_state_unavailable")
        # Existing ShaderLab state writer refuses unknown/dynamic fields rather
        # than fabricating fallback Blend/Depth/Cull semantics.
        state = serializer(p["m_State"], allow_selective_color_mask=True)
        if (not isinstance(state, str) or not state
                or not 0 < len(state.encode("utf-8")) <= MAX_STATE_BYTES
                or "\x00" in state):
            raise ValueError("original_Spectrum_state_serialization_incomplete")
        raw = state.encode("utf-8")
        texts.append(raw)
        rows.append({"pass_index": index, "bytes": len(raw),
                     "sha256": hashlib.sha256(raw).hexdigest()})
    return {
        "original_passes": PASSES,
        "original_property_count": len(props),
        "original_texture_property_count": sum(x["m_Type"] == 4 for x in props),
        "original_pass_state_text_bytes": sum(x["bytes"] for x in rows),
        "different_original_pass_state_blobs": len({x["sha256"] for x in rows}),
        "state_hashes_privately_verified": len(rows),
        "source_state_serialization_possible": True,
        "original_serialized_values_published": False,
        "Unity_ShaderLab_installed": False,
        "Unity_2021_import_verified": False,
        "Android_Adreno_pixels_verified": False,
    }, texts


def recover(source: Path, repo: Path, private: Path, out: Path,
            *, serializer=render_state, reader=_selected_original):
    source, repo, private, out = map(
        _safe, (source, repo, private, out))
    if (not source.is_dir() or not repo.is_dir()
            or not private.parent.is_dir() or not out.parent.is_dir()
            or private.exists() or out.exists()
            or any(x.is_relative_to(repo) for x in (source, private, out))
            or private.is_relative_to(source) or out.is_relative_to(source)):
        raise ValueError("private_Spectrum_state_paths_invalid")
    verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    _, _, original, attestation = reader(source)
    if (attestation.get("authenticated_original_passes") != PASSES
            or attestation.get("authenticated_variant_stage_programs") != 28):
        raise ValueError("original_B09_Spectrum_stage_provenance_incomplete")
    result, texts = validate(original.get("m_ParsedForm"), serializer=serializer)
    with tempfile.TemporaryDirectory(prefix="gt-spectrum-state-", dir=private.parent) as scratch:
        source_private = Path(scratch)
        for index, raw in enumerate(texts):
            path = source_private / f"source-pass-{index:02d}.state.txt"
            with path.open("xb") as fh:
                fh.write(raw)
                fh.flush()
                os.fsync(fh.fileno())
            if path.read_bytes() != raw:
                raise ValueError("private_original_render_state_write_drift")
        os.rename(source_private, private)
    result["status"] = "ORIGINAL_SPECTRUM_SEVEN_SOURCE_RENDER_STATES_PRIVATE"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    a=argparse.ArgumentParser(description=__doc__)
    for name in ("source", "repo", "private", "out"):
        a.add_argument("--" + name, type=Path, required=True)
    p=a.parse_args()
    try:
        result=recover(p.source,p.repo,p.private,p.out)
    except BaseException as exc:
        result={"status":"INCONCLUSIVE",
                "error_type":type(exc).__name__,
                "original_serialized_values_published":False,
                "Unity_ShaderLab_installed":False,
                "Android_Adreno_pixels_verified":False}
    print("GT_ORIGINAL_SPECTRUM_STATES_PRIVATE_SAFE " + json.dumps(result, sort_keys=True))
    return 0 if result["status"]=="ORIGINAL_SPECTRUM_SEVEN_SOURCE_RENDER_STATES_PRIVATE" else 2


if __name__=="__main__":
    raise SystemExit(main())
