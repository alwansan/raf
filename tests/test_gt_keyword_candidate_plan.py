"""Authored inputs only. Actual planner and composer function, stage transforms
stubbed; actual cpp/glslang/spirv-val for authored route marker programs.
No source assets, Unity import, original runtime proof or installation.
"""
import ast
import itertools
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from scripts import gt_keyword_candidate_plan as m

ROOT=Path(__file__).resolve().parents[1]
A,B="GT_AUTHORED_GLOBAL","GT_AUTHORED_LOCAL"
C="GT_AUTHORED_ORPHAN"

def make(keys=((A,),(),(A,B),(B,)), *, orphans=(), tags=(("LightMode","Always"),), fixed=(), reverse_fs=True):
    all_names=sorted(set().union(*(set(k) for k in (*keys,*orphans))))
    flags=[7 if n==B else 11 for n in all_names] # authored arbitrary flag bytes
    pairs=[];unpaired=[];vs=[];fs=[];refs={};files={}
    def stage(name,key,idx):
        ref=f"program-{2*idx+(name=='fs'):03d}"
        # Authored identity bytes, deliberately not original DXBC.
        raw=("authored placeholder "+ref).encode()
        files[ref+"/source.dxbc"]=raw
        refs[ref]={"stage":name,"dxbc_sha256":m.sha(raw)}
        md={"m_BlobIndex":2*idx+(name=="fs"),"m_ShaderHardwareTier":0,"m_KeywordIndices":[all_names.index(n) for n in sorted(key)],"m_GlobalKeywordIndices":[],"m_LocalKeywordIndices":[]}
        return dict(program_ref=ref,player_bucket=0,bucket_ordinal=idx,original_variant_metadata=md,original_D3D11_link=dict(blob_index=md["m_BlobIndex"],segment_index=0,metadata_sha256=m.commitment(md),entry_sha256=m.sha(b"authored entry "+raw)))
    rows=[]
    for i,key in enumerate(keys):
        v,f=stage("vs",key,i),stage("fs",key,i)
        vs.append(v["original_variant_metadata"]);fs.append(f["original_variant_metadata"])
        pairs.append(dict(subshader=0,**{"pass":0},vs=v,fs=f))
        rows.append(dict(enabled=list(key),vs=v["program_ref"],fs=f["program_ref"]))
        for j,s in enumerate(("vs","fs")):
            files[f"bound-stage-{2*i+j:03d}/resource-bound.hlsl"]=(f"main() {{}}\nGT_AUTH_MARKER_{s}_{i}\n").encode()
    for k,key in enumerate(orphans,len(keys)):
        v=stage("vs",key,k);vs.append(v["original_variant_metadata"])
        unpaired.append(dict(subshader=0,**{"pass":0},stage=1,variant=v))
    if reverse_fs:
        fs.reverse()
        for pair in pairs:pair["fs"]["bucket_ordinal"]=len(fs)-1-pair["fs"]["bucket_ordinal"]
    state={"m_Tags":{"tags":[list(t) for t in tags]}}
    item={"m_Type":0,"m_State":state,"progVertex":{"m_PlayerSubPrograms":[vs]},"progFragment":{"m_PlayerSubPrograms":[fs]}}
    manifest={"schema":1,"original_shader_ParsedForm_full_private":{"m_KeywordNames":all_names,"m_KeywordFlags":flags,"m_SubShaders":[{"m_Passes":[item]}]},"original_passes":[dict(subshader=0,**{"pass":0},original_state=state,original_vertex_program=item["progVertex"],original_fragment_program=item["progFragment"],matched_pairs=len(keys),unmatched_vertex=len(orphans),unmatched_fragment=0)],"paired":pairs,"unpaired":unpaired}
    packet=[dict(subshader=0,**{"pass":0},routes=rows,keyword_universe=[dict(name=n,serialized_flag=f) for n,f in zip(all_names,flags)],unmatched_vertex_keywords=[list(x) for x in orphans])]
    files["original-private-variant-manifest.json"]=json.dumps(manifest).encode()
    files["original-private-keyword-routes.json"]=json.dumps(packet).encode()
    files["original-private-layout.txt"]=b'Shader "GT/AuthoredCandidate" {\nSubShader { Pass {\n// Original stage programs attach here\n} } }\n'
    files["original-private-parameter-records.json"]=json.dumps({"stage_records":[{}]*(2*len(keys))}).encode()
    mode=m.mode_of(state)
    proof={"schema":1,"manifest_sha256":m.commitment(manifest),"packet_sha256":m.commitment(packet),"source_semantics_evidence_sha256":m.sha(b"authored semantics fixture only"),"passes":[dict(subshader=0,**{"pass":0},pass_state_sha256=m.commitment(state),pass_type=0,pass_mode=mode,keywords=[dict(name=n,serialized_flag=f,scope="engine_fixed" if n in fixed else "local" if n==B else "global",scope_evidence_sha256=m.sha(("authored scope "+n).encode())) for n,f in zip(all_names,flags)])],"programs":refs,"layout_sha256":m.sha(files["original-private-layout.txt"]),"parameter_records_sha256":m.sha(files["original-private-parameter-records.json"]),"bound_stage_sha256":[m.sha(files[f"bound-stage-{i:03d}/resource-bound.hlsl"]) for i in range(2*len(keys))]}
    return manifest,packet,proof,files

