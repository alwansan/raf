"""V10: ordinary Texture2D DXT5/BC3 -> actual PNG, decoded top mip only.

Pinned AssetRipperCLI 036098ab525a3f9f693dc101edeb21faad4d32d8
TextureConverter.TryConvertToBitmap(ITexture2D) invokes DXT5 decoder and
FlipY for non-cubemap. Independent Pillow DDS BC3 oracle; no normal-map
unpacking, Crunch, platform blob, GPU or reimport.
"""
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re

from scripts import gt_imported_png_route_pixels as png
from scripts import gt_texture_route_payload as native
from scripts.gt_bc3_array_layout import mip_bytes
from scripts.gt_compare_original_bc3_to_flipbook_pixels import dds_bc3
from scripts.gt_mesh_vertex_payload import verified_range_digests
from scripts.gt_zip2_payloads import MAX_BYTES as MAX_PROVIDER

DXT5=12

@dataclass(frozen=True)
class Proof(png.Proof):
    """Separate typed receipt; never a V8 RGBA32 or V9 importer proof."""

@dataclass(frozen=True)
class Request:
    descriptor: tuple
    mip_lengths: tuple
    provider: str
    offset: int

def need(ok,reason):
    if not ok:raise png.Unproven(reason)

def descriptor(tree):
    need(type(tree) is dict and all(k in tree for k in native.FIELDS),
         "missing_bc3_texture_descriptor")
    desc=tuple(tree[k] for k in native.FIELDS)
    need(all(type(v) is int for v in desc),"invalid_bc3_texture_descriptor")
    w,h,fmt,mips,images,dimension,size=desc
    need(0<w<=16384 and 0<h<=16384 and 4*w*h<=png.MAX_TOP and fmt==DXT5 and images==1 and dimension==2,
         "unsupported_bc3_texture_layout")
    need(1<=mips<=max(w,h).bit_length(),"invalid_bc3_mip_count")
    stripped=tree.get("m_MipsStripped",0)
    need(type(stripped) is int and stripped==0,"unsupported_bc3_stripped_mips")
    need(type(tree.get("m_LightmapFormat")) is int and tree["m_LightmapFormat"]==0,
         "unsupported_bc3_texture_usage")
    blob=tree.get("m_PlatformBlob",[])
    need(type(blob) in (list,bytes,bytearray) and not blob,"unsupported_bc3_platform_blob")
    sizes=tuple(mip_bytes(w,h,n) for n in range(mips))
    need(0<size<=native.MAX_BYTES and size==sum(sizes),"bc3_mip_size_mismatch")
    return desc,sizes

def decode_top(size,raw):
    from PIL import Image
    w,h=size
    need(0<w and 0<h and 4*w*h<=png.MAX_TOP and len(raw)==mip_bytes(w,h,0),
         "invalid_bc3_top_mip_extent")
    return dds_bc3(raw,w,h).transpose(Image.Transpose.FLIP_TOP_BOTTOM)

def image_proof(size,raw,*,from_stream=False):
    p=png.image_proof(decode_top(size,raw),from_stream=from_stream)
    return Proof(p.size,p.rgba_sha256,p.rgb_sha256,p.flipped_sha256,p.from_stream)

def source_request(tree,*,_descriptor=descriptor,_image_proof=image_proof,_request_type=Request):
    desc,sizes=_descriptor(tree)
    try:path,offset,size=native.stream_fields(tree)
    except native.Unproven as e:raise png.Unproven(str(e)) from None
    need("image data" in tree,"missing_bc3_payload")
    data=tree["image data"]
    need(type(data) in (bytes,bytearray,list),"invalid_bc3_payload")
    if path=="" and type(offset) is int and offset==0 and type(size) is int and size==0:
        need(len(data)==desc[-1],"bc3_inline_extent_mismatch")
        if type(data) is list:
            need(all(type(v) is int and 0<=v<=255 for v in data),"invalid_bc3_payload_byte")
        return _image_proof(desc[:2],bytes(data[:sizes[0]]))
    need(type(path) is str and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:resS|resource)",path)
         and ".." not in path,"unsupported_bc3_stream_provider")
    need(type(offset) is int and type(size) is int and offset>=0 and size==desc[-1]
         and offset+size<=MAX_PROVIDER,"invalid_bc3_stream_extent")
    need(len(data)==0,"ambiguous_bc3_inline_and_stream")
    return _request_type(desc,sizes,path,offset)

def safe_request(tree):
    try:return source_request(tree)
    except png.Unproven as e:return str(e)
    except (ValueError,TypeError,KeyError,OverflowError,OSError):return "unproved_bc3_source_decode"

def resolve_requests(root,records,requests,*,_image_proof=image_proof,_request_type=Request):
    result={};groups=defaultdict(dict)
    for key,req in requests.items():
        if type(req) is _request_type:groups[req.provider][key]=req
        else:result[key]=req
    for provider,group in groups.items():
        try:kind,size,pin=records["Raft_Data/"+provider]
        except KeyError:
            result.update((k,"bc3_stream_provider_not_pinned") for k in group);continue
        if (kind not in ("plain","split") or type(size) is not int or not 0<size<=MAX_PROVIDER
                or type(pin) is not str or not re.fullmatch(r"[0-9a-f]{64}",pin)):
            result.update((k,"invalid_bc3_stream_provider_pin") for k in group);continue
        valid={}
        for k,r in group.items():
            if r.offset+r.descriptor[-1]>size:result[k]="bc3_stream_extent_out_of_bounds"
            else:valid[k]=r
        if not valid:continue
        ranges={(r.offset,r.mip_lengths[0]) for r in valid.values()}
        if sum(n for _,n in ranges)>png.MAX_CAPTURE:
            result.update((k,"bc3_stream_capture_budget_exceeded") for k in valid);continue
        try:
            captures={}
            verified_range_digests(Path(root)/provider,(size,pin),ranges,captures=captures)
            for k,r in valid.items():
                result[k]=_image_proof(r.descriptor[:2],captures[(r.offset,r.mip_lengths[0])],from_stream=True)
        except (ValueError,OSError,TypeError,OverflowError) as e:
            reason={"vertex_provider_SHA_mismatch":"bc3_stream_provider_SHA_mismatch",
                    "vertex_provider_size_mismatch":"bc3_stream_provider_size_mismatch"}.get(str(e),"unproved_bc3_stream_provider")
            result.update((k,reason) for k in valid)
    return result
