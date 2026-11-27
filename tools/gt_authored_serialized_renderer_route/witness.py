#!/usr/bin/env python3
"""Independently authored multi-object v22 binary -> public exporter -> route gate.

No original files, C# asset construction, injected typetree loader or generated
YAML baseline. Shader is an identity-only authored empty program; not a GPU proof.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
import struct
import tempfile
from unittest.mock import patch
import warnings

from tools.gt_authored_mesh_binary import witness as w
from tools.gt_authored_mesh_actual_export import witness as old
from scripts import gt_renderer_submesh_routes as route
from scripts import gt_verify_original_mesh_export as mesh
from scripts import gt_material_route_values as values

OWNER="authored.assets"
VERSION=(2021,3,0,1)
PIN="036098ab525a3f9f693dc101edeb21faad4d32d8"
IDS={101:1,102:4,103:33,104:23,201:1,202:4,203:33,204:23,
     801:48,811:21,812:21,821:28,901:43,902:43}
SLOTS={104:[811,812],204:[812,811]}
MESHES={103:901,203:902}
TEXTURE=bytes((255,0,0,255,0,255,0,128,0,0,255,64,255,255,0,0))

def dump(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")

def schema(cls):
    return w.get_typetree_node(cls,VERSION)

def fields(node):
    return {n.m_Name:n for n in w.children(node)}

def pptr(pid):
    return {"m_FileID":0,"m_PathID":pid}

def xyz(x,y,z):
    return dict(x=x,y=y,z=z)

def uv(x,y):
    return dict(x=x,y=y)

def choose(node, data, optional):
    # Required authored fields must be present; only irrelevant defaults may
    # vary with public schema version.
    keys=fields(node)
    w.need(set(data)<=set(keys),"required_schema_field_missing:"+node.m_Name+":"+repr(set(data)-set(keys)))
    data.update({k:v for k,v in optional.items() if k in keys})
    return data

def fixture(*,swap_material=False,swap_mesh=False,uv_drift=False):
    schemas={cls:schema(cls) for cls in sorted(set(IDS.values()))}
    objects={}
    for base in (100,200):
        go,tr,flt,ren=(base+i for i in (1,2,3,4))
        objects[go]=choose(schemas[1],{"m_Name":"GT Authored Root "+str(base),
          "m_Component":[{"component":pptr(i)} for i in (tr,flt,ren)]},
          {"m_IsActive":True,"m_Layer":0,"m_Tag":0})
        objects[tr]=choose(schemas[4],{"m_GameObject":pptr(go),"m_LocalRotation":dict(x=0.,y=0.,z=0.,w=1.),
          "m_LocalPosition":xyz(0.,0.,0.),"m_LocalScale":xyz(1.,1.,1.),"m_Children":[],"m_Father":pptr(0)}, {})
        mesh_id=MESHES[flt] if not(swap_mesh and flt==103) else 902
        objects[flt]={"m_GameObject":pptr(go),"m_Mesh":pptr(mesh_id)}
        slots=list(SLOTS[ren])
        if swap_material and ren==104:slots.reverse()
        objects[ren]=choose(schemas[23],{"m_GameObject":pptr(go),"m_Materials":[pptr(i) for i in slots]},
          {"m_Enabled":True,"m_CastShadows":1,"m_ReceiveShadows":True})
    shader=fields(schemas[48])
    w.need("m_ParsedForm" in shader and "m_Name" in fields(shader["m_ParsedForm"]),"shader_name_schema")
    objects[801]=choose(schemas[48],{"m_ParsedForm":{"m_Name":"GT/AuthoredRouteIdentityOnly"}},{"m_Name":"GT Authored Shader Identity"})
    for pid in (811,812):
        tint=dict(r=.125,g=.25,b=.75,a=1.) if pid==811 else dict(r=.875,g=.5,b=.125,a=.5)
        saved={"m_TexEnvs":[("_MainTex",{"m_Texture":pptr(821 if pid==811 else 0),
                                      "m_Scale":uv(1.5,.75),"m_Offset":uv(.125,.25)})],
               "m_Colors":[("_Color",tint)],"m_Floats":[("_Glossiness",.25 if pid==811 else .75)]}
        saved_node=fields(schemas[21])["m_SavedProperties"]
        if "m_Ints" in fields(saved_node):saved["m_Ints"]=[("_Mode",1 if pid==811 else 2)]
        objects[pid]=choose(schemas[21],{"m_Name":"GT Authored Material "+str(pid),
                    "m_Shader":pptr(801),"m_SavedProperties":saved},{"m_CustomRenderQueue":-1})
    tex=schemas[28]; tk=fields(tex)
    image=[k for k in ("image data","m_ImageData") if k in tk]
    w.need(len(image)==1,"unsupported_texture_image_schema")
    objects[821]=choose(tex,{"m_Name":"GT Authored RGBA","m_Width":2,"m_Height":2,
          "m_TextureFormat":4,image[0]:list(TEXTURE)},
          {"m_CompleteImageSize":len(TEXTURE),"m_MipCount":1,"m_ImageCount":1,
           "m_TextureDimension":2,"m_IsReadable":True,"m_ColorSpace":0,
           "m_TextureSettings":{"m_FilterMode":0,"m_Aniso":1,"m_MipBias":0.0}})
    for pid in (901,902):
        raw=list(w.VERTICES)+[-1.,-1.,0.,.25,.25, 2.,-1.,0.,.75,.25, 2.,1.,0.,.75,.875]
        if pid==902:raw[3]=.375
        if uv_drift and pid==901:raw[3]=.625
        vb=struct.pack("<30f",*raw);ib=struct.pack("<6H",0,1,2,3,4,5)
        f=old.supported(schemas[43],raw=vb,indices=ib)
        f["m_Name"]="GT Authored Mesh "+str(pid)
        f["m_VertexData"]["m_VertexCount"]=6
        sub=deepcopy(f["m_SubMeshes"][0]);sub.update(firstByte=6,indexCount=3,firstVertex=3,vertexCount=3)
        f["m_SubMeshes"].append(sub)
        aabb={"m_Center":xyz(0.,.5,0.),"m_Extent":xyz(2.,1.5,.25)}
        if "m_LocalAABB" in f:f["m_LocalAABB"]=deepcopy(aabb)
        for row in f["m_SubMeshes"]:
            if "localAABB" in row:row["localAABB"]=deepcopy(aabb)
        objects[pid]=f
    w.need(set(objects)==set(IDS),"missing_authored_objects")
    return schemas,objects

def serialize(schemas,objects):
    # One actual SerializedFile with independent object table and unique IDs.
    classes=sorted(schemas); data=bytearray(); rows=[]
    for pid in sorted(objects):
        cls=IDS[pid];payload=bytearray()
        w.encode_node(schemas[cls],objects[pid],payload)
        w.pad(data,8);off=len(data);data.extend(payload)
        rows.append({"path_id":pid,"class_id":cls,"offset":off,**w.commit(bytes(payload))})
    meta=bytearray(w.UNITY.encode("ascii")+b"\0")
    meta.extend(struct.pack("<i?i",13,False,len(classes)))
    for cls in classes:meta.extend(struct.pack("<i?h",cls,False,-1)+bytes(16))
    meta.extend(struct.pack("<i",len(rows)))
    for row in rows:
        w.pad(meta,4)
        meta.extend(struct.pack("<qqIi",row["path_id"],row["offset"],row["bytes"],classes.index(row["class_id"])))
    meta.extend(struct.pack("<iii",0,0,0)+b"\0")
    start=(48+len(meta)+15)&~15
    header=struct.pack(">IIII",0,0,22,0)+b"\0"*4+struct.pack(">Iqqq",len(meta),start+len(data),start,0)
    return header+meta+bytes(start-48-len(meta))+data,rows

def records(source):
    raw=(source/OWNER).read_bytes()
    return {"Raft_Data/"+OWNER:w.pin(raw)}

def prepare(out):
    out.mkdir(parents=True,exist_ok=False)
    (out/"source").mkdir()
    schemas,objects=fixture()
    dump(out/"public-schemas.json",{cls:w.schema_rows(node) for cls,node in schemas.items()})
    raw,rows=serialize(schemas,objects)
    (out/"source"/OWNER).write_bytes(raw)
    dump(out/"input.json",{"owner":w.commit(raw),"objects":rows,"shader_scope":"identity only, empty authored program",
                           "expected_renderer_slots":SLOTS,"expected_filter_meshes":MESHES})
    env=w.UnityPy.load(raw)
    w.need(set(env.file.objects)==set(IDS),"actual_decoder_object_table_mismatch")
    # Check independent authored local PPtrs on real decoder data before export.
    for pid,cls in IDS.items():
        obj=env.file.objects[pid]
        w.need(obj.type.value==cls,"actual_decoder_class_mismatch")
        tree=obj.read_typetree()
        if cls==23:w.need(tree["m_Materials"]==[pptr(i) for i in SLOTS[pid]],"actual_decoder_material_order")
        if cls==33:w.need(tree["m_Mesh"]==pptr(MESHES[pid]),"actual_decoder_mesh_pointer")
    print("GT_SERIALIZED_ROUTE_INPUT",w.commit(raw),"objects",len(rows),flush=True)

def patch_host(root,cs):
    helper=root/"ar-host/Source/AssetRipper.Export.UnityProjects/RaftExportLineage.cs"
    s=helper.read_text()
    mark="internal static class RaftExportLineage\n{"
    w.need(s.count(mark)==1,"missing_lineage_class")
    s=s.replace(mark,mark+"\n    internal static Dictionary<long,IUnityObjectBase>? AuthoredLoadedRoute;")
    mark='                Identity(json, "source", asset);'
    w.need(s.count(mark)==3,"unexpected_lineage_identity_sites")
    # Insert scope before each record's WriteStartObject, not inside JSON.
    mark="                json.WriteStartObject();"
    w.need(s.count(mark)==3,"unexpected_lineage_record_sites")
    s=s.replace(mark,"""                if (asset.Collection.Name != "authored.assets")
                    continue;
                if (AuthoredLoadedRoute is null || !AuthoredLoadedRoute.TryGetValue(asset.PathID,out var loaded) ||
                    !ReferenceEquals(loaded,asset))
                    throw new InvalidDataException("Exported authored object reference differs from actual loaded object");