def refresh(manifest,packet,proof):
    proof.update(manifest_sha256=m.commitment(manifest),packet_sha256=m.commitment(packet))

def actual_compose():
    # Load exact versioned compose body; unavailable private translators are
    # intentionally mocked. Candidate planner, emitter, hashes and joins real.
    p=ROOT/"scripts/gt_original_921_shaderlab.py"
    node=next(x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef) and x.name=="compose")
    def legacy(*args,**kw):raise AssertionError("legacy fallback entered")
    ns=dict(json=json,re=re,engine_route_keys=legacy,strict_engine_router=legacy,routed_stage=legacy,paired_uniform_layouts=lambda records:({},{ }),rebind_constant_buffers=lambda text,layout,**kw:text,restore_vertex_inputs=lambda text,raw:(text,None),unity_varying_semantics=lambda x:x,pin_varying_locations=lambda x,y:x,unity_resource_bindings=lambda x,y:x,combine_stages=lambda v,f:v.splitlines()[1]+"\n"+f.splitlines()[1],pass_coverage=lambda s:dict(subshader_pass_counts=[s.count("HLSLPROGRAM")],passes_with_complete_program=s.count("ENDHLSL")))
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),"exec"),ns)
    return ns["compose"]
def materialize(root,files):
    for path,b in files.items():
        f=root/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)

