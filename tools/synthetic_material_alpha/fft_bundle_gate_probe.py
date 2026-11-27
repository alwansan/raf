"""G4 gate on only two independently pinned authored Unity bundles."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SESSION = ROOT / "clients/GT/sessions/20261127-fft-coordinate-diagnostic"
sys.path[:0] = [str(ROOT), str(SESSION)]
from review_coordinate_artifacts import review, read_archive, parse, exact_fields, PRAGMA
from fft_coordinate_probe import NAME, shaders, sample_ops, wrong_coordinate
from scripts.gt_fft_bundle_gate import (require, fingerprint, verify_members, verify_topology,
                                        verify_modules, validate_module, LANES)
from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules, spirv_execution_models
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_recover_depth_passes import stage_variants

PIN = {
    "dxc": "eedccb8afa34ca208604c111b232ea42bb7f91c0cab01d409253d7a4e8ee5972",
    "hlslcc": "95afbce3a5afb5073023caae625aabeda5b2fa7ed74c4c08aa025fc180558d6c",
}
RUN = "45935871773-1-5b6f8f21627269d946aa549cd7055384914cdf82"


def rejects(controls, name, prefix, operation):
    try:
        operation()
    except ValueError as exc:
        require(str(exc).startswith(prefix), "unexpected_rejection:" + name + ":" + str(exc))
        controls.append({"name": name, "rejected": True, "reason": str(exc)[:1400]})
    else:
        raise ValueError("negative_control_accepted:" + name)


def verify(path, mode, decoder):
    import UnityPy
    pinned = parse((SESSION / "artifact-review.json").read_bytes())["modes"][mode]
    require(pinned["archive"]["sha256"] == PIN[mode], "pinned_archive_identity")
    reviewed, source = review(path, PIN[mode], RUN + "-" + mode, mode, False)
    require(reviewed == pinned, "pinned_receipt_review_mismatch")
    archive, raw = read_archive(path, PIN[mode])
    require(fingerprint(archive) == pinned["archive"], "archive_commitment")
    verify_members(raw, pinned["members"])
    require(source == raw["authored.shader"] == shaders()[mode], "authored_source_identity")
    exact_fields(parse(raw["unity.json"]), {
        "checkpoint": "compiler_results", "errors": 0, "passCount": 7,
        "registeredKeywordVariants": 1, "privateBundleCompiled": True,
        "androidVulkanOnly": True, "unityVersion": "2021.3.45f2",
        "originalMaterialGuidProven": False, "gamePlayerBuilt": False,
        "devicePixelsProven": False, "compilerControl": mode,
        "candidateSha256": fingerprint(source)["sha256"],
    })
    trees = [o.read_typetree() for o in UnityPy.load(raw["authored.bundle"]).objects
             if o.type.name == "Shader"]
    require(len(trees) == 1 and trees[0]["m_ParsedForm"]["m_Name"] == NAME
            and list(trees[0]["platforms"]) == [18], "authored_bundle_identity")
    tree = trees[0]
    [(platform, segments)] = list(decoded_platforms(tree))
    require(platform == 18, "platform")
    entries, parsed = records(segments), tree["m_ParsedForm"]
    controls = []
    for member in ("authored.bundle", "unity.json", "authored.shader"):
        changed = dict(raw)
        data = raw[member]
        i = len(data) // 2
        changed[member] = data[:i] + bytes([data[i] ^ 1]) + data[i+1:]
        require(len(changed[member]) == len(data), "mutation_size")
        rejects(controls, "same_size_" + member, "member_commitment:" + member,
                lambda: verify_members(changed, pinned["members"]))
    with tempfile.TemporaryDirectory(prefix="gt-fft-gate-") as tmp:
        def gate(p, e=entries):
            return verify_modules(p, e, decoder, tmp, stage_variants, unity_vulkan_modules,
                                  spirv_execution_models, sample_ops)
        proof, asm = gate(parsed)
        require(proof["validated_unique_modules"] == 14, "authored_module_population")
        changed = deepcopy(parsed)
        changed["m_KeywordNames"][0] = "UNKNOWN_ENGINE_KEYWORD"
        rejects(controls, "unknown_unused_name", "unknown_keyword_table",
                lambda: verify_topology(changed, stage_variants))
        changed = deepcopy(parsed)
        changed["m_KeywordFlags"] = [1, 0, 0, 0]
        rejects(controls, "nonzero_keyword_flag", "keyword_flags",
                lambda: verify_topology(changed, stage_variants))
        for lane in LANES:
            changed = deepcopy(parsed)
            row = stage_variants(changed["m_SubShaders"][0]["m_Passes"][0]["progVertex"])[0][2]
            row[lane] = [0]
            rejects(controls, "active_" + lane, "active_or_invalid_keyword_lane:" + lane,
                    lambda: verify_topology(changed, stage_variants))
        changed = deepcopy(parsed)
        changed["m_SubShaders"][0]["m_Passes"][0]["progVertex"] = {}
        rejects(controls, "missing_vertex_table", "missing_vertex_stage:", lambda: gate(changed))
        # Preserve rows, remove real fragment execution from the referenced blobs.
        h = proof["passes"][0]["stages"]["progVertex"]["rows"][0]["module_sha256"][0]
        vs = (Path(tmp) / (h + ".spv")).read_bytes()
        table = bytearray(52)
        struct.pack_into("<II", table, 4, len(table), len(vs))
        table.extend(vs)
        header = bytearray(28)
        struct.pack_into("<I", header, 0, 202012090)
        vs_only = bytes(header) + struct.pack("<I", len(table)) + table
        altered = list(entries)
        p0 = parsed["m_SubShaders"][0]["m_Passes"][0]
        for stage in ("progVertex", "progFragment"):
            for _, _, row in stage_variants(p0[stage]):
                idx = row["m_BlobIndex"]
                altered[idx] = (entries[idx][0], vs_only)
        rejects(controls, "missing_fragment_execution_model", "missing_execution_stage:0:progFragment",
                lambda: gate(parsed, altered))
        for i, family in ((0, "sample"), (6, "fetch")):
            h = proof["passes"][i]["stages"]["progFragment"]["rows"][0]["module_sha256"][0]
            bad = Path(tmp) / ("bad-" + family + ".spvasm")
            bad.write_text(wrong_coordinate(asm[h], family))
            binary = bad.with_suffix(".spv")
            subprocess.run(["spirv-as", "--target-env", "vulkan1.1", str(bad), "-o", str(binary)],
                           capture_output=True, check=True, timeout=30)
            rejects(controls, "actual_bundle_wrong_" + family, "spirv_val_rejected:",
                    lambda: validate_module(binary.read_bytes(), tmp, spirv_execution_models, sample_ops))
            require(re.search(r"coordinate.*" + ("float" if family == "sample" else "(?:int|integer)"),
                              controls[-1]["reason"], re.I), "wrong_coordinate_rejection_reason")
    return dict(proof, mode=mode, archive=pinned["archive"], members=pinned["members"],
                receipt_run=RUN + "-" + mode, negative_controls=controls,
                original_assets_read=False, original_gate_changed=False), source


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for opt in ("decoder", "dxc", "hlslcc", "out"):
        p.add_argument("--" + opt, required=True, type=Path)
    a = p.parse_args()
    require(not a.out.exists(), "fresh_report")
    reports, sources = {}, {}
    for mode in PIN:
        reports[mode], sources[mode] = verify(getattr(a, mode), mode, a.decoder)
    require(sources["dxc"].replace(PRAGMA, b"") == sources["hlslcc"], "different_control_bodies")
    result = {"status": "PASS_AUTHORED_FFT_EMPTY_ROUTE_BUNDLE_GATE",
              "modes": reports, "original_gate_changed": False,
              "original_coordinate_root_cause_resolved": False,
              "original_game_or_device_pixels_verified": False, "XAPK_requested": False}
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({m: {"modules": r["validated_unique_modules"],
                          "negative_controls": len(r["negative_controls"]),
                          "passes": r["pass_count"]} for m, r in reports.items()}, sort_keys=True))
