"""Strict FFT metadata, bytes and actual Vulkan module contract.
No source authorization or original-GUID acceptance is implied.
"""
from hashlib import sha256
from pathlib import Path
import struct
import subprocess

STEREO = frozenset(("STEREO_INSTANCING_ON", "UNITY_SINGLE_PASS_STEREO",
                    "STEREO_MULTIVIEW_ON", "STEREO_CUBEMAP_RENDER_ON"))
LANES = ("m_KeywordIndices", "m_GlobalKeywordIndices", "m_LocalKeywordIndices")


def require(ok, why):
    if not ok:
        raise ValueError(why)


def fingerprint(data):
    return {"bytes": len(data), "sha256": sha256(data).hexdigest()}


def verify_members(raw, expected):
    require(set(raw) == set(expected), "member_population")
    for name, data in raw.items():
        require(fingerprint(data) == expected[name], "member_commitment:" + name)


def verify_topology(parsed, stage_variants):
    names = parsed.get("m_KeywordNames")
    flags = parsed.get("m_KeywordFlags")
    require(type(names) is list and all(type(n) is str for n in names)
            and len(names) == len(set(names)), "keyword_name_schema")
    require(not names or set(names) == STEREO, "unknown_keyword_table")
    require(isinstance(flags, (list, bytes, bytearray)) and len(flags) == len(names)
            and all(type(f) is int and f == 0 for f in flags), "keyword_flags")
    subs = parsed.get("m_SubShaders")
    require(type(subs) is list and len(subs) == 1, "subshader_topology")
    passes = subs[0].get("m_Passes")
    require(type(passes) is list and len(passes) == 7, "pass_topology")
    result = []
    for i, p in enumerate(passes):
        require(type(p.get("m_Type")) is int and p["m_Type"] == 0, "non_normal_pass:" + str(i))
        tables = {}
        for key, program in p.items():
            if not key.startswith("prog"):
                continue
            require(type(program) is dict, "program_schema:" + key)
            rows = stage_variants(program)
            if key not in ("progVertex", "progFragment"):
                require(not rows, "unexpected_program_stage:" + key)
                continue
            # No active lane may disappear through a later stage filter.
            for _, _, row in rows:
                require(type(row) is dict and any(k in row for k in LANES), "keyword_lane_missing")
                for k in LANES:
                    require(type(row.get(k, [])) is list and not row.get(k, []),
                            "active_or_invalid_keyword_lane:" + k)
            tables[key] = rows
        require("progVertex" in tables and "progFragment" in tables and tables["progVertex"],
                "missing_vertex_stage:" + str(i))
        fallback = not tables["progFragment"]
        if fallback:
            tables["progFragment"] = tables["progVertex"]
        result.append((tables, fallback))
    return names, result


def validate_module(data, workdir, execution_models, sample_ops):
    identity = fingerprint(data)
    path = Path(workdir) / (identity["sha256"] + ".spv")
    path.write_bytes(data)
    val = subprocess.run(["spirv-val", "--target-env", "vulkan1.1", str(path)],
                         capture_output=True, timeout=30)
    diagnostic = (val.stdout + val.stderr).decode(errors="replace").strip()
    require(val.returncode == 0, "spirv_val_rejected:" + diagnostic[:1200])
    models = execution_models(data)
    require(len(models) == 1 and models <= {0, 4}, "unexpected_execution_model")
    asm = subprocess.run(["spirv-dis", "--raw-id", str(path)], capture_output=True,
                         check=True, timeout=30).stdout.decode()
    return dict(identity, models=sorted(models), image_ops=[op for op, _ in sample_ops(asm)],
                validator_exit=val.returncode), asm


def verify_modules(parsed, entries, decoder, workdir, stage_variants,
                   unity_vulkan_modules, execution_models, sample_ops, *, authored_coordinate_profile=True):
    names, topology = verify_topology(parsed, stage_variants)
    blobs, modules, assembly, passes = {}, {}, {}, []
    def decode(index):
        require(type(index) is int and 0 <= index < len(entries), "invalid_blob_index")
        if index not in blobs:
            payload = entries[index][1]
            require(len(payload) >= 32 and struct.unpack_from("<I", payload, 24)[0] == 0,
                    "embedded_blob_keyword_table_not_empty")
            refs = []
            for data in unity_vulkan_modules(payload):
                if data[:4] == b"LOMS":
                    data = subprocess.run([str(decoder)], input=data, capture_output=True,
                                          check=True, timeout=15).stdout
                h = sha256(data).hexdigest()
                if h not in modules:
                    modules[h], assembly[h] = validate_module(data, workdir, execution_models, sample_ops)
                refs.append(h)
            require(bool(refs), "empty_compiled_blob")
            blobs[index] = refs
        return blobs[index]
    for i, (tables, fallback) in enumerate(topology):
        stages = {}
        for stage, model in (("progVertex", 0), ("progFragment", 4)):
            refs = []
            for bucket, ordinal, row in tables[stage]:
                index = row.get("m_BlobIndex")
                matching = [h for h in decode(index) if model in modules[h]["models"]]
                if matching:
                    refs.append({"bucket": bucket, "ordinal": ordinal,
                                 "blob_index": index, "module_sha256": matching})
            require(bool(refs), "missing_execution_stage:" + str(i) + ":" + stage)
            for ref in refs:
                for h in ref["module_sha256"]:
                    ops = modules[h]["image_ops"]
                    if not authored_coordinate_profile:
                        continue
                    if model == 0:
                        require(not ops, "unexpected_vertex_image_operation")
                    else:
                        require(len(ops) == 1 and
                                (ops[0] == "OpImageFetch" if i == 6 else ops[0].startswith("OpImageSample")),
                                "fragment_image_family:" + str(i))
            stages[stage] = {"route_keys": [[]], "rows": refs}
        passes.append({"pass": i, "fragment_table_fallback": fallback, "stages": stages})
    return {"serialized_keyword_names": names, "serialized_keyword_flags": list(parsed["m_KeywordFlags"]),
            "used_keyword_names": [], "pass_count": len(passes), "passes": passes,
            "validated_unique_modules": len(modules), "decoded_blobs": len(blobs),
            "modules": [modules[h] for h in sorted(modules)]}, assembly
