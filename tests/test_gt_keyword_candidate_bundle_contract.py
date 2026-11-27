"""Authored candidate receipt/table counterfactuals; no actual Unity claim."""
import unittest
from copy import deepcopy
from scripts import gt_keyword_candidate_bundle_contract as g
from scripts import gt_keyword_candidate_bundle_probe as w

class CandidateBundleContract(unittest.TestCase):
    def setUp(self):
        self.manifest,self.packet,self.proof,self.shader,self.c=w.payload()
        self.contract=w.dump(self.c);self.bundle=b"authored fake bundle only"
        self.r=dict(schema=1,status="OBSERVED_CANDIDATE_ANDROID_VULKAN_BUNDLE",run_id="fixture",unity_version="2021.3.45f2",errors=0,shader_name=self.c["shader_name"],android_vulkan_only=True,editor_graphics_api="Vulkan",candidate_sha256=g.p.sha(self.shader),contract_sha256=g.p.sha(self.contract),bundle_sha256=g.p.sha(self.bundle),bundle_bytes=len(self.bundle),original_assets_read=False,pass_count=1,error="",scopes=[dict(name=x["name"],overridable=x["scope"]=="global") for x in self.c["scopes"]],observations=[dict(pass_name=w.PASS,pass_type="Normal",stage=s,platform="Vulkan",keywords=v["keywords"]) for v in self.c["passes"][0]["variants"] for s in ("Vertex","Fragment")])
        names=[x["name"] for x in self.c["scopes"]];flags=[x["source_flag"] for x in self.c["scopes"]]
        table=[dict(m_KeywordIndices=[names.index(n) for n in v["keywords"]],m_BlobIndex=i) for i,v in enumerate(self.c["passes"][0]["variants"])]
        state={"m_Name":w.PASS,"m_Tags":{"tags":[["LightMode","Always"]]}}
        self.parsed={"m_Name":w.SHADER,"m_KeywordNames":names,"m_KeywordFlags":flags,"m_SubShaders":[{"m_Passes":[{"m_Type":0,"m_State":state,"progVertex":{"m_SubPrograms":table},"progFragment":{"m_SubPrograms":[]}}]}]}
        self.entries=[(0,bytes([i])) for i in range(4)]
        self.decode=lambda b:[dict(sha256=g.p.sha(b+bytes([model])),model=model,marker_constants=[(11 if model==0 else 21)+b[0]],spirv_val_exit=0) for model in (0,4)]
    def check(self,r=None):return g.check_receipt(self.c,self.r if r is None else r,self.shader,self.contract,self.bundle,"fixture")
    def decoded(self,q=None,**kw):return g.verify_parsed(self.c,self.parsed if q is None else q,self.entries,self.decode,**kw)
    def test_exact_callback_receipt(self):
        self.assertEqual(self.check()["observed_callback_route_stage_count"],8)
    def test_wrong_candidate_bundle_and_contract_bytes(self):
        for key in ("candidate_sha256","contract_sha256","bundle_sha256"):
            r=deepcopy(self.r);r[key]="0"*64
            with self.assertRaises(ValueError):self.check(r)
    def test_wrong_pass_type_scope_and_missing_stage(self):
        for mutate in (lambda r:r["observations"][0].update(pass_type="ForwardAdd"),lambda r:r["scopes"][0].update(overridable=not r["scopes"][0]["overridable"]),lambda r:r["observations"].pop()):
            r=deepcopy(self.r);mutate(r)
            with self.assertRaises(ValueError):self.check(r)
    def test_wrong_active_keyword_not_projected(self):
        r=deepcopy(self.r);r["observations"][0]["keywords"].append("OTHER")
        with self.assertRaisesRegex(ValueError,"unmapped_exact"):self.check(r)
    def test_exact_combined_stage_marker_rows(self):
        d=self.decoded(authored_marker_mode=True)
        w.verify_marker_rows(d["rows"]);self.assertTrue(all(r["combined_table"] for r in d["rows"]))
        self.assertFalse(d["original_runtime_verified"])
    def test_separate_scope_indices_unproved(self):
        q=deepcopy(self.parsed);q["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_SubPrograms"][0]["m_LocalKeywordIndices"]=[0]
        with self.assertRaisesRegex(ValueError,"scope_unproved"):self.decoded(q,authored_marker_mode=True)
    def test_unknown_keyword_and_missing_blob_stage(self):
        q=deepcopy(self.parsed);q["m_KeywordNames"].append("OTHER");q["m_KeywordFlags"].append(0)
        with self.assertRaisesRegex(ValueError,"unproved_extra"):self.decoded(q,authored_marker_mode=True)
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous_stage"):
            g.verify_parsed(self.c,self.parsed,self.entries,lambda b:self.decode(b)[:1],authored_marker_mode=True)
    def test_wrong_serialized_pass_name_mode_and_type(self):
        for k,value in (("m_Name","WRONG"),("m_Tags",{"tags":[["LightMode","ForwardAdd"]]})):
            q=deepcopy(self.parsed);q["m_SubShaders"][0]["m_Passes"][0]["m_State"][k]=value
            with self.assertRaisesRegex(ValueError,"pass_state_drift"):self.decoded(q,authored_marker_mode=True)
    def test_independent_program_commitment_required(self):
        with self.assertRaisesRegex(ValueError,"independent_stage_identity"):self.decoded()
        d=self.decoded(authored_marker_mode=True)
        expect={(r["pass_index"],tuple(r["keywords"]),r["stage"],r["source_ref"]):r["module"]["sha256"] for r in d["rows"]}
        self.assertTrue(self.decoded(expected_modules=expect)["source_flag_bytes_compared"])
        expect[next(iter(expect))]="0"*64
        with self.assertRaisesRegex(ValueError,"program_identity_mismatch"):self.decoded(expected_modules=expect)
    def test_route_swap_with_same_counts_rejected(self):
        q=deepcopy(self.parsed);rows=q["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_SubPrograms"]
        rows[0]["m_BlobIndex"],rows[1]["m_BlobIndex"]=rows[1]["m_BlobIndex"],rows[0]["m_BlobIndex"]
        with self.assertRaisesRegex(ValueError,"marker_mismatch"):w.verify_marker_rows(self.decoded(q,authored_marker_mode=True)["rows"])
    def test_missing_pass_name_blocks(self):
        m=deepcopy(self.manifest);s=m["original_shader_ParsedForm_full_private"]["m_SubShaders"][0]["m_Passes"][0]["m_State"];s.pop("m_Name");m["original_passes"][0]["original_state"]=s
        p=deepcopy(self.proof);p["manifest_sha256"]=g.p.commitment(m);p["passes"][0]["pass_state_sha256"]=g.p.commitment(s)
        with self.assertRaisesRegex(ValueError,"unique_named_source_pass"):g.contract(m,self.packet,p,self.shader)
    def test_editor_OpenGL_or_missing_graphics_api_rejected(self):
        for value in ("OpenGLCore",None):
            r=deepcopy(self.r)
            if value is None:r.pop("editor_graphics_api")
            else:r["editor_graphics_api"]=value
            with self.assertRaisesRegex(ValueError,"receipt_or_bytes_mismatch"):self.check(r)
    def test_receipt_cannot_authorize(self):
        self.assertFalse(self.decoded(authored_marker_mode=True)["installation_allowed"])
if __name__=="__main__":unittest.main()
