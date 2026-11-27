#!/usr/bin/env python3
"""Real authored binary -> pinned public AssetRipper -> unchanged native consumer.

Never generate an export YAML or synthetic trace. The previous authored binary
is byte-identical; two independent uncompressed cases exercise XYZ/UV/index.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import json
import shutil
import struct
import subprocess
import tempfile
import traceback
from unittest.mock import patch

from tools.gt_authored_mesh_binary import witness as w
from scripts import gt_verify_original_mesh_export as mesh

CASES=("retained_mixed","uncompressed_inline","uncompressed_streamed")
PIN="036098ab525a3f9f693dc101edeb21faad4d32d8"
OLD_SHA="eb128140292288b4adab34f9f253ccc14e497a5677332cebfc37a437b9e7193f"

def dump(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def schema():
    return w.get_typetree_node(w.CLASS,(2021,3,0,1))

def supported(node,*,streamed=False,raw=w.RAW,indices=w.INDICES):
    f=w.authored_fields(raw=raw,indices=indices)
    f.update(m_Name="GT authored uncompressed triangle",m_BindPose=[],
             m_BoneNameHashes=[],m_VariableBoneCountWeights={"m_Data":[]},
             m_CompressedMesh={})
    f["m_StreamData"]={"offset":16 if streamed else 0,"size":len(raw) if streamed else 0,
                       "path":w.PROVIDER if streamed else ""}
    f["m_VertexData"]["m_DataSize"]=[] if streamed else list(raw)
    root={n.m_Name:n for n in w.children(node)}
    for k in ("m_IsReadable","m_KeepVertices","m_KeepIndices"):
        if k in root:
            f[k]=True
    aabb={"m_Center":{"x":-0.5,"y":0.75,"z":0.0},
          "m_Extent":{"x":1.5,"y":1.25,"z":0.25}}
    if "m_LocalAABB" in root:
        f["m_LocalAABB"]=deepcopy(aabb)
    sub=w.children(w.children(root["m_SubMeshes"])[0])[1]
    if any(n.m_Name=="localAABB" for n in w.children(sub)):
        f["m_SubMeshes"][0]["localAABB"]=deepcopy(aabb)
    return f

def prepare(out):
    out.mkdir(parents=True,exist_ok=False)
    node=schema()
    dump(out/"public_schema.json",w.schema_rows(node))
    for case in CASES:
        source=out/case/"source"
        source.mkdir(parents=True)
        streamed=case=="uncompressed_streamed"
        fields=w.authored_fields() if case=="retained_mixed" else supported(node,streamed=streamed)
        raw,payload=w.owner_bytes(node,fields)
        if case=="retained_mixed":
            w.need(w.commit(raw)=={"bytes":728,"sha256":OLD_SHA},"retained_owner_not_byte_identical")
        (source/w.OWNER).write_bytes(raw)
        if streamed:
            (source/w.PROVIDER).write_bytes(b"0123456789abcdef"+w.RAW+b"end")
        pins={p.name:w.commit(p.read_bytes()) for p in sorted(source.iterdir())}
        dump(out/case/"input.json",{"case":case,"files":pins,"object":w.commit(payload),
                                    "vertex":w.commit(w.RAW),"index":w.commit(w.INDICES)})
        tree=w.decode(raw,payload,w.TypeTreeHelper.read_typetree_boost)
        w.need(bytes(tree["m_IndexBuffer"])==w.INDICES,"wrong_authored_index")
        w.need(bytes(tree["m_VertexData"]["m_DataSize"])==(b"" if streamed else w.RAW),
               "wrong_authored_vertex")
        print("GT_BINARY_INPUT",case,pins,flush=True)

def patch_host(root,cs):
    # Only disposable runner checkout; verify anchors, no production patch.
    helper=root/"ar-host/Source/AssetRipper.Export.UnityProjects/RaftExportLineage.cs"
    s=helper.read_text()
    mark="    private static void CaptureMeshes("
    w.need(s.count(mark)==1,"missing_capture_meshes")
    s=s.replace(mark,"    internal static IUnityObjectBase? AuthoredLoadedMesh;\n\n"+mark)
    mark="                if (asset.ClassID != 43)\n                    continue;"
    w.need(s.count(mark)==1,"missing_class43_capture")
    s=s.replace(mark,mark+"""
                if (asset.Collection.Name != "authored.assets")
                    continue;
                if (!ReferenceEquals(asset, AuthoredLoadedMesh))
                    throw new InvalidDataException("Export collection Mesh differs from loaded reference");""")
    mark='                Identity(json, "source", asset);'
    # Restrict insertion to CaptureMeshes, leaving other trace records alone.
    start=s.index("    private static void CaptureMeshes(")
    end=s.index("    private static void Identity(",start)
    chunk=s[start:end]
    w.need(chunk.count(mark)==1,"ambiguous_mesh_identity_hook")
    chunk=chunk.replace(mark,mark+'\n                json.WriteBoolean("authored_loaded_reference_equal", true);')
    helper.write_text(s[:start]+chunk+s[end:])
    shutil.copyfile(cs,helper.with_name("RaftAuthoredBinaryMeshWitness.cs"))
    p=root/"android-port/Experiments/ExportLineage/Program.cs"
    p.write_text("using AssetRipper.Export.UnityProjects;\nRaftAuthoredBinaryMeshWitness.Run(args);\n")

def records(source):
    return {"Raft_Data/"+p.name:w.pin(p.read_bytes()) for p in source.iterdir() if p.is_file()}

def controls(source,project,trace,instance):
    results=[]
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)
        raw=bytearray(w.RAW)
        raw[12:16]=struct.pack("<f",0.625)
        xyz=bytearray(w.RAW)
        xyz[:4]=struct.pack("<f",-3.0)
        for name,fields,expected in (
            ("uv_only",supported(schema(),raw=bytes(raw)),"vertex_buffer"),
            ("position_only",supported(schema(),raw=bytes(xyz)),"vertex_buffer"),
            ("index_only",supported(schema(),indices=struct.pack("<3H",0,2,1)),"index_buffer"),
        ):
            owner,_=w.owner_bytes(schema(),fields)
            (d/w.OWNER).write_bytes(owner)
            got=mesh.inspect(d,records(d),project,trace,instance,owners=(w.OWNER,))
            w.need(not got["all_source_mesh_geometry_matches"] and got["mismatch_fields"]=={expected:1},
                   "binary_control_failed:"+name+":"+repr(got))
            results.append({"name":name,"actual_binary":w.commit(owner),"result":got})
    try:
        mesh.inspect(source,records(source),project,trace,"0"*32,owners=(w.OWNER,))
    except ValueError as e:
        w.need("invalid_same_instance_mesh_trace" in str(e),"wrong_instance_failure")
        results.append({"name":"wrong_instance","reason":str(e)})
    else:
        raise AssertionError("wrong_instance_accepted")
    bad=deepcopy(trace)
    bad["meshes"][0]["export"]["file_id"]+=1
    got=mesh.inspect(source,records(source),project,bad,instance,owners=(w.OWNER,))
    w.need(not got["all_source_mesh_geometry_matches"] and
           got["counts"].get("source_or_export_decode_error")==1,"wrong_fileid_accepted")
    results.append({"name":"wrong_fileid","result":got})
    return results

def verify(out,export_root):
    rows=[]
    for case in CASES:
        root=out/case
        row={"case":case,"status":"FAIL","export_exit_code":int((root/"exit.txt").read_text())}
        try:
            source=root/"source"
            pins=json.loads((root/"input.json").read_text())["files"]
            w.need({p.name:w.commit(p.read_bytes()) for p in source.iterdir()}==pins,"source_mutated")
            raw_parser=json.loads((root/"raw-parser.json").read_text())
            source_receipt=json.loads((root/"input.json").read_text())
            w.need(raw_parser["generation"]==22 and raw_parser["owner"]==w.OWNER and
                   raw_parser["embedded_type_tree"] is False and
                   raw_parser["objects"]==[{"path_id":w.PATH_ID,"class_id":43,**source_receipt["object"]}],
                   "actual_pinned_raw_parser_identity_mismatch")
            row["actual_pinned_raw_parser"]=True
            census=json.loads((root/"load-census.json").read_text())
            row["load_census"]={k:census[k] for k in ("authored_objects","all_meshes")}
            loaded=json.loads((root/"loaded.json").read_text())
            w.need(loaded["phase"]=="actual_handler_load_before_processing" and
                   loaded["class_id"]==43 and loaded["mesh_count"]==1 and
                   loaded["source"]=={"owner":w.OWNER,"path_id":w.PATH_ID},"loaded_identity_mismatch")
            w.need({x["name"]:{"bytes":x["bytes"],"sha256":x["sha256"]} for x in loaded["inputs"]}==pins,
                   "actual_loader_input_hash_mismatch")
            row["actual_file_load"]=True
            w.need(row["export_exit_code"]==0,"export_process_failed")
            trace=json.loads((root/"mesh-trace.json").read_text())
            instance=json.loads((root/"export-trace.json").read_text())["export_instance"]
            w.need(trace["export_instance"]==instance and len(trace["meshes"])==1,"trace_instance_or_count")
            t=trace["meshes"][0]
            w.need(t["source"]==loaded["source"] and t["authored_loaded_reference_equal"] is True and
                   t["exportable"] is True,"trace_not_actual_loaded_reference")
            row["same_loaded_object_reference"]=True
            project=export_root/case/"ExportedProject"
            targets=mesh.index_project(project,{t["export"]["guid"]})
            target=targets[t["export"]["guid"]]
            # Retain exact emitted bytes, not a generated or normalized YAML.
            saved=root/"actual-export"/"Assets"
            saved.mkdir(parents=True)
            for p in (target,target.with_suffix(".asset.meta")):
                shutil.copyfile(p,saved/p.name)
                w.need(p.read_bytes()==(saved/p.name).read_bytes(),"export_copy_mismatch")
            row["actual_yaml"]=w.commit(target.read_bytes())
            row["actual_meta"]=w.commit(target.with_suffix(".asset.meta").read_bytes())
            row["pointer"]=t["export"]
            row["export_instance"]=instance
            saved_project=saved.parent
            results=[]
            boost=w.TypeTreeHelper.read_typetree_boost
            w.need(callable(boost),"compiled_reader_unavailable")
            for decoder,callback in (("compiled",boost),("python",False)):
                with patch.object(w.TypeTreeHelper,"read_typetree_boost",callback):
                    got=mesh.inspect(source,records(source),saved_project,trace,instance,owners=(w.OWNER,))
                results.append({"decoder":decoder,"native_inspect":got})
            row["native_results"]=results
            actual=mesh.export_geometry(saved/target.name,t["export"]["file_id"])
            env=w.UnityPy.load((source/w.OWNER).read_bytes())
            tree=env.file.objects[w.PATH_ID].read_typetree()
            expected=mesh.source_geometry(tree,source,records(source),set())
            row["geometry_fields"]=sorted(expected)
            row["geometry_drift"],row["bind_pose_signed_zero_differences"]=mesh.compare_geometry(expected,actual)
            row["source_vertex"],row["export_vertex"]=expected["vertex_buffer"],actual["vertex_buffer"]
            row["source_index"],row["export_index"]=expected["index_buffer"],actual["index_buffer"]
            w.need(expected["vertex_buffer"]==mesh.digest(w.RAW) and expected["index_buffer"]==mesh.digest(w.INDICES),
                   "source_payload_not_authored_constants")
            w.need(not row["geometry_drift"] and len(expected)==10 and
                   all(x["native_inspect"]["all_source_mesh_geometry_matches"] and
                       x["native_inspect"]["counts"]["matched_mesh_geometry"]==1 for x in results),
                   "full_native_geometry_drift")
            if case=="uncompressed_inline":
                row["negative_controls"]=controls(source,saved_project,trace,instance)
                w.need(len(row["negative_controls"])==5,"wrong_negative_count")
            row["status"]="PASS_ACTUAL_EXPORT_CONSUMER"
        except Exception as ex:
            row["error"]=type(ex).__name__+": "+str(ex)
            row["traceback"]=traceback.format_exc()
        dump(root/"comparison.json",row)
        rows.append(row)
        print("GT_ACTUAL_EXPORT_CASE",case,row["status"],row.get("error",""),flush=True)
    good=any(x["case"]=="uncompressed_inline" and x["status"]=="PASS_ACTUAL_EXPORT_CONSUMER" for x in rows)
    report={"status":"PASS_SUPPORTED_AUTHORED_ACTUAL_EXPORT" if good else "FAIL_SUPPORTED_AUTHORED_ACTUAL_EXPORT",
            "public_exporter_pin":PIN,"cases":rows,"original_assets_read":False,
            "original_geometry_verified":False,"unity_import_verified":False,"device_verified":False,
            "XAPK_requested":False,"authored_yaml_used_as_export":False}
    dump(out/"report.json",report)
    return 0 if good else 2

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("prepare","patch-host","verify"))
    p.add_argument("--out",type=Path)
    p.add_argument("--export-root",type=Path)
    p.add_argument("--root",type=Path)
    p.add_argument("--cs",type=Path)
    a=p.parse_args()
    if a.mode=="prepare":
        prepare(a.out)
    elif a.mode=="patch-host":
        patch_host(a.root,a.cs)
    else:
        raise SystemExit(verify(a.out,a.export_root))
