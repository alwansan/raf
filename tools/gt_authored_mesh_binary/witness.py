#!/usr/bin/env python3
"""Authored v22 SerializedFile / public Mesh TypeTree witness, NO game bytes.

Independent struct encoder uses the public schema solely for field order,
primitive types and alignment. YAML is independently authored from constants,
not from decoded data. No AssetRipper, Unity engine or device claims.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import struct
import tempfile
from unittest.mock import patch

import warnings

# UnityPy 1.23.0 uses importlib.resources.open_binary at TPK initialization.
# Suppress only that known third-party import deprecation on Python 3.12.
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message=r"open_binary is deprecated.*",
                            category=DeprecationWarning, module=r"UnityPy\.helpers\.Tpk")
    import UnityPy
from UnityPy.helpers import TypeTreeHelper
from UnityPy.helpers.Tpk import get_typetree_node
from UnityPy.helpers.UnityVersion import UnityVersion

from scripts import gt_verify_original_mesh_export as mesh

UNITY="2021.3.0f1"
CLASS=43
PATH_ID=937
FILE_ID=4300000
GUID="a"*32
INSTANCE="b"*32
OWNER="authored.assets"
PROVIDER="authored.resS"
VERTICES=(-2.0,0.0,0.25,0.125,0.75, 1.0,-0.5,0.25,0.875,0.0, 0.0,2.0,-0.25,0.5,1.0)
RAW=struct.pack("<15f",*VERTICES)
INDICES=struct.pack("<3H",0,1,2)
BONES=(0xc0000001,0xffffffff,0x12345678)
WEIGHTS=(0x80000000,0x00000001)
POSE={f"e{r}{c}":(-0.0 if (r,c)==(0,1) else 1.0 if r==c else 0.0)
      for r in range(4) for c in range(4)}
CHANNELS=[{"stream":0,"offset":0 if i!=4 else 12,"format":0,
           "dimension":3 if i==0 else 2 if i==4 else 0} for i in range(14)]
SUB={"firstByte":0,"indexCount":3,"topology":0,"baseVertex":0,"firstVertex":0,"vertexCount":3}
PRIMS={"SInt8":"b","UInt8":"B","char":"B","SInt16":"h","short":"h",
       "UInt16":"H","unsigned short":"H","SInt32":"i","int":"i","UInt32":"I",
       "unsigned int":"I","Type*":"I","SInt64":"q","long long":"q","UInt64":"Q",
       "unsigned long long":"Q","FileSize":"Q","float":"f","double":"d","bool":"?"}
MISSING=object()


def need(test,reason):
    if not test:
        raise AssertionError(reason)


def children(node):
    return node.m_Children


def aligned(node):
    return bool((node.m_MetaFlag or 0)&0x4000)


def pad(out,n):
    out.extend(b"\0"*((-len(out))%n))


def encode_node(node,value,out):
    """Minimal independent little-endian encoder for this fixed public schema.

    Defaults only unrelated fields. All explicit fields must be consumed.
    Refuse unsupported schema rather than silently skipping bytes.
    """
    typ=node.m_Type
    ch=children(node)
    align=aligned(node)
    if typ in PRIMS:
        if value is MISSING:
            value=False if typ=="bool" else 0
        out.extend(struct.pack("<"+PRIMS[typ],value))
    elif typ in ("string","TypelessData"):
        if value is MISSING:
            value="" if typ=="string" else b""
        raw=value.encode("utf-8") if typ=="string" else bytes(value)
        out.extend(struct.pack("<i",len(raw)))
        out.extend(raw)
        if typ=="string":
            pad(out,4)
    elif ch and ch[0].m_Type=="Array":
        if value is MISSING:
            value=[]
        array=ch[0]
        need(len(children(array))==2,"unexpected_array_schema")
        item=children(array)[1]
        out.extend(struct.pack("<i",len(value)))
        # Aligned primitive arrays align once after the complete vector.
        if aligned(item) and item.m_Type in PRIMS:
            for v in value:
                out.extend(struct.pack("<"+PRIMS[item.m_Type],v))
            pad(out,4)
        else:
            for v in value:
                encode_node(item,v,out)
        align=align or aligned(array)
    elif typ=="pair":
        vals=(MISSING,MISSING) if value is MISSING else value
        need(len(ch)==len(vals)==2,"unexpected_pair_schema")
        for n,v in zip(ch,vals):
            encode_node(n,v,out)
    elif ch:
        vals={} if value is MISSING else value
        need(type(vals) is dict and set(vals)<={n.m_Name for n in ch},
             "explicit_fixture_field_missing_from_public_schema:"+node.m_Name+":"+repr(set(vals)-{n.m_Name for n in ch}))
        for n in ch:
            encode_node(n,vals.get(n.m_Name,MISSING),out)
    else:
        raise AssertionError("unsupported_public_mesh_schema_leaf:"+typ+":"+node.m_Name)
    if align:
        pad(out,4)


def schema_rows(node):
    rows=[]
    def visit(n,depth):
        rows.append([depth,n.m_Type,n.m_Name,n.m_ByteSize,n.m_MetaFlag])
        for child in children(n):
            visit(child,depth+1)
    visit(node,0)
    return rows


def authored_fields(*,streamed=False,dual=False,raw=RAW,indices=INDICES,bones=BONES,pose=POSE,
                    packed=b"\x21\x43",stale=False):
    return {"m_Name":"GT authored Mesh binary witness",
            "m_SubMeshes":[SUB.copy()],
            "m_BindPose":[pose.copy()],
            "m_BoneNameHashes":list(bones),
            "m_VariableBoneCountWeights":{"m_Data":list(WEIGHTS)},
            "m_IndexFormat":0,"m_IndexBuffer":list(indices),
            "m_VertexData":{"m_VertexCount":3,"m_Channels":deepcopy(CHANNELS),
                            "m_DataSize":list(raw) if not streamed or dual else []},
            "m_CompressedMesh":{"m_UVInfo":1,"m_UV":{"m_NumItems":4,"m_Range":1.0,
                    "m_Start":-0.25,"m_BitSize":4,"m_Data":list(packed)}},
            "m_StreamData":{"offset":3 if streamed else 0,"size":len(RAW) if streamed else 0,
                            "path":PROVIDER if streamed or stale else ""}}


def owner_bytes(node,fields):
    payload=bytearray()
    encode_node(node,fields,payload)
    # SerializedFile v22 with one Mesh, no embedded tree, no external object
    # refs. Public TPK fallback is selected by the exact Unity version/Class43.
    meta=bytearray(UNITY.encode("ascii")+b"\0")
    meta.extend(struct.pack("<i?i",13,False,1))  # Android, no embedded tree, one type
    meta.extend(struct.pack("<i?h",CLASS,False,-1)+bytes(16))
    meta.extend(struct.pack("<i",1)) # one object
    pad(meta,4)
    meta.extend(struct.pack("<qqIi",PATH_ID,0,len(payload),0))
    meta.extend(struct.pack("<iii",0,0,0)+b"\0") # scripts, externals, refs, user info
    data_offset=(48+len(meta)+15)&~15
    header=struct.pack(">IIII",0,0,22,0)+b"\0"*4
    header+=struct.pack(">Iqqq",len(meta),data_offset+len(payload),data_offset,0)
    need(len(header)==48,"authored_header_size")
    return header+meta+bytes(data_offset-48-len(meta))+payload,bytes(payload)


def decode(raw,payload,boost):
    # Real file load + real ObjectReader, no fake object/typetree injection.
    env=UnityPy.load(raw)
    owner=env.file
    need(type(owner).__name__=="SerializedFile" and owner.header.version==22,"not_real_serialized_file")
    need(owner.unity_version==UNITY and list(owner.objects)==[PATH_ID],"wrong_authored_owner_identity")
    obj=owner.objects[PATH_ID]
    need(obj.type.name=="Mesh" and obj.byte_size==len(payload),"wrong_real_mesh_object")
    need(obj.get_raw_data()==payload,"object_payload_not_exact")
    with patch.object(TypeTreeHelper,"read_typetree_boost",boost):
        tree=obj.read_typetree()
    need(type(tree) is dict,"wrong_decoded_tree_type")
    return tree


def authored_yaml(node,*,raw=RAW,indices=INDICES,bones=BONES,pose=POSE,packed=b"\x21\x43"):
    """Generate matching YAML from authored constants, not decoded Mesh."""
    def hex_words(words):
        return struct.pack("<"+"I"*len(words),*words).hex()
    lines=["%YAML 1.1","%TAG !u! tag:unity3d.com,2011:",f"--- !u!43 &{FILE_ID}","Mesh:",
           "  m_VertexData:","    m_VertexCount: 3","    m_Channels:"]
    for c in CHANNELS:
        lines.append("    - stream: "+str(c["stream"]))
        lines.extend("      "+k+": "+str(c[k]) for k in ("offset","format","dimension"))
    lines.extend([f"    m_DataSize: {len(raw)}","    _typelessdata: "+raw.hex(),
                  "  m_IndexFormat: 0","  m_IndexBuffer: "+indices.hex(),
                  "  m_SubMeshes:",f"  - firstByte: {SUB['firstByte']}"])
    lines.extend("    "+k+": "+str(SUB[k]) for k in ("indexCount","topology","baseVertex","firstVertex","vertexCount"))
    lines.extend(["  m_BindPose:","  - e00: 1.0"])
    for r in range(4):
        for c in range(4):
            key=f"e{r}{c}"
            if key!="e00":
                v=pose[key]
                # Exercise the existing Unity "-0" float32 compatibility.
                lines.append("    "+key+": "+("-0" if struct.pack("<f",v)==b"\0\0\0\x80" else str(v)))
    lines.extend(["  m_BoneNameHashes: "+hex_words(bones),
                  "  m_VariableBoneCountWeights:","    m_Data: "+hex_words(WEIGHTS),"  m_CompressedMesh:"])
    cm=next(n for n in children(node) if n.m_Name=="m_CompressedMesh")
    for field in children(cm):
        if field.m_Name=="m_UVInfo":
            lines.append("    m_UVInfo: 1")
        else:
            keys={n.m_Name for n in children(field)}
            need({"m_NumItems","m_BitSize","m_Data"}<=keys,"unexpected_packed_schema:"+field.m_Name)
            uv=field.m_Name=="m_UV"
            lines.extend(["    "+field.m_Name+":",f"      m_NumItems: {4 if uv else 0}"])
            if "m_Range" in keys:lines.append("      m_Range: "+("1.0" if uv else "0.0"))
            if "m_Start" in keys:lines.append("      m_Start: "+("-0.25" if uv else "0.0"))
            lines.extend(["      m_Data: "+(packed.hex() if uv else ""),f"      m_BitSize: {4 if uv else 0}"])
    lines.extend(["  m_StreamData:","    offset: 0","    size: 0","    path:"])
    return "\n".join(lines)+"\n"


def pin(raw):
    return "plain",len(raw),sha256(raw).hexdigest()


def commit(raw):
    return {"bytes":len(raw),"sha256":sha256(raw).hexdigest()}


def require_equal(source,actual):
    need(mesh.compare_geometry(source,actual)==([],0),"geometry_drift:"+repr(mesh.compare_geometry(source,actual)))


def reject(fn,reason):
    try:fn()
    except ValueError as exc:
        need(reason in str(exc),"unexpected_rejection:"+str(exc))
    else:raise AssertionError("negative_control_accepted:"+reason)


def run(out):
    need(version("UnityPy")=="1.23.0","decoder_version_mismatch")
    boost=TypeTreeHelper.read_typetree_boost
    need(callable(boost),"compiled_typetree_decoder_unavailable")
    node=get_typetree_node(CLASS,UnityVersion.from_str(UNITY))
    need(node.m_Type=="Mesh","public_schema_not_mesh")
    schema=schema_rows(node)
    out.mkdir(parents=True,exist_ok=True)
    (out/"schema.json").write_text(json.dumps(schema,indent=2)+"\n")
    print("GT_SCHEMA",UNITY,CLASS,len(schema),flush=True)
    rows=[]
    controls=[]
    variants={}
    with tempfile.TemporaryDirectory(prefix="gt-authored-mesh-") as tmp:
        root=Path(tmp)
        project=root/"project"
        assets=project/"Assets"
        assets.mkdir(parents=True)
        source=root/"source"
        source.mkdir()
        target=assets/"AuthoredMesh.asset"
        target.with_suffix(".asset.meta").write_text("guid: "+GUID+"\n")
        provider=source/PROVIDER
        provider_raw=b"pre"+RAW+b"post"
        provider.write_bytes(provider_raw)
        yaml_text=authored_yaml(node)
        target.write_text(yaml_text)
        expected=mesh.export_geometry(target,FILE_ID)
        for label,fields in (("inline",authored_fields()),("streamed",authored_fields(streamed=True)),
                             ("dual_equal",authored_fields(streamed=True,dual=True))):
            raw,payload=owner_bytes(node,fields)
            variants[label]=(raw,payload)
            (source/OWNER).write_bytes(raw)
            records={"Raft_Data/"+OWNER:pin(raw),"Raft_Data/"+PROVIDER:pin(provider_raw)}
            for decoder,callback in (("compiled",boost),("python",False)):
                tree=decode(raw,payload,callback)
                # Test the decoded data values against independent constants.
                need(bytes(tree["m_VertexData"]["m_DataSize"])==
                     (b"" if label=="streamed" else RAW),"decoded_vertex_bytes")
                need(bytes(tree["m_IndexBuffer"])==INDICES,"decoded_index_bytes")
                need(tuple(tree["m_BoneNameHashes"])==BONES,"decoded_uint32_bone_hashes")
                need(tuple(tree["m_VariableBoneCountWeights"]["m_Data"])==WEIGHTS,"decoded_uint32_weights")
                need(bytes(tree["m_CompressedMesh"]["m_UV"]["m_Data"])==b"\x21\x43","decoded_packed_bytes")
                need(struct.pack("<f",tree["m_BindPose"][0]["e01"])==b"\0\0\0\x80","decoded_signed_zero")
                seen=set()
                got=mesh.source_geometry(tree,source,records,seen)
                require_equal(got,expected)
                need(len(got)==10 and got==expected,"wrong_geometry_field_population")
                need(seen==({PROVIDER} if label!="inline" else set()),"wrong_stream_accounting")
                # Exercise the entire native inspect path, including pinned owner
                # hash, ObjectReader, GUID/fileID join and comparison.
                trace={"schema_version":1,"export_instance":INSTANCE,
                       "meshes":[{"source":{"owner":OWNER,"path_id":PATH_ID},
                                  "exportable":True,"export":{"guid":GUID,"file_id":FILE_ID,"type":2}}]}
                with patch.object(TypeTreeHelper,"read_typetree_boost",callback):
                    report=mesh.inspect(source,records,project,trace,INSTANCE,owners=(OWNER,))
                need(report["all_source_mesh_geometry_matches"] and
                     report["counts"]["matched_mesh_geometry"]==1 and
                     not report["renderer_bindings_or_unity_import_verified"],"full_native_consumer_mismatch")
                rows.append({"storage":label,"decoder":decoder,"owner":commit(raw),"object":commit(payload),
                             "full_native_inspect":report,"geometry_fields":len(got),"all_geometry_fields_equal":got==expected,
                             "types":{"vertex":type(tree["m_VertexData"]["m_DataSize"]).__name__,
                                      "index":type(tree["m_IndexBuffer"]).__name__,
                                      "packed":type(tree["m_CompressedMesh"]["m_UV"]["m_Data"]).__name__,
                                      "bones":type(tree["m_BoneNameHashes"]).__name__,
                                      "weights":type(tree["m_VariableBoneCountWeights"]["m_Data"]).__name__}})
                print("GT_REAL_MESH_MATCH",label,decoder,flush=True)
        # Independent binary counterfactuals, not dictionary mutations after decode.
        changed=bytearray(RAW);changed[12:16]=struct.pack("<f",0.625)
        moved=bytearray(RAW);moved[:4]=struct.pack("<f",-3.0)
        pose=dict(POSE,e01=0.125)
        for label,fields,drift in (
            ("uv_only",authored_fields(raw=bytes(changed)),"vertex_buffer"),
            ("position_only",authored_fields(raw=bytes(moved)),"vertex_buffer"),
            ("indices",authored_fields(indices=struct.pack("<3H",0,2,1)),"index_buffer"),
            ("bone_hash",authored_fields(bones=(0xc0000002,*BONES[1:])),"bone_name_hashes"),
            ("packed",authored_fields(packed=b"\x22\x43"),"compressed_attributes"),
            ("pose",authored_fields(pose=pose),"bind_pose_matrices"),
        ):
            raw,payload=owner_bytes(node,fields)
            for decoder,callback in (("compiled",boost),("python",False)):
                tree=decode(raw,payload,callback)
                got=mesh.source_geometry(tree,source,{},set())
                need(mesh.compare_geometry(got,expected)==([drift],0),"missed_or_extra_binary_drift:"+label)
                controls.append({"case":label,"decoder":decoder,"rejected_field":drift,"owner":commit(raw)})
        for decoder,callback in (("compiled",boost),("python",False)):
            for label,fields,reason in (
                ("stale_zero_provider",authored_fields(stale=True),"invalid_original_mesh_stream_descriptor"),
                ("dual_conflict",authored_fields(streamed=True,dual=True,raw=bytes(changed)),
                 "conflicting_original_mesh_vertex_payload"),
            ):
                raw,payload=owner_bytes(node,fields)
                tree=decode(raw,payload,callback)
                reject(lambda:mesh.source_geometry(tree,source,{"Raft_Data/"+PROVIDER:pin(provider_raw)},set()),reason)
                controls.append({"case":label,"decoder":decoder,"error":reason,"owner":commit(raw)})
            raw,payload=variants["streamed"]
            tree=decode(raw,payload,callback)
            provider.write_bytes(b"X"+provider_raw[1:])
            reject(lambda:mesh.source_geometry(tree,source,{"Raft_Data/"+PROVIDER:pin(provider_raw)},set()),
                   "pinned_pixel_provider_SHA_mismatch")
            provider.write_bytes(provider_raw)
            controls.append({"case":"provider_mutated","decoder":decoder,"error":"pinned_pixel_provider_SHA_mismatch"})
        # Keep reproducible authored payloads, not original assets.
        (out/"authored-inline.assets").write_bytes(variants["inline"][0])
        (out/"authored-streamed.assets").write_bytes(variants["streamed"][0])
        (out/"authored-dual.assets").write_bytes(variants["dual_equal"][0])
        (out/"authored.resS").write_bytes(provider_raw)
        (out/"authored-mesh.asset").write_text(yaml_text)
    need(len(rows)==6 and len(controls)==18,"wrong_receipt_population")
    report={"status":"PASS_AUTHORED_REAL_MESH_BINARY_CONSUMER","unitypy":version("UnityPy"),
            "public_schema_unity_version":UNITY,"class_id":CLASS,"serialized_file_version":22,
            "schema_nodes":len(schema),"schema":commit((out/"schema.json").read_bytes()),
            "source_encoder":"independent struct encoder using public TPK schema",
            "actual_serialized_file_load":True,"actual_objectreader_typetree_decode":True,
            "actual_native_inspect_consumer":True,"actual_export_consumer":True,
            "actual_assetripper_export":False,"authored_yaml":True,
            "positive_cases":rows,"negative_controls":controls,"positive_count":6,"negative_count":18,
            "original_assets_read":False,"original_geometry_verified":False,
            "unity_import_verified":False,"device_render_verified":False,"XAPK_requested":False,
            "payload_commitments":{"vertex":commit(RAW),"index":commit(INDICES),
                                   "provider":commit(provider_raw),"yaml":commit(yaml_text.encode())}}
    (out/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("GT_REAL_MESH_BINARY_PASS positives=6 negatives=18",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    run(parser.parse_args().out)
