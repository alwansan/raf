"""T2: prepare strictly private SHA-256 Foam Shader texture-string target ledger.

Only SHA-verified original Shader stage sources are used. The plain source
names and stage-specific register-to-name mapping stay in CI process memory;
the hashes are runner-temp only and NEVER uploaded. Managed Cecil probe
consumes SHA-256 hex strings to count genuine ldstr matching original names.
A literal match is not proof of a Unity property upload.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.t2_foam_member_abi import original_source_tree, _physical
from scripts.t2_foam_material_property_bridge import original_stage_shader_property_join
from scripts.t2_foam_resource_abi import ORIGINAL_TEXTURES_PER_STAGE
from scripts.t2_foam_member_abi import STAGES

SHA_LEN=64


def sha(text):
    if not isinstance(text,str) or not 0<len(text)<=256 or "\x00" in text:
        raise ValueError("Private original shader identifier invalid")
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def prepare_private_hashes(profile):
    if not isinstance(profile,dict):
        raise ValueError("Private shader source profile absent")
    authored=profile.get("_private_authored_textures")
    rows=profile.get("_private_stage_rows")
    if not isinstance(authored,set) or not isinstance(rows,list) or len(rows)!=4:
        raise ValueError("Original Shader stage/profile missing")
    if profile.get("original_texture_name_to_shader_texture_property_matches")!=2:
        raise ValueError("Original authored Foam Texture property name evidence changed")
    if profile.get("original_source_texture_rows")!=6 or len(authored)!=1:
        raise ValueError("Original Foam source texture/property counts changed")
    seen=set()
    names_pass0=[]
    names_pass1=[]
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("Foam stage source row malformed")
        key=row.get("pass"),row.get("stage_code")
        if key in seen or key not in STAGES:
            raise ValueError("Original Foam stage identity ambiguous")
        seen.add(key)
        names=row.get("_source_names")
        if (not isinstance(names,list) or
                len(names)!=ORIGINAL_TEXTURES_PER_STAGE[key] or
                len(set(names))!=len(names)):
            raise ValueError("Original Foam stage texture property list drift")
        if key==(0,0):
            names_pass0=names
        elif key==(1,0):
            names_pass1=names
        elif names:
            raise ValueError("Original Foam vertex has unsupported texture name")
    if seen!=set(STAGES):
        raise ValueError("Original Foam stage coverage incomplete")
    authored_used=set(names_pass0)&authored
    if len(authored_used)!=1 or set(names_pass1)!=authored_used:
        raise ValueError("Original Foam authored property is not same two-pass Texture source")
    non_authored=set(names_pass0)-authored
    if len(non_authored)!=4:
        raise ValueError("Original Foam non-property Texture resource count changed")
    private_names=set(non_authored)|authored_used
    if len(private_names)!=5:
        raise ValueError("Original Foam private texture name collision")
    targets={
        "schema_version":1,
        "source_kind":"SHA_AUTHENTIC_ORIGINAL_FOAM_SHADER_TEXTURE_NAMES",
        "non_authored_sha256":sorted(sha(n) for n in non_authored),
        "authored_texture_sha256":sorted(sha(n) for n in authored_used),
        "original_source_texture_occurrences":6,
        "original_distinct_source_texture_names":5,
        "native_to_spirv_six_active_descriptor_pairs_proven_prior":True,
        "runtime_upload_proven":False,
    }
    if len(set(targets["non_authored_sha256"]))!=4 or (
            set(targets["non_authored_sha256"])&set(targets["authored_texture_sha256"])):
        raise ValueError("Original private texture hash collision")
    return targets


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    try:
        source=args.source.absolute()
        out=args.out.absolute()
        if out.exists() or not out.parent.is_dir() or not _physical(out) or (
                out.is_relative_to(source)):
            raise ValueError("Unsafe original managed texture literal target path")
        profile=original_stage_shader_property_join(original_source_tree(source))
        result=prepare_private_hashes(profile)
        out.write_text(json.dumps(result,sort_keys=True)+"\n",encoding="utf8")
        print("T2_FOAM_MANAGED_TARGETS "+json.dumps({
            "status":"source_authentic_hashes_staged_in_private_runner_temp",
            "original_non_authored_texture_names":4,
            "original_authored_texture_names":1,
            "exact_managed_bindings_verified":False,
            "private_names_or_hashes_published":False,
        }))
        return 0
    except BaseException as exc:
        print("T2_FOAM_MANAGED_TARGETS "+json.dumps({
            "status":"blocked","error_type":type(exc).__name__,
            "private_names_or_hashes_published":False,
        }))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
