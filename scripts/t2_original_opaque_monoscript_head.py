"""T2: recover original MonoBehaviour.m_Script links from opaque scene data.

This DOES NOT deserialize missing custom MonoBehaviour fields. It reads the
Unity-version class-database MonoBehaviour base header only, not a generated
typetree with possibly misaligned m_Script. PPtr owner+PathID is source
evidence; filename alone is not an authenticated GUID/runtime binding.
All proprietary names, object identifiers and original byte arrays remain in
private, SHA-pinned runner scratch. Output finite counts only.
"""
import argparse
import gc
import json
import subprocess
from pathlib import Path

from scripts.t2_original_scene_foam_component_scan import (
    select_original_levels, walk_tree_pptrs, COMPONENT_TYPES,
    EXPECTED_BYTES, EXPECTED_SCENES,
)
from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
from scripts.t2_foam_original_external_pptr_graph import (
    FOAM_OWNER, MAX_EXTERNALS, MAX_OBJECTS,
)
from scripts.w1_stage_zip2_owners import ZIP2_SHA, PINS, stage, safe, fingerprint

SOURCE_BYTES = EXPECTED_BYTES + PINS[FOAM_OWNER][0]
EXPECTED_COMPONENTS = 240961
EXPECTED_PARSED = 185633
EXPECTED_OPAQUE = 55328
MAX_TYPED_SCRIPT_OBJECTS = 65536
MAX_OPAQUE_MB = 150000
MAX_HEADERS_CROSSCHECKED = 128


def script_header_ptr(header):
    """Validate real UnityPy header object or a synthetic stand-in."""
    script = getattr(header, "m_Script", None)
    f, p = getattr(script, "m_FileID", None), getattr(script, "m_PathID", None)
    if type(f) is not int or type(p) is not int or f < 0 or p < 0:
        raise ValueError("opaque_MonoBehaviour_Script_PPtr_invalid")
    return f, p


def source_owner_fileids(externals):
    if not isinstance(externals, list) or len(externals) > MAX_EXTERNALS:
        raise ValueError("scene_external_count_unbounded")
    result = set()
    for idx, path in enumerate(externals, 1):
        if not isinstance(path, str) or not 0 < len(path) <= 1024 or "\x00" in path:
            raise ValueError("opaque_scene_external_path_invalid")
        if path.replace("\\", "/").rsplit("/", 1)[-1].casefold() == \
                "sharedassets0.assets":
            result.add(idx)
    return result


