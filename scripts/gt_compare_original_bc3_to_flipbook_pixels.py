#!/usr/bin/env python3
"""GT exact original BC3 mip/slice ordering vs actually exported Texture2DArray PNG.

No original pixels, decoded images, GUIDs, filenames or raw hashes leave CI.
Pillow's DDS BC3 decoder is used as an independent CPU pixel reference; tests
must distinguish original slice-major and mip-major layouts without presuming
one. Reports only aggregate exact match counts. A format mismatch remains
inconclusive, never converted into a fake visual parity claim.
"""
from __future__ import annotations

from collections import Counter
import io
import json
from pathlib import Path
import struct

from scripts.gt_bc3_array_layout import mip_bytes
from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_validate_texture2darray_flipbook import (
    index_exported_array_meta, png_dimensions,
)

LAYOUTS=("slice_major","mip_major")
MAX_ARRAY=512*1024*1024


def dds_bc3(raw:bytes,width:int,height:int):
    """DXT5 single-mip DDS wrapper, decoded by Pillow's BC3 implementation."""
    from PIL import Image
    if len(raw)!=mip_bytes(width,height,0):
        raise InventoryError("corrupt_private_BC3_mip_data")
    flags=0x0002100F
    payload=(b"DDS "+struct.pack("<7I",124,flags,height,width,len(raw),0,1)
             +bytes(44)+struct.pack("<8sI",b"",0))  # replaced below by DDS_PIXELFORMAT
    pixfmt=struct.pack("<8I",32,4,int.from_bytes(b"DXT5","little"),0,0,0,0,0)
    header=(b"DDS "+struct.pack("<7I",124,flags,height,width,len(raw),0,1)
            +bytes(44)+pixfmt+struct.pack("<5I",0x1000,0,0,0,0))
    if len(header)!=128:
        raise InventoryError("invalid_synthetic_DDS_header")
    with Image.open(io.BytesIO(header+raw)) as img:
        return img.convert("RGBA").copy()


def mip_range(width:int,height:int,depth:int,mips:int,element:int,mip:int,layout:str):
    if (layout not in LAYOUTS or type(depth) is not int or not 0<depth<=2048
        or type(element) is not int or not 0<=element<depth
        or type(mip) is not int or not 0<=mip<mips):
        raise InventoryError("invalid_original_mip_slice_layout")
    sizes=[mip_bytes(width,height,i) for i in range(mips)]
    if layout=="slice_major":
        offset=element*sum(sizes)+sum(sizes[:mip])
    else:
        offset=depth*sum(sizes[:mip])+element*sizes[mip]
    return offset,sizes[mip]


