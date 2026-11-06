"""T2: source-authentic original MonoScript -> managed TypeDef identity bridge.

Uses SHA-pinned ZIP2 file manifest, independently verifies two small original
providers (one MonoScript serialized owner and Assembly-CSharp.dll), and compares
only exact namespace/class metadata privately. Emits counts only.
This does NOT reconstruct MonoBehaviour custom fields, prove original Foam
Shader binding, or test Android graphics.
"""
import argparse
import gc
import json
import subprocess
from collections import Counter
from pathlib import Path

from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
from scripts.w1_stage_zip2_owners import ZIP2_SHA, stage, safe, fingerprint
from scripts.t2_foam_original_external_pptr_graph import MAX_OBJECTS

MONO_OWNER_BYTES = 758412
MANAGED_BYTES = 3211776
MIN_TARGET_TYPED_MONO_SCRIPTS = 473
MAX_MONO_SCRIPTS = 16000
MAX_MANAGED_TYPES = 50000
TARGET_ASSEMBLY = "Assembly-CSharp.dll"


def unique_original_source_rows(manifest):
    """Find a manifest-unique source size, then verify the DLL name privately."""
    if not isinstance(manifest, list) or len(manifest) != 366:
        raise ValueError("original_manifest_count_drift")
    mono = [x for x in manifest if x["bytes"] == MONO_OWNER_BYTES]
    dll = [x for x in manifest if x["bytes"] == MANAGED_BYTES]
    if len(mono) != 1 or len(dll) != 1:
        raise ValueError("original_source_unique_provider_size_drift")
    if (dll[0]["path"].replace("\\", "/").rsplit("/", 1)[-1] != TARGET_ASSEMBLY
            or not dll[0]["path"].startswith("Raft_Data/Managed/")
            or any(x["kind"] != "plain" for x in (*mono, *dll))
            or mono[0]["path"] == dll[0]["path"]):
        raise ValueError("original_source_assembly_provider_or_kind_drift")
    return mono[0], dll[0]


def normalized_script_record(raw):
    """Read authored MonoScript metadata; malformed data stays unknown."""
    if type(raw) is not dict:
        return None
    fields = ("m_ClassName", "m_Namespace", "m_AssemblyName")
    if any(type(raw.get(k)) is not str for k in fields):
        return None
    name, ns, asm = (raw[k] for k in fields)
    if (not name or len(name) > 256 or len(ns) > 512
            or not asm or len(asm) > 128
            or any("\x00" in val for val in (name, ns, asm))
            or any("\n" in val or "\r" in val for val in (name, ns, asm))):
        return None
    return (asm, ns, name)


def type_catalog(type_rows):
    """Managed TypeDef names retain exact case; duplicates are not guessed."""
    if not isinstance(type_rows, (list, tuple)) or not 0 < len(type_rows) <= MAX_MANAGED_TYPES:
        raise ValueError("managed_typedef_rows_invalid")
    counts = Counter()
    for raw in type_rows:
        if (type(raw) is not tuple or len(raw) != 2
                or any(type(k) is not str or len(k) > 512 or "\x00" in k for k in raw)
                or not raw[1] or len(raw[1]) > 256):
            raise ValueError("managed_typedef_row_malformed")
        counts[raw] += 1
    return counts


def classify_script_metadata(records, managed_type_counts):
    """Private record tuples in, finite safe scalar counts out."""
    if (not isinstance(records, list) or not 0 < len(records) <= MAX_MONO_SCRIPTS
            or not isinstance(managed_type_counts, Counter)):
        raise ValueError("original_script_join_input_unbounded")
    output = dict(
        original_typed_MonoScript_objects_total=len(records),
        original_MonoScript_class_metadata_unreadable=0,
        original_MonoScript_other_assembly=0,
        original_MonoScript_Assembly_CSharp_candidate=0,
        original_MonoScript_Assembly_CSharp_unique_TypeDef=0,
        original_MonoScript_Assembly_CSharp_ambiguous_TypeDef=0,
        original_MonoScript_Assembly_CSharp_missing_TypeDef=0,
    )
    for record in records:
        if record is None:
            output["original_MonoScript_class_metadata_unreadable"] += 1
            continue
        if not isinstance(record, tuple) or len(record) != 3:
            raise ValueError("original_metadata_record_shape")
        assembly, namespace, classname = record
        if any(type(x) is not str for x in record):
            raise ValueError("original_metadata_record_types")
        if assembly != TARGET_ASSEMBLY and assembly != "Assembly-CSharp":
            output["original_MonoScript_other_assembly"] += 1
            continue
        output["original_MonoScript_Assembly_CSharp_candidate"] += 1
        matched = managed_type_counts.get((namespace, classname), 0)
        field = ("original_MonoScript_Assembly_CSharp_unique_TypeDef" if matched == 1
                 else "original_MonoScript_Assembly_CSharp_ambiguous_TypeDef" if matched > 1
                 else "original_MonoScript_Assembly_CSharp_missing_TypeDef")
        output[field] += 1
    if (sum(output[k] for k in (
            "original_MonoScript_class_metadata_unreadable",
            "original_MonoScript_other_assembly",
            "original_MonoScript_Assembly_CSharp_candidate")) != len(records)
            or sum(output[k] for k in (
                "original_MonoScript_Assembly_CSharp_unique_TypeDef",
                "original_MonoScript_Assembly_CSharp_ambiguous_TypeDef",
                "original_MonoScript_Assembly_CSharp_missing_TypeDef"))
            != output["original_MonoScript_Assembly_CSharp_candidate"]):
        raise ValueError("original_MonoScript_managed_partition_mismatch")
    return output


