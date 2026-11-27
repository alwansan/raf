"""Bounded native inline RGBA32 Texture2D byte parity (no GPU/import claims).

Only one image, dimension Tex2D, finite positive explicit mip chain with
no stripping or streams. The source tree must come from the authenticated
owner snapshot; the export proof must come from its exact GUID/anchor.
"""
from dataclasses import dataclass
from hashlib import sha256
import re


MAX_BYTES=64*1024*1024
FIELDS=("m_Width","m_Height","m_TextureFormat","m_MipCount",
        "m_ImageCount","m_TextureDimension","m_CompleteImageSize")


class Unproven(ValueError):
    pass


class Mismatch(ValueError):
    pass


@dataclass(frozen=True)
class Proof:
    descriptor: tuple
    length: int
    sha256: str
    mip_lengths: tuple
    mip_sha256: tuple


def need(condition,reason):
    if not condition:
        raise Unproven(reason)


def proof(tree, *, exported=False):
    need(type(tree) is dict and all(k in tree for k in FIELDS),
         "missing_texture_descriptor")
    desc=tuple(tree[k] for k in FIELDS)
    need(all(type(x) is int for x in desc),"invalid_texture_descriptor")
    w,h,fmt,mips,images,dimension,size=desc
    need(0<w<=16384 and 0<h<=16384 and fmt==4 and images==1 and dimension==2,
         "unsupported_native_RGBA32_texture_layout")
    need(1<=mips<=max(w,h).bit_length(),"invalid_texture_mip_count")
    stripped=tree.get("m_MipsStripped",0)
    need(type(stripped) is int and stripped==0,"unsupported_stripped_texture_mips")
    lengths=tuple(4*max(1,w>>n)*max(1,h>>n) for n in range(mips))
    need(0<size<=MAX_BYTES and sum(lengths)==size,"texture_mip_size_mismatch")
    stream=tree.get("m_StreamData")
    need(type(stream) is dict and set(stream)=={"path","offset","size"},
         "missing_texture_stream_descriptor")
    # Unity YAML empty strings may be parsed as null; source must be explicit.
    path=stream["path"]
    need((path=="" or (exported and path is None)) and
         type(stream["offset"]) is int and stream["offset"]==0 and
         type(stream["size"]) is int and stream["size"]==0,
         "unsupported_texture_stream_payload")
    need("image data" in tree,"missing_texture_payload")
    raw=tree["image data"]
    if exported:
        need(type(raw) is int and raw==size,"texture_payload_length_mismatch")
        encoded=tree.get("_typelessdata")
        need(type(encoded) is str and len(encoded)==2*size and
             re.fullmatch(r"[0-9a-fA-F]+",encoded) is not None,
             "texture_payload_hex_or_length_mismatch")
        data=bytes.fromhex(encoded)
    else:
        need(type(raw) in (bytes,bytearray,list) and len(raw)==size,
             "texture_payload_length_mismatch")
        if type(raw) is list:
            need(all(type(x) is int and 0<=x<=255 for x in raw),"invalid_texture_payload_byte")
        data=bytes(raw)
    pos=0;digests=[]
    for length in lengths:
        digests.append(sha256(memoryview(data)[pos:pos+length]).hexdigest())
        pos+=length
    return Proof(desc,size,sha256(data).hexdigest(),lengths,tuple(digests))


def safe_proof(tree, *, exported=False):
    try:
        return proof(tree,exported=exported)
    except Unproven as exc:
        return str(exc)
    except (KeyError,TypeError,ValueError,OverflowError):
        return "unsupported_texture_payload_schema"


def compare(source,actual):
    need(isinstance(source,Proof),source if type(source) is str else "missing_source_texture_payload_proof")
    need(isinstance(actual,Proof),actual if type(actual) is str else "missing_native_export_texture_payload_proof")
    if source.descriptor!=actual.descriptor:
        raise Mismatch("same_route_texture_descriptor_drift")
    if (source.length,source.sha256,source.mip_lengths,source.mip_sha256)!=(
            actual.length,actual.sha256,actual.mip_lengths,actual.mip_sha256):
        raise Mismatch("same_route_texture_payload_bytes_drift")
    return source.length,len(source.mip_lengths)
