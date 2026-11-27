"""V6: explicit pinned flat resource range -> native inline mip proof.

Only direct Raft_Data .resS/.resource providers; archive/CAB aliases are
not guessed. Owner metadata must come from the same authenticated bytes.
All hashes (whole provider, whole texture, individual mips) originate in
one bounded sequential provider read. No implicit UnityPy stream lookup.
"""
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re

from scripts import gt_texture_route_payload as inline
from scripts.gt_mesh_vertex_payload import verified_range_digests
from scripts.gt_zip2_payloads import MAX_BYTES as MAX_PROVIDER


@dataclass(frozen=True)
class Request:
    descriptor: tuple
    mip_lengths: tuple
    provider: str
    offset: int


@dataclass(frozen=True)
class StreamProof:
    content: inline.Proof
    provider: str
    offset: int
    provider_size: int
    provider_sha256: str


def source_request(tree):
    desc,lengths=inline.descriptor(tree)
    path,offset,size=inline.stream_fields(tree)
    if path=="" and type(offset) is int and offset==0 and type(size) is int and size==0:
        return inline.proof(tree)
    inline.need(type(path) is str and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:resS|resource)",path)
                and ".." not in path,"unsupported_texture_stream_provider")
    inline.need(type(offset) is int and type(size) is int and offset>=0 and size==desc[-1]
                and offset+size<=MAX_PROVIDER,"invalid_texture_stream_extent")
    inline.need("image data" in tree,"missing_texture_payload")
    raw=tree["image data"]
    inline.need(type(raw) in (bytes,bytearray,list) and len(raw)==0,
                "ambiguous_inline_and_stream_texture_payload")
    return Request(desc,lengths,path,offset)


def safe_request(tree):
    try:
        return source_request(tree)
    except inline.Unproven as exc:
        return str(exc)
    except (KeyError,TypeError,ValueError,OverflowError):
        return "unsupported_texture_payload_schema"


def ranges(req):
    result=[(req.offset,req.descriptor[-1])]
    pos=req.offset
    for size in req.mip_lengths:
        result.append((pos,size))
        pos+=size
    return result


def resolve_requests(root,records,requests):
    """Resolve exact flat manifest identities; no raw resource bytes retained."""
    grouped=defaultdict(dict)
    result={}
    for key,value in requests.items():
        if isinstance(value,Request):
            grouped[value.provider][key]=value
        else:
            result[key]=value
    for provider,group in grouped.items():
        try:
            kind,size,digest=records["Raft_Data/"+provider]
        except KeyError:
            result.update((key,"texture_stream_provider_not_pinned") for key in group)
            continue
        if (kind not in ("plain","split") or type(size) is not int or not 0<size<=MAX_PROVIDER
                or type(digest) is not str or not re.fullmatch(r"[0-9a-f]{64}",digest)):
            result.update((key,"invalid_texture_stream_provider_pin") for key in group)
            continue
        valid={}
        for key,req in group.items():
            if req.offset+req.descriptor[-1]>size:
                result[key]="texture_stream_extent_out_of_bounds"
            else:
                valid[key]=req
        if not valid:continue
        try:
            hashes=verified_range_digests(Path(root)/provider,(size,digest),
                        [r for req in valid.values() for r in ranges(req)])
            for key,req in valid.items():
                all_ranges=ranges(req)
                content=inline.Proof(req.descriptor,req.descriptor[-1],hashes[all_ranges[0]],
                                     req.mip_lengths,tuple(hashes[r] for r in all_ranges[1:]))
                result[key]=StreamProof(content,provider,req.offset,size,digest)
        except (ValueError,OSError,TypeError) as exc:
            # Stable aggregate categories only; never provider names/paths.
            reason={"vertex_provider_SHA_mismatch":"texture_stream_provider_SHA_mismatch",
                    "vertex_provider_size_mismatch":"texture_stream_provider_size_mismatch",
                    "vertex_range_work_budget_exceeded":"texture_stream_work_budget_exceeded",
                    "invalid_vertex_range_population":"texture_stream_range_population_invalid"}.get(
                        str(exc),"unreadable_or_unproved_texture_stream_provider")
            result.update((key,reason) for key in valid)
    return result


def compare(source,actual):
    if isinstance(source,StreamProof):
        return inline.compare(source.content,actual)
    return inline.compare(source,actual)