def classify_opaque_script_links(
    source_indices, opaque_rows, source_script_pathids,
    local_script_pathids,
):
    """Conservative per-scene private PPtr classifier; never output IDs."""
    if (not isinstance(source_indices, set) or
            any(type(i) is not int or i <= 0 for i in source_indices) or
            not isinstance(opaque_rows, list) or len(opaque_rows) > MAX_OPAQUE_MB or
            not isinstance(source_script_pathids, set) or
            not isinstance(local_script_pathids, set)):
        raise ValueError("opaque_script_input_shapes")
    if any(type(p) is not int or p <= 0 for p in
           source_script_pathids | local_script_pathids):
        raise ValueError("typed_MonoScript_PathID_invalid")
    counts = {
        "opaque_MonoBehaviour_records": len(opaque_rows),
        "opaque_MonoBehaviour_header_parsed": 0,
        "opaque_MonoBehaviour_header_unparsed": 0,
        "opaque_MonoBehaviour_header_null_script": 0,
        "opaque_MonoBehaviour_script_to_external_owner": 0,
        "opaque_MonoBehaviour_script_to_external_typed_MonoScript": 0,
        "opaque_MonoBehaviour_script_to_external_not_typed_MonoScript": 0,
        "opaque_MonoBehaviour_script_to_other_external_owner": 0,
        "opaque_MonoBehaviour_script_to_local_typed_MonoScript": 0,
        "opaque_MonoBehaviour_script_to_local_not_typed_MonoScript": 0,
        "opaque_MonoBehaviour_script_invalid_external_fileID": 0,
    }
    matched_typed_ids = set()
    for row in opaque_rows:
        if row is None:
            counts["opaque_MonoBehaviour_header_unparsed"] += 1
            continue
        if (not isinstance(row, (tuple, list)) or len(row) != 3
                or type(row[0]) is not int or type(row[1]) is not int
                or type(row[2]) is not int):
            raise ValueError("opaque_header_rows_invalid")
        f, p, n = row
        if f < 0 or p < 0 or n < 0:
            raise ValueError("opaque_header_pointer_or_external_range_invalid")
        counts["opaque_MonoBehaviour_header_parsed"] += 1
        if p == 0:
            counts["opaque_MonoBehaviour_header_null_script"] += 1
        elif f > n:
            counts["opaque_MonoBehaviour_script_invalid_external_fileID"] += 1
        elif f == 0:
            key = ("opaque_MonoBehaviour_script_to_local_typed_MonoScript"
                   if p in local_script_pathids else
                   "opaque_MonoBehaviour_script_to_local_not_typed_MonoScript")
            counts[key] += 1
        elif f in source_indices:
            counts["opaque_MonoBehaviour_script_to_external_owner"] += 1
            if p in source_script_pathids:
                counts["opaque_MonoBehaviour_script_to_external_typed_MonoScript"] += 1
                matched_typed_ids.add(p)  # private, count only
            else:
                counts["opaque_MonoBehaviour_script_to_external_not_typed_MonoScript"] += 1
        else:
            counts["opaque_MonoBehaviour_script_to_other_external_owner"] += 1
    counts["opaque_MonoBehaviour_distinct_external_typed_script_targets"] = len(matched_typed_ids)
    if (counts["opaque_MonoBehaviour_header_parsed"] +
            counts["opaque_MonoBehaviour_header_unparsed"] != len(opaque_rows)
            or counts["opaque_MonoBehaviour_script_to_external_owner"] !=
            counts["opaque_MonoBehaviour_script_to_external_typed_MonoScript"] +
            counts["opaque_MonoBehaviour_script_to_external_not_typed_MonoScript"]):
        raise ValueError("opaque_MonoScript_evidence_partition_error")
    return counts


def aggregate_source_counts(owner_rows, component_count, full_parse_count,
                            opaque_nonmono, source_sha_bytes,
                            original_typed_script_count, crosscheck):
    if (not isinstance(owner_rows, list) or len(owner_rows) != EXPECTED_SCENES
            or component_count != EXPECTED_COMPONENTS
            or full_parse_count != EXPECTED_PARSED
            or source_sha_bytes != SOURCE_BYTES
            or type(opaque_nonmono) is not int or opaque_nonmono < 0
            or type(original_typed_script_count) is not int
            or original_typed_script_count < 0
            or type(crosscheck) is not int
            or not 0 <= crosscheck <= MAX_HEADERS_CROSSCHECKED):
        raise ValueError("source_original_opaque_baseline_or_sha_drift")
    expected = set(classify_opaque_script_links(set(), [], set(), set()))
    if any(not isinstance(row, dict) or set(row) != expected
           or any(type(v) is not int or v < 0 for v in row.values())
           for row in owner_rows):
        raise ValueError("opaque_monoscript_result_shape")
    summed = {key: sum(r[key] for r in owner_rows) for key in expected}
    if (summed["opaque_MonoBehaviour_records"]+opaque_nonmono != EXPECTED_OPAQUE
            or summed["opaque_MonoBehaviour_header_parsed"] +
            summed["opaque_MonoBehaviour_header_unparsed"] !=
            summed["opaque_MonoBehaviour_records"]
            or summed["opaque_MonoBehaviour_script_to_external_typed_MonoScript"] >
            summed["opaque_MonoBehaviour_script_to_external_owner"]):
        raise ValueError("opaque_source_coverage_incomplete")
    # Source IDs can repeat in different scenes. Summing distinct-per-scene
    # is not the distinct global source script object count.
    summed["sum_per_scene_distinct_external_typed_script_targets"] = summed.pop(
        "opaque_MonoBehaviour_distinct_external_typed_script_targets"
    )
    return {
        "status": "source_original_MonoBehaviour_base_header_script_PPtr_census",
        "original_zip2_SHA_authenticated": True,
        "original_scene_file_count_SHA_verified": EXPECTED_SCENES,
        "original_scene_bytes_SHA_verified": EXPECTED_BYTES,
        "original_foam_owner_bytes_SHA_verified": PINS[FOAM_OWNER][0],
        "combined_original_sha_verified_bytes": source_sha_bytes,
        "original_source_typed_MonoScript_objects_in_owner": original_typed_script_count,
        "original_scene_components_examined": component_count,
        "original_scene_components_fully_parsed": full_parse_count,
        "original_scene_components_opaque": EXPECTED_OPAQUE,
        "opaque_non_MonoBehaviour_components": opaque_nonmono,
        "source_builtin_header_vs_full_typetree_script_PPtr_crosschecks": crosscheck,
        **summed,
        "script_PPtr_is_original_Foam_Shader_runtime_identity_proven": False,
        "script_name_or_original_GUID_published": False,
        "generated_custom_typetree_alignment_proven": False,
        "opaque_custom_fields_recovered": False,
        "source_original_Foam_Material_CB0_upload_verified": False,
        "Android_Adreno_water_pixels_verified": False,
    }


