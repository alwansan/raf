#!/usr/bin/env python3
"""GT exact Unity GraphicsFormat BC3/DXT5 (100/101) Texture2DArray mip byte sizes.

Unity 2021 GraphicsFormat enum values 100=RGBA_DXT5_SRGB and
101=RGBA_DXT5_UNorm; both are block-compressed BC3, 4x4 pixels per
16-byte block. Original raw byte order within each Array is left UNPROVEN
until validated against actual Unity Editor; this helper proves only byte
extent/mip geometry, never layer pixels, color parity or GPU compatibility.
"""
from __future__ import annotations

from scripts.gt_stage_serialized_owners import InventoryError

BC3_GRAPHICS_FORMATS=frozenset((100,101))
MAX_DIMENSION=16384
MAX_MIPS=15
MAX_ARRAY_LAYERS=2048


def mip_bytes(width:int,height:int,mip:int)->int:
    if (type(width) is not int or type(height) is not int or
        not 0<width<=MAX_DIMENSION or not 0<height<=MAX_DIMENSION or
        type(mip) is not int or not 0<=mip<MAX_MIPS):
        raise InventoryError("invalid_BC3_mip_dimensions")
    w=max(1,width>>mip)
    h=max(1,height>>mip)
    return max(1,(w+3)//4)*max(1,(h+3)//4)*16


def array_payload_bytes(width:int,height:int,depth:int,mips:int,
                        graphics_format:int)->int:
    if (type(graphics_format) is not int or
        graphics_format not in BC3_GRAPHICS_FORMATS):
        raise InventoryError("unsupported_original_array_GraphicsFormat")
    if (type(depth) is not int or not 0<depth<=MAX_ARRAY_LAYERS or
        type(mips) is not int or not 0<mips<=MAX_MIPS):
        raise InventoryError("invalid_original_array_layer_or_mip_count")
    max_allowed=max(width,height).bit_length()
    if mips>max_allowed:
        raise InventoryError("source_array_excessive_mip_count")
    return depth*sum(mip_bytes(width,height,n) for n in range(mips))


def original_layout_report(arrays:dict)->dict:
    if len(arrays)!=9:
        raise InventoryError("expected_nine_original_texture_arrays")
    expected=0
    present=0
    absent=0
    populated=0
    for info in arrays.values():
        byte_count=info.get("original_stream_size")
        if type(byte_count) is not int or byte_count<0:
            raise InventoryError("original_array_stream_size_unavailable")
        source_format=info.get("source_format_enum")
        required=array_payload_bytes(info["width"],info["height"],
            info["depth"],info["source_mipmap_count"],source_format)
        expected+=required
        if byte_count==0:
            absent+=info["depth"]
        elif byte_count!=required:
            raise InventoryError("original_array_BC3_full_mipmap_byte_extent_mismatch")
        else:
            populated+=info["depth"]
            present+=byte_count
    return {
        "schema":"GT_NINE_ORIGINAL_BC3_ARRAY_SOURCE_LAYOUT_V1",
        "source_arrays":len(arrays),
        "source_total_logical_layers":sum(v["depth"] for v in arrays.values()),
        "source_layers_with_original_stream_bytes":populated,
        "source_layers_without_original_stream_bytes":absent,
        "original_GPU_compressed_BC3_stream_bytes":present,
        "bytes_if_every_original_array_layer_had_payload":expected,
        "original_source_full_BC3_mip_extent_validated":True,
        "original_zero_stream_slices_are_untouched_not_fabricated":True,
        "source_array_layer_and_mip_order_proven":False,
        "Android_transcode_and_device_pixels_verified":False,
    }
