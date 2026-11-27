"""V8 imported PNG top mip only; never native mip, Unity import or GPU parity.

Pinned AssetRipperCLI TextureConverter.TryConvertToBitmap(ITexture2D)
decodes RGBA32 and FlipY for non-cubemap. Source raw rows are independently
decoded bottom-up to top-left exactly once; export orientation is unchanged.
"""
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re
import struct

from scripts import gt_texture_route_payload as native
from scripts import gt_streamed_texture_route_payload as streamed
from scripts.gt_mesh_vertex_payload import verified_range_digests
from scripts.gt_particle108_source_pixel_parity import bounded_snapshot, validate_decoded_image
from scripts.gt_zip2_payloads import MAX_BYTES as MAX_PROVIDER
from scripts.b15_texture_sampler_parity import normalize, FIELDS, MIP_BIAS_UNSET

MAX_TOP=16*1024*1024
MAX_CAPTURE=64*1024*1024
MAX_PNG=MAX_TOP+1024*1024


class Unproven(ValueError):
    pass


class Mismatch(ValueError):
    pass


@dataclass(frozen=True)
class Proof:
    size: tuple
    rgba_sha256: str
    rgb_sha256: str
    flipped_sha256: tuple
    from_stream: bool


def need(ok,reason):
    if not ok:raise Unproven(reason)


def decode_top(size,raw):
    from PIL import Image
    w,h=size
    need(0<w and 0<h and 4*w*h<=MAX_TOP and len(raw)==4*w*h,"png_source_top_mip_size_invalid")
    return Image.frombytes("RGBA",(w,h),raw,"raw","RGBA",0,-1)


def digest(image):
    return sha256(image.tobytes()).hexdigest()


def image_proof(image,*,from_stream=False):
    from PIL import Image
    need(image.mode=="RGBA" and 0<4*image.width*image.height<=MAX_TOP,"unsupported_png_RGBA8_image")
    return Proof(image.size,digest(image),digest(image.convert("RGB")),
                 tuple(digest(image.transpose(op)) for op in (Image.Transpose.FLIP_TOP_BOTTOM,
                     Image.Transpose.FLIP_LEFT_RIGHT,Image.Transpose.ROTATE_180)),from_stream)


def source_request(tree):
    need(type(tree) is dict and type(tree.get("m_LightmapFormat")) is int and tree["m_LightmapFormat"]==0,
         "unsupported_png_source_texture_usage")
    blob=tree.get("m_PlatformBlob",[])
    need(type(blob) in (list,bytes,bytearray) and not blob,"unsupported_png_source_platform_blob")
    try:req=streamed.source_request(tree)
    except native.Unproven as e:raise Unproven(str(e)) from None
    need(req.mip_lengths[0]<=MAX_TOP,"png_source_top_mip_size_invalid")
    if isinstance(req,streamed.Request):
        return req
    return image_proof(decode_top(req.descriptor[:2],bytes(tree["image data"])[:req.mip_lengths[0]]))


def safe_request(tree):
    try:return source_request(tree)
    except Unproven as exc:return str(exc)
    except (ValueError,TypeError,KeyError,OverflowError):return "unsupported_png_source_schema"


def resolve_requests(root,records,requests):
    result={};groups=defaultdict(dict)
    for key,req in requests.items():
        if isinstance(req,streamed.Request):groups[req.provider][key]=req
        else:result[key]=req
    for provider,group in groups.items():
        try:kind,size,digest_pin=records["Raft_Data/"+provider]
        except KeyError:
            result.update((k,"png_stream_provider_not_pinned") for k in group);continue
        if (kind not in ("plain","split") or type(size) is not int or not 0<size<=MAX_PROVIDER
            or type(digest_pin) is not str or not re.fullmatch(r"[0-9a-f]{64}",digest_pin)):
            result.update((k,"invalid_png_stream_provider_pin") for k in group);continue
        valid={}
        for k,req in group.items():
            # Whole declared extent must exist; only first mip is decoded.
            if req.offset+req.descriptor[-1]>size:result[k]="png_stream_extent_out_of_bounds"
            else:valid[k]=req
        if not valid:continue
        ranges=set((r.offset,r.mip_lengths[0]) for r in valid.values())
        if sum(n for _,n in ranges)>MAX_CAPTURE:
            result.update((k,"png_stream_capture_budget_exceeded") for k in valid);continue
        try:
            captures={}
            verified_range_digests(Path(root)/provider,(size,digest_pin),ranges,captures=captures)
            for k,r in valid.items():
                data=captures[(r.offset,r.mip_lengths[0])]
                result[k]=image_proof(decode_top(r.descriptor[:2],data),from_stream=True)
        except (ValueError,OSError,TypeError,OverflowError) as exc:
            reason={"vertex_provider_SHA_mismatch":"png_stream_provider_SHA_mismatch",
                    "vertex_provider_size_mismatch":"png_stream_provider_size_mismatch"}.get(str(exc),
                     "unproved_png_stream_provider")
            result.update((k,reason) for k in valid)
    return result