def inspect_original_source(zip2, scratch, progress=lambda _: None):
    import UnityPy
    zip2, scratch = Path(zip2).absolute(), Path(scratch).absolute()
    safe(zip2)
    safe(scratch)
    if scratch.is_relative_to(zip2):
        raise ValueError("original_private_staging_overwrites_ZIP2")
    progress("immutable_provider_commit_and_manifest")
    sha = subprocess.check_output(
        ["git", "-C", str(zip2), "rev-parse", "HEAD"], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
    if sha != ZIP2_SHA:
        raise ValueError("original_ZIP2_commit_drift")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    scenes = select_original_levels(manifest)
    paths = ["/RAFT_FILE_MANIFEST.tsv"]
    allrows = [*scenes, next((r for r in manifest if r["path"] == FOAM_OWNER), None)]
    if allrows[-1] is None or (
        allrows[-1]["bytes"], allrows[-1]["sha256"]
    ) != PINS[FOAM_OWNER]:
        raise ValueError("original_Foam_owner_pin_invalid")
    for row in allrows:
        name = row["path"]
        paths.append("/Raft/" + name + ("/*" if row["kind"] == "split" else ""))
    progress("sparse_authentic_original_source_files")
    subprocess.run(
        ["git", "-C", str(zip2), "sparse-checkout", "set",
         "--no-cone", *paths],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300,
    )
    progress("reconstruct_verify_41_individual_source_SHA256")
    pins = {r["path"]: (r["bytes"], r["sha256"]) for r in allrows}
    result = stage(zip2, scratch, pins)
    if (result["provider_sha"] != ZIP2_SHA or
            result["verified_bytes"] != SOURCE_BYTES or result["lfs_used"]):
        raise ValueError("original_41_provider_SHA_invalid")
    progress("load_original_typed_MonoScript_owner")
    ownerfile = scratch / FOAM_OWNER
    safe(ownerfile)
    if fingerprint(ownerfile) != PINS[FOAM_OWNER]:
        raise ValueError("original_foam_owner_sha_drift")
    env = UnityPy.load(str(ownerfile))
    objects = list(env.file.objects.values())
    if len(objects) > MAX_OBJECTS:
        raise ValueError("foam_owner_objects_exceed_budget")
    scripts = set()
    for obj in objects:
        if obj.type.name == "MonoScript":
            key = int(obj.path_id)
            if key <= 0 or key in scripts or len(scripts) > MAX_TYPED_SCRIPT_OBJECTS:
                raise ValueError("original_MonoScript_local_object_duplicate_or_unbounded")
            scripts.add(key)
    # A source owner with zero MonoScript objects is a valid negative,
    # not evidence that source scripts or runtime links do not exist elsewhere.
    del objects, env
    gc.collect()
    progress("load_original_level_MonoBehaviour_headers")
    results = []
    component_count, parsed_full, nonmono_opaque, crosschecks = 0, 0, 0, 0
    for item in scenes:
        name = item["path"]
        filename = scratch / name
        safe(filename)
        if fingerprint(filename) != pins[name]:
            raise ValueError("original_scene_file_SHA_drift")
        env = UnityPy.load(str(filename))
        file = env.file
        objs = list(file.objects.values())
        if len(objs) > MAX_OBJECTS or len(file.externals) > MAX_EXTERNALS:
            raise ValueError("original_scene_object_external_budget")
        source_ids = source_owner_fileids([x.path for x in file.externals])
        local_scripts = {int(x.path_id) for x in objs if x.type.name == "MonoScript"}
        opaque_rows = []
        for obj in objs:
            kind = obj.type.name
            if kind not in COMPONENT_TYPES:
                continue
            component_count += 1
            tree = None
            try:
                tree = obj.read_typetree()
                # Reuse original graph predicate. An oversized typetree is
                # truly opaque for this experiment, not a successful parse.
                list(walk_tree_pptrs(tree))
                parsed_full += 1
            except Exception:
                if kind != "MonoBehaviour":
                    nonmono_opaque += 1
                    continue
                try:
                    # Reads the class-database base header, not a generated
                    # custom script layout. No raw or original names exported.
                    head = obj.parse_monobehaviour_head()
                    fid, pid = script_header_ptr(head)
                    opaque_rows.append((fid, pid, len(file.externals)))
                except Exception:
                    opaque_rows.append(None)
            else:
                if kind == "MonoBehaviour" and crosschecks < MAX_HEADERS_CROSSCHECKED:
                    # A non-opaque MonoBehaviour can validate built-in header
                    # alignment by matching its full-typetree m_Script pointer.
                    ptr = tree.get("m_Script") if isinstance(tree, dict) else None
                    if isinstance(ptr, dict):
                        base = obj.parse_monobehaviour_head()
                        fid, pid = script_header_ptr(base)
                        if (fid, pid) != (ptr.get("m_FileID"), ptr.get("m_PathID")):
                            raise ValueError("builtin_header_fails_authenticated_full_tree_crosscheck")
                        crosschecks += 1
        results.append(classify_opaque_script_links(
            source_ids, opaque_rows, scripts, local_scripts,
        ))
        del objs, file, env
        gc.collect()
    return aggregate_source_counts(
        results, component_count, parsed_full, nonmono_opaque,
        result["verified_bytes"], len(scripts), crosschecks,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip2", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    stage_name = "input"
    def progress(value):
        nonlocal stage_name
        stage_name = value
    try:
        out = args.out.absolute()
        safe(out)
        if (out.exists() or not out.parent.is_dir() or
                any(out.is_relative_to(x.absolute()) for x in (args.zip2,args.scratch))):
            raise ValueError("original_report_must_not_overlap_source")
        response = inspect_original_source(args.zip2, args.scratch, progress)
        out.write_text(json.dumps(response,sort_keys=True)+"\n",encoding="utf8")
        print("T2_ORIGINAL_MONO_SCRIPT_HEADER_SAFE "+json.dumps(response,sort_keys=True))
        return 0
    except BaseException:
        print("T2_ORIGINAL_MONO_SCRIPT_HEADER_SAFE "+json.dumps({
            "status":"blocked", "safe_phase":stage_name,
            "private_original_source_names_bytes_or_GUID_disclosed":False,
        },sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
