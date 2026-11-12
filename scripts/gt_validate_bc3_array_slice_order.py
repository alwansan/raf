#!/usr/bin/env python3
"""GT independently validate original compressed BC3 Texture2DArray slice order.

Authenticates all 82 original ZIP2 containers and each temporary source
stream SHA256, then asks UnityPy's original Texture2DArray reader for actual
decoded per-layer pixels. Compare those to two candidate placements of the
same original DXT5 top-mip bytes via independent Pillow decoder. Never emit
source names, GUIDs, pixels, private hashes or mutable game objects.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_verify_original_array_export import source_arrays
from scripts.gt_compare_original_bc3_to_flipbook_pixels import (
    dds_bc3,mip_range,LAYOUTS
)


def compare_frames(raw:bytes,frames:list,width:int,height:int,depth:int,mips:int)->dict:
    from PIL import ImageOps
    if not isinstance(frames,(list,tuple)) or len(frames)!=depth:
        raise InventoryError("original_UnityPy_array_layers_missing")
    candidates={layout:Counter() for layout in LAYOUTS}
    samples=sorted({0,1,depth-1})
    for layer in samples:
        if not hasattr(frames[layer],"convert") or frames[layer].size!=(width,height):
            raise InventoryError("original_UnityPy_array_frame_dimensions_invalid")
        source=frames[layer].convert("RGBA").tobytes()
        for layout in LAYOUTS:
            start,size=mip_range(width,height,depth,mips,layer,0,layout)
            decoded=dds_bc3(raw[start:start+size],width,height)
            if source==decoded.tobytes():
                candidates[layout]["as_is"]+=1
            elif source==ImageOps.flip(decoded).tobytes():
                candidates[layout]["vertically_flipped"]+=1
            else:
                candidates[layout]["mismatch"]+=1
    return {layout:{"sample_layers":len(samples),
       "exact_source_pixel_matches":sum(candidates[layout][k] for k in
                                       ("as_is","vertically_flipped")),
       "vertical_flip_needed":candidates[layout]["vertically_flipped"],
       "mismatched_source_layers":candidates[layout]["mismatch"]}
       for layout in LAYOUTS}


def decoded_original_frames(obj,raw:bytes,source:dict):
    """Decode exact SHA-pinned external bytes through UnityPy, in memory only.

    Isolated serialized owners intentionally have no adjacent original .resS.
    UnityPy's .images property otherwise sees empty inline image_data and can
    raise 'Texture2D has no image data' despite the independently verified
    streamed payload. Never alter the original serialized file on disk.
    """
    try:
        native=obj.read()
    except (AttributeError,NotImplementedError,ValueError,OSError) as err:
        raise InventoryError("original_UnityPy_array_object_read_failed") from err
    if (getattr(native,"m_Width",None)!=source["width"] or
        getattr(native,"m_Height",None)!=source["height"] or
        getattr(native,"m_Depth",None)!=source["depth"] or
        getattr(native,"m_MipCount",None)!=source["source_mipmap_count"] or
        getattr(native,"m_Format",None)!=source["source_format_enum"] or
        getattr(native,"m_DataSize",None) not in (0,len(raw)) or
        not hasattr(native,"image_data")):
        raise InventoryError("original_UnityPy_array_native_metadata_mismatch")
    # The source stream payload was SHA256 verified before reaching this
    # helper. A zero inline m_DataSize is legitimate for external streams.
    native.m_DataSize=len(raw)
    native.image_data=raw
    try:
        return native.images
    except (AttributeError,NotImplementedError,ValueError,OSError) as err:
        raise InventoryError("original_UnityPy_Texture2DArray_decoder_failed") from err


def inspect(source_root:Path,original:dict,private_stage:Path,loader=None)->dict:
    if len(original)!=9 or not source_root.is_dir() or source_root.is_symlink():
        raise InventoryError("invalid_SHA_authenticated_original_array_scope")
    manifest=private_stage/"private-array-import-manifest.json"
    if private_stage.is_symlink() or manifest.is_symlink() or not manifest.is_file():
        raise InventoryError("invalid_private_array_stage")
    data=json.loads(manifest.read_text())
    rows=data.get("arrays")
    if data.get("schema")!="GT_PRIVATE_ORIGINAL_ARRAY_IMPORT_INPUT_V1" or not isinstance(rows,list) or len(rows)!=9:
        raise InventoryError("invalid_authenticated_array_stage_manifest")
    if loader is None:
        import UnityPy
        loader=lambda file:UnityPy.load(str(file))
    pairings={identity:rows[i] for i,identity in enumerate(sorted(original))}
    counters=Counter()
    per_array=[]
    loaded_owners=set()
    for name in sorted({owner for owner,_ in original}):
        env=loader(source_root/name)
        loaded_owners.add(name)
        for obj in env.objects:
            if str(obj.type.name)!="Texture2DArray": continue
            identity=(name,obj.path_id)
            if identity not in pairings:
                raise InventoryError("untrusted_original_array_object_identity")
            row=pairings[identity]
            source=original[identity]
            if (row["depth"]!=source["depth"] or row["width"]!=source["width"] or
                row["height"]!=source["height"] or
                row["mipmap_count"]!=source["source_mipmap_count"] or
                row["source_format_enum"]!=source["source_format_enum"]):
                raise InventoryError("private_array_source_type_mismatch")
            if row["payload_bytes"]==0:
                if (source["original_stream_size"]!=0 or
                    row.get("relative_payload") is not None):
                    raise InventoryError("fabricated_unpopulated_original_array")
                counters["original_array_objects_without_source_pixel_bytes"]+=1
                continue
            path=private_stage/row["relative_payload"]
            if (path.is_symlink() or not path.is_file() or
                path.stat().st_size!=row["payload_bytes"]):
                raise InventoryError("missing_original_SHA_verified_BC3_payload")
            raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=row["sha256"]:
                raise InventoryError("corrupt_original_array_BC3_private_stage")
            frames=decoded_original_frames(obj,raw,source)
            per_array.append(compare_frames(raw,frames,source["width"],source["height"],
                                            source["depth"],source["source_mipmap_count"]))
            counters["source_array_objects_with_independently_decoded_pixels"]+=1
    if len(loaded_owners)==0 or len(per_array)!=8 or counters["original_array_objects_without_source_pixel_bytes"]!=1:
        raise InventoryError("original_source_array_independent_decoder_scope_incomplete")
    possible=[]
    for layout in LAYOUTS:
        n=0
        unambiguous=0
        for row in per_array:
            test=row[layout]
            if test["exact_source_pixel_matches"]==test["sample_layers"]:
                n+=1
                other=next(x for x in LAYOUTS if x!=layout)
                if row[other]["exact_source_pixel_matches"]<row[other]["sample_layers"]:
                    unambiguous+=1
        counters["original_source_array_"+layout+"_full_match"]+=n
        counters["original_source_array_"+layout+"_unambiguous"]+=unambiguous
        if n==8 and unambiguous>0:
            possible.append(layout)
    layout=possible[0] if len(possible)==1 else None
    return {
        "schema":"GT_ORIGINAL_BC3_SLICE_LAYOUT_INDEPENDENT_SOURCE_DECODER_V1",
        "authenticated_original_array_objects":9,
        "source_arrays_with_decoded_BC3_pixels":8,
        "original_zero_pixel_source_array_objects":1,
        "layout_selected_from_independent_UnityPy_source_decoder":layout,
        "source_array_layout_unambiguous":len(possible)==1,
        "counts":dict(sorted(counters.items())),
        "Unity_Editor_array_asset_import_verified":False,
        "Android_GPU_pixel_colors_verified":False,
        "original_source_bytes_or_names_disclosed":False,
        "original_or_exported_Unity_objects_modified":False
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--source-manifest",type=Path,required=True)
    p.add_argument("--private-original-array-stage",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    if (args.report.resolve().is_relative_to(args.source.resolve()) or
        args.report.resolve().is_relative_to(args.private_original_array_stage.resolve())):
        raise InventoryError("independent_array_report_overlaps_original_game_data")
    result=inspect(args.source,source_arrays(args.source,args.source_manifest),
                   args.private_original_array_stage)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_REAL_ORIGINAL_ARRAY_SOURCE_DECODER_LAYOUT "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
