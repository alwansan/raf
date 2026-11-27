#!/usr/bin/env python3
"""Read-only residual ShaderLab GUID fanout of ONE exported Assets namespace.

A name digest is not a GUID. Count documents, serialized slots and distinct
Renderer anchors separately. Do not resolve prefab instances, native shader
programs, original source identity, GPU or pixels. All identifiers stay private.
The whole-scope commitment detects byte changes, not producer authenticity.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import stat
import os
import yaml

from scripts import verify_exported_material_texture_links as registry
from scripts.b03_verify_renderer_material_links import RENDERERS
from scripts.restore_builtin_shaders import exported_shader_identity

SUFFIXES={".mat",".asset",".unity",".prefab"}
GUID=re.compile(r"[a-fA-F0-9]{32}\Z")
HEAD=re.compile(r"---[ \t]+!u!([0-9]{1,10})[ \t]+&(-?[0-9]{1,19})(?:[ \t]+(stripped))?[ \t]*\Z")
ROOTS={21:"Material",48:"Shader",**{int(k):v for k,v in RENDERERS.items()}}
MAX_FILE=128*1024*1024
MAX_DOCS=2_000_000
MAX_SLOTS=4096
STATUS="GT_EXACT_EXPORTED_SHADER_GUID_FANOUT_ONLY"

def need(ok,code):
    if not ok:raise ValueError(code)

def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")

def snapshot(path,limit):
    fd=os.open(path,os.O_RDONLY | getattr(os,"O_NOFOLLOW",0) | getattr(os,"O_CLOEXEC",0) | getattr(os,"O_NONBLOCK",0))
    with os.fdopen(fd,"rb") as f:
        a=os.fstat(f.fileno())
        need(stat.S_ISREG(a.st_mode) and a.st_size<=limit,"bounded_regular_input")
        b=f.read(limit+1)
        z=os.fstat(f.fileno())
        need(len(b)==a.st_size<=limit and (a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_size,z.st_mtime_ns,z.st_ctime_ns),"unstable_input")
    return b

class UniqueLoader(yaml.BaseLoader):
    def compose_node(self,parent,index):
        need(not self.check_event(yaml.AliasEvent),"yaml_alias_unsupported")
        return super().compose_node(parent,index)
    def construct_mapping(self,node,deep=False):
        d={}
        for k,v in node.value:
            key=self.construct_object(k,deep=deep)
            need(type(key) is str and key not in d,"duplicate_or_invalid_yaml_key")
            d[key]=self.construct_object(v,deep=deep)
        return d

def document(body,cls):
    d=yaml.load(body,Loader=UniqueLoader)
    need(type(d) is dict and set(d)=={ROOTS[cls]} and type(d[ROOTS[cls]]) is dict,
         "typed_document_root")
    return d[ROOTS[cls]]

def integer(raw):
    need(type(raw) is str and re.fullmatch(r"-?(0|[1-9][0-9]{0,18})",raw),"pointer_integer")
    v=int(raw)
    need(-(1<<63)<=v<(1<<63) and str(v)==raw,"pointer_integer")
    return v

def pointer(p,owner):
    need(type(p) is dict and set(p) in ({"fileID"},{"fileID","guid","type"}),"pointer_shape")
    fid=integer(p["fileID"])
    g=p.get("guid",registry.ZERO)
    t=integer(p.get("type","0"))
    need(type(g) is str and GUID.fullmatch(g),"pointer_guid")
    g=g.lower()
    if not fid:
        need(g==registry.ZERO and t==0,"ambiguous_null_pointer")
        return "null",None
    if g==registry.ZERO:
        need(t==0,"invalid_local_pointer_type")
        return "local",(owner,fid)
    if g in registry.BUILTIN:
        return ("builtin" if t==0 and fid>0 else "unsupported"),None
    if g in registry.RESERVED_META_GUIDS:
        return "unsupported",None
    if t==2:return "native",(g,fid)
    if t==3:return "importer",(g,fid)
    return "unsupported",None

def scan(project):
    root=Path(project).absolute()
    need(not any(p.is_symlink() for p in (root,*root.parents)),"unsafe_project")
    assets=root/"Assets"
    need(assets.is_dir() and not assets.is_symlink(),"missing_assets")
    files,dirs=registry.physical_entries(assets)
    digest=hashlib.sha256(b"GT_FANOUT_SNAPSHOT_V1\0")
    committed=0
    def read(path,limit):
        nonlocal committed
        raw=snapshot(path,limit)
        # Private relative path and exact-byte digest enter only the combined
        # scope commitment, not individual public identifiers or per-edge hashes.
        digest.update(canonical([path.relative_to(assets).as_posix(),len(raw),hashlib.sha256(raw).hexdigest()])+b"\n")
        committed+=1
        return raw
    targets={}
    owners={}
    for path in sorted(files):
        if not path.name.lower().endswith(".meta"):continue
        need(path.name.endswith(".meta"),"noncanonical_meta_suffix")
        text=read(path,4*1024*1024).decode("utf-8-sig").replace("\r\n","\n")
        g,folder=registry.meta_identity(text)
        asset=path.with_name(path.name[:-5])
        need(g not in targets and g not in registry.RESERVED_META_GUIDS,"duplicate_or_reserved_meta_guid")
        need((asset in dirs and folder) or (asset in files and not folder and not asset.name.lower().endswith(".meta")),"invalid_meta_target")
        targets[g]=(asset,folder,text)
        if not folder:owners[asset]=g
    shaders={}
    native_shaders=set()
    materials={}
    renderers={}
    counts=Counter()
    total_docs=0
    for p in sorted(files):
        suffix=p.suffix.lower()
        if suffix not in SUFFIXES|{".shader"}:continue
        need(p in owners,"missing_candidate_meta")
        owner=owners[p]
        raw=read(p,8*1024*1024 if suffix==".shader" else MAX_FILE)
        if suffix==".shader":
            meta=targets[owner][2]
            need(len(re.findall(r"(?m)^ShaderImporter:[ \t]*$",meta))==1,
                 "shader_importer_meta_required")
            text=raw.decode("utf-8-sig")
            name=exported_shader_identity(text)
            need(isinstance(name,str) and bool(name),"missing_shader_identity")
            # Exact old AssetRipper marker is classification only; absence is
            # not source authenticity, compiled parity or readiness.
            shaders[owner]=(name,"dummy" if "//DummyShaderTextExporter" in text else "non_dummy")
            continue
        if not raw.lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
            need(suffix!=".mat","non_yaml_material")
            counts["non_yaml_candidate_files"]+=1
            continue
        text=raw.decode("utf-8-sig").replace("\r\n","\n")
        heads=list(re.finditer(r"(?m)^---[^\n]*$",text))
        need(heads and len(heads)<=MAX_DOCS-total_docs,"missing_or_excessive_yaml_documents")
        seen=set()
        for i,h in enumerate(heads):
            m=HEAD.fullmatch(h.group())
            need(m is not None,"malformed_yaml_document_header")
            cls,fid=int(m[1]),integer(m[2])
            need(fid and fid not in seen,"duplicate_or_zero_yaml_anchor")
            seen.add(fid)
            total_docs+=1
            if cls not in ROOTS:continue
            if m[3]:
                counts["stripped_relevant_documents"]+=1
                if str(cls) in RENDERERS:counts["stripped_renderer_documents"]+=1
                continue
            body=text[h.end():heads[i+1].start() if i+1<len(heads) else len(text)]
            key=(owner,fid)
            if cls==48:
                need(body.lstrip().startswith("Shader:\n"),"typed_native_shader_root")
                native_shaders.add(key)
                continue
            obj=document(body,cls)
            if cls==21:
                materials[key]=pointer(obj.get("m_Shader"),owner)
            else:
                slots=obj.get("m_Materials")
                need(type(slots) is list and len(slots)<=MAX_SLOTS,"missing_or_excessive_material_slots")
                renderers[key]=(suffix,[pointer(x,owner) for x in slots])
    need(materials and renderers,"missing_materials_or_renderer_population")
    material_classes={}
    groups=defaultdict(lambda:{"material_documents":0,"renderer_slots":0,"scene_slots":0,"prefab_slots":0,"other_slots":0,"renderer_objects":0,"exclusive_dummy_renderer_objects":0})
    for key,(kind,target) in materials.items():
        cls,sg="unresolved_or_unsupported_shader",None
        if kind=="null":cls="null_shader"
        elif kind=="builtin":cls="builtin_shader_unverified"
        elif kind=="importer" and target[1]==4800000 and target[0] in shaders:
            sg=target[0]
            cls=shaders[sg][1]
            if cls=="dummy":groups[sg]["material_documents"]+=1
        elif kind in ("local","native") and target in native_shaders:
            cls="native_shader_document_unverified"
        material_classes[key]=(cls,sg)
        counts["material_"+cls]+=1
    for key,(suffix,slots) in renderers.items():
        saw=set()
        unknown=False
        for kind,target in slots:
            counts["renderer_slots"]+=1
            if kind=="null":cls="null_material"
            elif kind=="builtin":cls="builtin_material_unverified"
            elif kind not in ("local","native"):cls="unsupported_material_pointer"
            elif target not in material_classes:cls="unresolved_material"
            else:
                counts["renderer_slots_resolved_native_material"]+=1
                cls,sg=material_classes[target]
                if cls=="dummy":
                    g=groups[sg]
                    g["renderer_slots"]+=1
                    g[{".unity":"scene_slots"}.get(suffix,"prefab_slots" if suffix==".prefab" else "other_slots")]+=1
                    saw.add(sg)
            counts["slot_"+cls]+=1
            if cls not in ("dummy","non_dummy"):unknown=True
        for sg in saw:groups[sg]["renderer_objects"]+=1
        if saw:counts["renderers_with_dummy_slots"]+=1
        if len(saw)==1 and not unknown:
            groups[next(iter(saw))]["exclusive_dummy_renderer_objects"]+=1
        if len(saw)>1:counts["renderers_with_multiple_dummy_targets"]+=1
        if unknown:counts["renderers_with_unverified_slots"]+=1
    # Slot count, distinct Renderer count, then document count. Tie order is
    # deterministic but not a semantic priority; no GUID emitted in safe output.
    def score(g):return (-g["renderer_slots"],-g["renderer_objects"],-g["material_documents"])
    ranked=sorted(groups.items(),key=lambda kv:(score(kv[1]),kv[0]))
    name_counts=Counter(shaders[g][0] for g in groups)
    need(sum(v["material_documents"] for v in groups.values())==counts["material_dummy"] and
         sum(v["renderer_slots"] for v in groups.values())==counts["slot_dummy"],"fanout_accounting")
    report={"status":STATUS,"schema":1,"snapshot_commitment_sha256":digest.hexdigest(),
        "committed_files":committed,"registered_guids":len(targets),
        "material_documents":len(materials),"renderer_documents":len(renderers),
        "dummy_shader_guid_targets":len(groups),"dummy_shader_name_groups":len(name_counts),
        "shared_name_groups":sum(n>1 for n in name_counts.values()),
        "dummy_targets_without_serialized_renderer_use":sum(not v["renderer_slots"] for v in groups.values()),
        "rank_order":"renderer_slots_desc_then_distinct_renderer_documents_desc_then_material_documents_desc",
        "ranked_anonymous_targets":[v for _,v in ranked],
        "counts":dict(sorted(counts.items())),
        "source_shader48_identity_proven":False,"prefab_instance_expansion_proven":False,
        "shader_program_or_runtime_variant_proven":False,"gpu_or_white_mesh_repair_proven":False,
        "snapshot_is_signed_producer_attestation":False,"production_install_allowed":False}
    return report,ranked

def compare_receipt(current,previous):
    need(type(previous) is dict and canonical(current)==canonical(previous),"different_export_snapshot_or_report")

def unique_json(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,"duplicate_receipt_key")
        out[k]=v
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("project",type=Path)
    p.add_argument("--expected-receipt",type=Path)
    a=p.parse_args()
    try:
        report,_=scan(a.project)
        if a.expected_receipt:
            old=json.loads(snapshot(a.expected_receipt,4*1024*1024),object_pairs_hook=unique_json)
            compare_receipt(report,old)
        print(json.dumps(report,sort_keys=True))
    except (ValueError,OSError,yaml.YAMLError,RecursionError,UnicodeError) as e:
        # No private paths, data, GUID or parser traceback in public CLI output.
        print(json.dumps({"status":"INCONCLUSIVE","error_type":type(e).__name__,"production_install_allowed":False}))
        raise SystemExit(2)

if __name__=="__main__":main()
