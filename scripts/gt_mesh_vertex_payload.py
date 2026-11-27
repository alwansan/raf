"""Bounded vertex/UV byte evidence; no acquisition or GPU claims.

The route gate accepts only uncompressed, contiguous single-stream layouts
with float32 XYZ and UV0. Provider range hashes and the full provider SHA
are derived from the same sequential read, never a verify-then-seek cache.
"""
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from scripts.gt_particle108_source_pixel_parity import regular_open, CHUNK, MAX_PAYLOAD
from scripts.gt_zip2_payloads import MAX_BYTES

WIDTHS = {0:4,1:2,2:1,3:1,4:2,5:2,6:1,7:1,8:2,9:2,10:4,11:4}


@dataclass(frozen=True)
class Proof:
    length: int
    sha256: str
    storage: str
    # Internal provenance only; never included in aggregate reports.
    provider: str = ""
    offset: int = 0
    provider_size: int = 0
    provider_sha256: str = ""


@dataclass(frozen=True)
class Request:
    provider: str
    offset: int
    length: int


def need(test, reason):
    if not test:
        raise ValueError(reason)


def supported_length(tree):
    v = tree["m_VertexData"]
    n, ch = v["m_VertexCount"], v["m_Channels"]
    need(type(n) is int and 0 < n <= 16_000_000 and type(ch) is list
         and 5 <= len(ch) <= 32, "unsupported_vertex_payload_layout")
    need(ch[0] == {"stream":0,"offset":0,"format":0,"dimension":3}
         and ch[4]["format"] == 0 and ch[4]["dimension"] in (2,3,4),
         "unsupported_position_or_UV0_payload")
    intervals = []
    for row in ch:
        s,o,f,d = (row[k] for k in ("stream","offset","format","dimension"))
        need(all(type(x) is int for x in (s,o,f,d)) and 0 <= d <= 4
             and 0 <= o <= 255 and f in WIDTHS, "unsupported_vertex_payload_layout")
        if d:
            need(s == 0, "unsupported_multi_vertex_stream_layout")
            intervals.append((o,o+d*WIDTHS[f]))
    stride = 0
    for lo,hi in sorted(intervals):
        need(lo == stride, "unsupported_vertex_channel_overlap_or_gap")
        stride = hi
    size = n*stride
    need(0 < size <= MAX_PAYLOAD, "unsupported_vertex_payload_size")
    cm = tree["m_CompressedMesh"]
    need(type(cm) is dict and type(cm.get("m_UVInfo")) is int and cm["m_UVInfo"] == 0
         and tree.get("m_MeshCompression",0) == 0, "unsupported_compressed_vertex_payload")
    for value in cm.values():
        if isinstance(value, dict):
            need(type(value.get("m_NumItems")) is int and value["m_NumItems"] == 0
                 and value.get("m_Data") in (None,"",[],b""),
                 "unsupported_compressed_vertex_payload")
    return size


def inline_bytes(raw):
    need(type(raw) in (list, bytes, bytearray), "unsupported_source_vertex_storage")
    need(len(raw) <= MAX_PAYLOAD, "unsupported_vertex_payload_size")
    return bytes(raw)


def stream_descriptor(tree):
    s = tree["m_StreamData"]
    name, offset, size = s["path"], s["offset"], s["size"]
    need((name is None or type(name) is str) and type(offset) is int and type(size) is int
         and offset >= 0 and size >= 0, "invalid_vertex_stream_descriptor")
    if not name and offset == 0 and size == 0:
        return None
    need(bool(name) and re.fullmatch(r"[A-Za-z0-9_.-]+\.resS",name) is not None
         and 0 < size <= MAX_PAYLOAD, "unsupported_vertex_stream_provider")
    return Request(name,offset,size)


def source_request(tree):
    size = supported_length(tree)
    raw = inline_bytes(tree["m_VertexData"]["m_DataSize"])
    stream = stream_descriptor(tree)
    if stream is None:
        need(len(raw) == size, "source_vertex_payload_size_mismatch")
        return Proof(size,sha256(raw).hexdigest(),"inline")
    need(not raw, "ambiguous_inline_and_stream_vertex_payload")
    need(stream.length == size, "source_vertex_payload_size_mismatch")
    return stream


