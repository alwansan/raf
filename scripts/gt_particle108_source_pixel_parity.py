"""Private Particle108 byte-bound source top mip and export pixel parity.

No source acquisition, implicit UnityPy stream lookup, saved texture, or
private identifiers in public results. Pixel comparison is decoded RGBA8
in top-left orientation; it is not Unity import, colorspace or GPU parity.
"""
from __future__ import annotations

import csv
from hashlib import sha1, sha256
from importlib.metadata import version as package_version
from io import BytesIO, StringIO
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
from types import SimpleNamespace

from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.gt_zip2_payloads import MANIFEST_BLOB, MAX_BYTES
from scripts.t3_original_texture_stream_dependencies import COLUMNS

MAX_OWNER = 128 * 1024 * 1024
MAX_PAYLOAD = 256 * 1024 * 1024
MAX_PIXELS = 16 * 1024 * 1024
CHUNK = 2 * 1024 * 1024
DECODER_VERSION = "1.23.0"
MODES = frozenset(("RGB", "RGBA", "L", "LA", "P"))


def regular_open(path):
    """Open without following leaf symlinks; reject linked input paths."""
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("pixel_input_symlink")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("pixel_input_not_single_regular_file")
        return os.fdopen(fd, "rb"), info.st_size
    except BaseException:
        os.close(fd)
        raise


def bounded_snapshot(path, limit):
    stream, size = regular_open(path)
    with stream:
        if not 0 < size <= limit:
            raise ValueError("pixel_input_size_out_of_bounds")
        data = stream.read(size + 1)
        if len(data) != size:
            raise ValueError("pixel_input_size_changed")
    return data


def verified_range(path, pin, offset, length):
    """Digest and capture the requested bytes in the SAME sequential read.

    Large providers stay bounded in memory; no separate post-hash seek or
    decoder-driven resource search can substitute a different byte range.
    """
    if (type(pin) is not tuple or len(pin)!=2 or type(pin[0]) is not int
            or not 0 < pin[0] <= MAX_BYTES or type(pin[1]) is not str
            or not re.fullmatch("[0-9a-f]{64}",pin[1])
            or type(offset) is not int or type(length) is not int
            or offset<0 or not 0<length<=MAX_PAYLOAD or offset+length>pin[0]):
        raise ValueError("invalid_pinned_pixel_byte_range")
    stream,size=regular_open(path)
    digest=sha256()
    chunks=[]
    pos=0
    with stream:
        if size!=pin[0]:
            raise ValueError("pinned_pixel_provider_size_mismatch")
        while pos<size:
            block=stream.read(min(CHUNK,size-pos))
            if not block:
                raise ValueError("pinned_pixel_provider_truncated")
            digest.update(block)
            end=pos+len(block)
            lo,hi=max(pos,offset),min(end,offset+length)
            if lo<hi:
                chunks.append(block[lo-pos:hi-pos])
            pos=end
        if stream.read(1) or pos!=pin[0] or digest.hexdigest()!=pin[1]:
            raise ValueError("pinned_pixel_provider_SHA_mismatch")
    data=b"".join(chunks)
    if len(data)!=length:
        raise ValueError("pinned_pixel_range_capture_mismatch")
    return data


