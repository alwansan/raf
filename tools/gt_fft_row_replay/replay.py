"""Revalidate exact authored FFT bundles and reject partial serialized rows.

Mutations are in-memory counterfactuals built from real decoded VS/FS bytes.
Never read original game assets, run Unity, or modify the retained input ZIPs.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
SESSION = ROOT / "clients/GT/sessions/20261127-fft-coordinate-diagnostic"
sys.path[:0] = [str(ROOT), str(SESSION), str(ROOT / "tools/synthetic_material_alpha")]
from review_coordinate_artifacts import review, read_archive, parse, PRAGMA
from fft_coordinate_probe import NAME, sample_ops
from scripts.gt_fft_bundle_gate import require, fingerprint, verify_members, verify_modules
from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules, spirv_execution_models
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_recover_depth_passes import stage_variants

PINS = {
    "dxc": "eedccb8afa34ca208604c111b232ea42bb7f91c0cab01d409253d7a4e8ee5972",
    "hlslcc": "95afbce3a5afb5073023caae625aabeda5b2fa7ed74c4c08aa025fc180558d6c",
}
RUN = "45935871773-1-5b6f8f21627269d946aa549cd7055384914cdf82"
PRIOR = ROOT / "clients/GT/sessions/20261127-fft-bundle-gate/actual-run-45937731362.zip"
PRIOR_SHA = "eaed24f33f8f862a233a5612510aabaac0d9de17c77bbdaae948f4e5af7cde0b"
PRIOR_MEMBER = "91e32402fa41ee6c9c259b66a6b49085db810c95f1ae3aa0be89fe36cee9caff"


def previous_proof():
    require(fingerprint(PRIOR.read_bytes()) == {"bytes": 3929, "sha256": PRIOR_SHA},
            "prior_gate_archive_commitment")
    with ZipFile(PRIOR) as z:
        require(z.namelist() == ["gate.json"] and z.testzip() is None, "prior_gate_archive_members")
        raw = z.read("gate.json")
    require(fingerprint(raw) == {"bytes": 44100, "sha256": PRIOR_MEMBER}, "prior_gate_member")
    return parse(raw)


def packed_modules(*modules):
    """Serialize actual decoded module bytes into a minimal Unity program wrapper."""
    require(0 < len(modules) <= 6, "counterfactual_module_count")
    table = bytearray(52)
    for i, module in enumerate(modules):
        require(module[:4] == b"\x03\x02\x23\x07", "counterfactual_not_real_spirv")
        struct.pack_into("<II", table, 4 + 8*i, len(table), len(module))
        table.extend(module)
    header = bytearray(28)
    struct.pack_into("<I", header, 0, 202012090)
    return bytes(header) + struct.pack("<I", len(table)) + table


def rejects(controls, name, expected, operation):
    try:
        operation()
    except ValueError as exc:
        require(str(exc) == expected, "wrong_rejection:" + name + ":" + str(exc))
        controls.append({"name": name, "rejected": True, "reason": str(exc)})
    else:
        raise ValueError("negative_control_accepted:" + name)


def verify(path, mode, decoder, prior):
    import UnityPy
    pinned = parse((SESSION / "artifact-review.json").read_bytes())["modes"][mode]
    reviewed, source = review(path, PINS[mode], RUN + "-" + mode, mode, False)
    require(reviewed == pinned, "historical_archive_receipt_changed")
    archive, raw = read_archive(path, PINS[mode])
    require(fingerprint(archive) == pinned["archive"], "archive_commitment")
    verify_members(raw, pinned["members"])
    trees = [o.read_typetree() for o in UnityPy.load(raw["authored.bundle"]).objects
             if o.type.name == "Shader"]
    require(len(trees) == 1 and trees[0]["m_ParsedForm"]["m_Name"] == NAME
            and list(trees[0]["platforms"]) == [18], "authored_shader_platform")
    tree = trees[0]
    [(platform, segments)] = list(decoded_platforms(tree))
    require(platform == 18, "platform")
    entries, parsed = records(segments), tree["m_ParsedForm"]
    controls = []
    with tempfile.TemporaryDirectory(prefix="gt-fft-row-replay-") as tmp:
        def gate(p, e=entries):
            return verify_modules(p, e, str(decoder), tmp, stage_variants,
                                  unity_vulkan_modules, spirv_execution_models, sample_ops)[0]

        proof = gate(parsed)
        require(all(prior.get(k) == v for k, v in proof.items()), "positive_proof_differs_from_prior")
        require(proof["pass_count"] == 7 and proof["validated_unique_modules"] == 14
                and proof["decoded_blobs"] == 7, "positive_module_population")
        for p in proof["passes"]:
            require(p["fragment_table_fallback"] is True, "expected_actual_combined_table")
            for stage in ("progVertex", "progFragment"):
                rows = p["stages"][stage]["rows"]
                require([r["bucket"] for r in rows] == [0, 1, 2]
                        and all(r["ordinal"] == 0 and len(r["module_sha256"]) == 1 for r in rows),
                        "actual_row_population")

        def pass_at(p, i):
            return p["m_SubShaders"][0]["m_Passes"][i]

        def row_at(p, i, stage, bucket):
            matches = [r for b, o, r in stage_variants(pass_at(p, i)[stage])
                       if b == bucket and o == 0]
            require(len(matches) == 1, "counterfactual_row_identity")
            return matches[0]

        def real_module(i, stage, bucket=1):
            h = next(r["module_sha256"][0] for r in proof["passes"][i]["stages"][stage]["rows"]
                     if r["bucket"] == bucket)
            data = (Path(tmp) / (h + ".spv")).read_bytes()
            require(sha256(data).hexdigest() == h, "decoded_module_commitment")
            return data

        def altered_row(i, stage, modules, *, separate=False):
            changed = deepcopy(parsed)
            if separate:
                p = pass_at(changed, i)
                p["progFragment"] = deepcopy(p["progVertex"])
            altered = list(entries)
            row = row_at(changed, i, stage, 1)
            old_index = row["m_BlobIndex"]
            row["m_BlobIndex"] = len(altered)
            altered.append((entries[old_index][0], packed_modules(*modules)))
            # Original complete rows/blobs stay byte-identical.
            require(altered[:len(entries)] == entries, "original_entries_changed")
            return changed, altered

        vs = real_module(0, "progVertex")
        fs = real_module(0, "progFragment")
        for name, modules, reason in (
                ("partial_combined_fs_missing", (vs,), "missing_execution_stage:0:progFragment"),
                ("partial_combined_vs_missing", (fs,), "missing_execution_stage:0:progVertex"),
                ("duplicate_combined_fs_module", (vs, fs, fs), "ambiguous_execution_stage:0:progFragment"),
                ("duplicate_combined_vs_module", (vs, vs, fs), "ambiguous_execution_stage:0:progVertex")):
            changed, altered = altered_row(0, "progVertex", modules)
            rejects(controls, name, reason, lambda: gate(changed, altered))

        changed = deepcopy(parsed)
        bucket = pass_at(changed, 0)["progVertex"]["m_PlayerSubPrograms"][1]
        bucket.append(deepcopy(bucket[0]))
        rejects(controls, "duplicate_empty_bucket_row", "duplicate_empty_route_bucket:0:progVertex",
                lambda: gate(changed))

        changed = deepcopy(parsed)
        p = pass_at(changed, 0)
        p["progFragment"] = deepcopy(p["progVertex"])
        p["progFragment"]["m_PlayerSubPrograms"][1] = []
        rejects(controls, "separate_bucket_population_mismatch", "stage_bucket_mismatch:0",
                lambda: gate(changed))

        changed, altered = altered_row(0, "progFragment", (vs,), separate=True)
        rejects(controls, "partial_separate_fs_missing", "missing_execution_stage:0:progFragment",
                lambda: gate(changed, altered))

        changed, altered = altered_row(0, "progVertex", (fs,), separate=True)
        rejects(controls, "partial_separate_vs_missing", "missing_execution_stage:0:progVertex",
                lambda: gate(changed, altered))

        changed, altered = altered_row(6, "progVertex", (real_module(6, "progVertex"),))
        rejects(controls, "last_pass_partial_fs_missing", "missing_execution_stage:6:progFragment",
                lambda: gate(changed, altered))

        require(len(controls) == 9, "control_population")
    return {"archive": pinned["archive"], "members": pinned["members"],
            "proof": proof, "positive_proof_identical_to_45937731362": True,
            "actual_vs_rows": 21, "actual_fs_rows": 21, "controls": controls,
            "counterfactuals_not_actual_serialized_bundle": True}, source


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("dxc", "hlslcc", "decoder", "out"):
        p.add_argument("--" + key, required=True, type=Path)
    a = p.parse_args()
    require(not a.out.exists() and not a.out.is_symlink(), "fresh_report")
    prior = previous_proof()
    rows, sources = {}, {}
    for mode in PINS:
        rows[mode], sources[mode] = verify(getattr(a, mode), mode, a.decoder, prior["modes"][mode])
    require(sources["dxc"].replace(PRAGMA, b"") == sources["hlslcc"], "pragma_only_source_difference")
    result = {"status": "PASS_AUTHORED_FFT_COMPLETE_ROW_COVERAGE", "modes": rows,
              "prior_gate_run": 45937731362, "input_run": 45935871773,
              "actual_unity_reexecution": False, "original_assets_read": False,
              "original_game_or_device_pixels_verified": False, "XAPK_requested": False}
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("GT_FFT_COMPLETE_ROW_COVERAGE modes=2 passes=14 unique_modules_sum=28 "
          "vertex_rows=42 fragment_rows=42 controls_rejected=18 authored_only=true")


if __name__ == "__main__":
    main()
