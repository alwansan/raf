"""B24 authentic Foam/Global 2-pass original-DXBC-to-Vulkan feasibility.
Never publish original source, HLSL, DXBC, ShaderLab or private identifiers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from scripts.w1_stage_zip2_owners import PINS, fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import linked_program, stage_variants
from scripts.a12_shader_parameter_decode import parse_parameter_blob

TARGET = "UltimateWater/Foam/Global"
OWNER = "Raft_Data/sharedassets0.assets"
OBJECT_ID = 2420
CB = {1: ((160, 2, 0), (176, 0, 1), (368, 0, 1)), 0: ((160, 2, 0),)}


def validate_stage(program, stage, diagnostic=None):
    diagnostic = diagnostic if diagnostic is not None else {}
    if not isinstance(program, dict):
        raise ValueError("Original Foam stage absent")
    variants = stage_variants(program)
    if len(variants) != 1 or variants[0][0] is None:
        raise ValueError("Foam original player variant count changed")
    bucket, offset, metadata = variants[0]
    if metadata.get("m_KeywordIndices"):
        raise ValueError("Foam original keyword permutation unresolved")
    players = program.get("m_PlayerSubPrograms")
    table = program.get("m_ParameterBlobIndices")
    if not isinstance(players, list) or not isinstance(table, list) or len(players) != len(table):
        raise ValueError("Foam original parameter table mismatched")
    if bucket >= len(table) or offset >= len(table[bucket]):
        raise ValueError("Foam original parameter index missing")
    parameter_index = table[bucket][offset]
    if type(parameter_index) is not int or parameter_index < 0:
        raise ValueError("Foam original parameter index invalid")
    common = program.get("m_CommonParameters")
    if not isinstance(common, dict):
        raise ValueError("Foam original common parameters missing")
    buffers, bindings = common.get("m_ConstantBuffers"), common.get("m_ConstantBufferBindings")
    expected = CB[stage]
    if not isinstance(buffers, list) or not isinstance(bindings, list) or len(buffers) != len(expected) or len(bindings) != len(expected):
        raise ValueError("Foam original CB counts mismatch")
    for slot, ((size, vec, mat), b, ref) in enumerate(zip(expected, buffers, bindings)):
        diagnostic["cb_index"] = slot
        # The source-pinned second Foam vertex pass varies partial-CB
        # members. Recover its actual bounded count; never force first-pass
        # member counts onto another authentic original pass.
        measured = len(b.get("m_VectorParams", [])) if isinstance(b, dict) else -1
        varied = (slot == 0 and diagnostic.get("original_pass") == 1)
        vectors_valid = (0 <= measured <= size // 16) if varied else measured == vec
        if varied:
            diagnostic["original_second_pass_vector_members"] = measured
        tests = (
            ("record-shape", isinstance(b, dict) and isinstance(ref, dict)),
            ("buffer-size", isinstance(b, dict) and b.get("m_Size") == size),
            ("partial-flag", isinstance(b, dict) and b.get("m_IsPartialCB") is True),
            ("vector-count", isinstance(b, dict) and vectors_valid),
            ("matrix-count", isinstance(b, dict) and len(b.get("m_MatrixParams", [])) == mat),
            ("buffer-name-index", isinstance(b, dict) and b.get("m_NameIndex") == slot),
            ("binding-name-index", isinstance(ref, dict) and ref.get("m_NameIndex") == slot),
            ("binding-register", isinstance(ref, dict) and ref.get("m_Index") == slot),
            ("binding-array", isinstance(ref, dict) and ref.get("m_ArraySize") == 1),
        )
        for reason, ok in tests:
            if not ok:
                diagnostic["cb_rejection_reason"] = reason
                raise ValueError("Foam original partial-CB size/slot/member drift")
    return metadata, parameter_index


def inspect(parsed, entries, scratch, *,
            link=linked_program, translator=translate, parse=parse_parameter_blob,
            diagnostic=None):
    diagnostic = diagnostic if diagnostic is not None else {}
    diagnostic["phase"] = "original-two-pass-shape"
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Foam original shader identity mismatch")
    subs = parsed.get("m_SubShaders")
    if not isinstance(subs, list) or len(subs) != 1:
        raise ValueError("Foam original subshader count mismatch")
    passes = subs[0].get("m_Passes")
    if not isinstance(passes, list) or len(passes) != 2:
        raise ValueError("Foam original two-pass count mismatch")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 256:
        raise ValueError("Foam original compressed program table invalid")
    results = []
    for pass_index, p in enumerate(passes):
        diagnostic["original_pass"] = pass_index
        diagnostic["phase"] = "original-pass-type"
        if not isinstance(p, dict) or p.get("m_Type") != 0:
            raise ValueError("Foam original pass kind unsupported")
        for stage, name in ((1, "progVertex"), (0, "progFragment")):
            diagnostic["stage_code"] = stage
            diagnostic["phase"] = "original-partial-cb-and-parameter-index"
            metadata, index = validate_stage(p.get(name), stage, diagnostic)
            if index >= len(entries) or not isinstance(entries[index][1], bytes):
                raise ValueError("Foam original parameter entry absent")
            raw = entries[index][1]
            diagnostic["phase"] = "original-parameter-decode"
            parameter = parse(raw)
            if not isinstance(parameter, dict):
                raise ValueError("Foam original parameter decoder returned no shape")
            diagnostic["phase"] = "original-dxbc-stage-link"
            dxbc, binding = link(metadata, entries, stage)
            if not isinstance(dxbc, bytes) or len(dxbc) < 32:
                raise ValueError("Foam original linked GPU program invalid")
            dest = scratch / ("pass%d-stage%d" % (pass_index, stage))
            dest.mkdir()
            diagnostic["phase"] = "private-stage-translation"
            converted = translator(dxbc, stage, dest)
            results.append({
                "pass": pass_index, "stage_code": stage,
                "original_blob_index": binding["blob_index"],
                "original_program_sha256": hashlib.sha256(dxbc).hexdigest(),
                "original_parameter_sha256": hashlib.sha256(raw).hexdigest(),
                "parameter_bytes": len(raw), "parameter_shape": parameter,
                "partial_cb_slots": len(CB[stage]),
                "original_second_pass_vector_members": diagnostic.get("original_second_pass_vector_members") if pass_index == 1 else None,
                "original_spirv_valid": converted["vulkan11_valid"],
                "private_hlsl_recovered": converted["hlsl_recovered"],
                "rebuilt_spirv_valid": converted["roundtrip_vulkan11_valid"],
                "source_published": False,
            })
    if len(results) != 4:
        raise ValueError("Foam original four stages missing")
    return results


def probe(source, diagnostic=None):
    diagnostic = diagnostic if diagnostic is not None else {}
    diagnostic["phase"] = "owner-sha-verification"
    import UnityPy
    path = source / OWNER
    if not path.is_file() or path.is_symlink() or fingerprint(path) != PINS[OWNER]:
        raise ValueError("Foam original ZIP2 owner authentication failed")
    diagnostic["phase"] = "original-unity-object-read"
    env = UnityPy.load(str(path))
    objs = [x for x in env.file.objects.values()
            if x.type.name == "Shader" and int(x.path_id) == OBJECT_ID]
    if len(objs) != 1:
        raise ValueError("Foam original asset object missing")
    original = objs[0]
    original_sha = hashlib.sha256(original.get_raw_data()).hexdigest()
    diagnostic["phase"] = "original-parsed-form"
    tree = original.read_typetree()
    diagnostic["phase"] = "original-d3d11-platform-table"
    tables = [(platform, records(segments)) for platform, segments in decoded_platforms(tree) if platform == 4]
    if len(tables) != 1:
        raise ValueError("Foam original D3D11 table missing")
    with tempfile.TemporaryDirectory(prefix="b24-foam-private-") as dirname:
        stages = inspect(tree.get("m_ParsedForm"), tables[0][1], Path(dirname), diagnostic=diagnostic)
    return {
        "authentic_source_sha256": PINS[OWNER][1],
        "object_sha256": original_sha,
        "original_object_path_id": OBJECT_ID,
        "original_passes": 2, "linked_stages": len(stages),
        "all_original_spirv_valid": all(row["original_spirv_valid"] for row in stages),
        "all_private_hlsl_recovered": all(row["private_hlsl_recovered"] for row in stages),
        "all_rebuilt_spirv_valid": all(row["rebuilt_spirv_valid"] for row in stages),
        "stages": stages,
        "shaderlab_restored": False,
        "partial_cb_runtime_binding_verified": False,
        "unity_or_phone_verified": False,
        "original_gpu_source_published": False,
        "water_ready": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    diagnostic = {}
    try:
        report = probe(args.source, diagnostic=diagnostic)
        args.out.write_text(json.dumps(report, sort_keys=True) + "\n")
        print("B24_FOAM_PROBE " + json.dumps(report, sort_keys=True))
        return 0 if report["all_rebuilt_spirv_valid"] else 2
    except Exception as exc:
        # Exception class only: do not echo private paths, names or shader text.
        report = {"status": "incomplete", "error_type": type(exc).__name__,
                  "bounded_failure_phase": diagnostic.get("phase", "unknown"),
                  "bounded_failure_pass": diagnostic.get("original_pass"),
                  "bounded_failure_stage": diagnostic.get("stage_code"),
                  "bounded_cb_slot": diagnostic.get("cb_index"),
                  "bounded_cb_reason": diagnostic.get("cb_rejection_reason"),
                  "original_gpu_source_published": False, "shaderlab_restored": False,
                  "unity_or_phone_verified": False}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, sort_keys=True) + "\n")
        print("B24_FOAM_PROBE " + json.dumps(report, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