def authenticated_provider_pins(manifest):
    """Use the immutable ZIP2 manifest blob, not an arbitrary caller's pins."""
    raw=bounded_snapshot(manifest,1024*1024)
    if sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()!=MANIFEST_BLOB:
        raise ValueError("pixel_manifest_git_blob_mismatch")
    rows=csv.DictReader(StringIO(raw.decode("utf-8-sig"),newline=""),delimiter="\t")
    if tuple(rows.fieldnames or ())!=COLUMNS:
        raise ValueError("pixel_manifest_schema_mismatch")
    pins={}
    for row in rows:
        rel=row.get("relative_path_under_Raft")
        if not isinstance(rel,str) or not rel.startswith("Raft_Data/") or not rel.endswith((".resS",".resource")):
            continue
        # The authorized staging layout places these providers directly
        # under Raft_Data; never resolve arbitrary/recursive basename aliases.
        parts=rel.split("/")
        if (len(parts)!=2 or not parts[1] or "\\" in rel or parts[1] in (".","..")
                or parts[1] in pins):
            raise ValueError("pixel_manifest_provider_ambiguous")
        size=int(row["bytes"])
        digest=row["sha256"]
        if not 0<size<=MAX_BYTES or not re.fullmatch("[0-9a-f]{64}",digest):
            raise ValueError("pixel_manifest_provider_pin_invalid")
        pins[parts[1]]=(size,digest)
    if not pins:
        raise ValueError("pixel_manifest_provider_missing")
    return pins


def exact_payload(texture, original_data, manifest):
    """Resolve inline OR explicit authenticated stream, never both."""
    inline=texture.image_data
    if type(inline) not in (bytes,bytearray,memoryview):
        raise ValueError("unsupported_inline_texture_payload")
    inline=bytes(inline)
    raw=getattr(texture,"m_StreamData",None)
    if raw is None:
        path,offset,size="",0,0
    else:
        path,offset,size=raw.path,raw.offset,raw.size
    if (type(path) is not str or type(offset) is not int or type(size) is not int
            or offset<0 or size<0):
        raise ValueError("invalid_texture_stream_descriptor")
    if not path and not offset and not size:
        if not 0<len(inline)<=MAX_PAYLOAD:
            raise ValueError("missing_or_oversize_inline_texture")
        return inline,"inline"
    if inline or not path or not size:
        raise ValueError("ambiguous_inline_stream_texture")
    normalized=path.replace("\\","/")
    parts=normalized.split("/")
    if any(p in ("",".","..") for p in parts) or not parts[-1].endswith((".resS",".resource")):
        raise ValueError("unsupported_texture_stream_path")
    # Unity commonly uses archive:/CAB-.../name.resS. No absolute filesystem
    # or traversal resolution; a unique pinned provider name is sufficient.
    if len(parts)>1 and parts[0]!="archive:":
        raise ValueError("unsupported_texture_stream_path")
    name=PurePosixPath(normalized).name
    pins=authenticated_provider_pins(manifest)
    if name not in pins:
        raise ValueError("texture_stream_provider_not_pinned")
    return verified_range(original_data/name,pins[name],offset,size),"stream"


def validate_decoded_image(image):
    if (image.mode not in MODES or not 0<image.width*image.height<=MAX_PIXELS
            or getattr(image,"n_frames",1)!=1):
        raise ValueError("unsupported_decoded_texture_image")
    image.load()
    return image


def decode_payload(texture, payload):
    """Call the pinned public UnityPy decoder through an explicit byte adapter.

    The adapter has no assets_file, resource reader, or stream descriptor.
    It only exposes the authenticated data and decode metadata. No mutation
    of the original Texture2D, even in memory, is necessary.
    """
    if package_version("UnityPy")!=DECODER_VERSION:
        raise ValueError("texture_decoder_version_mismatch")
    from UnityPy.export.Texture2DConverter import get_image_from_texture2d
    width,height=texture.m_Width,texture.m_Height
    if (type(width) is not int or type(height) is not int
            or not 0<width*height<=MAX_PIXELS or width<=0 or height<=0
            or texture.m_TextureDimension!=2 or texture.m_ImageCount!=1
            or getattr(texture,"m_MipsStripped",0) not in (None,0)
            or type(texture.m_MipCount) is not int or texture.m_MipCount<1):
        raise ValueError("unproven_original_texture_top_mip")
    reader=texture.object_reader
    adapter=SimpleNamespace(m_Width=width,m_Height=height,m_TextureFormat=texture.m_TextureFormat,
                            m_PlatformBlob=getattr(texture,"m_PlatformBlob",None),
                            object_reader=SimpleNamespace(version=reader.version,platform=reader.platform),
                            image_data=payload,get_image_data=lambda:payload)
    image=validate_decoded_image(get_image_from_texture2d(adapter,flip=True))
    if image.size!=(width,height):
        raise ValueError("decoded_original_top_mip_size_mismatch")
    return image


