"""V11: BC3 storage decode/FlipY, then pinned T3 UnpackNormal semantics.
Strict format12/usage3/Gamma0; separate proof, never ordinary V10 or GPU.
"""
from dataclasses import dataclass
from scripts import gt_imported_bc3_route_pixels as bc3
from scripts import gt_imported_png_route_pixels as png
from scripts.t3_normalmap_dxt5_semantic import semantic_rgba_input

@dataclass(frozen=True)
class Proof(png.Proof):
    packed_rgba_sha256: str

@dataclass(frozen=True)
class Request(bc3.Request):
    pass

def descriptor(tree):
    png.need(type(tree) is dict and type(tree.get("m_LightmapFormat")) is int
             and tree["m_LightmapFormat"]==3 and type(tree.get("m_ColorSpace")) is int
             and tree["m_ColorSpace"]==0,"unsupported_dxt5nm_usage_or_color_space")
    return bc3.descriptor(dict(tree,m_LightmapFormat=0))

def decode_top(size,raw):
    packed=bc3.decode_top(size,raw)
    return packed,semantic_rgba_input(packed,format_code=12,color_space=0,lightmap_format=3)

def image_proof(size,raw,*,from_stream=False):
    packed,normal=decode_top(size,raw)
    p=png.image_proof(normal,from_stream=from_stream)
    return Proof(p.size,p.rgba_sha256,p.rgb_sha256,p.flipped_sha256,p.from_stream,png.digest(packed))

def source_request(tree):
    return bc3.source_request(tree,_descriptor=descriptor,_image_proof=image_proof,_request_type=Request)

def safe_request(tree):
    try:return source_request(tree)
    except png.Unproven as e:return str(e)
    except (ValueError,TypeError,KeyError,OverflowError,OSError):return "unproved_dxt5nm_source_decode"

def resolve_requests(root,records,requests):
    return bc3.resolve_requests(root,records,requests,_image_proof=image_proof,_request_type=Request)

def compare(source,path,meta,ptr):
    png.need(type(source) is Proof,source if type(source) is str else "missing_dxt5nm_source_proof")
    imp=png.importer_document(meta,ptr,texture_type=1)
    for obj,key,expected in ((imp,"textureFormat",12),(imp.get("mipmaps"),"sRGBTexture",0)):
        png.need(type(obj) is dict and type(obj.get(key)) is int,"missing_dxt5nm_importer_"+key)
        if obj[key]!=expected:raise png.Mismatch("same_route_dxt5nm_importer_"+key+"_drift")
    return png.compare(source,path,meta,ptr,texture_type=1)