"""+mark+'\n                json.WriteBoolean("authored_loaded_reference_equal", true);')
    helper.write_text(s)
    shutil.copyfile(cs,helper.with_name("RaftAuthoredSerializedRendererRoute.cs"))
    (root/"android-port/Experiments/ExportLineage/Program.cs").write_text(
        "using AssetRipper.Export.UnityProjects;\nRaftAuthoredSerializedRendererRoute.Run(args);\n")

def load_traces(out):
    material,meshes,components=(json.loads((out/n).read_text()) for n in
      ("export-trace.json","mesh-trace.json","renderer-trace.json"))
    rows=[(x["source"]["path_id"],x) for trace,key in
          ((material,"objects"),(meshes,"meshes"),(components,"components")) for x in trace[key]]
    wanted={pid for pid,cls in IDS.items() if cls!=4}
    w.need(len(rows)==len(wanted) and {pid for pid,_ in rows}==wanted,"trace_population_mismatch")
    w.need(all(x["source"]["owner"]==OWNER and x["authored_loaded_reference_equal"] is True and
               x["exportable"] is True for _,x in rows),"actual_loaded_reference_not_exported")
    return material,meshes,components,route.traces(material,meshes,components)

def retain(project,out,mapping):
    # Only exact traced authored assets/meta. Excludes injected engine files,
    # exporter-generated support scripts, and any unrelated resources.
    files,docs=route.actual_index(project,mapping)
    target=out/"actual-export"/"Assets";target.mkdir(parents=True,exist_ok=False)
    for guid,(path,_) in files.items():
        dest=target/path.relative_to(project/"Assets")
        dest.parent.mkdir(parents=True,exist_ok=True)
        for p,d in ((path,dest),(path.with_name(path.name+".meta"),dest.with_name(dest.name+".meta"))):
            shutil.copyfile(p,d)
            w.need(p.read_bytes()==d.read_bytes(),"retained_bytes_drift")
    return target.parent

def compare(source,project,mapping,*,material_values=False):
    payloads={}
    objects,externals=route.source_records(source,records(source),(OWNER,),vertex_payloads=payloads)
    files,docs=route.actual_index(project,mapping)
    return route.compare(objects,externals,mapping,files,docs,vertex_payloads=payloads,material_values=material_values)

def controls(source,project,mapping):
    result=[]
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);d=root/"source";d.mkdir()
        for name,opts,reason in (
            ("actual_binary_material_order",{"swap_material":True},"ordered_pointer_target_mismatch"),
            ("actual_binary_mesh_reference",{"swap_mesh":True},"ordered_pointer_target_mismatch"),
            ("actual_binary_uv_bytes",{"uv_drift":True},"same_route_vertex_or_UV_bytes_drift")):
            raw,_=serialize(*fixture(**opts))
            (d/OWNER).write_bytes(raw)
            got=compare(d,project,mapping)
            w.need(not got["selected_renderer_routes_preserved"] and got["reason_counts"]=={reason:1},
                   name+":"+repr(got))
            result.append({"name":name,"source_owner":w.commit(raw),"report":got})
        # Actual exported prefab bytes mutated, no authored YAML baseline.
        files,docs=route.actual_index(project,mapping)
        rptr=mapping[(OWNER,104)][1]
        mptr=mapping[(OWNER,811)][1]; other=mapping[(OWNER,812)][1]
        prefab=files[rptr[0]][0]; orig=prefab.read_bytes()
        text=orig.decode("utf-8-sig")
        w.need(mptr[0]!=other[0],"material_guids_not_distinct")
        w.need(text.count(mptr[0])==1 and text.count(other[0])==1,"ambiguous_material_guid_mutation")
        try:
            text=text.replace(mptr[0],"@"*32).replace(other[0],mptr[0]).replace("@"*32,other[0])
            prefab.write_text(text)
            got=compare(source,project,mapping)
            w.need(not got["selected_renderer_routes_preserved"] and
                   got["reason_counts"]=={"ordered_pointer_target_mismatch":1},"actual_export_material_swap_accepted")
            result.append({"name":"actual_export_material_guid_order","report":got})
        finally:prefab.write_bytes(orig)
        # Same valid traced file but wrong exact fileID.
        bad=dict(mapping); cls,ptr,exportable=bad[(OWNER,901)]
        bad[(OWNER,901)]=(cls,(ptr[0],ptr[1]+1,ptr[2]),exportable)
        got=compare(source,project,bad)
        w.need(not got["selected_renderer_routes_preserved"],"wrong_mesh_fileid_accepted")
        result.append({"name":"wrong_mesh_trace_fileid","report":got})
    return result

def verify(out,project):
    pin=json.loads((out/"input.json").read_text())
    raw=json.loads((out/"raw-parser.json").read_text())
    typed=json.loads((out/"typed-load.json").read_text())
    w.need(raw["generation"]==22 and raw["owner"]==OWNER and raw["embedded_type_tree"] is False and
           raw["owner_sha256"]==pin["owner"]["sha256"],"raw_parser_owner_mismatch")
    w.need(sorted(raw["objects"],key=lambda x:x["path_id"])==
           [{k:v for k,v in row.items() if k!="offset"} for row in pin["objects"]],"raw_parser_payload_commitments")
    w.need({x["path_id"]:x["class_id"] for x in typed["objects"]}==IDS and
           all(x["typed"] and x["serialized_collection"] and x["owner"]==OWNER for x in typed["objects"]),
           "actual_typed_population_mismatch")
    w.need(w.commit((out/"source"/OWNER).read_bytes())==pin["owner"],"source_mutated")
    mat,mtrace,ctrace,mapping=load_traces(out)
    saved=retain(project,out,mapping)
    proofs=[]
    boost=w.TypeTreeHelper.read_typetree_boost
    w.need(callable(boost),"compiled_decoder_missing")
    for backend,cb in (("compiled",boost),("python",False)):
        with patch.object(w.TypeTreeHelper,"read_typetree_boost",cb):
            report=compare(out/"source",saved,mapping)
            geometry=mesh.inspect(out/"source",records(out/"source"),saved,mtrace,mat["export_instance"],owners=(OWNER,))
            # Separate non-vacuous material-value scope; if a schema field is
            # absent report measured unproven rather than invent it.
            value=compare(out/"source",saved,mapping,material_values=True)
        c=report["counts"]
        w.need(report["selected_same_route_vertex_and_UV_bytes_verified"] and
               c.get("complete_renderer_routes")==2 and c.get("complete_vertex_byte_bound_submesh_routes")==4 and
               c.get("material_shader_links_matched")==4 and c.get("material_texenv_slots_matched")==4 and
               c.get("material_null_texture_slots_preserved")==2,"actual_route_gate_failed:"+repr(report))
        w.need(geometry["all_source_mesh_geometry_matches"] and geometry["counts"]["matched_mesh_geometry"]==2,
               "actual_mesh_consumer_mismatch:"+repr(geometry))
        proofs.append({"decoder":backend,"route":report,"mesh":geometry,"material_values":value})
    neg=controls(out/"source",saved,mapping)
    w.need(len(neg)==5,"negative_population")
    emitted={str(p.relative_to(saved)):w.commit(p.read_bytes()) for p in sorted(saved.rglob("*")) if p.is_file()}
    dump(out/"report.json",{"status":"PASS_ACTUAL_AUTHORED_SERIALIZED_RENDERER_ROUTE","public_exporter_pin":PIN,
        "actual_raw_objects":14,"actual_typed_objects":14,"same_loaded_reference_traces":len(mapping),
        "proofs":proofs,"negative_controls":neg,"emitted":emitted,"actual_source_binary":True,
        "actual_yaml_export":True,"authored_yaml_used_as_export":False,"shader_program_verified":False,
        "original_assets_read":False,"original_renderer_routes_verified":False,
        "unity_import_verified":False,"device_verified":False,"XAPK_requested":False})
    print("GT_ACTUAL_ROUTE_PASS",len(proofs),"renderer_routes_per_decoder",2,"submeshes_per_decoder",4,
          "negative_controls",len(neg),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("prepare","patch-host","verify"))
    p.add_argument("--out",type=Path);p.add_argument("--project",type=Path)
    p.add_argument("--root",type=Path);p.add_argument("--cs",type=Path)
    a=p.parse_args()
    if a.mode=="prepare":prepare(a.out)
    elif a.mode=="patch-host":patch_host(a.root,a.cs)
    else:verify(a.out,a.project)
