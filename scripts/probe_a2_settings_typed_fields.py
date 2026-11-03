"""ZIP2-pinned source-only Settings.cs serialization field-shape inventory.

Exact small original files from immutable ZIP2 are read as ordinary Git blobs.
Reports no original CSharp code, field names, binaries or asset content.
The candidate source-field order does NOT itself prove Unity byte offsets.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from scripts.probe_a2_scene_ui_layout import verified_scene, SCENE_BLOBS, git_blob_sha
from scripts.probe_a2_canvas_scaler_monoscript import ORIGINAL_SCRIPTS_BLOB, SCRIPT_SOURCE
from scripts.probe_a2_settings_owner_links import source_pin, SETTINGS_SHA
from scripts.probe_original_android_display_paths import mask_csharp_noncode

ZIP2_PIN = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
DLL_BLOB = "fc9d4ba920a178fdb89c970d9d772a01051dadc6"
MAX_SOURCE = 300000
FIELDS = re.compile(
    r"^\s*(?P<attrs>(?:\[[^\]]{1,300}\]\s*)*)"
    r"(?P<mods>(?:(?:public|private|protected|internal|static|readonly|const|new|volatile)\s+)+)"
    r"(?P<type>[A-Za-z_][\w.<>, \[\]?]*)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*(?:=\s*[^;]*)?;\s*$", re.DOTALL)
UNITY_TYPES = set("GameObject RectTransform Transform Canvas CanvasScaler Button Image RawImage ScrollRect Slider Toggle Text Dropdown InputField CanvasGroup Scrollbar RectMask2D Camera Material Sprite Texture Graphic".split())

def class_scope(source):
    if not isinstance(source, str) or not 1 <= len(source) <= MAX_SOURCE:
        raise ValueError("Missing or oversized original Settings class")
    code = mask_csharp_noncode(source)
    matches = list(re.finditer(r"\bclass\s+Settings\b", code))
    if len(matches) != 1:
        raise ValueError("Settings class missing or ambiguous")
    start = code.find("{", matches[0].end())
    if start < 0 or start - matches[0].end() > 400:
        raise ValueError("Settings declaration malformed")
    level = 1
    for i in range(start+1,len(code)):
        if code[i] == "{":
            level += 1
        elif code[i] == "}":
            level -= 1
            if level == 0:
                return code[start+1:i]
    raise ValueError("Settings class brace mismatch")

def top_level_members(scope):
    level, buffer = 0, []
    for ch in scope:
        if ch == "{":
            if level == 0:
                buffer = []
            level += 1
        elif ch == "}":
            if level <= 0:
                raise ValueError("Member brace mismatch")
            level -= 1
            if level == 0:
                buffer = []
        elif level == 0:
            buffer.append(ch)
            if ch == ";":
                yield "".join(buffer)
                buffer = []
    if level != 0:
        raise ValueError("Member brace mismatch")

def field_signature(source, original_script_names=None):
    kinds, skips = Counter(), Counter()
    accepted, total = [], 0
    source_type_classes = Counter()
    catalog = set(original_script_names or [])
    collection_element_categories = Counter()
    for stmt in top_level_members(class_scope(source)):
        total += 1
        if total > 768:
            raise ValueError("Unbounded member count")
        m = FIELDS.fullmatch(stmt)
        if not m:
            skips["unparsed_statement"] += 1
            continue
        modifiers = m.group("mods").split()
        attrs = m.group("attrs")
        if any(v in modifiers for v in ("static","const","readonly")):
            skips["static_const_readonly"] += 1
            continue
        if "NonSerialized" in attrs:
            skips["nonserialized"] += 1
            continue
        if "public" not in modifiers and "SerializeField" not in attrs:
            skips["private_without_serializefield"] += 1
            continue
        typ = m.group("type").replace(" ","")
        short = typ.split(".")[-1]
        if typ.endswith("[]") or typ.startswith("List<"):
            kind = "array_or_collection_unknown_element"
            element = typ[:-2] if typ.endswith("[]") else typ[5:-1]
            element_kind = ("original_assembly_monoscript_classname_match"
                            if element.split(".")[-1] in catalog else
                            "known_unity_native_type" if element.split(".")[-1] in UNITY_TYPES else
                            "other_unverified_element_type")
            collection_element_categories[element_kind] += 1
        elif short in UNITY_TYPES:
            kind = "known_unity_native_object_reference"
        elif short in ("bool","int","float","double","long","string","Vector2","Vector3","Color"):
            kind = "builtin_value_or_struct"
        else:
            kind = "custom_type_or_enum_unverified"
        kinds[kind] += 1
        if kind == "custom_type_or_enum_unverified":
            source_type_classes["original_assembly_monoscript_classname_match" if
                                short in catalog else "other_unverified"] += 1
        accepted.append(kind)
        if len(accepted) > 256:
            raise ValueError("Unbounded candidate field inventory")
    if not accepted:
        raise ValueError("No Settings serialized field candidates")
    return {
        "candidate_serializable_field_count": len(accepted),
        "candidate_type_categories": dict(sorted(kinds.items())),
        "candidate_categories_in_source_declaration_order": accepted,
        "custom_type_original_script_classname_match_count": dict(sorted(source_type_classes.items())),
        "collection_element_classification": dict(sorted(collection_element_categories.items())),
        "excluded_and_unparsed_counts": dict(sorted(skips.items())),
        "type_order_signature_sha256": hashlib.sha256("\n".join(accepted).encode()).hexdigest(),
        "typed_unity_serialization_order_verified": False,
        "source_names_or_bodies_emitted": False,
        "typed_original_pointer_offsets_recovered": False,
    }

def scan(source_root, ilspy_root):
    if source_root.is_symlink() or not source_root.is_dir():
        raise ValueError("Unsafe ZIP2 root")
    if ilspy_root.is_symlink() or not ilspy_root.is_dir():
        raise ValueError("Unsafe ILSpy root")
    for n in ("level0","level1"):
        verified_scene(source_root/n,SCENE_BLOBS[n])
    verified_scene(source_root/SCRIPT_SOURCE,ORIGINAL_SCRIPTS_BLOB)
    dll = source_root/"Managed"/"Assembly-CSharp.dll"
    if dll.is_symlink() or not dll.is_file() or dll.stat().st_size != 3211776:
        raise ValueError("Invalid original managed size")
    if git_blob_sha(dll.read_bytes()) != DLL_BLOB:
        raise ValueError("Original managed Git blob mismatch")
    source_pin(ilspy_root)
    paths = list(ilspy_root.rglob("Settings.cs"))
    if len(paths) != 1:
        raise ValueError("Settings private original source ambiguous")
    text = paths[0].read_text(encoding="utf-8-sig").replace("\r\n","\n")
    import UnityPy
    global_file = UnityPy.load(str(source_root/SCRIPT_SOURCE)).file
    script_names = set()
    for obj in global_file.objects.values():
        if str(obj.type.name) != "MonoScript":
            continue
        tree = obj.read_typetree(check_read=False)
        if not isinstance(tree,dict):
            continue
        if tree.get("m_AssemblyName") in ("Assembly-CSharp","Assembly-CSharp.dll"):
            name = tree.get("m_ClassName")
            if isinstance(name,str) and name:
                script_names.add(name)
    return {
        "zip2_source_pinned_commit": ZIP2_PIN,
        "original_small_files_sha_locked": 4,
        "original_settings_cs_sha256": SETTINGS_SHA,
        "field_shape": field_signature(text, script_names),
        "original_assembly_script_registry_available": bool(script_names),
        "original_script_name_catalog_emitted": False,
        "original_lfs_downloaded": False,
        "unity_or_android_executed": False,
        "android_settings_cause_proven": False,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--decompiled",type=Path,required=True)
    a=p.parse_args()
    print("RAFT_A2_ZIP2_SETTINGS_FIELD_SIGNATURE "+json.dumps(scan(a.source,a.decompiled),sort_keys=True))
if __name__=="__main__":
    main()
