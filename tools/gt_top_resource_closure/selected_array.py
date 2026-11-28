"""Exact selected inline BC3 array: source cells and reversible grid-only repair.

Pinned AssetRipper TextureConverter uses layer-major complete mip extents,
FlipY per layer, and DirectBitmap.SaveAsPng stacks layers vertically.
No Unity import or lower-mip pixel acceptance is inferred from PNG parity.
"""
import hashlib
import os
from pathlib import Path
import re
from types import SimpleNamespace
from PIL import ImageOps
from scripts import gt_bc3_array_layout as bc3
from scripts import gt_compare_original_bc3_to_flipbook_pixels as layout
from scripts import gt_particle108_source_pixel_parity as pixels
from tools.gt_top_resource_closure import texture_observation as obs

class SelectedArrayError(ValueError):
    pass

def need(ok,code):
    if not ok:
        raise SelectedArrayError(code)

def exact_inline(tree):
    source=obs.array_source(tree)
    w,h,d,n=(source[k] for k in ("width","height","depth","mipcount"))
    need((w,h,d,n,source["format_enum"])==(1024,1024,2,11,100),
         "selected_array_source_shape_format_drift")
    stream=tree.get("m_StreamData")
    need(isinstance(stream,dict) and stream.get("size")==0 and stream.get("offset")==0
         and stream.get("path") in ("",None),"selected_array_not_exact_inline")
    raw=tree.get("m_ImageData",tree.get("image data"))
    expected=bc3.array_payload_bytes(w,h,d,n,100)
    need(isinstance(raw,(list,tuple,bytes,bytearray)) and len(raw)==expected
         and source["inline_data_bytes"]==expected,"selected_array_inline_extent_mismatch")
    raw=bytes(raw)
    if "m_ImageData" in tree and "image data" in tree:
        need(bytes(tree["m_ImageData"])==bytes(tree["image data"]),"ambiguous_array_inline_payload")
    return source,raw

def compare_layers(raw,atlas,w,h,d,n,*,decode=None):
    # A caller cannot select the orientation giving the lowest error.
    # The pinned converter flips rows within each layer and writes a
    # vertical stack; the independent Pillow comparison is supplemental.
    need(atlas.size==(w,h*d),"selected_array_vertical_stack_extent")
    expected=bc3.array_payload_bytes(w,h,d,n,100)
    need(len(raw)==expected,"selected_array_BC3_extent_mismatch")
    if decode is None:
        decode=lambda data,w,h: ImageOps.flip(layout.dds_bc3(data,w,h))
    ranges=[]
    for layer in range(d):
        for mip in range(n):
            start,size=layout.mip_range(w,h,d,n,layer,mip,"slice_major")
            ranges.append((start,size))
    cursor=0
    for start,size in ranges:
        need(start==cursor and size>0,"selected_array_mip_extent_gap")
        cursor+=size
    need(cursor==len(raw),"selected_array_mip_extent_incomplete")
    source=[]
    target=[]
    independent=[]
    for layer in range(d):
        start,size=layout.mip_range(w,h,d,n,layer,0,"slice_major")
        tile=raw[start:start+size]
        source.append(decode(tile,w,h).convert("RGBA"))
        target.append(atlas.crop((0,layer*h,w,(layer+1)*h)).convert("RGBA"))
        independent.append(ImageOps.flip(layout.dds_bc3(tile,w,h)))
    rows=[pixels.compare_pixels(a,b) for a,b in zip(source,target,strict=True)]
    matched=sum(r["rgba8_samples_equal"] for r in rows)
    wrong_order=sum(pixels.compare_pixels(source[i],target[d-1-i])["rgba8_samples_equal"] for i in range(d))
    wrong_orientation=sum(pixels.compare_pixels(ImageOps.flip(source[i]),target[i])["rgba8_samples_equal"] for i in range(d))
    independent_matches=sum(pixels.compare_pixels(a,b)["rgba8_samples_equal"] for a,b in zip(independent,target,strict=True))
    return {"layers":d,"top_mip_layers_exact":matched,
            "top_mip_pixel_coordinates_compared":sum(r["pixel_coordinates_compared"] for r in rows),
            "top_mip_rgb_mismatches":sum(r["rgb_mismatch_pixels"] for r in rows),
            "top_mip_alpha_mismatches":sum(r["alpha_mismatch_pixels"] for r in rows),
            "pillow_independent_top_mip_layers_exact":independent_matches,
            "reversed_layer_order_exact":wrong_order,
            "wrong_vertical_orientation_exact":wrong_orientation,
            "layer_order_distinguished":matched==d and wrong_order<d,
            "orientation_distinguished":matched==d and wrong_orientation<d,
            "all_mip_byte_extents_verified":len(ranges),"inline_payload_bytes":len(raw),
            "all_top_mip_layers_exact":matched==d,
            "full_lower_mip_pixel_equivalence":False}

