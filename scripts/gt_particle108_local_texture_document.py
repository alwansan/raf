"""Private local Texture2D payload diagnostic; no standalone image inference.

A fresh bounded physical YAML snapshot must reproduce every Material TexEnv
document of the selected GUID from B05 before the local class28 body in
that SAME snapshot is decoded. Only ordinary RGBA32/BC3 top-mip storage and
inline native export are supported. Unpinned export streams stay unknown.
"""
from __future__ import annotations

from pathlib import Path
import re
from types import SimpleNamespace

from scripts import gt_particle108_source_pixel_parity as source
from scripts import gt_texture_route_payload as native
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_imported_bc3_route_pixels as bc3
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts.verify_export_lineage import identity
from scripts.b44_verify_material_colors import GUID,ENGINE

ZERO="0"*32
MAX_DOCUMENT=128*1024*1024
MAX_META=256*1024


class Unproven(ValueError):
    pass


def need(ok,code):
    if not ok:
        raise Unproven(code)


def strict_mapping(text):
    import yaml
    class Loader(yaml.SafeLoader):
        def compose_node(self,parent,index):
            event=self.peek_event()
            if isinstance(event,yaml.AliasEvent) or getattr(event,"anchor",None) is not None:
                raise Unproven("local_document_yaml_alias_or_anchor")
            return super().compose_node(parent,index)

        def construct_mapping(self,node,deep=False):
            result={}
            for k,v in node.value:
                key=self.construct_object(k,deep=deep)
                need(type(key) in (str,int) and key not in result,"local_document_duplicate_or_invalid_key")
                if key in ("_typelessdata","guid") and isinstance(v,yaml.ScalarNode):
                    need(v.tag in ("tag:yaml.org,2002:str","tag:yaml.org,2002:int"),
                         "local_document_invalid_lexical_scalar")
                    v.tag="tag:yaml.org,2002:str"
                result[key]=self.construct_object(v,deep=deep)
            return result
    try:
        value=yaml.load(text,Loader=Loader)
    except yaml.YAMLError:
        raise Unproven("local_document_malformed_yaml") from None
    need(type(value) is dict,"local_document_mapping_missing")
    return value


def local_body(project,key,materials):
    """Unique physical GUID, exact class28 anchor, all same-file Materials."""
    anchor,guid=key
    need(type(anchor) is int and anchor>0 and type(guid) is str
         and re.fullmatch("[0-9a-f]{32}",guid) and guid not in {ZERO,*ENGINE},
         "local_document_invalid_identity")
    assets=(Path(project)/"Assets").absolute()
    need(assets.is_dir() and not any(p.is_symlink() for p in (assets,*assets.parents)),
         "local_document_unsafe_assets")
    entries=list(assets.rglob("*"))
    need(len(entries)<=150000 and not any(p.is_symlink() for p in entries),"local_document_unsafe_inventory")
    candidate=None
    for meta in entries:
        if not meta.is_file() or meta.suffix!=".meta":
            continue
        try:
            text=source.bounded_snapshot(meta,MAX_META).decode("utf-8-sig")
        except (OSError,ValueError,UnicodeError):
            raise Unproven("local_document_meta_inventory_unproved") from None
        hits=GUID.findall(text)
        if guid not in {g.lower() for g in hits}:
            continue
        need(len(hits)==1,"local_document_ambiguous_meta_guid")
        need(candidate is None,"local_document_duplicate_meta_guid")
        data=strict_mapping(text)
        need(type(data.get("guid")) is str and data["guid"].lower()==guid,
             "local_document_meta_identity_mismatch")
        candidate=meta.with_suffix("")
    need(candidate is not None and candidate.is_file() and
         candidate.suffix in (".asset",".mat",".unity",".prefab"),
         "local_document_meta_identity_unproved")
    # Every parsed Material and texture body is from this exact byte read.
    text=source.bounded_snapshot(candidate,MAX_DOCUMENT).decode("utf-8-sig")
    broad=list(re.finditer(r"(?m)^---[^\r\n]*",text))
    pattern=re.compile(r"--- !u!(\d+) &(-?\d+)(?: (stripped))?[ \t]*\Z")
    seen=set();body=None;actual={}
    need(text.startswith("%YAML") and broad and not re.search(r"(?m)^\.\.\.[ \t]*$",text),
         "local_document_invalid_serialized_headers")
    for i,h in enumerate(broad):
        match=pattern.fullmatch(h.group())
        need(match is not None,"local_document_invalid_serialized_header")
        cls,fid=int(match[1]),int(match[2])
        need(fid and fid not in seen,"local_document_duplicate_or_zero_anchor")
        seen.add(fid)
        segment=text[h.end():broad[i+1].start() if i+1<len(broad) else len(text)]
        if fid==anchor:
            need(cls==28 and not match[3],"local_document_wrong_class_or_stripped")
            body=segment
        if cls==21:
            need(not match[3],"local_document_stripped_material")
            d=strict_mapping(segment)
            need(set(d)=={"Material"} and type(d["Material"]) is dict,"local_document_wrong_material_root")
            saved=d["Material"].get("m_SavedProperties")
            need(type(saved) is dict and "m_TexEnvs" in saved,"local_document_missing_material_texenv")
            actual[(fid,guid)]=normalize_texenvs(saved["m_TexEnvs"],exported=True)
    # The original->export join was made using B05's earlier material
    # snapshot. No changed pointer, UV, anchor or missing document can
    # survive this rejoin to the SAME bytes that contain the texture.
    expected={k:v for k,v in materials.items() if k[1]==guid}
    need(expected and actual==expected,"local_document_material_snapshot_drift")
    need(body is not None,"local_document_texture_anchor_missing")
    return body