def inspect_original(zip2, scratch, checkpoint=lambda _: None):
    import UnityPy
    import dnfile
    zip2, scratch = Path(zip2).absolute(), Path(scratch).absolute()
    safe(zip2)
    safe(scratch)
    if scratch.is_relative_to(zip2) or not scratch.is_dir():
        raise ValueError("private_source_stage_path_invalid")
    checkpoint("verify_immutable_original_provider_and_manifest")
    sha = subprocess.check_output(
        ["git", "-C", str(zip2), "rev-parse", "HEAD"], text=True,
        stderr=subprocess.DEVNULL).strip()
    if sha != ZIP2_SHA:
        raise ValueError("original_provider_commit_mismatch")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    mono, dll = unique_original_source_rows(manifest)
    checkpoint("sparse_checkout_only_original_small_source_files")
    patterns = ["/RAFT_FILE_MANIFEST.tsv"]
    for item in (mono, dll):
        patterns.append("/Raft/" + item["path"])
    subprocess.run(["git", "-C", str(zip2), "sparse-checkout",
                    "set", "--no-cone", *patterns], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   timeout=180)
    pins = {x["path"]: (x["bytes"], x["sha256"]) for x in (mono, dll)}
    checkpoint("verify_both_original_sha_files")
    result = stage(zip2, scratch, pins)
    if (result["provider_sha"] != ZIP2_SHA
            or result["verified_bytes"] != MONO_OWNER_BYTES+MANAGED_BYTES
            or result["lfs_used"] is not False):
        raise ValueError("original_SHA_verified_stage_drift")
    for item in (mono, dll):
        if fingerprint(scratch / item["path"]) != pins[item["path"]]:
            raise ValueError("original_file_sha_verification_drift")
    checkpoint("read_original_MonoScript_built_in_metadata")
    env = UnityPy.load(str(scratch / mono["path"]))
    objs = list(env.file.objects.values())
    if len(objs) > MAX_OBJECTS:
        raise ValueError("original_target_object_count_unbounded")
    records = []
    for obj in objs:
        if obj.type.name != "MonoScript":
            continue
        if len(records) >= MAX_MONO_SCRIPTS:
            raise ValueError("original_typed_MonoScript_count_unbounded")
        try:
            record = normalized_script_record(obj.read_typetree())
        except Exception:
            record = None
        records.append(record)
    del objs, env
    gc.collect()
    if len(records) < MIN_TARGET_TYPED_MONO_SCRIPTS:
        raise ValueError("original_target_MonoScript_coverage_below_known_references")

    checkpoint("parse_source_authenticated_managed_typedef_metadata")
    pe = dnfile.dnPE(str(scratch / dll["path"]))
    if (pe.net is None or pe.net.mdtables is None
            or pe.net.mdtables.TypeDef is None):
        raise ValueError("original_managed_typedef_metadata_missing")
    rows = pe.net.mdtables.TypeDef.rows
    managed_rows = [(str(row.TypeNamespace), str(row.TypeName)) for row in rows]
    catalog = type_catalog(managed_rows)
    counts = classify_script_metadata(records, catalog)
    # Explicit numerical/boolean only output, never original namespaces/names.
    return {
        "status": "original_MonoScript_to_SHA_managed_TypeDef_census",
        "immutable_original_zip2_SHA_verified": True,
        "original_manifest_rows_metadata_verified": len(manifest),
        "original_unique_MonoScript_owner_size_candidate": True,
        "original_unique_managed_DLL_size_candidate": True,
        "original_typed_MonoScript_owner_SHA_verified_bytes": MONO_OWNER_BYTES,
        "original_managed_Assembly_CSharp_SHA_verified_bytes": MANAGED_BYTES,
        "original_managed_TypeDef_rows": len(managed_rows),
        "original_managed_distinct_TypeDef_namespace_class_keys": len(catalog),
        **counts,
        "original_scripts_current_scene_473_references_rechecked": False,
        "original_MonoScript_custom_fields_reconstructed": False,
        "source_Unity_GUID_identity_proven": False,
        "original_Foam_runtime_Material_or_Shader_bound": False,
        "Android_water_pixels_verified": False,
        "private_original_class_names_or_assembly_strings_exported": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2", required=True, type=Path)
    p.add_argument("--scratch", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    phase = "input"
    def update(x):
        nonlocal phase
        phase = x
    try:
        output = args.out.absolute()
        safe(output)
        if output.exists() or not output.parent.is_dir() or any(
                output.is_relative_to(v.absolute()) for v in (args.zip2, args.scratch)):
            raise ValueError("unsafe_original_report_destination")
        r = inspect_original(args.zip2, args.scratch, update)
        if any(type(v) not in (int, bool, str) for v in r.values()):
            raise ValueError("original_safe_report_shape")
        output.write_text(json.dumps(r, sort_keys=True) + "\n", encoding="utf8")
        print("T2_ORIGINAL_MONO_MANAGED_CLASS_SAFE " + json.dumps(r, sort_keys=True))
        return 0
    except BaseException:
        print("T2_ORIGINAL_MONO_MANAGED_CLASS_SAFE " + json.dumps({
            "status": "blocked", "safe_phase": phase,
            "private_original_class_names_or_source_content_exported": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