def repair_bytes(raw,guid,rows,columns):
    need(type(raw) is bytes and 0<len(raw)<=4*1024*1024,"invalid_selected_array_meta_extent")
    need(re.fullmatch(r"[0-9a-f]{32}",guid) is not None,"invalid_selected_array_GUID")
    need(re.findall(rb"(?m)^guid: ([0-9a-f]{32})\r?$",raw)==[guid.encode()],
         "selected_array_meta_GUID_mismatch")
    need(len(re.findall(rb"(?m)^TextureImporter:[ \t]*\r?$",raw))==1
         and len(re.findall(rb"(?m)^[ \t]+textureShape:[ \t]*4[ \t]*\r?$",raw))==1,
         "selected_array_importer_shape_mismatch")
    need((rows,columns)==(2,1),"unexpected_selected_array_grid")
    result=raw
    for name,value in ((b"flipbookRows",b"2"),(b"flipbookColumns",b"1")):
        hits=list(re.finditer(rb"(?m)^[ \t]+"+name+rb":[ \t]*(\d+)[ \t]*\r?$",result))
        need(len(hits)==1 and hits[0].group(1)==b"0","selected_array_grid_not_exact_zero")
        start,end=hits[0].span(1)
        result=result[:start]+value+result[end:]
    need(len(raw)==len(result) and sum(a!=b for a,b in zip(raw,result,strict=True))==2,
         "selected_array_grid_changed_other_bytes")
    return result

def run(obj,path,meta,guid,fid,kind,*,repair):
    tree=obj.read_typetree(check_read=False)
    source,raw=exact_inline(tree)
    before=obs.array_png_observation(source,path,meta,fid,kind)
    need(before["all_source_sized_cells_present"] and before["textureShape"]==4,
         "selected_array_grid_geometry_unproven")
    atlas=pixels.read_export_png(path)
    # Use UnityPy's reviewed single-texture decoder on the exact BC3 mip
    # ranges; the second independent Pillow decoder is compared separately.
    native=obj.read()
    reader=native.object_reader
    def decode(data,w,h):
        adapter=SimpleNamespace(m_Width=w,m_Height=h,m_TextureDimension=2,
            m_ImageCount=1,m_MipCount=1,m_TextureFormat=12,
            object_reader=reader,m_PlatformBlob=None)
        return pixels.decode_payload(adapter,data)
    w,h,d,n=(source[k] for k in ("width","height","depth","mipcount"))
    parity=compare_layers(raw,atlas,w,h,d,n,decode=decode)
    result={"before_grid":before,"pixel_comparison":parity,
            "private_grid_repair_applied":False,"only_two_grid_digits_changed":False,
            "png_bytes_unchanged":False,"GUID_preserved":False,"Unity_import_verified":False}
    if not repair or not parity["all_top_mip_layers_exact"] or not parity["layer_order_distinguished"] or not parity["orientation_distinguished"]:
        return result
    meta_path=path.with_name(path.name+".meta")
    need(not meta_path.is_symlink() and meta_path.is_file(),"unsafe_selected_array_meta")
    old=meta_path.read_bytes()
    need(old.decode("utf-8-sig").replace("\r\n","\n")==meta,"selected_array_meta_snapshot_drift")
    patched=repair_bytes(old,guid,2,1)
    digest=hashlib.sha256(path.read_bytes()).digest()
    tmp=meta_path.with_name(meta_path.name+".gt-grid-tmp")
    need(not tmp.exists() and not tmp.is_symlink(),"selected_array_temp_exists")
    try:
        with tmp.open("xb") as stream:
            stream.write(patched)
        need(meta_path.read_bytes()==old,"selected_array_meta_changed_before_write")
        os.replace(tmp,meta_path)
        after=obs.array_png_observation(source,path,meta_path.read_text(encoding="utf-8-sig"),fid,kind)
        need(after["importer_grid_matches"] and meta_path.read_bytes()==patched
             and hashlib.sha256(path.read_bytes()).digest()==digest,"selected_array_repair_postcheck_failed")
    except BaseException:
        if meta_path.read_bytes()==patched:
            meta_path.write_bytes(old)
        raise
    finally:
        tmp.unlink(missing_ok=True)
    result.update(private_grid_repair_applied=True,only_two_grid_digits_changed=True,
                  png_bytes_unchanged=True,GUID_preserved=True,after_grid=after)
    return result
