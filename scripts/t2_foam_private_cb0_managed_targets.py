"""Private SHA-original Foam CB0 name targets for managed IL caller discovery.

Matches true original serialized CB0 name indexes (not guessed translated HLSL
identifiers) to managed ldstr later. Exact names/hashes stay in runner temp.
This is lexical evidence, never original Unity uniform upload.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.b20_foam_cb_descriptor_lineage import SOURCE_SLOTS
from scripts.b25_foam_cb_namebridge import original_name_registry, inspect_parsed
from scripts.t2_foam_member_abi import STAGES, original_source_tree, original_members, _physical
from scripts.b24_original_foam_stage_translation import TARGET, validate_stage

MAX_NAMES = 128
MAX_INPUT_BYTES = 4096


def _name(registry, idx):
    if type(idx) is not int or idx not in registry:
        return None
    value = registry[idx]
    if not isinstance(value, str) or not 0 < len(value) <= 256 or "\x00" in value:
        raise ValueError("unsafe_private_source_name")
    return value


def build_private_target_set(parsed):
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("not_SHA_original_Foam_parsed_shader")
    attest = inspect_parsed(parsed)
    if attest.get("matched_constant_buffer_bindings") != 8:
        raise ValueError("original_CB_registry_unattested")
    passes = parsed["m_SubShaders"][0]["m_Passes"]
    names = {"buffer": set(), "vector": set(), "matrix": set()}
    counts = {"original_stage_count": 0, "original_cb0_stage_bindings": 0,
              "original_cb0_vector_parameters": 0,
              "original_cb0_matrix_parameters": 0,
              "original_cb0_parameter_name_indices_unresolved": 0}
    seen = set()
    for pi, stage in STAGES:
        if (pi, stage) in seen or 0 not in SOURCE_SLOTS.get((pi, stage), ()):
            raise ValueError("original_CB0_stage_identity_missing")
        seen.add((pi, stage))
        p = passes[pi]
        registry = original_name_registry(p["m_NameIndices"])
        program = p["progVertex" if stage == 1 else "progFragment"]
        validate_stage(program, stage, {"original_pass": pi})
        buffers = program["m_CommonParameters"]["m_ConstantBuffers"]
        if not isinstance(buffers, list) or not buffers:
            raise ValueError("original_CB0_buffer_absent")
        cb0 = buffers[0]
        original_members(cb0)  # same authenticated structural row bounds as T2 ABI
        cbname = _name(registry, cb0.get("m_NameIndex"))
        if cbname is None:
            raise ValueError("original_CB0_buffer_registry_reference_missing")
        names["buffer"].add(cbname)
        for role, key in (("vector", "m_VectorParams"),
                          ("matrix", "m_MatrixParams")):
            rows = cb0.get(key)
            if not isinstance(rows, list) or len(rows) > MAX_NAMES:
                raise ValueError("original_CB0_parameter_list_malformed")
            counts["original_cb0_" + role + "_parameters"] += len(rows)
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError("original_CB0_parameter_malformed")
                n = _name(registry, row.get("m_NameIndex"))
                if n is None:
                    counts["original_cb0_parameter_name_indices_unresolved"] += 1
                    continue
                names[role].add(n)
        counts["original_stage_count"] += 1
        counts["original_cb0_stage_bindings"] += 1
    if counts["original_stage_count"] != 4 or counts["original_cb0_stage_bindings"] != 4:
        raise ValueError("original_CB0_stage_count_drift")
    all_values = set().union(*names.values())
    if not all_values or sum(map(len, names.values())) > MAX_NAMES:
        raise ValueError("original_CB0_name_target_count_invalid")
    # Per-category hashes only in temporary CI input, never stdout/artifacts.
    targets = {role: sorted(hashlib.sha256(v.encode("utf8")).hexdigest()
                            for v in values)
               for role, values in names.items()}
    # This digest is private CI scratch-only, derived from the exact
    # serialized source Shader.m_Name. Never log or upload it: even a digest
    # of a predictable shader name can disclose the original name.
    shader_name = parsed["m_Name"]
    if (not isinstance(shader_name, str) or not shader_name
            or len(shader_name) > 256 or chr(0) in shader_name):
        raise ValueError("invalid_original_Foam_shader_name")
    original_shader_digest = hashlib.sha256(shader_name.encode("utf8")).hexdigest()
    return {"schema": 1, "source_kind": "SHA_original_Foam_CB0_source_name_registry",
            "categories_sha256": targets, **counts,
            "original_Foam_Shader_mName_SHA256_private": original_shader_digest,
            "distinct_target_names": len(all_values),
            "actual_Unity_upload_proven": False}


def _owner_catalog_from_rows(shaders, materials, foam_name, foam_path_id):
    """Privacy-preserving synthetic/original typed name and local PPtr census.

    Source strings are hashed and retained *only* in runner scratch. The
    (file_id,path_id) pair is mandatory: a foreign asset can reuse PathID.
    Unparseable objects must be counted and cannot imply exhaustive results.
    """
    if (not isinstance(foam_name, str) or not foam_name or len(foam_name) > 256
            or chr(0) in foam_name or type(foam_path_id) is not int):
        raise ValueError("original_Foam_identity_unbounded")
    if not isinstance(shaders, list) or not isinstance(materials, list):
        raise ValueError("original_owner_catalog_shape")
    if len(shaders) > 8192 or len(materials) > 32768:
        raise ValueError("original_owner_catalog_unbounded")
    foam_count = 0
    seen = set()
    other = {}
    shader_unparsed = 0
    material_unparsed = 0
    local_foam_refs = 0
    external_shader_refs = 0
    for path_id, name in shaders:
        if type(path_id) is not int or path_id in seen:
            raise ValueError("duplicate_or_invalid_shader_object")
        seen.add(path_id)
        if name is None:
            shader_unparsed += 1
            continue
        if not isinstance(name, str) or not 0 < len(name) <= 256 or chr(0) in name:
            raise ValueError("original_Shader_name_invalid")
        if path_id == foam_path_id:
            if name != foam_name:
                raise ValueError("original_Foam_identity_mismatch")
            foam_count += 1
        else:
            digest = hashlib.sha256(name.encode("utf8")).hexdigest()
            other[digest] = other.get(digest, 0) + 1
    if foam_count != 1:
        raise ValueError("original_Foam_not_unique_in_owner")
    for ptr in materials:
        if ptr is None:
            material_unparsed += 1
            continue
        if (not isinstance(ptr, (tuple, list)) or len(ptr) != 2
                or any(type(n) is not int for n in ptr)):
            material_unparsed += 1
            continue
        file_id, path_id = ptr
        if file_id < 0 or path_id < 0:
            material_unparsed += 1
        elif file_id == 0 and path_id == foam_path_id:
            local_foam_refs += 1
        elif file_id != 0:
            external_shader_refs += 1
    return {
        "original_owner_other_Shader_names_SHA256_private": other,
        "original_owner_shader_objects_examined": len(shaders),
        "original_owner_other_shader_names_count": sum(other.values()),
        "original_owner_shader_name_unparsed_count": shader_unparsed,
        "original_owner_material_objects_examined": len(materials),
        "original_owner_material_source_pointer_unparsed_count": material_unparsed,
        "original_owner_material_local_Foam_Shader_ref_count": local_foam_refs,
        "original_owner_material_external_Shader_ref_count": external_shader_refs,
        "original_owner_material_Foam_PathID_other_fileID_not_counted": True,
        "original_owner_material_ref_is_runtime_bound_verified": False,
    }


def original_owner_catalog(source, parsed):
    """Read only the exact independently SHA-pinned sharedassets0 owner."""
    import UnityPy
    owner_path = Path(source) / OWNER
    if (not _physical(owner_path) or not owner_path.is_file()
            or fingerprint(owner_path) != PINS[OWNER]):
        raise ValueError("original_owner_catalog_SHA_mismatch")
    foam_name = parsed.get("m_Name")
    env = UnityPy.load(str(owner_path))
    objects = list(env.file.objects.values())
    if len(objects) > 250000:
        raise ValueError("original_owner_object_count_unbounded")
    shaders, materials = [], []
    for obj in objects:
        if obj.type.name == "Shader":
            if len(shaders) >= 8192:
                raise ValueError("original_Shader_count_unbounded")
            path_id = int(obj.path_id)
            if path_id == 2420:
                from scripts.b24_original_foam_stage_translation import ORIGINAL_OBJECT_SHA256
                if hashlib.sha256(obj.get_raw_data()).hexdigest() != ORIGINAL_OBJECT_SHA256:
                    raise ValueError("original_Foam_object_SHA_mismatch")
            try:
                shader_tree = obj.read_typetree()
                name = shader_tree["m_ParsedForm"]["m_Name"]
            except Exception:
                # Other original Shader typetrees may be unsupported on this
                # pinned UnityPy version. Count them as unparsed, never as a
                # proven absence of a name.
                name = None
            shaders.append((path_id,name))
        elif obj.type.name == "Material":
            if len(materials) >= 32768:
                raise ValueError("original_Material_count_unbounded")
            try:
                mat_tree = obj.read_typetree()
                ref = mat_tree["m_Shader"]
                pointer = (ref["m_FileID"],ref["m_PathID"])
            except Exception:
                # Material typetree failures block exhaustive claims but must
                # not take down SHA-authentic Foam Shader-object evidence.
                pointer = None
            materials.append(pointer)
    result = _owner_catalog_from_rows(shaders,materials,foam_name,2420)
    del env
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    phase = "input_guard"
    try:
        source, out = a.source.absolute(), a.out.absolute()
        if (not source.is_dir() or not _physical(source)
                or not out.parent.is_dir() or not _physical(out)
                or out.exists() or out.is_relative_to(source)):
            raise ValueError("unsafe_original_private_input_output")
        phase = "original_shader_sha"
        parsed = original_source_tree(source)
        phase = "private_CB0_registry"
        r = build_private_target_set(parsed)
        phase = "same_owner_catalog"
        r.update(original_owner_catalog(source,parsed))
        phase = "safe_private_output"
        out.write_text(json.dumps(r, sort_keys=True) + "\n", encoding="utf8")
        result = {
            "status": "original_CB0_private_name_targets_prepared",
            "original_stages": r["original_stage_count"],
            "CB0_stage_bindings": r["original_cb0_stage_bindings"],
            "original_CB0_parameter_name_indices_unresolved":
                r["original_cb0_parameter_name_indices_unresolved"],
            "exact_name_values_or_hashes_published": False,
            "original_owner_source_census_derived_only": True,
            "original_Shader_names_or_hashes_published": False,
            "Unity_CB0_upload_verified": False,
        }
        rc = 0
    except BaseException as err:
        # Only allowlisted diagnostic codes, never exception messages about
        # original Shader objects, private paths or game data.
        allowed = {
            "original_Foam_identity_unbounded",
            "original_owner_catalog_shape",
            "original_owner_catalog_unbounded",
            "duplicate_or_invalid_shader_object",
            "original_Shader_name_invalid",
            "original_Foam_identity_mismatch",
            "original_Foam_not_unique_in_owner",
            "original_owner_catalog_SHA_mismatch",
            "original_owner_object_count_unbounded",
            "original_Shader_count_unbounded",
            "original_Material_count_unbounded",
            "original_Foam_object_SHA_mismatch",
            "invalid_original_Foam_shader_name",
            "unsafe_original_private_input_output",
        }
        code = str(err) if type(err) is ValueError and str(err) in allowed else "other_error"
        safe_kinds = {
            "KeyError", "TypeError", "AttributeError", "IndexError",
            "ValueError", "RuntimeError", "AssertionError", "OverflowError",
            "NotImplementedError", "UnicodeError", "ImportError",
            "ModuleNotFoundError", "MemoryError", "OSError",
        }
        kind = type(err).__name__ if type(err).__name__ in safe_kinds else "other"
        result = {"status": "blocked_original_CB0_name_targets",
                  "safe_pipeline_phase": phase,
                  "safe_pipeline_error_code": code,
                  "safe_exception_class": kind,
                  "exact_name_values_or_hashes_published": False,
                  "Unity_CB0_upload_verified": False}
        rc = 2
    print("T2_FOAM_CB0_PRIVATE_TARGETS " + json.dumps(result, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
