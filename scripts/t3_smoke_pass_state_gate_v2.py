#!/usr/bin/env python3
"""Fail-closed, metadata-only per-pass smoke Shader48 state comparator.

No shader bytecode or original asset data may be passed to this tool.
A match is limited to supplied pass metadata, not GPU/device parity.
"""
import argparse
import json
import re
from pathlib import Path

ROLE = "smoke_linked_34_use_shader48"
FIELDS = ("src_blend", "dst_blend", "blend_op", "zwrite", "cull", "color_mask",
          "alpha_clip", "program_present")
BLEND = {"Zero", "One", "SrcColor", "OneMinusSrcColor", "DstColor",
         "OneMinusDstColor", "SrcAlpha", "OneMinusSrcAlpha", "DstAlpha",
         "OneMinusDstAlpha", "SrcAlphaSaturate"}
OPS = {"Add", "Subtract", "ReverseSubtract", "Min", "Max"}
CULL = {"Off", "Front", "Back"}

def _validate(side):
    if not isinstance(side, dict) or side.get("identity_role") != ROLE:
        raise ValueError("wrong_shader_identity")
    for key, expected in (("smoke_named_renderer_count", 17), ("material_slot_count", 34)):
        if type(side.get(key)) is not int or side[key] != expected:
            raise ValueError("graph_count_not_verified")
    digest = side.get("source_sha256")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None:
        raise ValueError("invalid_source_fingerprint")
    passes = side.get("passes")
    if not isinstance(passes, list) or not passes:
        raise ValueError("missing_passes")
    names = set()
    for p in passes:
        if not isinstance(p, dict):
            raise ValueError("invalid_pass")
        name = p.get("name")
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("invalid_pass_name")
        names.add(name)
        if set(p) != set(FIELDS) | {"name"}:
            raise ValueError("incomplete_pass_state")
        if p["src_blend"] not in BLEND or p["dst_blend"] not in BLEND:
            raise ValueError("invalid_blend_factor")
        if p["blend_op"] not in OPS or p["cull"] not in CULL:
            raise ValueError("invalid_render_enum")
        for key in ("zwrite", "alpha_clip", "program_present"):
            if type(p[key]) is not bool:
                raise ValueError("unknown_render_state:" + key)
        if type(p["color_mask"]) is not int or not 0 <= p["color_mask"] <= 15:
            raise ValueError("invalid_color_mask")
    return digest.lower()

def audit(data):
    if not isinstance(data, dict) or data.get("schema") != "t3-smoke-pass-state-v2":
        raise ValueError("unsupported_schema")
    original, exported = data["original"], data["exported"]
    a, b = _validate(original), _validate(exported)
    if a != b:
        raise ValueError("different_original_source")
    mismatches = []
    if len(original["passes"]) != len(exported["passes"]):
        mismatches.append("pass_count")
    for i, (left, right) in enumerate(zip(original["passes"], exported["passes"])):
        for key in ("name",) + FIELDS:
            if left[key] != right[key]:
                mismatches.append("pass[%d].%s" % (i, key))
    return {"status": "STATE_MISMATCH" if mismatches else "SCOPED_PASS_STATE_MATCH",
            "mismatches": mismatches, "device_pixels_proven": False,
            "texture_alpha_proven": False, "shader_program_authenticity_proven": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_json", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(json.loads(args.metadata_json.read_text())), sort_keys=True))

if __name__ == "__main__":
    main()
