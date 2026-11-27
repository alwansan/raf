"""GT read-only Mesh -> ordered Renderer Material -> Shader/TexEnv identity.

Strict bounded candidate: triangle-list submeshes with inline indices and
UV0 descriptors. Unsupported topology/renderer/material scope is UNKNOWN,
never auto-repaired. V1 identity and V2 byte-binding APIs remain available;
CLI requires V4 same-route material keyword/pass state, values and bytes.
V3 remains a value-only API. No active-variant or GPU claim.
Private original source and three traces are never published.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import struct

from scripts.gt_stage_serialized_owners import OWNERS
from scripts.gt_zip2_payloads import manifest
from scripts.gt_original_material_link_graph import pointer as source_pointer, declared_external_owner
from scripts.gt_particle108_source_pixel_parity import verified_range, bounded_snapshot
from scripts.gt_next23b_unity_receipt import strict_json
from scripts import gt_mesh_vertex_payload as vertex_payload
from scripts import gt_material_route_values as material_value
from scripts import gt_material_route_keyword_state as material_keyword
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts.verify_exported_material_texture_links import is_texture, BUILTIN, ZERO, IMAGES
from scripts.b03_verify_renderer_material_links import GUID

CLASSES={1:"GameObject",21:"Material",23:"MeshRenderer",28:"Texture2D",
         33:"MeshFilter",43:"Mesh",48:"Shader",84:"RenderTexture",89:"Cubemap",
         117:"Texture3D",137:"SkinnedMeshRenderer",187:"Texture2DArray"}
TEX={28,84,89,117,187}
COMPONENTS={1,23,33,137}
RENDERERS={23,137}
NAMES={v:k for k,v in CLASSES.items()}
HEX=re.compile("[0-9a-f]{32}")
HEADER=re.compile(r"(?m)^--- !u!(\d+) &(-?\d+)(?: (stripped))?[ \t]*$")
WIDTHS={0:4,1:2,2:1,3:1,4:2,5:2,6:1,7:1,8:2,9:2,10:4,11:4}
CHANNELS=("stream","offset","format","dimension")
SUBMESH=("firstByte","indexCount","topology","baseVertex","firstVertex","vertexCount")
MAX_DOC=128*1024*1024
MAX_INDEX=16*1024*1024


class Unknown(ValueError):
    pass


class Drift(ValueError):
    pass


def require(test,code,cls=Drift):
    if not test:raise cls(code)


def mesh_layout(tree,exported=False):
    """Validate and retain exact ordered submesh ranges, indices and UV layout.

    No stride reconstruction or inferred UV samples. Compressed/unsupported
    index storage is explicitly outside this bounded test.
    """
    v=tree["m_VertexData"]
    n=v["m_VertexCount"]
    require(type(n) is int and 0<n<=16_000_000,"unsupported_vertex_count",Unknown)
    channels=v["m_Channels"]
    require(type(channels) is list and 5<=len(channels)<=32,"UV0_layout_missing",Unknown)
    layout=[]
    for ch in channels:
        row=tuple(ch[k] for k in CHANNELS)
        require(all(type(x) is int for x in row),"invalid_vertex_channel")
        stream,offset,fmt,dim=row
        require(0<=stream<16 and 0<=offset<=255 and 0<=dim<=4 and fmt in WIDTHS,
                "unsupported_vertex_channel",Unknown)
        layout.append(row)
    require(layout[4][3] in (2,3,4),"UV0_not_present",Unknown)
    fmt=tree["m_IndexFormat"]
    require(type(fmt) is int and fmt in (0,1),"unsupported_index_format",Unknown)
    raw=tree["m_IndexBuffer"]
    if exported:
        require(type(raw) is str and len(raw)<=2*MAX_INDEX and re.fullmatch("[0-9a-fA-F]+",raw),
                "unsupported_export_index_storage",Unknown)
        raw=bytes.fromhex(raw)
    else:
        require(type(raw) in (bytes,bytearray,list),"unsupported_source_index_storage",Unknown)
        raw=bytes(raw)
    width=2 if fmt==0 else 4
    require(0<len(raw)<=MAX_INDEX and len(raw)%width==0,"unsupported_index_payload",Unknown)
    rows=tree["m_SubMeshes"]
    require(type(rows) is list and 0<len(rows)<=256,"unsupported_submesh_count",Unknown)
    out=[]
    for row in rows:
        vals=tuple(row[k] for k in SUBMESH)
        require(all(type(x) is int and x>=0 for x in vals),"invalid_submesh_range")
        start,count,topology,base,first,length=vals
        require(topology==0,"non_triangle_list_submesh",Unknown)
        require(count>0 and count%3==0 and start%width==0 and
                start+count*width<=len(raw) and length>0 and first+length<=n,
                "invalid_submesh_range")
        for (index,) in struct.iter_unpack("<H" if fmt==0 else "<I",raw[start:start+count*width]):
            require(first<=index+base<first+length,"submesh_index_outside_vertex_range")
        out.append(vals)
    return n,tuple(layout),fmt,sha256(raw).hexdigest(),tuple(out)


def source_key(raw):
    require(type(raw) is dict and set(raw)=={"owner","path_id"},"malformed_trace_identity")
    owner,pid=raw["owner"],raw["path_id"]
    require(type(owner) is str and type(pid) is int and pid>0,"malformed_trace_identity")
    name=owner.rsplit("/",1)[-1]
    require(owner in (name,"Raft_Data/"+name),"ambiguous_trace_owner")
    return name,pid


def trace_pointer(raw):
    require(type(raw) is dict and set(raw)=={"file_id","guid","type"},"malformed_trace_pointer")
    fid,guid,kind=raw["file_id"],raw["guid"],raw["type"]
    require(type(fid) is int and fid!=0 and type(guid) is str and HEX.fullmatch(guid)
            and type(kind) is int and kind in (0,2,3),"malformed_trace_pointer")
    return guid,fid,kind


def traces(material,mesh,components):
    instance=material.get("export_instance")
    require(type(instance) is str and HEX.fullmatch(instance),"missing_export_instance")
    mapping={};reverse={}
    for trace,field,classes in ((material,"objects",{21,48}|TEX),(mesh,"meshes",{43}),
                                (components,"components",COMPONENTS)):
        require(type(trace.get("schema_version")) is int and trace["schema_version"]==1
                and trace.get("export_instance")==instance and type(trace.get(field)) is list,
                "mixed_or_invalid_export_instance")
        for row in trace[field]:
            cls=43 if field=="meshes" else row["class_id"]
            if cls not in classes:continue
            require(type(cls) is int,"malformed_trace_class")
            key=source_key(row["source"])
            require(key not in mapping,"duplicate_source_trace_identity")
            ptr=trace_pointer(row["export"])
            exportable=row.get("exportable")
            require(exportable is None or type(exportable) is bool,"invalid_trace_exportability")
            mapping[key]=(cls,ptr,exportable)
            if ptr[2] in (2,3) and ptr[0] not in {ZERO,*BUILTIN}:
                require(ptr[:2] not in reverse,"collapsed_export_document_identity")
                reverse[ptr[:2]]=key
    return mapping


def yaml_tree(body,cls):
    import yaml
    class Loader(yaml.SafeLoader):
        def construct_mapping(self,node,deep=False):
            out={}
            for k,v in node.value:
                key=self.construct_object(k,deep=deep)
                if key in out:raise Drift("duplicate_yaml_mapping_key")
                if key in {"guid","m_IndexBuffer","_typelessdata"} and isinstance(v,yaml.ScalarNode):
                    v.tag="tag:yaml.org,2002:str"
                elif cls==21 and isinstance(v,yaml.ScalarNode) and v.tag=="tag:yaml.org,2002:int" and v.value=="-0":
                    # Unity may emit binary32 negative zero as -0. Do not
                    # silently erase its sign; an int with this spelling is
                    # conservatively outside the strict material value gate.
                    v.tag="tag:yaml.org,2002:float"
                out[key]=self.construct_object(v,deep=deep)
            return out
    data=yaml.load(body,Loader=Loader)
    require(type(data) is dict and set(data)=={CLASSES[cls]} and
            type(data[CLASSES[cls]]) is dict,"export_document_class_root_mismatch")
    return data[CLASSES[cls]]


def actual_index(project,mapping):
    assets=Path(project)/"Assets"
    require(assets.is_dir() and not any(p.is_symlink() for p in (assets,*assets.parents)),
            "unsafe_export_project")
    entries=list(assets.rglob("*"))
    require(len(entries)<=250000 and not any(p.is_symlink() for p in entries),"unsafe_export_inventory")
    wanted={row[1][0] for row in mapping.values() if row[1][2] in (2,3)}
    files={};docs={}
    for path in entries:
        if not path.is_file() or path.suffix!=".meta":continue
        meta=bounded_snapshot(path,256*1024).decode("utf-8-sig")
        hits=GUID.findall(meta)
        if not set(h.lower() for h in hits)&wanted:continue
        require(len(hits)==1,"ambiguous_export_meta")
        guid=hits[0].lower()
        require(guid not in files,"duplicate_export_asset_guid")
        asset=path.with_suffix("")
        require(asset.is_file(),"missing_export_asset",Unknown)
        files[guid]=(asset,meta)
        if asset.suffix.lower() not in {".mat",".asset",".prefab",".unity",".cubemap",".rendertexture",".texture2d",".texture3d",".texture2darray"}:continue
        raw=bounded_snapshot(asset,MAX_DOC)
        if not raw.lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):continue
        text=raw.decode("utf-8-sig")
        heads=list(HEADER.finditer(text));seen=set()
        for i,h in enumerate(heads):
            cls,fid=int(h[1]),int(h[2])
            require(fid and fid not in seen,"duplicate_or_zero_export_anchor")
            seen.add(fid)
            if cls not in CLASSES or h[3]:continue
            if cls in {48,*TEX}:
                # Only actual native class/root; no texture bytes retained.
                body=text[h.end():heads[i+1].start() if i+1<len(heads) else len(text)]
                require(body.lstrip().startswith(CLASSES[cls]+":"),"export_document_class_root_mismatch")
                docs[(guid,fid)]=(cls,None)
            else:
                body=text[h.end():heads[i+1].start() if i+1<len(heads) else len(text)]
                tree=yaml_tree(body,cls)
                docs[(guid,fid)]=(cls,tree)
    return files,docs


def actual_pointer(raw,owner):
    require(type(raw) is dict and set(raw) in ({"fileID"},{"fileID","guid","type"}),"malformed_export_pptr")
    fid=raw["fileID"];guid=raw.get("guid",ZERO);kind=raw.get("type",0)
    require(type(fid) is int and type(guid) is str and HEX.fullmatch(guid) and type(kind) is int,
            "malformed_export_pptr")
    if fid==0:
        require(guid==ZERO and kind==0,"malformed_null_export_pptr")
        return None
    if guid==ZERO:
        require(kind==0,"invalid_local_pointer_type")
        return owner,fid,0
    require(kind in (2,3) and guid not in BUILTIN,"unsupported_builtin_or_pointer",Unknown)
    return guid,fid,kind


def src_target(owner,raw,externals):
    fid,pid=source_pointer(raw)
    if not pid:return None
    if not fid:return owner,pid
    table=externals[owner]
    require(fid<=len(table),"source_external_index_out_of_bounds")
    target=declared_external_owner(table[fid-1])
    require(target is not None,"unresolved_source_provider",Unknown)
    return target,pid


def source_records(root,records,owners,*,loader=None,vertex_payloads=None):
    """Parse the actual bytes matched to pinned manifest size and SHA."""
    if loader is None:
        import UnityPy
        loader=UnityPy.load
    objects={};externals={};requests={}
    for name in owners:
        _,size,digest=records["Raft_Data/"+name]
        raw=verified_range(root/name,(size,digest),0,size)
        env=loader(raw)
        externals[name]=[getattr(e,"path",None) for e in env.file.externals]
        for obj in env.file.objects.values():
            cls=NAMES.get(obj.type.name)
            if cls is None:continue
            key=(name,obj.path_id)
            require(type(key[1]) is int and key[1]>0 and key not in objects,"duplicate_source_identity")
            tree=obj.read_typetree() if cls not in {48,*TEX} else None
            if cls==43:
                if vertex_payloads is not None:
                    try:requests[key]=vertex_payload.source_request(tree)
                    except (KeyError,TypeError,ValueError,OverflowError) as e:
                        requests[key]=str(e) if type(e) is ValueError and re.fullmatch(r'[A-Za-z0-9_]+',str(e)) else 'unsupported_source_vertex_payload'
                try:tree=mesh_layout(tree)
                except (Unknown,Drift,KeyError,TypeError,ValueError):tree=None
            objects[key]=(cls,tree)
    if vertex_payloads is not None:
        require(not vertex_payloads,'fresh_vertex_payload_mapping_required')
        vertex_payloads.update(vertex_payload.resolve_requests(root,records,requests))
    return objects,externals


def compare(objects,externals,mapping,files,docs,*,vertex_payloads=None,material_values=False,material_keywords=False):
    require(not material_values or vertex_payloads is not None,"material_value_gate_requires_vertex_binding",Unknown)
    require(not material_keywords or material_values,"material_keyword_gate_requires_value_binding",Unknown)
    counts=Counter();reasons=Counter()
    filters=defaultdict(list)
    for key,(cls,tree) in objects.items():
        if cls==33:
            try:filters[src_target(key[0],tree["m_GameObject"],externals)].append(key)
            except (ValueError,KeyError,TypeError):counts["unresolved_source_mesh_filters"]+=1

    def source(key,classes):
        require(key in objects,"source_target_not_in_authenticated_scope",Unknown)
        cls,tree=objects[key]
        require(cls in classes,"source_target_wrong_class")
        return cls,tree

    def target(key,classes):
        cls,_=source(key,classes)
        require(key in mapping,"missing_source_export_trace",Unknown)
        traced,ptr,exportable=mapping[key]
        require(traced==cls,"trace_class_mismatch")
        require(exportable is True and ptr[2] in (2,3) and ptr[0] not in {ZERO,*BUILTIN},
                "unproven_exportable_global_target",Unknown)
        doc=docs.get(ptr[:2])
        if doc is not None:
            require(doc[0]==cls,"export_target_wrong_class")
            require(ptr[2]==2,"serialized_document_trace_type_mismatch")
            return ptr,doc[1]
        require(ptr[0] in files,"missing_actual_export_target",Unknown)
        path,meta=files[ptr[0]]
        require(path.stat().st_size>0,"empty_actual_export_target",Unknown)
        if cls==48:
            require(ptr[1]==4800000 and path.suffix==".shader" and
                    re.search(r"(?m)^ShaderImporter:[ \t]*$",meta),"shader_importer_identity_mismatch")
        elif cls in TEX:
            # Non-YAML images must have the expected native file ID/class.
            require(cls in (28,187) and path.suffix.lower() in IMAGES and ptr[1]==cls*100000
                    and is_texture(path,meta,ptr[1]),
                    "texture_importer_identity_mismatch")
        else:raise Unknown("missing_actual_serialized_target")
        return ptr,None

    def edge(source_owner,raw,export_owner,actual,classes):
        key=src_target(source_owner,raw,externals)
        observed=actual_pointer(actual,export_owner)
        if key is None:
            require(observed is None,"source_null_pointer_changed")
            return None
        ptr,_=target(key,classes)
        require(observed is not None and observed[:2]==ptr[:2] and
                observed[2] in (0,ptr[2]),"ordered_pointer_target_mismatch")
        return key

    def component_members(tree,exported=False):
        rows=tree.get("m_Component")
        require(type(rows) is list,"unsupported_gameobject_component_list",Unknown)
        out=[]
        for row in rows:
            require(type(row) is dict and set(row)=={"component"},"unsupported_component_entry",Unknown)
            out.append(row["component"])
        return out

    for key,(cls,tree) in objects.items():
        if cls not in RENDERERS:continue
        counts["source_renderers"]+=1
        try:
            rp,actual=target(key,{cls})
            go=edge(key[0],tree["m_GameObject"],rp[0],actual["m_GameObject"],{1})
            require(go is not None,"renderer_gameobject_missing")
            gp,gactual=target(go,{1})
            # A component is owned by its GameObject in the same serialized
            # document. A matching cross-document GUID/anchor is not a legal
            # substitute for the actual local hierarchy edge.
            require(rp[0]==gp[0],"renderer_gameobject_document_mismatch")
            require(actual_pointer(actual["m_GameObject"],rp[0])==(gp[0],gp[1],0),
                    "renderer_gameobject_not_local")
            _,gsource=source(go,{1})
            src_members=[src_target(go[0],p,externals) for p in component_members(gsource)]
            exp_members=[actual_pointer(p,gp[0]) for p in component_members(gactual,True)]
            require(src_members.count(key)==1 and exp_members.count((rp[0],rp[1],0))==1 and
                    sum(p is not None and p[:2]==rp[:2] for p in exp_members)==1,
                    "renderer_gameobject_membership_mismatch")
            if cls==23:
                candidates=filters.get(go,[])
                require(len(candidates)==1,"ambiguous_or_missing_source_mesh_filter",Unknown)
                fk=candidates[0];fp,fa=target(fk,{33})
                require(fp[0]==gp[0],"mesh_filter_gameobject_document_mismatch")
                require(src_members.count(fk)==1 and exp_members.count((fp[0],fp[1],0))==1 and
                        sum(p is not None and p[:2]==fp[:2] for p in exp_members)==1,
                        "mesh_filter_gameobject_membership_mismatch")
                _,ft=source(fk,{33})
                require(edge(fk[0],ft["m_GameObject"],fp[0],fa["m_GameObject"],{1})==go,
                        "mesh_filter_gameobject_mismatch")
                require(actual_pointer(fa["m_GameObject"],fp[0])==(gp[0],gp[1],0),
                        "mesh_filter_gameobject_not_local")
                mesh=edge(fk[0],ft["m_Mesh"],fp[0],fa["m_Mesh"],{43})
            else:mesh=edge(key[0],tree["m_Mesh"],rp[0],actual["m_Mesh"],{43})
            require(mesh is not None,"mesh_null_unproven",Unknown)
            mp,ma=target(mesh,{43});_,expected=source(mesh,{43})
            require(expected is not None,"unsupported_source_mesh_layout",Unknown)
            observed=mesh_layout(ma,True)
            require(expected==observed,"mesh_index_submesh_or_UV_layout_drift")
            counts["renderer_mesh_layouts_matched"]+=1
            if vertex_payloads is not None:
                proof=vertex_payloads.get(mesh)
                require(isinstance(proof,vertex_payload.Proof),
                        proof if type(proof) is str else "missing_same_route_vertex_payload",Unknown)
                try: actual_proof=vertex_payload.exported_proof(ma)
                except (KeyError,TypeError,ValueError,OverflowError) as exc:
                    raise Unknown(str(exc) if type(exc) is ValueError and re.fullmatch(r"[A-Za-z0-9_]+",str(exc))
                                  else "unsupported_export_vertex_payload") from None
                require((proof.length,proof.sha256)==(actual_proof.length,actual_proof.sha256),
                        "same_route_vertex_or_UV_bytes_drift")
                counts["renderer_vertex_payloads_matched"]+=1
            before,after=tree["m_Materials"],actual["m_Materials"]
            require(type(before) is list and type(after) is list,"invalid_material_slot_array")
            require(len(before)==len(after),"renderer_material_slot_count_drift")
            require(len(before)==len(expected[-1]),"non_one_to_one_submesh_material_policy",Unknown)
            for slot,(b,a) in enumerate(zip(before,after,strict=True)):
                mat=edge(key[0],b,rp[0],a,{21})
                require(mat is not None,"null_material_slot_unproven",Unknown)
                mptr,ma=target(mat,{21});_,ms=source(mat,{21})
                counts["ordered_material_slots_matched"]+=1
                shader=edge(mat[0],ms["m_Shader"],mptr[0],ma["m_Shader"],{48})
                require(shader is not None,"null_material_shader",Unknown)
                counts["material_shader_links_matched"]+=1
                btex=normalize_texenvs(ms["m_SavedProperties"]["m_TexEnvs"])
                atex=normalize_texenvs(ma["m_SavedProperties"]["m_TexEnvs"],exported=True)
                require(set(btex)==set(atex),"material_texenv_property_drift")
                for prop,(bp,uv) in btex.items():
                    ap,auv=atex[prop]
                    require(uv is not None and auv is not None,"missing_UV_transform",Unknown)
                    require(all(math.isclose(x,y,rel_tol=1e-6,abs_tol=1e-6) for x,y in zip(uv,auv,strict=True)),
                            "material_texenv_UV_drift")
                    tex=edge(mat[0],{"m_FileID":bp[0],"m_PathID":bp[1]},mptr[0],
                             {"fileID":ap[0],"guid":ap[1],"type":ap[2]},TEX)
                    counts["material_texenv_slots_matched"]+=1
                    counts["material_null_texture_slots_preserved"]+=int(tex is None)
                counts["complete_submesh_material_identity_routes"]+=1
                if material_values:
                    try: value_counts=material_value.compare(ms,ma)
                    except material_value.Unproven as exc:raise Unknown(str(exc)) from None
                    except material_value.Mismatch as exc:raise Drift(str(exc)) from None
                    for kind,total in value_counts.items():
                        counts["material_"+kind+"_slots_matched"]+=total
                    counts["complete_material_value_bound_submesh_routes"]+=1
                if material_keywords:
                    try: keyword_counts=material_keyword.compare(ms,ma)
                    except material_keyword.Unproven as exc:raise Unknown(str(exc)) from None
                    except material_keyword.Mismatch as exc:raise Drift(str(exc)) from None
                    for kind,total in keyword_counts.items():
                        counts["material_"+kind+"_entries_matched"]+=total
                    counts["complete_material_keyword_bound_submesh_routes"]+=1
            counts["complete_renderer_routes"]+=1
            if material_keywords:
                counts["complete_material_keyword_bound_renderer_routes"]+=1
            if material_values:
                counts["complete_material_value_bound_renderer_routes"]+=1
            if vertex_payloads is not None:
                counts["complete_vertex_byte_bound_renderer_routes"]+=1
                counts["complete_vertex_byte_bound_submesh_routes"]+=len(before)
        except Unknown as error:
            counts["unproven_renderer_routes"]+=1
            reasons[str(error)]+=1
        except Drift as error:
            counts["mismatched_renderer_routes"]+=1
            reasons[str(error)]+=1
        except (KeyError,TypeError,ValueError,AttributeError,OverflowError,struct.error):
            counts["unproven_renderer_routes"]+=1
            reasons["unsupported_private_object_layout"]+=1
    complete=bool(counts["source_renderers"]) and counts["complete_renderer_routes"]==counts["source_renderers"]
    byte_bound=vertex_payloads is not None and complete and (
        counts["complete_vertex_byte_bound_renderer_routes"]==counts["source_renderers"])
    value_bound=material_values and byte_bound and (
        counts["complete_material_value_bound_renderer_routes"]==counts["source_renderers"])
    keyword_bound=material_keywords and value_bound and (
        counts["complete_material_keyword_bound_renderer_routes"]==counts["source_renderers"])
    return {"schema_version":4 if material_keywords else 3 if material_values else 2 if vertex_payloads is not None else 1,
            "counts":dict(sorted(counts.items())),"reason_counts":dict(sorted(reasons.items())),
            "selected_renderer_routes_preserved":complete,
            "full_game_renderers_verified":False,
            "vertex_payload_or_UV_samples_verified":byte_bound,
            "selected_same_route_vertex_and_UV_bytes_verified":byte_bound,
            "selected_same_route_material_values_verified":value_bound,
            "selected_same_route_material_keyword_pass_state_verified":keyword_bound,
            "active_shader_variant_or_runtime_keyword_scope_verified":False,
            "UV_decoded_values_or_GPU_verified":False,
            "shader_program_color_scalar_or_GPU_parity_verified":False,"private_identifiers_published":False}


def audit(source,zip2,project,material_trace,mesh_trace,renderer_trace,owners):
    require(owners and len(owners)==len(set(owners)) and set(owners)<=set(OWNERS),"invalid_source_owner_scope")
    pins=manifest(zip2)
    payloads={}
    objects,externals=source_records(source,pins,owners,vertex_payloads=payloads)
    mapping=traces(*(strict_json(bounded_snapshot(p,MAX_DOC)) for p in (material_trace,mesh_trace,renderer_trace)))
    files,docs=actual_index(project,mapping)
    report=compare(objects,externals,mapping,files,docs,vertex_payloads=payloads,material_values=True,material_keywords=True)
    report["authenticated_selected_source_owners"]=len(owners)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ("source","zip2","project","material-trace","mesh-trace","renderer-trace","out"):
        p.add_argument("--"+field,type=Path,required=True)
    p.add_argument("--owner",action="append",required=True)
    a=p.parse_args()
    if a.out.exists() or any(a.out.resolve().is_relative_to(x.resolve()) for x in (a.source,a.zip2,a.project)):
        p.error("private source/export report boundary")
    try:
        report=audit(a.source,a.zip2,a.project,a.material_trace,a.mesh_trace,a.renderer_trace,a.owner)
    except Exception as exc:
        report={"schema_version":4,"status":"INCONCLUSIVE","error_type":type(exc).__name__,
                "selected_renderer_routes_preserved":False,"private_identifiers_published":False}
    with a.out.open("x") as f:json.dump(report,f,sort_keys=True,indent=2);f.write("\n")
    return 0 if report["selected_renderer_routes_preserved"] else 2


if __name__=="__main__":
    raise SystemExit(main())
