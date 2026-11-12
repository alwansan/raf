#!/usr/bin/env python3
"""B46: fail-closed exported Material->Texture references; no device claims."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import struct

HEADER=re.compile(r"(?m)^---[ \t]+!u!(\d+)[ \t]+&(-?\d+)(?:[ \t]+stripped)?[ \t]*$")
GUID=re.compile(r"(?m)^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*$")
TEXENV=re.compile(r"(?m)^    m_TexEnvs:[ \t]*(\[\]|\{\})?[ \t]*$")
SLOT=re.compile(r"(?m)^    - [^:\r\n]+:[ \t]*$")
SLOT_MAPPING=re.compile(r"(?m)^      [^:\r\n{}]+:[ \t]*$")
TEX=re.compile(r"(?m)^        m_Texture:[ \t]*(\{[^\r\n{}]*\})[ \t]*$")
NEXT=re.compile(r"(?m)^    m_[A-Za-z][A-Za-z0-9_]*:")
IMAGES={".png",".jpg",".jpeg",".tga",".psd",".tif",".tiff",".bmp",".exr",".hdr",".dds",".ktx",".pvr",".webp"}
CLASSES={28,84,86,89,117,187,188,205}
BUILTIN={"0000000000000000e000000000000000","0000000000000000f000000000000000"}
ZERO="0"*32

class GuardError(ValueError):
    pass

def fail(code):
    raise GuardError(code)

def read(path):
    if not path.is_file() or path.is_symlink(): fail("unsafe_or_missing_asset")
    if path.stat().st_size>4*1024*1024: fail("oversized_asset")
    try: return path.read_text(encoding="utf-8-sig")
    except UnicodeError: fail("invalid_utf8")

def pointer(raw):
    if not raw.startswith("{") or not raw.endswith("}"): fail("bad_texture_pointer")
    fields={}
    for p in raw[1:-1].split(","):
        pair=p.strip().split(":",1)
        if len(pair)!=2 or pair[0].strip() in fields: fail("bad_texture_pointer")
        fields[pair[0].strip()]=pair[1].strip()
    if set(fields) not in ({"fileID"},{"fileID","guid","type"}): fail("bad_texture_pointer")
    if not re.fullmatch(r"-?\d+",fields["fileID"]): fail("bad_texture_pointer")
    fid=int(fields["fileID"])
    if fid<=-(2**63) or fid>=2**63: fail("bad_texture_pointer")
    if "guid" not in fields: return fid,None,None
    if not re.fullmatch("[a-fA-F0-9]{32}",fields["guid"]) or not re.fullmatch(r"\d+",fields["type"]):
        fail("bad_texture_pointer")
    kind=int(fields["type"])
    if kind>3: fail("bad_texture_pointer")
    return fid,fields["guid"].lower(),kind

def material_docs(source):
    heads=list(HEADER.finditer(source))
    if not heads: fail("missing_yaml_headers")
    result=[]; local={}
    for i,h in enumerate(heads):
        cls,fid=int(h[1]),int(h[2])
        if fid==0 or fid in local: fail("duplicate_or_zero_object_id")
        local[fid]=cls
        if cls==21: result.append(source[h.end():heads[i+1].start() if i+1<len(heads) else len(source)])
    if not result: fail("missing_material_records")
    return result,local

def texenv(doc):
    if len(re.findall(r"(?m)^  m_SavedProperties:[ \t]*$",doc))!=1: fail("invalid_saved_properties")
    matches=list(TEXENV.finditer(doc))
    if len(matches)!=1: fail("missing_or_duplicate_texenv")
    m=matches[0]
    next_field=NEXT.search(doc,m.end())
    region=doc[m.end():next_field.start() if next_field else len(doc)]
    # An explicit empty array cannot have nested slot data; accepting such
    # malformed YAML silently hides broken material-to-texture references.
    if m[1] in ("[]", "{}"):
        if region.strip(): fail("unexpected_texenv_content")
        return []
    sequence_slots=list(SLOT.finditer(region))
    mapping_slots=list(SLOT_MAPPING.finditer(region))
    # AssetRipper may preserve native Unity m_TexEnvs as a YAML mapping
    # rather than Unity's sequence-of-single-key-maps. Both are genuine;
    # reject mixed or malformed layouts instead of assuming absent textures.
    if sequence_slots and mapping_slots: fail("mixed_texenv_slot_encodings")
    slots=sequence_slots if sequence_slots else mapping_slots
    if not slots: fail("empty_or_unrecognized_texenv")
    if region[:slots[0].start()].strip(): fail("unrecognized_texenv_prefix")
    result=[]
    for i,slot in enumerate(slots):
        end=slots[i+1].start() if i+1<len(slots) else len(region)
        refs=TEX.findall(region[slot.end():end])
        if len(refs)!=1: fail("missing_or_duplicate_texture_pointer")
        result.append(pointer(refs[0]))
    if len(TEX.findall(region))!=len(result): fail("orphan_texture_pointer")
    return result

def is_texture(path,meta,fid):
    # Real Unity importer subobjects have distinct native fileIDs.
    # Original Texture2DArray (ClassID 187) can be an imported PNG flipbook,
    # not only a serialized .asset. Never convert it to Texture2D/2800000.
    if path.suffix.lower() in IMAGES:
        if not re.search(r"(?m)^TextureImporter:[ \t]*$",meta):
            return False
        if fid==2800000:
            # An imported array is never a plain Texture2D sub-object.
            # Missing textureShape remains valid for legacy flat-2D
            # AssetRipper imports, but an explicitly array-shaped importer
            # must not accept a falsified fileID=2800000 reference.
            shapes=re.findall(r"(?m)^[ \t]*textureShape:[ \t]*(\d+)[ \t]*$",meta)
            return len(shapes)<=1 and (not shapes or int(shapes[0]) in (0,1))
        if fid==18700000 and path.suffix.lower()==".png":
            # The *separate* GT source-authoritative gate verifies the real
            # original 9 class187 identities, 28 Material refs and exact
            # per-array source depth. This generic B46 target guard can
            # independently establish that Unity's actual imported PNG
            # settings describe a complete positive flipbook grid.
            values={}
            for name in ("textureShape","flipbookRows","flipbookColumns"):
                hits=re.findall(r"(?m)^[ \t]*"+name+r":[ \t]*(\d+)[ \t]*$",meta)
                if len(hits)!=1:return False
                values[name]=int(hits[0])
            if values["textureShape"]!=4:
                return False
            rows,cols=values["flipbookRows"],values["flipbookColumns"]
            if rows<1 or cols<1 or rows*cols>2048:
                return False
            try:
                with path.open("rb") as stream:
                    head=stream.read(24)
                if (len(head)!=24 or head[:8]!=b"\x89PNG\r\n\x1a\n"
                    or head[12:16]!=b"IHDR" or
                    int.from_bytes(head[8:12],"big")!=13):
                    return False
                width,height=struct.unpack(">II",head[16:24])
            except OSError:
                return False
            return (0<width<=16384 and 0<height<=16384
                    and width%cols==0 and height%rows==0
                    and width//cols>0 and height//rows>0)
        return False
    if path.suffix.lower() in {".asset",".cubemap",".rendertexture"}:
        return any(int(h[2])==fid and int(h[1]) in CLASSES
                   for h in HEADER.finditer(read(path)))
    return False

def audit(project,expected_materials=None):
    root=Path(os.path.abspath(project))
    if any(p.is_symlink() for p in (root,*root.parents)): fail("symlinked_project_root")
    assets=root/"Assets"
    if not assets.is_dir() or assets.is_symlink(): fail("missing_assets_root")
    entries=list(assets.rglob("*"))
    if len(entries)>250000 or any(p.is_symlink() for p in entries): fail("unsafe_or_excessive_export")
    files={p for p in entries if p.is_file()}
    targets={}
    for meta in files:
        if not meta.name.endswith(".meta"): continue
        data=read(meta); hits=GUID.findall(data)
        if len(hits)!=1: fail("missing_or_duplicate_meta_guid")
        guid=hits[0].lower(); target=meta.with_name(meta.name[:-5])
        if guid in targets or guid in BUILTIN or guid==ZERO: fail("duplicate_or_reserved_meta_guid")
        if target not in files: fail("orphan_asset_meta")
        targets[guid]=(target,data)
    mats=sorted(p for p in files if p.suffix.lower()==".mat")
    if not mats: fail("missing_exported_materials")
    counts=Counter(); verified={}
    for mat in mats:
        if mat.with_name(mat.name+".meta") not in files: fail("missing_material_meta")
        docs,local=material_docs(read(mat))
        for d in docs:
            counts["materials"]+=1
            for fid,guid,kind in texenv(d):
                counts["slots"]+=1
                if fid==0:
                    if guid is not None and (guid!=ZERO or kind!=0): fail("invalid_null_texture_pointer")
                    counts["null"]+=1
                elif fid<0: fail("negative_texture_file_id")
                elif guid is None or guid==ZERO:
                    if kind not in (None,0) or local.get(fid) not in CLASSES: fail("unresolved_local_texture")
                    counts["embedded"]+=1
                elif guid in BUILTIN:
                    if kind!=0: fail("invalid_builtin_texture_type")
                    counts["builtin"]+=1
                else:
                    if kind not in (2,3): fail("invalid_external_texture_type")
                    if guid not in targets: fail("missing_texture_guid")
                    key=(guid,fid)
                    if key not in verified: verified[key]=is_texture(*targets[guid],fid)
                    if not verified[key]: fail("reference_target_not_verified_texture")
                    counts["resolved"]+=1
    if expected_materials is not None and (expected_materials<=0 or expected_materials!=counts["materials"]):
        fail("expected_material_count_mismatch")
    return {"material_files":len(mats),"material_objects":counts["materials"],
            "texture_slots":counts["slots"],"null_slots":counts["null"],
            "resolved_local_texture_refs":counts["resolved"],
            "local_embedded_texture_refs":counts["embedded"],
            "builtin_unverified_refs":counts["builtin"],
            "export_texture_guid_target_integrity_verified":True,
            "source_export_equivalence_verified":False,"texture_pixel_color_verified":False,
            "device_render_verified":False,"ready_for_build":False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--expected-materials",type=int)
    args=p.parse_args(argv)
    try:
        print("RAFT_B46_TEXTURE_LINKS "+json.dumps({"status":"PASS",**audit(args.project,args.expected_materials)},sort_keys=True))
        return 0
    except (GuardError,OSError) as exc:
        reason=str(exc) if isinstance(exc,GuardError) else "unreadable_export"
        print("RAFT_B46_TEXTURE_LINKS "+json.dumps({"status":"REJECTED","error_code":reason,"ready_for_build":False},sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