def importer_document(meta,ptr):
    """Strict importer schema and trace identity, not Unity import proof."""
    import yaml
    class Loader(yaml.SafeLoader):
        def construct_mapping(self,node,deep=False):
            out={}
            for k,v in node.value:
                key=self.construct_object(k,deep=deep)
                need(type(key) in (str,int) and key not in out,"duplicate_png_importer_key")
                if key=="guid" and isinstance(v,yaml.ScalarNode):
                    v.tag="tag:yaml.org,2002:str"
                if key=="mipBias" and isinstance(v,yaml.ScalarNode) and v.value=="-0" and v.tag=="tag:yaml.org,2002:int":
                    v.tag="tag:yaml.org,2002:float"
                out[key]=self.construct_object(v,deep=deep)
            return out
    try:doc=yaml.load(meta,Loader=Loader)
    except yaml.YAMLError:raise Unproven("invalid_png_importer_YAML") from None
    need(type(doc) is dict and type(doc.get("fileFormatVersion")) is int and doc["fileFormatVersion"]==2,
         "invalid_png_importer_schema")
    need(type(doc.get("guid")) is str and doc["guid"]==ptr[0] and ptr[1:]==(2800000,3),
         "png_trace_importer_identity_mismatch")
    imp=doc.get("TextureImporter")
    need(type(imp) is dict and not any(k.endswith("Importer") and k!="TextureImporter" for k in doc if type(k) is str),
         "missing_unique_png_TextureImporter")
    need(type(imp.get("textureShape")) is int and imp["textureShape"]==1 and
         type(imp.get("textureType")) is int and imp["textureType"]==0,
         "unsupported_png_importer_shape_or_type")
    return imp


def importer(meta,ptr):
    imp=importer_document(meta,ptr)
    settings=imp.get("textureSettings")
    need(type(settings) is dict,"missing_png_importer_sampler_schema")
    try:values=normalize(settings,original=False)
    except (ValueError,TypeError,OverflowError):raise Unproven("invalid_png_importer_sampler_schema") from None
    return {"sampler_fields_present":len(FIELDS),"importer_mip_bias_unset":values[2]==MIP_BIAS_UNSET}


def exported_image(path):
    from PIL import Image
    raw=bounded_snapshot(path,MAX_PNG)
    need(len(raw)>=33 and raw[:8]==b"\x89PNG\r\n\x1a\n" and raw[8:16]==b"\0\0\0\rIHDR",
         "invalid_png_signature_or_IHDR")
    w,h,depth,ctype,compression,filter_method,interlace=struct.unpack(">IIBBBBB",raw[16:29])
    need(0<w and 0<h and 4*w*h<=MAX_TOP and depth==8 and ctype==6 and
         compression==filter_method==0 and interlace in (0,1),"unsupported_png_RGBA8_image")
    try:
        with Image.open(BytesIO(raw)) as im:
            need(im.format=="PNG" and getattr(im,"n_frames",1)==1,"unsupported_png_animation")
            im.verify()
        with Image.open(BytesIO(raw)) as im:
            need(im.mode=="RGBA" and im.size==(w,h),"unsupported_png_RGBA8_image")
            validate_decoded_image(im)
            return image_proof(im)
    except Unproven:raise
    except (OSError,ValueError,TypeError,Image.DecompressionBombError):
        raise Unproven("invalid_png_pixel_decode") from None


def compare(source,path,meta,ptr):
    need(isinstance(source,Proof),source if type(source) is str else "missing_png_source_top_mip_proof")
    need(path.suffix.lower()==".png","unsupported_png_export_target")
    imp=importer(meta,ptr)
    try:actual=exported_image(path)
    except (OSError,ValueError) as e:
        if isinstance(e,Unproven):raise
        raise Unproven("unreadable_png_export") from None
    if source.size!=actual.size:raise Mismatch("same_route_png_DIMENSION_MISMATCH")
    if source.rgba_sha256!=actual.rgba_sha256:
        # T3 compare_pair category order, with hashes instead of retained pixels.
        for name,h in zip(("VERTICAL_FLIP","HORIZONTAL_FLIP","BOTH_AXES_FLIP"),source.flipped_sha256,strict=True):
            if h==actual.rgba_sha256:raise Mismatch("same_route_png_"+name)
        if source.rgb_sha256==actual.rgb_sha256:raise Mismatch("same_route_png_ALPHA_ONLY_DRIFT")
        raise Mismatch("same_route_png_RGB_DRIFT")
    return source.size[0]*source.size[1],source.from_stream,imp["importer_mip_bias_unset"]