class CandidateTests(unittest.TestCase):
    def test_exact_join_and_nonzero_empty_route(self):
        a,b,p,_=make();r=m.plan(a,b,p)
        self.assertEqual(r["status"],"PREPARED_PRIVATE_CANDIDATE_ONLY")
        row=r["passes"][0];self.assertEqual(row["engine_keys"].index(()),1)
        self.assertEqual(row["program_pairs"],[(x["vs"],x["fs"]) for x in b[0]["routes"]])
        self.assertEqual(m.emit(row,dict(enumerate("ABCD")))[0],[f"#pragma multi_compile __ {A}",f"#pragma multi_compile_local __ {B}"])
        for k in ("original_authorization_verified","original_runtime_verified","production_activation","installation_allowed"):self.assertIs(r[k],False)
    def test_missing_scope_proof_blocks(self):
        a,b,_,_=make();r=m.plan(a,b)
        self.assertIn("source_scope_and_pass_semantics_unproved",r["passes"][0]["blocked_reasons"])
        with self.assertRaises(ValueError):m.emit(r["passes"][0],dict(enumerate("ABCD")))
    def test_scope_proof_hash_not_authorization(self):
        a,b,p,_=make();p["passes"][0]["keywords"][0]["scope"]="unresolved"
        r=m.plan(a,b,p);self.assertEqual(r["status"],"BLOCKED_PRIVATE_CANDIDATE")
        self.assertIn("unresolved_keyword_scope",r["passes"][0]["blocked_reasons"])
        self.assertFalse(r["original_authorization_verified"])
    def test_sparse_and_missing_empty_blocked(self):
        for keys in (((),(A,B)),((A,), (B,)),((A,),)):
            a,b,p,_=make(keys);r=m.plan(a,b,p);self.assertIn("sparse_or_missing_empty_keyword_lattice",r["passes"][0]["blocked_reasons"])
    def test_orphans_classified_without_program_substitution(self):
        a,b,p,_=make(((),(A,)),orphans=((C,),));r=m.plan(a,b,p);self.assertEqual(r["passes"][0]["orphan_vertex_count"],1)
        self.assertIn("unmatched_stage_semantics_unproved",r["passes"][0]["blocked_reasons"]);self.assertEqual(len(r["passes"][0]["program_pairs"]),2)
        b[0]["unmatched_vertex_keywords"]=[];refresh(a,b,p)
        with self.assertRaisesRegex(ValueError,"orphan_classification"):m.plan(a,b,p)
    def test_source_ordinal_metadata_and_link_mutations(self):
        for mutation in (lambda a:a["paired"][0]["fs"].update(bucket_ordinal=0),lambda a:a["paired"][0]["vs"].update(original_variant_metadata={"m_BlobIndex":9}),lambda a:a["paired"][0]["vs"]["original_D3D11_link"].update(metadata_sha256="0"*64),lambda a:a["paired"][0]["fs"].update(program_ref=a["paired"][0]["vs"]["program_ref"])):
            a,b,p,_=make();mutation(a);refresh(a,b,p)
            with self.assertRaises(ValueError):m.plan(a,b,p)
    def test_full_source_population_and_packet_join(self):
        for change in (lambda a,b:a["paired"].pop(),lambda a,b:b[0]["routes"][0].update(fs=b[0]["routes"][1]["fs"]),lambda a,b:b[0]["keyword_universe"][0].update(serialized_flag=200),lambda a,b:b[0]["routes"][0].update(enabled=[])):
            a,b,p,_=make();change(a,b);refresh(a,b,p)
            with self.assertRaises(ValueError):m.plan(a,b,p)
    def test_pass_mode_from_source_and_unknown_blocked(self):
        a,b,p,_=make(tags=());self.assertEqual(m.plan(a,b,p)["passes"][0]["pass_mode"],"Untagged")
        a,b,p,_=make(tags=(("LightMode","MadeUp"),));self.assertIn("unknown_original_pass_mode",m.plan(a,b,p)["passes"][0]["blocked_reasons"])
        a,b,p,_=make();p["passes"][0]["pass_mode"]="ForwardBase"
        with self.assertRaisesRegex(ValueError,"pass_mode_proof_binding"):m.plan(a,b,p)
        a,b,p,_=make();a["original_shader_ParsedForm_full_private"]["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1;refresh(a,b,p)
        with self.assertRaisesRegex(ValueError,"non_normal"):m.plan(a,b,p)
    def test_fixed_macro_requires_exact_pass_and_every_route(self):
        d="DIRECTIONAL";a,b,p,_=make(((d,A),(d,)),tags=(("LightMode","ForwardBase"),),fixed=(d,))
        r=m.plan(a,b,p);self.assertEqual(r["passes"][0]["engine_keys"],[(A,),()])
        a,b,p,_=make(((d,A),()),tags=(("LightMode","ForwardBase"),),fixed=(d,))
        with self.assertRaisesRegex(ValueError,"fixed_macro"):m.plan(a,b,p)
    def test_instancing_requires_separate_semantics(self):
        a,b,p,_=make(((),("INSTANCING_ON",)))
        self.assertIn("instancing_pragma_semantics_unproved",m.plan(a,b,p)["passes"][0]["blocked_reasons"])
    def test_actual_compose_candidate_body_and_commitments(self):
        a,b,p,files=make();fn=actual_compose()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);materialize(root,files);shader=fn(root,candidate_proof=p)
            self.assertEqual(shader.count(m.ERROR),1);self.assertNotIn("GT_ORIGINAL_921_",shader)
            self.assertIn("GT_AUTH_MARKER_vs_1\nGT_AUTH_MARKER_fs_1",shader)
            for filename,error in (("original-private-layout.txt","layout_commitment"),("original-private-parameter-records.json","parameter_record_commitment"),("program-001/source.dxbc","DXBC_commitment"),("bound-stage-001/resource-bound.hlsl","bound_stage_commitment")):
                f=root/filename;f.write_bytes(files[filename]+b"\n")
                with self.assertRaisesRegex(ValueError,error):fn(root,candidate_proof=p)
                f.write_bytes(files[filename])
            with self.assertRaisesRegex(ValueError,"ambiguous_candidate"):fn(root,engine_keywords=True,candidate_proof=p)
    def test_actual_compose_blocks_sparse_before_stage_transform(self):
        a,b,p,files=make(((),(A,B)))
        with tempfile.TemporaryDirectory() as t:
            materialize(Path(t),files)
            with self.assertRaisesRegex(ValueError,"candidate_blocked"):actual_compose()(Path(t),candidate_proof=p)
    def test_safe_report_no_names_or_hashes(self):
        a,b,p,_=make();s=json.dumps(m.safe_summary(m.plan(a,b,p)))
        self.assertNotIn(A,s);self.assertNotIn("program-",s);self.assertNotIn("sha256",s)
    def test_actual_cpp_1156_route_markers(self):
        self.assertIsNotNone(shutil.which("cpp"),"required actual preprocessor")
        total=0
        for n in (9,2,7,9):
            names=[f"AUTHORED_KEY_{i}" for i in range(n)]
            keys=[tuple(x for x,on in zip(names,bits) if on) for bits in itertools.product((False,True),repeat=n)]
            keys=keys[1:]+keys[:1];a,b,p,_=make(keys)
            row=m.plan(a,b,p)["passes"][0];markers={i:f"MARKER_{i}" for i in range(len(keys))}
            _,code=m.emit(row,markers)
            with tempfile.TemporaryDirectory() as t:
                (Path(t)/"router.h").write_text(code);blocks=[]
                for k in keys:
                    blocks.extend(f"#define {x} 1" for x in k);blocks.append('#include "router.h"');blocks.extend(f"#undef {x}" for x in k)
                r=subprocess.run(["cpp","-P","-undef","-nostdinc","-I",t,"-x","c","-"],input="\n".join(blocks)+"\n",text=True,capture_output=True,check=True,timeout=30)
            self.assertEqual(r.stdout.split(),list(markers.values()));total+=len(keys)
        self.assertEqual(total,1156)
    def test_actual_cpp_deleted_branch_is_error(self):
        a,b,p,_=make();_,code=m.emit(m.plan(a,b,p)["passes"][0],dict(enumerate("ABCD")))
        code=code.replace(f"#elif !defined({A}) && !defined({B})\nB\n","")
        r=subprocess.run(["cpp","-P","-undef","-nostdinc","-x","c","-"],input=code,text=True,capture_output=True,timeout=10)
        self.assertNotEqual(r.returncode,0);self.assertIn("Unmapped_original_keyword_set",r.stderr);self.assertNotIn("A",r.stdout)

if __name__=="__main__":unittest.main()
