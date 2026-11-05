#!/usr/bin/env python3
"""T3 deterministic equivalent of pinned AssetRipperCLI TextureConverter.UnpackNormal.

Requires exact source m_LightmapFormat == TextureUsageMode.NormalmapDXT5nm
and m_TextureFormat DXT5 before callers compare the transformed *in-memory*
original decoded RGBA to the PNG exported by the SAME AssetRipper instance.
Never rewrite a game asset/PNG. This is not a GPU normal-map or sRGB test.

Pinned upstream source:
nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8
Source/AssetRipper.Export.Modules.Textures/TextureConverter.cs:
  byte r = pixelSpan[3], g = pixelSpan[1], a = pixelSpan[2];
  pixelSpan[2]=r; pixelSpan[3]=a;
  blue=(byte)((sqrt(255*255-min((r*2-255)^2+(g*2-255)^2,255*255))+255)/2)
DirectBitmap pixelSpan is BGRA; Pillow image channel order is RGBA.
"""
from __future__ import annotations

from functools import lru_cache
import math

MAX_PIXELS = 16384 * 16384
DXT5 = 12
NORMALMAP_DXT5NM = 3


@lru_cache(maxsize=1)
def _z_blue_table() -> bytes:
    """Byte-equivalent positive C# double square-root and (byte) truncation."""
    out=bytearray(256*256)
    mag=255*255
    for alpha in range(256):
        va=alpha*2-255
        for green in range(256):
            vg=green*2-255
            hs=min(va*va+vg*vg,mag)
            z=(math.sqrt(mag-hs)+255.0)/2.0
            out[(alpha<<8)|green]=int(z)
    return bytes(out)


def unpack_original_dxt5nm_rgba(image):
    """Exact BGRA UnpackNormal remapped into PIL RGBA, no input mutation."""
    from PIL import Image
    if not isinstance(image,Image.Image) or image.mode!="RGBA":
        raise ValueError("original_dxt5nm_requires_RGBA")
    width,height=image.size
    if width<=0 or height<=0 or width*height>MAX_PIXELS:
        raise ValueError("untrusted_original_DXT5nm_dimensions")
    original=image.tobytes()
    if len(original)!=width*height*4:
        raise ValueError("invalid_RGBA_image_bytes")
    z=_z_blue_table()
    output=bytearray(len(original))
    for pos in range(0,len(original),4):
        old_r,old_g,old_b,old_a=original[pos:pos+4]
        output[pos]=old_a                # new R from packed normal X in alpha
        output[pos+1]=old_g              # G preserved
        output[pos+2]=z[(old_a<<8)|old_g] # new B, reconstructed normal Z
        output[pos+3]=old_r              # new A from old red
    return Image.frombytes("RGBA",(width,height),bytes(output))


def semantic_rgba_input(decoded, *, format_code:int, color_space:int,
                        lightmap_format:int):
    """Transform only genuine original Gamma/DXT5nm, reject forged usage."""
    if (type(format_code) is not int or type(color_space) is not int
        or type(lightmap_format) is not int or color_space not in (0,1)
        or not 0<=lightmap_format<=11):
        raise ValueError("malformed_original_normalmap_usage")
    if lightmap_format==NORMALMAP_DXT5NM:
        if format_code!=DXT5 or color_space!=0:
            raise ValueError("unexpected_dxt5nm_original_codec_color_space")
        return unpack_original_dxt5nm_rgba(decoded)
    return decoded