def decode_original_texture(original, manifest, key, *, loader=None):
    """Authenticate the exact serialized owner bytes used by the parser."""
    if (type(key) is not tuple or len(key)!=2 or key[0] not in SHADER_OWNERS
            or type(key[1]) is not int or key[1]<=0):
        raise ValueError("unverified_original_texture_identity")
    owner,pid=key
    pin=SHADER_OWNERS[owner]
    if pin[0]>MAX_OWNER:
        raise ValueError("original_owner_over_byte_budget")
    root=Path(original)/"Raft_Data"
    raw=verified_range(root/owner,pin,0,pin[0])
    if loader is None:
        if package_version("UnityPy")!=DECODER_VERSION:
            raise ValueError("texture_decoder_version_mismatch")
        import UnityPy
        loader=UnityPy.load
    # The parser receives the authenticated bytes, NOT a filename that it
    # could reopen after hashing. The explicit payload decoder cannot resolve
    # external resources independently.
    env=loader(raw)
    matches=[obj for obj in env.file.objects.values() if obj.path_id==pid]
    if len(matches)!=1 or matches[0].type.name!="Texture2D":
        raise ValueError("authenticated_source_not_unique_Texture2D28")
    texture=matches[0].read()
    payload,kind=exact_payload(texture,root,manifest)
    return decode_payload(texture,payload),kind


def read_export_png(path):
    """Limit parity proof to explicit 8-bit PNG top-left decoded samples."""
    from PIL import Image
    raw=bounded_snapshot(path,MAX_PAYLOAD)
    if (len(raw)<33 or raw[:8]!=b"\x89PNG\r\n\x1a\n"
            or raw[8:16]!=b"\0\0\0\rIHDR" or raw[24]!=8):
        raise ValueError("export_pixel_parity_requires_8bit_PNG")
    width,height=struct.unpack(">II",raw[16:24])
    if not 0<width*height<=MAX_PIXELS:
        raise ValueError("export_pixel_dimensions_out_of_bounds")
    with Image.open(BytesIO(raw)) as image:
        if image.format!="PNG" or image.getexif().get(274,1)!=1:
            raise ValueError("export_pixel_orientation_not_canonical")
        validate_decoded_image(image)
        if image.size!=(width,height):
            raise ValueError("export_png_header_size_mismatch")
        return image.convert("RGBA")


def compare_pixels(source, exported):
    """Compare exact coordinates, no histogram matching, resizing or flip search."""
    from PIL import Image,ImageChops
    validate_decoded_image(source)
    validate_decoded_image(exported)
    if source.size!=exported.size:
        return {"dimensions_match":False,"alpha_samples_equal":False,"rgb_samples_equal":False,
                "rgba8_samples_equal":False,"alpha_loss_pixels":0,
                "pixel_coordinates_compared":0,"alpha_mismatch_pixels":0,"rgb_mismatch_pixels":0,
                "alpha_increased_pixels":0,"alpha_decreased_pixels":0,
                "alpha_vertical_flip_only_match":False}
    a,b=source.convert("RGBA"),exported.convert("RGBA")
    n=a.width*a.height
    ar,ag,ab,aa=a.split();br,bg,bb,ba=b.split()
    alpha_diff=ImageChops.difference(aa,ba)
    rgb_diff=ImageChops.lighter(ImageChops.lighter(ImageChops.difference(ar,br),
                           ImageChops.difference(ag,bg)),ImageChops.difference(ab,bb))
    alpha_mismatch=n-alpha_diff.histogram()[0]
    rgb_mismatch=n-rgb_diff.histogram()[0]
    increase=n-ImageChops.subtract(ba,aa).histogram()[0]
    decrease=n-ImageChops.subtract(aa,ba).histogram()[0]
    # Strict evidence: a formerly nonopaque source pixel became fully opaque.
    lost=ImageChops.multiply(aa.point([255]*255+[0]),ba.point([0]*255+[255]))
    return {"dimensions_match":True,"pixel_coordinates_compared":n,
            "alpha_samples_equal":alpha_mismatch==0,"rgb_samples_equal":rgb_mismatch==0,
            "rgba8_samples_equal":alpha_mismatch==0 and rgb_mismatch==0,
            "alpha_mismatch_pixels":alpha_mismatch,"rgb_mismatch_pixels":rgb_mismatch,
            "alpha_increased_pixels":increase,"alpha_decreased_pixels":decrease,
            "alpha_loss_pixels":lost.histogram()[255],
            "alpha_vertical_flip_only_match":bool(alpha_mismatch and
                not ImageChops.difference(aa,ba.transpose(Image.Transpose.FLIP_TOP_BOTTOM)).getbbox())}


