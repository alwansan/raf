#!/usr/bin/env python3
"""Four real authored v22 files, colliding PathIDs and independent external tables.

Use prior independent public TPK struct encoder, never original game bytes.
Native consumer unmodified; no loader injection, generated source objects,
or substitute YAML. Shader identity-only, PNG identity-only.
"""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import shutil
import struct
import tempfile
from unittest.mock import patch

from tools.gt_authored_mesh_binary import witness as w
from tools.gt_authored_serialized_renderer_route import witness as local
from scripts import gt_renderer_submesh_routes as route
from scripts import gt_verify_original_mesh_export as mesh

ROOT_A,ROOT_B,PROV_A,PROV_B=OWNERS=tuple(f"sharedassets{i}.assets" for i in range(30,34))
ROOT_IDS={101:1,102:4,103:33,104:23}
PROV_IDS={801:48,811:21,821:28,901:43}
IDS={ROOT_A:ROOT_IDS,ROOT_B:ROOT_IDS,PROV_A:PROV_IDS,PROV_B:PROV_IDS}
TABLES={ROOT_A:[PROV_A,PROV_B],ROOT_B:[PROV_B,PROV_A],PROV_A:[PROV_B],PROV_B:[PROV_A]}
PIN=local.PIN

def ptr(fid,pid):
    return {"m_FileID":fid,"m_PathID":pid}

def fixture():
    schemas,prior=local.fixture()
    roots={ROOT_A:{pid:deepcopy(prior[pid]) for pid in ROOT_IDS},
           ROOT_B:{pid:deepcopy(prior[pid+100]) for pid in ROOT_IDS}}
    for name,objects in roots.items():
        if name==ROOT_B:
            objects[101]["m_Component"]=[{"component":ptr(0,p)} for p in (102,103,104)]
            for pid in (102,103,104):objects[pid]["m_GameObject"]=ptr(0,101)
        objects[103]["m_Mesh"]=ptr(1,901)
        objects[104]["m_Materials"]=[ptr(1,811),ptr(2,811)]
    for name,oldmesh,oldmat,suffix in ((PROV_A,901,811,"A"),(PROV_B,902,812,"B")):
        objects={801:deepcopy(prior[801]),811:deepcopy(prior[oldmat]),
                 821:deepcopy(prior[821]),901:deepcopy(prior[oldmesh])}
        for pid,obj in objects.items():
            if "m_Name" in obj:obj["m_Name"]="GT External "+str(pid)+" "+suffix
        objects[801]["m_ParsedForm"]["m_Name"]="GT/ExternalIdentity"+suffix
        objects[811]["m_Shader"]=ptr(1,801)
        objects[811]["m_SavedProperties"]["m_TexEnvs"][0][1]["m_Texture"]=ptr(1,821)
        if name==PROV_B:
            image=next(k for k in ("image data","m_ImageData") if k in objects[821])
            objects[821][image]=list(reversed(local.TEXTURE))
        roots[name]=objects
    return schemas,roots

def external_bytes(name):
    # Unity v22 FileIdentifier: empty cached AssetPath, zero synthetic GUID,
    # kind 0 (path-based), NUL-terminated provider name. Never original GUIDs.
    return b"\0"+bytes(16)+struct.pack("<i",0)+name.encode("ascii")+b"\0"

def serialize(schemas,ids,objects,external_names):
    classes=sorted(set(ids.values()));data=bytearray();rows=[]
    for pid in sorted(objects):
        cls=ids[pid];payload=bytearray()
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
    meta.extend(struct.pack("<ii",0,len(external_names)))
    for name in external_names:meta.extend(external_bytes(name))
    meta.extend(struct.pack("<i",0)+b"\0")
    start=(48+len(meta)+15)&~15
    header=struct.pack(">IIII",0,0,22,0)+b"\0"*4+struct.pack(">Iqqq",len(meta),start+len(data),start,0)
    return header+meta+bytes(start-48-len(meta))+data,rows

def records(source):
    return {"Raft_Data/"+name:w.pin((source/name).read_bytes()) for name in OWNERS}

def edge(owner,pid,fid,target_pid,cls,tables=TABLES):
    return dict(owner=owner,path_id=pid,file_id=fid,target_owner=tables[owner][fid-1],
                target_path_id=target_pid,target_class_id=cls)

def expected_edges():
    rows=[]
    for owner in (ROOT_A,ROOT_B):
        rows.extend((edge(owner,103,1,901,43),edge(owner,104,1,811,21),edge(owner,104,2,811,21)))
    for owner in (PROV_A,PROV_B):
        rows.extend((edge(owner,811,1,801,48),edge(owner,811,1,821,28)))
    return rows

