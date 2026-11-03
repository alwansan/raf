"""Original ZIP2 Settings metadata FieldDef/MonoScript identity contract (CPU only).

Private managed field/class names never leave runner. Exact managed FieldDef
tokens are NOT Unity serialized field offsets; no runtime geometry is inferred.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from scripts.probe_a2_scene_ui_layout import verified_scene, SCENE_BLOBS, git_blob_sha
from scripts.probe_a2_canvas_scaler_monoscript import SCRIPT_SOURCE, ORIGINAL_SCRIPTS_BLOB, script_registry, resolve_script
from scripts.probe_a2_settings_owner_links import source_pin, SETTINGS_CATEGORY
from scripts.probe_a2_settings_typed_fields import DLL_BLOB, ZIP2_PIN, FIELDS, class_scope, top_level_members

MAX_FIELDS = 256
MAX_META_BYTES = 524288

def candidate_source_names(source):
    found=[]
    for statement in top_level_members(class_scope(source)):
        f=FIELDS.fullmatch(statement)
        if f is None:
            continue
        mods=f.group("mods").split()
        attrs=f.group("attrs")
        if any(x in mods for x in ("static","const","readonly")) or "NonSerialized" in attrs:
            continue
        if "public" in mods or "SerializeField" in attrs:
            found.append(f.group("name"))
    if not 1<=len(found)<=MAX_FIELDS or len(found)!=len(set(found)):
        raise ValueError("Original source candidate fields ambiguous")
    return found

def verify_fielddefs(data, assembly, namespace, source_names):
    if not isinstance(data,dict) or data.get("format_version")!=1:
        raise ValueError("Unsafe private metadata format")
    if data.get("assembly_name")!=assembly:
        raise ValueError("Original managed assembly identity drift")
    types=data.get("candidate_types")
    if not isinstance(types,list) or not 1<=len(types)<=16:
        raise ValueError("Original Settings metadata type inventory unsafe")
    # Unity MonoScript m_Namespace is a namespace, not a nested declaring
    # type. Mono.Cecil may expose numerous nested classes named Settings
    # with an empty Namespace; only the exact top-level full-name matches.
    full = (namespace + "." if namespace else "") + "Settings"
    matches=[t for t in types if isinstance(t,dict) and
             t.get("name")=="Settings" and t.get("namespace_name")==namespace
             and t.get("full_name")==full]
    if len(matches)!=1:
        # No source type or namespace is printed. Different assemblies may
        # contain a Settings MonoScript with a matching class-name only.
        details = {
            "matching_typedef_count": len(matches),
            "settings_typedef_candidates": len(types),
            "scene_namespace_is_empty": namespace == "",
            "candidate_empty_namespace_count": sum(
                t.get("namespace_name") == "" for t in types if isinstance(t,dict)),
            "matching_casefold_count": sum(
                isinstance(t,dict) and isinstance(t.get("namespace_name"),str)
                and t["namespace_name"].casefold() == namespace.casefold()
                for t in types),
        }
        raise ValueError("Original scene script to TypeDef identity ambiguous "
                         + json.dumps(details,sort_keys=True))
    item=matches[0]
    if type(item.get("token")) is not int or item["token"]>>24 != 2:
        raise ValueError("Original TypeDef token invalid")
    fields=item.get("fields")
    if not isinstance(fields,list) or len(fields)>MAX_FIELDS:
        raise ValueError("Original metadata FieldDef count unsafe")
    previous,seen,eligible=0,set(),[]
    for f in fields:
        if not isinstance(f,dict):
            raise ValueError("Malformed original FieldDef")
        name,token=f.get("name"),f.get("token")
        if not isinstance(name,str) or not name or name in seen:
            raise ValueError("Original FieldDef names ambiguous")
        if type(token) is not int or token>>24 != 4 or token<=previous:
            raise ValueError("Original FieldDef tokens not ordered")
        seen.add(name);previous=token
        if (f.get("is_static") or f.get("is_const") or f.get("is_readonly") or
                f.get("is_not_serialized") or f.get("has_nonserialized_attribute")):
            continue
        if not (f.get("is_public") or f.get("has_serialize_field") or
                f.get("has_serialize_reference")):
            continue
        kind,element=f.get("kind"),f.get("element_kind")
        if not isinstance(kind,str):
            raise ValueError("Original field kind missing")
        eligible.append((name,kind,element,token))
    ordered=[x[0] for x in eligible]
    if len(source_names)!=len(set(source_names)):
        raise ValueError("Duplicate original Settings candidate source fields")
    # CSharp9 text is a lexical candidate list; metadata is authoritative
    # on field identities but NOT on Unity's full serializer rules. Classify
    # mismatches without printing any original private field/type names.
    source_set=set(source_names)
    eligible_set=set(ordered)
    all_definitions={f["name"]:f for f in fields}
    missing_counts=Counter()
    for name in source_set-eligible_set:
        item=all_definitions.get(name)
        if item is None:
            missing_counts["source_only_no_matching_fielddef"]+=1
        elif item.get("is_static") or item.get("is_const") or item.get("is_readonly"):
            missing_counts["source_candidate_static_or_readonly_in_metadata"]+=1
        elif item.get("is_not_serialized") or item.get("has_nonserialized_attribute"):
            missing_counts["source_candidate_not_serialized_in_metadata"]+=1
        elif not (item.get("is_public") or item.get("has_serialize_field")
                  or item.get("has_serialize_reference")):
            missing_counts["source_candidate_not_marked_for_serialization"]+=1
        else:
            missing_counts["metadata_filter_unknown"]+=1
    intersection=set(source_names)&eligible_set
    common_source=[name for name in source_names if name in intersection]
    common_meta=[name for name in ordered if name in intersection]
    family=Counter(x[1] for x in eligible)
    nested=Counter(x[2] or "unknown" for x in eligible if x[1] in
                   ("array","list_generic","generic_other"))
    fingerprint=hashlib.sha256("\n".join(
        f"{token}:{kind}:{element or '-'}" for _,kind,element,token in eligible).encode()).hexdigest()
    return {
        "original_scene_typedef_identity_matched":True,
        "original_total_fielddefs":len(fields),
        "original_candidate_eligible_fielddefs":len(eligible),
        "eligible_field_families":dict(sorted(family.items())),
        "collection_element_families":dict(sorted(nested.items())),
        "source_field_count":len(source_names),
        "source_field_name_set_equals_metadata":set(source_names)==set(ordered),
        "source_declaration_order_equals_metadata_order":list(source_names)==ordered,
        "shared_source_to_metadata_order_equal":common_source==common_meta,
        "source_only_exclusion_reason_counts":dict(sorted(missing_counts.items())),
        "source_candidates_absent_from_eligible_metadata":len(source_set-eligible_set),
        "metadata_eligible_fields_absent_from_source_candidates":len(eligible_set-source_set),
        "fielddef_token_order_validated":True,
        "metadata_kind_sequence_sha256":fingerprint,
        "source_type_and_field_names_emitted":False,
        "unity_custom_typetree_available":False,
        "original_unity_serialized_field_offsets_proven":False,
    }


def enforce_pinned_original_contract(result):
    """Strong original-only invariant, not assumed for unrelated synthetic samples."""
    expected = (result.get("original_total_fielddefs") == 21
                and result.get("original_candidate_eligible_fielddefs") == 13
                and result.get("source_field_count") == 14
                and result.get("source_candidates_absent_from_eligible_metadata") == 1
                and result.get("metadata_eligible_fields_absent_from_source_candidates") == 0
                and result.get("shared_source_to_metadata_order_equal") is True
                and result.get("source_only_exclusion_reason_counts") ==
                    {"source_only_no_matching_fielddef": 1})
    if not expected:
        raise ValueError("Pinned original Settings source versus FieldDef contract drift")
    return True


def scene_settings_identity(root, loader=None):
    if loader is None:
        import UnityPy
        loader=lambda p:UnityPy.load(str(p))
    glob=loader(root/SCRIPT_SOURCE).file
    scripts={int(o.path_id):o.read_typetree(check_read=False)
             for o in glob.objects.values() if str(o.type.name)=="MonoScript"}
    categories,_=script_registry(glob.objects.values())
    found=[]
    for scene in ("level0","level1"):
        owner=loader(root/scene).file
        externals=[x.path for x in owner.externals]
        local,_=script_registry(owner.objects.values())
        instances=[]
        for o in owner.objects.values():
            if str(o.type.name)!="MonoBehaviour":
                continue
            base=o.read_typetree(check_read=False)
            if resolve_script(base.get("m_Script"),externals,local,categories)!=SETTINGS_CATEGORY:
                continue
            pointer=base.get("m_Script",{})
            fid,pid=pointer.get("m_FileID"),pointer.get("m_PathID")
            if (type(fid) is not int or type(pid) is not int or
                not 1<=fid<=len(externals) or
                externals[fid-1].replace("\\","/").rsplit("/",1)[-1]!=SCRIPT_SOURCE):
                raise ValueError("Original Settings script owner not authenticated")
            script=scripts.get(pid)
            if not isinstance(script,dict) or script.get("m_ClassName")!="Settings" or (
                script.get("m_AssemblyName") not in ("Assembly-CSharp","Assembly-CSharp.dll")):
                raise ValueError("Original Settings MonoScript identity drift")
            ns=script.get("m_Namespace")
            if not isinstance(ns,str):
                raise ValueError("Unknown original Settings namespace")
            raw=o.get_raw_data()
            if len(raw)!=612:
                raise ValueError("Original Settings serialized record length drift")
            for off,key in ((0,"m_GameObject"),(16,"m_Script")):
                expected=base.get(key)
                if not isinstance(expected,dict) or struct.unpack_from("<iq",raw,off)!=(
                    expected.get("m_FileID"),expected.get("m_PathID")):
                    raise ValueError("Original Settings base pointer fields mismatch")
            instances.append((ns,pid))
        if len(instances)!=1:
            raise ValueError("Original Settings scene ownership ambiguous")
        found.append(instances[0])
    if found[0]!=found[1]:
        raise ValueError("Original Settings MonoScript type differs between scenes")
    return {"namespace":found[0][0], "assembly":"Assembly-CSharp",
            "verified_script_linked_scene_owners":2}

def audit(root,meta_path,private_sources,loader=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe original source directory")
    for scene in ("level0","level1"):
        verified_scene(root/scene,SCENE_BLOBS[scene])
    verified_scene(root/SCRIPT_SOURCE,ORIGINAL_SCRIPTS_BLOB)
    dll=root/"Managed"/"Assembly-CSharp.dll"
    if dll.is_symlink() or not dll.is_file() or dll.stat().st_size!=3211776:
        raise ValueError("Original managed DLL missing or unsafe")
    if git_blob_sha(dll.read_bytes())!=DLL_BLOB:
        raise ValueError("Original ZIP2 managed source Git blob mismatch")
    if meta_path.is_symlink() or not meta_path.is_file() or meta_path.stat().st_size>MAX_META_BYTES:
        raise ValueError("Private Cecil metadata unsafe")
    private=json.loads(meta_path.read_text(encoding="utf-8"))
    source_pin(private_sources)
    src=list(private_sources.rglob("Settings.cs"))
    if len(src)!=1:
        raise ValueError("Private original Settings source ambiguous")
    names=candidate_source_names(src[0].read_text(encoding="utf-8-sig").replace("\r\n","\n"))
    identity=scene_settings_identity(root,loader=loader)
    fields=verify_fielddefs(private,identity["assembly"],identity["namespace"],names)
    enforce_pinned_original_contract(fields)
    return {
        "original_source_zip2_commit":ZIP2_PIN,
        "original_input_git_sha_pins_matched":4,
        "original_settings_monoscript_scene_owners":identity["verified_script_linked_scene_owners"],
        "pinned_settings_managed_and_source_field_contract_verified":True,
        "metadata":fields,
        "private_original_code_or_field_names_emitted":False,
        "lfs_downloaded":False,
        "unity_or_android_executed":False,
        "active_settings_ui_canvas_path_proven":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--metadata",required=True,type=Path)
    p.add_argument("--decompiled",required=True,type=Path)
    a=p.parse_args()
    print("RAFT_A2_ZIP2_ORIGINAL_SETTINGS_METADATA "+json.dumps(
        audit(a.source,a.metadata,a.decompiled),sort_keys=True))

if __name__=="__main__":
    main()