def external_parity(original,manifest,selected,routes,index):
    """Only exact independent PPtr joins authorize a source/export comparison."""
    keys=[key for key,route in routes.items() if route["pointer"][2] in (2,3)
          and selected.get(key)==route["pointer"]]
    counters=dict(independently_traced_external_targets=len(keys),targets_decoded=0,
                  source_inline_targets=0,source_stream_targets=0,dimension_mismatch_targets=0,
                  coordinate_compared_targets=0,exact_alpha_targets=0,exact_rgb_targets=0,
                  exact_rgba8_targets=0,targets_with_alpha_loss=0,targets_with_alpha_flip_only=0,
                  coordinates_compared=0,alpha_mismatch_pixels=0,rgb_mismatch_pixels=0,
                  alpha_increased_pixels=0,alpha_decreased_pixels=0,alpha_loss_pixels=0,
                  targets_unavailable=0)
    for key in keys:
        try:
            source,kind=decode_original_texture(original,manifest,key)
            path=index[routes[key]["pointer"][1]][0]
            exported=read_export_png(path)
            row=compare_pixels(source,exported)
        except (OSError,ValueError,TypeError,AttributeError,KeyError,ImportError,NotImplementedError,RuntimeError):
            counters["targets_unavailable"]+=1
            continue
        counters["targets_decoded"]+=1
        counters["source_"+kind+"_targets"]+=1
        counters["dimension_mismatch_targets"]+=int(not row["dimensions_match"])
        counters["coordinate_compared_targets"]+=int(row["dimensions_match"])
        for result,field in (("exact_alpha_targets","alpha_samples_equal"),("exact_rgb_targets","rgb_samples_equal"),
                             ("exact_rgba8_targets","rgba8_samples_equal"),("targets_with_alpha_flip_only","alpha_vertical_flip_only_match")):
            counters[result]+=int(row[field])
        counters["targets_with_alpha_loss"]+=int(row["alpha_loss_pixels"]>0)
        counters["coordinates_compared"]+=row["pixel_coordinates_compared"]
        for field in ("alpha_mismatch_pixels","rgb_mismatch_pixels","alpha_increased_pixels",
                      "alpha_decreased_pixels","alpha_loss_pixels"):
            counters[field]+=row[field]
    return {**counters,"all_independently_traced_external_alpha_samples_equal":bool(keys and counters["exact_alpha_targets"]==len(keys)),
            "all_independently_traced_external_RGBA8_samples_equal":bool(keys and counters["exact_rgba8_targets"]==len(keys)),
            "sample_policy":"decoded_RGBA8_top_left_exact_coordinates_no_color_transform",
            "original_or_exported_pixels_published":False,"Unity_import_or_GPU_parity_proven":False}