def descriptor(tree):
    need(type(tree) is dict and type(tree.get("m_LightmapFormat")) is int and
         tree["m_LightmapFormat"]==0,"local_texture_unsupported_usage")
    blob=tree.get("m_PlatformBlob",[])
    need(type(blob) in (list,bytes,bytearray) and not blob,"local_texture_unsupported_platform_blob")
    fmt=tree.get("m_TextureFormat")
    need(type(fmt) is int and fmt in (4,12),"local_texture_unsupported_format")
    try:
        desc,sizes=(native.descriptor(tree) if fmt==4 else bc3.descriptor(tree))
    except (native.Unproven,png.Unproven):
        raise Unproven("local_texture_invalid_descriptor") from None
    need(4*desc[0]*desc[1]<=png.MAX_TOP,"local_texture_top_mip_budget")
    return desc,sizes


def decode_storage(desc,sizes,payload):
    need(type(payload) is bytes and len(payload)==desc[-1],"local_texture_payload_extent_mismatch")
    raw=payload[:sizes[0]]
    return (png.decode_top(desc[:2],raw) if desc[2]==4 else bc3.decode_top(desc[:2],raw))


def decode_export_body(body):
    doc=strict_mapping(body)
    need(set(doc)=={"Texture2D"} and type(doc["Texture2D"]) is dict,"local_document_wrong_texture_root")
    tree=doc["Texture2D"]
    desc,sizes=descriptor(tree)
    try:
        path,offset,size=native.stream_fields(tree,exported=True)
    except native.Unproven:
        raise Unproven("local_export_invalid_stream_descriptor") from None
    # No separately authenticated same-export resource manifest exists.
    need((path=="" or path is None) and type(offset) is int and offset==0 and
         type(size) is int and size==0,"local_export_stream_not_authenticated")
    count=tree.get("image data");encoded=tree.get("_typelessdata")
    need(type(count) is int and count==desc[-1],"local_export_payload_length_mismatch")
    need(type(encoded) is str and len(encoded)==2*count and re.fullmatch(r"[0-9a-fA-F]+",encoded),
         "local_export_payload_hex_mismatch")
    return decode_storage(desc,sizes,bytes.fromhex(encoded)),desc[2]


def decode_source(original,manifest,key):
    need(type(key) is tuple and len(key)==2 and key[0] in source.SHADER_OWNERS
         and type(key[1]) is int and key[1]>0,"local_source_identity_unproved")
    owner,pid=key
    pin=source.SHADER_OWNERS[owner]
    need(pin[0]<=source.MAX_OWNER,"local_source_owner_budget")
    root=Path(original)/"Raft_Data"
    raw=source.verified_range(root/owner,pin,0,pin[0])
    need(source.package_version("UnityPy")==source.DECODER_VERSION,"local_source_decoder_version")
    import UnityPy
    env=UnityPy.load(raw)
    matches=[o for o in env.file.objects.values() if o.path_id==pid]
    need(len(matches)==1 and matches[0].type.name=="Texture2D","local_source_not_unique_class28")
    tree=matches[0].read_typetree()
    desc,sizes=descriptor(tree)
    try:
        path,offset,size=native.stream_fields(tree)
    except native.Unproven:
        raise Unproven("local_source_invalid_stream_descriptor") from None
    inline=tree.get("image data")
    need(type(inline) in (bytes,bytearray,list) and
         (type(inline) is not list or all(type(v) is int and 0<=v<=255 for v in inline)),
         "local_source_invalid_inline_payload")
    adapter=SimpleNamespace(image_data=bytes(inline),
                            m_StreamData=SimpleNamespace(path=path,offset=offset,size=size))
    payload,kind=source.exact_payload(adapter,root,manifest)
    return decode_storage(desc,sizes,payload),kind,desc[2]