def write_source(source,schemas,objects,tables):
    source.mkdir(parents=True,exist_ok=True);pins={}
    for name in OWNERS:
        raw,rows=serialize(schemas,IDS[name],objects[name],tables[name])
        (source/name).write_bytes(raw)
        pins[name]={"owner":w.commit(raw),"objects":rows,"externals":tables[name]}
    return pins

def prepare(out):
    out.mkdir(parents=True,exist_ok=False)
    schemas,objects=fixture()
    pins=write_source(out/"source",schemas,objects,TABLES)
    local.dump(out/"input.json",{"owners":pins,"expected_edges":expected_edges(),
              "scope":"four authored owners; repeated PathIDs; zero GUID path-based external records"})
    local.dump(out/"public-schemas.json",{cls:w.schema_rows(node) for cls,node in schemas.items()})
    observed=[]
    for name in OWNERS:
        raw=(out/"source"/name).read_bytes()
        env=w.UnityPy.load(raw);file=env.file
        w.need(file.header.version==22 and set(file.objects)==set(IDS[name]),"actual_decoder_object_table")
        w.need([x.path for x in file.externals]==TABLES[name],"actual_decoder_external_table")
        for pid,cls in IDS[name].items():
            obj=file.objects[pid];w.need(obj.type.value==cls,"actual_decoder_class")
            tree=obj.read_typetree()
            if cls==33:w.need(tree["m_Mesh"]==ptr(1,901),"actual_mesh_external_pptr")
            if cls==23:w.need(tree["m_Materials"]==[ptr(1,811),ptr(2,811)],"actual_material_external_order")
            if cls==21:
                w.need(tree["m_Shader"]==ptr(1,801),"actual_shader_external_pptr")
                from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
                tex=normalize_texenvs(tree["m_SavedProperties"]["m_TexEnvs"])
                w.need(tex["_MainTex"][0]==(1,821),"actual_texture_external_pptr")
            observed.append({"owner":name,"path_id":pid,"class_id":cls,"raw":w.commit(obj.get_raw_data())})
        print("GT_EXTERNAL_OWNER",name,pins[name]["owner"],TABLES[name],flush=True)
    local.dump(out/"decoder-preflight.json",observed)

def patch_host(root,cs):
    helper=root/"ar-host/Source/AssetRipper.Export.UnityProjects/RaftExportLineage.cs"
    s=helper.read_text()
    mark="internal static class RaftExportLineage\n{"
    w.need(s.count(mark)==1,"missing_lineage_class")
    s=s.replace(mark,mark+"\n    internal static Dictionary<(string,long),IUnityObjectBase>? AuthoredLoadedExternalRoute;")
    mark="                json.WriteStartObject();"
    w.need(s.count(mark)==3,"unexpected_lineage_record_sites")
    s=s.replace(mark,"""                if (!RaftAuthoredExternalPPtrRoute.Owners.Contains(asset.Collection.Name))
                    continue;
                if (AuthoredLoadedExternalRoute is null ||
                    !AuthoredLoadedExternalRoute.TryGetValue((asset.Collection.Name,asset.PathID),out var loaded) ||
                    !ReferenceEquals(loaded,asset))
                    throw new InvalidDataException("Exported external authored object differs from loaded owner/path reference");
"""+mark+'\n                json.WriteBoolean("authored_loaded_reference_equal", true);')
    helper.write_text(s)
    shutil.copyfile(cs,helper.with_name("RaftAuthoredExternalPPtrRoute.cs"))
    (root/"android-port/Experiments/ExportLineage/Program.cs").write_text(
        "using AssetRipper.Export.UnityProjects;\nRaftAuthoredExternalPPtrRoute.Run(args);\n")

def read(path):
    return json.loads(path.read_text())

def load_traces(out):
    mat,meshes,comps=(read(out/n) for n in ("export-trace.json","mesh-trace.json","renderer-trace.json"))
    rows=[x for tr,key in ((mat,"objects"),(meshes,"meshes"),(comps,"components")) for x in tr[key]]
    wanted={(name,pid) for name,ids in IDS.items() for pid,cls in ids.items() if cls!=4}
    w.need(len(rows)==len(wanted) and {route.source_key(x["source"]) for x in rows}==wanted,"trace_population")
    w.need(all(x["authored_loaded_reference_equal"] is True and x["exportable"] is True for x in rows),
           "actual_reference_not_exported")
    mapping=route.traces(mat,meshes,comps)
    # Equal PathID across physical owners MUST have different export identity.
    for a,b,ids in ((ROOT_A,ROOT_B,ROOT_IDS),(PROV_A,PROV_B,PROV_IDS)):
        for pid,cls in ids.items():
            if cls!=4:
                w.need(mapping[(a,pid)][1][:2]!=mapping[(b,pid)][1][:2],"equal_pathid_export_identity_collapsed")
    return mat,meshes,comps,mapping

