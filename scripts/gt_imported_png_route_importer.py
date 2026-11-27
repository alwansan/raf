"""V9: serialized importer state, not Unity import, original runtime or GPU.

Pinned nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8:
Textures/ImporterFactory.cs, TextureExportCollection.cs and
SourceGenerated.Extensions/TextureImporterExtensions.cs. Numeric enum ABI
must be independently checked in the compiled authored witness.
"""
from dataclasses import dataclass
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_native_texture_route_sampler as native
from scripts import gt_texture_route_payload as payload
from scripts.b15_texture_sampler_parity import normalize, FIELDS, MIP_BIAS_UNSET
from scripts.b22_verify_material_scalars import _float_bits

SOURCE_FIELDS=("m_ColorSpace","m_IsReadable","m_StreamingMipmaps",
               "m_StreamingMipmapsPriority","m_LightmapFormat")
SAMPLER_FIELDS=tuple(out for _,out in FIELDS)

class Unproven(ValueError):
    pass

class Mismatch(ValueError):
    pass

@dataclass(frozen=True)
class Proof:
    sampler: tuple
    color_space: int
    mip_count: int
    mip_enabled: int
    readable: int
    streaming: int
    priority: int
    format: int
    size: tuple
    max_size: int

def need(ok,reason):
    if not ok:raise Unproven(reason)

def boolean(value):
    need(type(value) in (int,bool) and value in (0,1),"invalid_png_source_importer_boolean")
    return int(value)

def source_proof(tree):
    need(type(tree) is dict and all(k in tree for k in SOURCE_FIELDS),
         "missing_png_source_importer_state")
    try:
        desc,_=payload.descriptor(tree)
        sampler=native.proof(tree).values
    except (payload.Unproven,native.Unproven) as exc:
        raise Unproven(str(exc)) from None
    w,h,fmt,mips,_,_,_=desc
    color=tree["m_ColorSpace"]
    need(type(color) is int and color in (0,1),"unknown_png_source_color_space")
    usage=tree["m_LightmapFormat"]
    need(type(usage) is int and usage==0,"unsupported_png_source_texture_usage")
    priority=tree["m_StreamingMipmapsPriority"]
    need(type(priority) is int and -(2**31)<=priority<2**31,"invalid_png_source_streaming_priority")
    # Factory uses explicit count OR historical m_MipMap if present.
    old_mip=boolean(tree["m_MipMap"]) if "m_MipMap" in tree else 0
    return Proof(sampler,color,mips,int(mips>1 or old_mip),boolean(tree["m_IsReadable"]),
                 boolean(tree["m_StreamingMipmaps"]),priority,fmt,(w,h),
                 max(2048,1<<(max(w,h)-1).bit_length()))

def safe_source(tree):
    try:return source_proof(tree)
    except Unproven as exc:return str(exc)
    except (ValueError,TypeError,KeyError,OverflowError):return "unsupported_png_source_importer_state"

def field(obj,key,expected,scope):
    need(type(obj) is dict and key in obj,"missing_png_"+scope+"_"+key)
    value=obj[key]
    need(type(value) is type(expected),"invalid_png_"+scope+"_"+key)
    if value!=expected:raise Mismatch("same_route_png_"+scope+"_"+key+"_drift")

def compare(source,meta,ptr):
    need(isinstance(source,Proof),source if type(source) is str else "missing_png_source_importer_proof")
    try:imp=png.importer_document(meta,ptr)
    except png.Unproven as exc:raise Unproven(str(exc)) from None
    settings=imp.get("textureSettings")
    need(type(settings) is dict and set(settings)==set(SAMPLER_FIELDS)|{"serializedVersion"} and
         type(settings["serializedVersion"]) is int and settings["serializedVersion"]==2,
         "unsupported_png_importer_sampler_schema")
    try:
        values=normalize(settings,original=False)
        bias=_float_bits(settings["mipBias"])
    except (TypeError,ValueError,OverflowError):raise Unproven("invalid_png_importer_sampler_state") from None
    need(values[2]!=MIP_BIAS_UNSET and -1 not in (values[0],values[1],*values[3:]),
         "unknown_png_importer_sampler_default")
    need(0<=values[0]<=2,"invalid_png_importer_sampler_state")
    for name,before,after in zip(SAMPLER_FIELDS,source.sampler,(values[0],values[1],bias,*values[3:]),strict=True):
        if before!=after:raise Mismatch("same_route_png_importer_"+name+"_drift")
    # ColorSpace.Linear=1 is a serialized enum ABI, not a color transform.
    for name,expected in (("enableMipMap",source.mip_enabled),("sRGBTexture",int(source.color_space==1))):
        field(imp.get("mipmaps"),name,expected,"source_mapping")
    for name,expected in (("isReadable",source.readable),("streamingMipmaps",source.streaming),
                          ("streamingMipmapsPriority",source.priority),("textureFormat",source.format),
                          ("textureShape",1),("textureType",0),("maxTextureSize",source.max_size)):
        field(imp,name,expected,"source_mapping")
    # Exporter decisions, not recovered original runtime properties.
    for name,expected in (("nPOTScale",0),("alphaUsage",1),("alphaIsTransparency",1),
                          ("swizzle",50462976),("compressionQuality",50)):
        field(imp,name,expected,"exporter_policy")
    platforms=imp.get("platformSettings")
    need(type(platforms) is list and len(platforms)==1 and type(platforms[0]) is dict,
         "unknown_png_importer_platform_population")
    for name,expected in (("serializedVersion",3),("buildTarget","DefaultTexturePlatform"),
                          ("maxTextureSize",source.max_size),("textureFormat",-1),
                          ("textureCompression",2),("compressionQuality",50),("resizeAlgorithm",0),
                          ("crunchedCompression",0),("allowsAlphaSplitting",0),("overridden",0),
                          ("androidETC2FallbackOverride",0),("forceMaximumCompressionQuality_BC6H_BC7",0)):
        field(platforms[0],name,expected,"exporter_policy")
    return 6,9,17
