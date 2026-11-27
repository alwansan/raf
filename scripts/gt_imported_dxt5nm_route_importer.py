"""V12: supported serialized NormalMap importer state on the same V11 route.

The source proof uses strict DXT5nm descriptor (format12/usage3/Gamma0).
The exporter maps six sampler fields and nine source/derived fields; its
explicit policy is separate from the three observed bumpmap defaults.
The pinned schema omits swizzle: unknown, not inferred RGBA equality.
No Unity reimport, GPU sampling, original importer or Android proof.
"""
from dataclasses import dataclass
from scripts import gt_imported_png_route_importer as common
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_imported_dxt5nm_route_pixels as normal

@dataclass(frozen=True)
class Proof(common.Proof):
    pass

def source_proof(tree):
    try:return common._source_proof(tree,descriptor=normal.descriptor,usage_mode=3,proof_type=Proof)
    except png.Unproven as exc:raise common.Unproven(str(exc)) from None

def safe_source(tree):
    try:return source_proof(tree)
    except common.Unproven as exc:return str(exc)
    except (ValueError,TypeError,KeyError,OverflowError):return "unsupported_dxt5nm_source_importer_state"

def compare(source,meta,ptr):
    sampler,mapping,policy,unknown=common._compare(source,meta,ptr,texture_type=1,proof_type=Proof)
    try:imp=png.importer_document(meta,ptr,texture_type=1)
    except png.Unproven as exc:raise common.Unproven(str(exc)) from None
    bump=imp.get("bumpmap")
    # ImporterFactory explicitly sets HeightScale; the remaining values
    # are observed generated-schema defaults, not original source fields.
    common.field(bump,"heightScale",.25,"normal_exporter_policy")
    for name in ("convertToNormalMap","externalNormalMap","normalMapFilter"):
        common.field(bump,name,0,"normal_observed_bumpmap_default")
    return sampler,mapping,policy+1,unknown,3