def compare(source,project,mapping):
    payloads={}
    objects,externals=route.source_records(source,records(source),OWNERS,vertex_payloads=payloads)
    files,docs=route.actual_index(project,mapping)
    return route.compare(objects,externals,mapping,files,docs,vertex_payloads=payloads,material_values=True)

def control(out,project,mapping):
    results=[]
    def reject(name,source,reason,count=1):
        got=compare(source,project,mapping)
        w.need(not got["selected_renderer_routes_preserved"] and got["reason_counts"]=={reason:count},
               name+":"+repr(got))
        results.append({"name":name,"report":got,
            "sources":{n:w.commit((source/n).read_bytes()) for n in OWNERS}})
    with tempfile.TemporaryDirectory() as tmp:
        source=Path(tmp)/"source"
        for name,mode,reason,count in (
            ("binary_external_table_order_only","table","ordered_pointer_target_mismatch",1),
            ("binary_material_file_index_only","material","ordered_pointer_target_mismatch",1),
            ("binary_mesh_file_index_only","mesh","ordered_pointer_target_mismatch",1),
            ("binary_wrong_external_provider_index","range","source_external_index_out_of_bounds",1),
            ("binary_material_shader_file_index_only","shader","ordered_pointer_target_mismatch",2),
            ("binary_material_texture_file_index_only","texture","ordered_pointer_target_mismatch",2)):
            schemas,objs=fixture();tables=deepcopy(TABLES)
            if mode=="table":tables[ROOT_A].reverse()
            if mode=="material":objs[ROOT_A][104]["m_Materials"].reverse()
            if mode=="mesh":objs[ROOT_A][103]["m_Mesh"]=ptr(2,901)
            if mode=="range":objs[ROOT_A][103]["m_Mesh"]=ptr(3,901)
            if mode=="shader":objs[PROV_A][811]["m_Shader"]=ptr(0,801)
            if mode=="texture":objs[PROV_A][811]["m_SavedProperties"]["m_TexEnvs"][0][1]["m_Texture"]=ptr(0,821)
            write_source(source,schemas,objs,tables);reject(name,source,reason,count)
        # Control: correct external table reorder AND pointer remap preserves routes.
        schemas,objs=fixture();tables=deepcopy(TABLES)
        tables[ROOT_A].reverse()
        objs[ROOT_A][103]["m_Mesh"]=ptr(2,901)
        objs[ROOT_A][104]["m_Materials"]=[ptr(2,811),ptr(1,811)]
        write_source(source,schemas,objs,tables)
        remap=compare(source,project,mapping)
        w.need(remap["selected_same_route_material_values_verified"],"consistent_remap_false_rejection")
        # Actual exported prefab, same class/fileID and another valid owner's GUID.
        files,_=route.actual_index(project,mapping)
        prefab=files[mapping[(ROOT_A,104)][1][0]][0]
        orig=prefab.read_bytes()
        a=mapping[(PROV_A,811)][1];b=mapping[(PROV_B,811)][1]
        w.need(a[1]==b[1] and a[0]!=b[0],"expected_equal_material_main_fileids")
        text=orig.decode("utf-8-sig")
        w.need(text.count(a[0])==text.count(b[0])==1,"ambiguous_material_guid_swap")
        try:
            prefab.write_text(text.replace(a[0],"@"*32).replace(b[0],a[0]).replace("@"*32,b[0]))
            got=compare(out/"source",project,mapping)
            w.need(not got["selected_renderer_routes_preserved"] and
                   got["reason_counts"]=={"ordered_pointer_target_mismatch":1},"actual_guid_swap_accepted")
            results.append({"name":"actual_export_equal_fileid_wrong_owner_guid","report":got})
        finally:prefab.write_bytes(orig)
        bad=dict(mapping);cls,p,exportable=bad[(PROV_A,901)]
        bad[(PROV_A,901)]=(cls,(p[0],p[1]+1,p[2]),exportable)
        got=compare(out/"source",project,bad)
        w.need(not got["selected_renderer_routes_preserved"] and
               got["reason_counts"]=={"missing_actual_serialized_target":1},"wrong_fileid_accepted")
        results.append({"name":"wrong_trace_mesh_fileid","report":got})
    return results,remap