def alpha_profile(image):
    bins=image.getchannel("A").histogram()
    return {"has_explicit_alpha":True,"all_opaque":bins[255]==image.width*image.height,
            "has_transparent_pixels":sum(bins[:255])>0,
            "has_partially_transparent_pixels":sum(bins[1:255])>0,
            "fully_transparent_pixel_present":bins[0]>0}


def compare_local(original,manifest,project,trace,selected,routes,exportability,materials):
    """Aggregate-only report. No private paths, identities, hashes or pixels."""
    keys=[k for k,r in routes.items() if r["pointer"][2]==0]
    result={"status":"NO_LOCAL_TARGET" if not keys else "UNPROVEN",
            "local_targets":len(keys),"document_snapshot_verified":False,
            "source_top_mip_decoded":False,"serialized_export_top_mip_decoded":False,
            "source_payload_kind":None,"source_alpha_profile":None,
            "source_format":None,"serialized_export_format":None,
            "coordinate_compared_targets":0,"exact_alpha_targets":0,"exact_rgba8_targets":0,
            "targets_with_alpha_loss":0,"targets_with_all_transparency_lost":0,
            "comparison":None,"reason":None,"exported_image_proof":False,
            "lower_mip_parity_proven":False,"Unity_import_or_GPU_parity_proven":False,
            "private_identifiers_or_pixels_published":False}
    if not keys:
        return result
    try:
        need(len(keys)==1,"local_texture_population_unproved")
        key=keys[0];route=routes[key];ptr=route["pointer"]
        expected=selected.get(key);docs=route.get("document_guids",set())
        need(ptr[1:]==(ZERO,0) and type(ptr[0]) is int and ptr[0]>0
             and len(docs)==1 and type(route.get("slots")) is int and route["slots"]>0
             and expected is not None and expected[2] in (2,3)
             and exportability.get(key) is True and expected[:2]==(ptr[0],next(iter(docs))),
             "local_texture_document_route_unproved")
        claimants=[]
        for row in trace["objects"]:
            dst=row.get("export") if type(row) is dict else None
            if (type(dst) is dict and type(dst.get("guid")) is str and
                dst["guid"].lower()==expected[1] and dst.get("file_id")==expected[0]
                and dst.get("type") in (2,3)):
                claimants.append(row)
        need(len(claimants)==1 and type(claimants[0].get("class_id")) is int and
             claimants[0]["class_id"]==28 and identity(claimants[0]["source"])==key
             and claimants[0].get("exportable") is True,"local_texture_global_trace_collision")
        body=local_body(project,expected[:2],materials)
        result["document_snapshot_verified"]=True
        exported,fmt=decode_export_body(body)
        result.update(serialized_export_top_mip_decoded=True,serialized_export_format=fmt)
        before,kind,fmt=decode_source(original,manifest,key)
        result.update(source_top_mip_decoded=True,source_payload_kind=kind,
                      source_alpha_profile=alpha_profile(before),source_format=fmt)
        row=source.compare_pixels(before,exported)
        result.update(status=("EXACT_RGBA8" if row["rgba8_samples_equal"] else
                              "PIXEL_DRIFT" if row["dimensions_match"] else "DIMENSION_MISMATCH"),
                      coordinate_compared_targets=int(row["dimensions_match"]),
                      exact_alpha_targets=int(row["alpha_samples_equal"]),
                      exact_rgba8_targets=int(row["rgba8_samples_equal"]),
                      targets_with_alpha_loss=int(row["net_nonopaque_population_decreased"]),
                      targets_with_all_transparency_lost=int(row["all_source_transparency_lost"]),
                      comparison=row)
    except Unproven as exc:
        result["reason"]=str(exc)
    except (OSError,ValueError,TypeError,AttributeError,KeyError,ImportError,NotImplementedError,RuntimeError,OverflowError) as exc:
        known={"pinned_pixel_provider_SHA_mismatch","pinned_pixel_provider_size_mismatch",
               "invalid_pinned_pixel_byte_range","pixel_manifest_git_blob_mismatch",
               "texture_stream_provider_not_pinned","ambiguous_inline_stream_texture",
               "unsupported_texture_stream_path","pixel_input_symlink","pixel_input_not_single_regular_file"}
        result["reason"]=str(exc) if str(exc) in known else "local_texture_unavailable_"+type(exc).__name__
    return result