def evaluate(payload:bytes,atlas,depth:int,mips:int,width:int,height:int,cols:int,layout:str,sample_layers=None)->dict:
    from PIL import ImageOps
    if len(payload)!=sum(mip_bytes(width,height,i) for i in range(mips))*depth:
        raise InventoryError("wrong_private_original_BC3_array_byte_length")
    samples=sorted({0,1,depth-1}) if sample_layers is None else sorted(set(sample_layers))
    if not samples or any(type(x) is not int or x<0 or x>=depth for x in samples):
        raise InventoryError("invalid_original_array_visible_sample_layers")
    counts=Counter()
    for layer in samples:
        x=(layer%cols)*width
        y=(layer//cols)*height
        target=atlas.crop((x,y,x+width,y+height)).convert("RGBA")
        offset,size=mip_range(width,height,depth,mips,layer,0,layout)
        decoded=dds_bc3(payload[offset:offset+size],width,height)
        if decoded.tobytes()==target.tobytes():
            counts["exact_raw_orientation_match"]+=1
        elif ImageOps.flip(decoded).tobytes()==target.tobytes():
            counts["exact_vertical_flip_match"]+=1
        else:
            counts["nonidentical_reference_pixels"]+=1
    return {"samples":len(samples),**dict(sorted(counts.items()))}


def inspect(stage:Path,project:Path)->dict:
    from PIL import Image
    stage=stage.absolute()
    manifest=stage/"private-array-import-manifest.json"
    if stage.is_symlink() or not manifest.is_file() or manifest.is_symlink():
        raise InventoryError("invalid_private_original_array_import_manifest")
    data=json.loads(manifest.read_text())
    arrays=data.get("arrays")
    if data.get("schema")!="GT_PRIVATE_ORIGINAL_ARRAY_IMPORT_INPUT_V1" or not isinstance(arrays,list) or len(arrays)!=9:
        raise InventoryError("invalid_private_original_array_manifest_schema")
    targets=index_exported_array_meta(project)
    counts=Counter()
    disambiguated=0
    all_samples=0
    for array in arrays:
        guid=array.get("target_export_guid")
        if not isinstance(guid,str) or guid.lower() not in targets:
            raise InventoryError("missing_exported_private_array_target")
        file,meta=targets[guid.lower()]
        if (file.suffix.lower()!=".png" or
            array.get("target_fileID")!=18700000 or
            array.get("target_export_type") not in (2,3)):
            raise InventoryError("wrong_original_array_importer_class_or_target")
        body=meta.read_text(encoding="utf-8-sig")
        import re
        def value(key):
            finds=re.findall(r"(?m)^\s*"+key+r":\s*(\d+)\s*$",body)
            return int(finds[0]) if len(finds)==1 else 0
        rows,cols=value("flipbookRows"),value("flipbookColumns")
        if value("textureShape")!=4:
            raise InventoryError("original_array_importer_shape_mismatch")
        image_width,image_height=png_dimensions(file)
        width,height=array["width"],array["height"]
        if image_width%width or image_height%height:
            counts["export_png_not_divisible_into_source_layer_cells"]+=1
            continue
        real_cols,real_rows=image_width//width,image_height//height
        displayed_cells=real_cols*real_rows
        if displayed_cells==array["depth"]:
            counts["export_png_contains_all_source_layer_cells"]+=1
        elif displayed_cells==1:
            counts["export_png_contains_one_source_layer_cell"]+=1
        else:
            counts["export_png_contains_partial_or_extra_layer_cells"]+=1
        if rows<1 or cols<1 or rows*cols!=array["depth"]:
            counts["export_meta_flipbook_grid_inconsistent_with_source"]+=1
        if array.get("payload_bytes")==0:
            if array.get("relative_payload") is not None:
                raise InventoryError("fabricated_empty_source_array_payload")
            counts["source_zero_pixel_arrays"]+=1
            continue
        # An ordinary one-cell exporter preview is useful to check whether
        # original BC3 source pixels survive, but never authenticates the
        # other original layers or the slice/mip byte ordering.
        if displayed_cells not in (1,array["depth"]):
            continue
        raw_path=stage/array["relative_payload"]
        if raw_path.is_symlink() or not raw_path.is_file() or raw_path.stat().st_size>MAX_ARRAY:
            raise InventoryError("unsafe_private_original_array_BC3")
        import hashlib
        raw=raw_path.read_bytes()
        if (len(raw)!=array["payload_bytes"] or
            hashlib.sha256(raw).hexdigest()!=array["sha256"]):
            raise InventoryError("private_original_array_SHA256_mismatch")
        with Image.open(file) as opened:
            atlas=opened.convert("RGBA")
        candidate={}
        visible_layers=(
            [0] if displayed_cells==1 else sorted({0,1,array["depth"]-1})
        )
        for layout in LAYOUTS:
            candidate[layout]=evaluate(raw,atlas,array["depth"],array["mipmap_count"],
                width,height,real_cols,layout,visible_layers)
        matches={layout:sum(val.get(k,0) for k in (
            "exact_raw_orientation_match","exact_vertical_flip_match"))
            for layout,val in candidate.items()}
        sample_count=next(iter(candidate.values()))["samples"]
        if displayed_cells==1:
            counts["single_tile_pixel_probes_without_slice_order_proof"]+=1
        for k in LAYOUTS:
            counts[k+"_exact_samples"]+=matches[k]
        all_samples+=sample_count
        valid=[layout for layout in LAYOUTS if matches[layout]==sample_count]
        if len(valid)==1 and displayed_cells==array["depth"]:
            counts["unambiguous_original_BC3_slice_layout_"+valid[0]]+=1
            disambiguated+=1
        elif len(valid)==2 or (len(valid)==1 and displayed_cells==1):
            counts["ambiguous_both_layouts_match_exactly"]+=1
        else:
            counts["no_exact_source_BC3_to_export_PNG_match"]+=1
        counts["real_source_array_payloads_compared"]+=1
    return {
        "schema":"GT_ORIGINAL_BC3_ARRAY_TO_ASSETRIPPER_FLIPBOOK_PIXEL_EQUIVALENCE_V1",
        "original_arrays_with_pixels":counts["real_source_array_payloads_compared"],
        "original_source_empty_pixel_arrays":counts["source_zero_pixel_arrays"],
        "sampled_original_source_layer0_mips_vs_PNG_cells":all_samples,
        "original_BC3_layout_unambiguously_matched_array_count":disambiguated,
        "counts":dict(sorted(counts.items())),
        "all_original_BC3_source_array_PNG_pixels_proven":(
            counts["real_source_array_payloads_compared"]==8 and
            counts["export_png_contains_all_source_layer_cells"]==9 and
            counts["no_exact_source_BC3_to_export_PNG_match"]==0 and
            counts["ambiguous_both_layouts_match_exactly"]==0),
        "full_mip_chain_pixel_equivalence_proven":False,
        "Unity_Android_GPU_pixels_verified":False,
        "original_arrays_published":False
    }


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-original-array-stage",type=Path,required=True)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    if (a.report.absolute().is_relative_to(a.project.absolute()) or
        a.report.absolute().is_relative_to(a.private_original_array_stage.absolute())):
        raise InventoryError("pixel_parity_aggregate_inside_private_game_data")
    d=inspect(a.private_original_array_stage,a.project)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GT_REAL_ORIGINAL_BC3_FLIPBOOK_PIXEL_PARITY "+json.dumps(d,sort_keys=True))


if __name__=="__main__":
    main()