def verify(out,project):
    pin=read(out/"input.json");raw=read(out/"raw-parser.json");typed=read(out/"typed-load.json")
    w.need(len(raw)==4 and {x["owner"] for x in raw}==set(OWNERS),"raw_owner_population")
    for row in raw:
        owner=row["owner"];p=pin["owners"][owner]
        w.need(row["generation"]==22 and row["embedded_type_tree"] is False and
               row["owner_sha256"]==p["owner"]["sha256"] and
               p["owner"]==w.commit((out/"source"/owner).read_bytes()),"raw_owner_authentication")
        w.need([x["path"] for x in row["externals"]]==TABLES[owner] and
               all(x["path"]==x["resolved_name"] and x["type"]==0 for x in row["externals"]),
               "raw_external_table_drift")
        w.need(sorted(row["objects"],key=lambda x:x["path_id"])==
               [{k:v for k,v in x.items() if k!="offset"} for x in p["objects"]],"raw_payload_commitment")
    ids={(name,pid):cls for name,items in IDS.items() for pid,cls in items.items()}
    w.need(len(typed["objects"])==16 and {(x["owner"],x["path_id"]):x["class_id"] for x in typed["objects"]}==ids and
           all(x["typed"] and x["serialized_collection"] for x in typed["objects"]),"typed_population")
    w.need({x["owner"]:x["dependencies"] for x in typed["collections"]}==
           {name:[name]+TABLES[name] for name in OWNERS},"typed_dependency_table_order")
    edges=read(out/"typed-external-edges.json")
    w.need(len(edges)==10 and all(x["reference_equal"] for x in edges),"typed_external_reference_population")
    keys=("owner","path_id","file_id","target_owner","target_path_id","target_class_id")
    w.need(Counter(tuple(x[k] for k in keys) for x in edges)==
           Counter(tuple(x[k] for k in keys) for x in expected_edges()),"typed_external_edge_drift")
    mat,mtrace,ctrace,mapping=load_traces(out)
    saved=local.retain(project,out,mapping)
    proofs=[]
    boost=w.TypeTreeHelper.read_typetree_boost
    w.need(callable(boost),"compiled_decoder_missing")
    for backend,callback in (("compiled",boost),("python",False)):
        with patch.object(w.TypeTreeHelper,"read_typetree_boost",callback):
            report=compare(out/"source",saved,mapping)
            geometry=mesh.inspect(out/"source",records(out/"source"),saved,mtrace,
                                  mat["export_instance"],owners=OWNERS)
        c=report["counts"]
        w.need(report["selected_same_route_material_values_verified"] and
               c.get("complete_renderer_routes")==2 and c.get("complete_vertex_byte_bound_submesh_routes")==4 and
               c.get("material_shader_links_matched")==4 and c.get("material_texenv_slots_matched")==4 and
               c.get("material_null_texture_slots_preserved")==0 and
               all(c.get("material_"+k+"_slots_matched")==4 for k in ("color","float","int")),
               "actual_external_route_failed:"+repr(report))
        w.need(geometry["all_source_mesh_geometry_matches"] and geometry["counts"]["matched_mesh_geometry"]==2,
               "actual_mesh_geometry_mismatch:"+repr(geometry))
        proofs.append({"decoder":backend,"route":report,"geometry":geometry})
    neg,remap=control(out,saved,mapping)
    emitted={str(p.relative_to(saved)):w.commit(p.read_bytes()) for p in sorted(saved.rglob("*")) if p.is_file()}
    local.dump(out/"report.json",{"status":"PASS_ACTUAL_AUTHORED_EXTERNAL_PPTR_ROUTE","public_exporter_pin":PIN,
        "owners":4,"actual_raw_objects":16,"actual_typed_objects":16,"typed_nonnull_external_pptrs":10,
        "same_loaded_reference_traces":len(mapping),"equal_pathid_pairs":8,"proofs":proofs,
        "negative_controls":neg,"consistent_remap_positive_control":remap,"emitted":emitted,
        "actual_source_binary":True,"actual_yaml_export":True,"original_assets_read":False,
        "shader_program_verified":False,"texture_pixels_verified":False,"original_renderer_routes_verified":False,
        "unity_import_verified":False,"device_verified":False,"XAPK_requested":False})
    print("GT_ACTUAL_EXTERNAL_PPTR_PASS",len(proofs),"renderers_per_decoder",2,"submeshes_per_decoder",4,
          "typed_external_edges",len(edges),"negative_controls",len(neg),"consistent_remap",1,flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("prepare","patch-host","verify"))
    p.add_argument("--out",type=Path);p.add_argument("--project",type=Path)
    p.add_argument("--root",type=Path);p.add_argument("--cs",type=Path)
    a=p.parse_args()
    if a.mode=="prepare":prepare(a.out)
    elif a.mode=="patch-host":patch_host(a.root,a.cs)
    else:verify(a.out,a.project)