def exported_proof(tree):
    size = supported_length(tree)
    need(stream_descriptor(tree) is None, "unbound_export_vertex_stream")
    v = tree["m_VertexData"]
    encoded = v["_typelessdata"]
    need(type(v["m_DataSize"]) is int and v["m_DataSize"] == size
         and type(encoded) is str and len(encoded) == size*2
         and re.fullmatch(r"[0-9a-fA-F]+",encoded) is not None,
         "export_vertex_payload_size_or_hex_mismatch")
    return Proof(size,sha256(bytes.fromhex(encoded)).hexdigest(),"exported_inline")


def verified_range_digests(path,pin,ranges,*,captures=None):
    """Hash any number of declared ranges during one authenticated read.

    Memory is bounded by one block and per-range digest state. Nothing is
    returned until full SHA, size and all captured lengths are verified.
    """
    size, expected = pin
    need(type(size) is int and 0 < size <= MAX_BYTES and type(expected) is str
         and re.fullmatch(r"[0-9a-f]{64}",expected) is not None,
         "invalid_vertex_provider_pin")
    ranges = sorted(set(ranges))
    need(0 < len(ranges) <= 100_000, "invalid_vertex_range_population")
    for offset,length in ranges:
        need(type(offset) is int and type(length) is int and offset >= 0
             and 0 < length <= MAX_PAYLOAD and offset+length <= size,
             "invalid_vertex_provider_range")
    need(sum(length for _,length in ranges) <= 4*size, "vertex_range_work_budget_exceeded")
    # Optional bounded capture, published only after full provider authentication.
    need(captures is None or (type(captures) is dict and not captures and
         sum(length for _,length in ranges)<=64*1024*1024),"invalid_range_capture_budget")
    captured=None if captures is None else {r:bytearray() for r in ranges}
    full = sha256()
    states = {r:[sha256(),0] for r in ranges}
    active = []
    idx = pos = 0
    handle, actual_size = regular_open(path)
    with handle:
        need(actual_size == size,"vertex_provider_size_mismatch")
        while pos < size:
            block = handle.read(min(CHUNK,size-pos))
            need(bool(block),"vertex_provider_truncated")
            full.update(block)
            end = pos+len(block)
            while idx < len(ranges) and ranges[idx][0] < end:
                active.append(ranges[idx])
                idx += 1
            for r in active:
                off,length = r
                lo,hi = max(pos,off),min(end,off+length)
                if lo < hi:
                    piece=memoryview(block)[lo-pos:hi-pos]
                    states[r][0].update(piece)
                    if captured is not None:captured[r].extend(piece)
                    states[r][1] += hi-lo
            active = [r for r in active if r[0]+r[1] > end]
            pos = end
        need(not handle.read(1) and pos == size and full.hexdigest() == expected,
             "vertex_provider_SHA_mismatch")
    need(all(states[r][1] == r[1] for r in ranges),"vertex_range_capture_mismatch")
    if captured is not None:captures.update((r,bytes(data)) for r,data in captured.items())
    return {r:states[r][0].hexdigest() for r in ranges}


def resolve_requests(root,records,requests):
    """Bind internal mesh identities to inline or verified range proofs."""
    result = {}
    grouped = defaultdict(dict)
    for key,value in requests.items():
        if isinstance(value,Request):
            grouped[value.provider][key] = value
        else:
            result[key] = value
    for name,group in grouped.items():
        try:
            _,size,digest = records["Raft_Data/"+name]
            # A malformed extent must not poison other unrelated providers.
            valid = {}
            for key,req in group.items():
                if req.offset+req.length > size:
                    result[key] = "invalid_vertex_provider_range"
                else:
                    valid[key] = req
            if not valid:
                continue
            hashes = verified_range_digests(Path(root)/name,(size,digest),
                                            [(r.offset,r.length) for r in valid.values()])
            for key,r in valid.items():
                result[key] = Proof(r.length,hashes[(r.offset,r.length)],"stream",
                                    name,r.offset,size,digest)
        except KeyError:
            for key in group:
                result[key] = "unbound_source_vertex_stream"
        except (ValueError,OSError,TypeError) as exc:
            # No paths, SHA, identifiers or data in outward error messages.
            reason = str(exc) if type(exc) is ValueError and re.fullmatch(
                r"[A-Za-z0-9_]+",str(exc)) else "unreadable_vertex_provider"
            for key in group:
                result[key] = reason
    return result
