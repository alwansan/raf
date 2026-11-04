"""B45: isolate authenticated original Blur ShaderLab wrapper failure, no private payload.

The W5 raster comparison already passed both original passes. This narrowly
checks the remaining serialized ShaderLab state conversion on pinned ZIP2.
Diagnostic placeholder stages are never written, installed, or published.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.a12_build_original_blur_wrapper import OBJECT_SHA256, PARSED_SHA256, wrapper
from scripts.a12_probe_original_blur_passes import TARGET, original_shader
from scripts.w1_depth_shaderlab import render_state


def digest(parsed):
    return hashlib.sha256(json.dumps(
        parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")).hexdigest()


def diagnose(parsed):
    """Return only safe, bounded categorical facts about original serialization."""
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original ShaderLab identity rejected")
    subs = parsed.get("m_SubShaders")
    if not isinstance(subs, list) or len(subs) != 1 or not isinstance(subs[0], dict):
        raise ValueError("Original Blur subshader topology rejected")
    passes = subs[0].get("m_Passes")
    if not isinstance(passes, list) or len(passes) != 2:
        raise ValueError("Original Blur pass topology rejected")
    props = parsed.get("m_PropInfo", {}).get("m_Props", [])
    if not isinstance(props, list):
        raise ValueError("Unexpected original material property schema")
    report = {
        "original_blur_passes": 2,
        "original_property_entries": len(props),
        "render_state": [],
        "wrapper_diagnostic_completed": False,
        "private_stage_or_shaderlab_published": False,
        "game_source_or_guid_modified": False,
        "numeric_or_device_equivalence_proven": False,
    }
    for index, shader_pass in enumerate(passes):
        if not isinstance(shader_pass, dict):
            raise ValueError("Invalid original pass schema")
        entry = {"pass_index": index, "original_pass_type": shader_pass.get("m_Type"),
                 "render_state_serialized": False, "failure_type": None}
        try:
            render_state(shader_pass["m_State"])
            entry["render_state_serialized"] = True
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            # Never emit arbitrary original data or exception text; only type.
            entry["failure_type"] = type(exc).__name__
        report["render_state"].append(entry)
    if len(props) == 0 and all(p["render_state_serialized"] and
                                 p["original_pass_type"] == 0 for p in report["render_state"]):
        # Diagnostic inert text only: NO original program or synthesized shader
        # is installed, written or included in artifact.
        try:
            _ = wrapper(parsed, {(0, 0): ("probe_vertex", "probe_fragment", "5.0"),
                                  (0, 1): ("probe_vertex", "probe_fragment", "5.0")})
            report["wrapper_diagnostic_completed"] = True
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            report["wrapper_failure_type"] = type(exc).__name__
    report["candidate_installation_eligible"] = False
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        _, object_sha, tree = original_shader(args.source, args.repo)
        parsed = tree["m_ParsedForm"]
        if object_sha != OBJECT_SHA256 or digest(parsed) != PARSED_SHA256:
            raise ValueError("Pinned original Blur object/parsed form changed")
        result = diagnose(parsed)
        result.update(authenticated_original=True, original_object_sha256=object_sha,
                      parsed_form_sha256=PARSED_SHA256)
        status = "wrapper_structurally_supported" if result["wrapper_diagnostic_completed"] else "wrapper_blocked"
        result["status"] = status
    except BaseException as exc:
        result = {"status": "source_or_probe_blocked", "failure_type": type(exc).__name__,
                  "private_stage_or_shaderlab_published": False, "game_source_or_guid_modified": False}
    args.out.write_text(json.dumps(result, sort_keys=True) + "\n")
    print("RAFT_B45_BLUR_WRAPPER " + json.dumps(result, sort_keys=True))
    if result["status"] != "wrapper_structurally_supported":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
