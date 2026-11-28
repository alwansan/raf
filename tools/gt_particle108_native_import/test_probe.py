import copy
import unittest
from tools.gt_particle108_native_import import probe as p

def fixture():
    s=dict(m_FilterMode=1,m_Aniso=1,m_MipBias=0,m_WrapU=0,m_WrapV=0,m_WrapW=0)
    cfg=dict(run_id="test",guid="authored",file_id=2800000,source_color_space=1,source_sampler=s,mips=[],
             export_basename_preserved=True,export_stem_matches_serialized_name=True)
    r=dict(status="OBSERVED",run_id="test",unity_version="2021.3.45f2",backend="Vulkan",color_space="Linear",device="fixture",
           guid="authored",file_id=2800000,native_importer=True,texture_loaded=True,private_log_guard=True,
           importer_kind="native_format",width=64,height=64,mip_count=7,texture_format="RGBA32",
           filter_mode=1,aniso=1,wrap_u=0,wrap_v=0,wrap_w=0,mip_bias=0,graphics_format="fixture",srgb=False,readable=True,
           mips=[],force_zero=[.25],force_one=[1.])
    for i,n in enumerate(p.LENGTHS):
        size=64>>i;a=[(j+17*i)%256 for j in range(size*size)]
        sha=p.digest(bytes(n))
        cfg["mips"].append(dict(level=i,size=size,alpha=a,sha256=sha))
        r["mips"].append(dict(level=i,size=size,cpu_bytes=n,cpu_sha256=sha,alpha=[p.blend(x) for x in a]))
    return cfg,r

class Tests(unittest.TestCase):
    def test_complete(self):
        c,r=fixture();d=p.evaluate(c,r,True,0)
        self.assertEqual(d["status"],p.PASS);self.assertEqual(d["original_alpha_texels_checked"],5461)
        self.assertNotIn("authored",str(d));self.assertNotIn("cpu_sha256",str(d))
    def test_last_mip_byte_drift(self):
        c,r=fixture();r["mips"][6]["cpu_sha256"]="wrong"
        d=p.evaluate(c,r,True,0);self.assertEqual(d["imported_cpu_mips_equal"],6);self.assertNotEqual(d["status"],p.PASS)
    def test_last_mip_alpha_drift(self):
        c,r=fixture();r["mips"][6]["alpha"]=[1.]
        d=p.evaluate(c,r,True,0);self.assertEqual(d["actual_vulkan_mips_equal"],6);self.assertNotEqual(d["status"],p.PASS)
    def test_no_fake_backend_or_pointer(self):
        for k,v in (("backend","OpenGL"),("file_id",2),("guid","wrong"),("native_importer",False),("filter_mode",2)):
            c,r=fixture();r[k]=v;self.assertNotEqual(p.evaluate(c,r,True,0)["status"],p.PASS)
    def test_no_readability_override_or_modified_asset(self):
        c,r=fixture();r["readable"]=False
        self.assertNotEqual(p.evaluate(c,r,True,0)["status"],p.PASS)
        c,r=fixture();self.assertNotEqual(p.evaluate(c,r,False,0)["status"],p.PASS)
    def test_no_nonfinite_or_missing_mip(self):
        c,r=fixture();r["mips"][2]["alpha"][0]=float("nan");self.assertNotEqual(p.evaluate(c,r,True,0)["status"],p.PASS)
        c,r=fixture();r["mips"].pop();self.assertNotEqual(p.evaluate(c,r,True,0)["status"],p.PASS)
    def test_controls_and_run_binding(self):
        c,r=fixture();r["force_zero"]=[1.];self.assertNotEqual(p.evaluate(c,r,True,0)["status"],p.PASS)
        c,r=fixture();r["run_id"]="stale";self.assertNotEqual(p.evaluate(c,r,True,0)["status"],p.PASS)
        c,r=fixture();self.assertNotEqual(p.evaluate(c,r,True,1)["status"],p.PASS)
    def test_private_log_guard_missing_rejected(self):
        c,r=fixture();r["private_log_guard"]=False
        self.assertEqual(p.evaluate(c,r,True,0)["reason"],"private_editor_log_guard_missing")
    def test_exact_export_basename_and_unsupported_extension(self):
        from pathlib import Path
        self.assertEqual(p.native_asset_path(Path("private/Original.texture2D")),"Assets/GTSource/Original.texture2D")
        with self.assertRaises(ValueError):p.native_asset_path(Path("private/Original.png"))
    def test_partial_import_phase_and_no_identity_leak(self):
        c,r=fixture();r["status"]="INCONCLUSIVE";r["phase"]="file_id_match";r["file_id"]=99
        d=p.evaluate(c,r,True,1)
        self.assertFalse(d["unity_import_verified"]);self.assertEqual(d["editor_phase"],"file_id_match")
        self.assertTrue(d["imported_guid_matches"]);self.assertFalse(d["imported_file_id_matches"])
        self.assertNotIn("authored",str(d))
    def test_generic_importer_keeps_actual_mip_measurement_but_not_pass(self):
        c,r=fixture();r["native_importer"]=False;r["importer_kind"]="generic_asset"
        d=p.evaluate(c,r,True,0)
        self.assertEqual(d["actual_vulkan_mips_equal"],7);self.assertFalse(d["unity_import_verified"])
        self.assertNotEqual(d["status"],p.PASS)
def diag_fixture():
    c,r=fixture()
    r["sampler_unchanged_after_draws"]=True;r["original_texture_rebound"]=True
    for e,m in zip(c["mips"],r["mips"]):
        m["load_alpha"]=[p.blend(v) for v in e["alpha"]]
        m["point_alpha"]=m["load_alpha"][:]
    r["calibration"]=[]
    for i in range(4):
        size=8>>i;a=[p.blend(11+41*i+7*x+3*y) for y in range(size) for x in range(size)]
        r["calibration"].append(dict(level=i,size=size,load_alpha=a,point_alpha=a[:]))
    r["calibration_wrong_mip"]=[p.blend(11)]
    return c,r

class DiagnosticTests(unittest.TestCase):
    def test_sampler_difference_not_storage_loss(self):
        c,r=diag_fixture();r["native_importer"]=False;r["importer_kind"]="generic_asset";r["readable"]=False
        r["mips"][0]["alpha"][0]=.8
        d=p.diagnostic(c,r,p.evaluate(c,r,True,0))
        self.assertEqual(d["status"],p.DIAGNOSTIC)
        self.assertEqual(d["interpretation"],"EXACT_GPU_ALPHA_VIA_LOAD_AND_POINT_ORIGINAL_SAMPLER_DIFFERS")
        self.assertEqual(d["actual_original_alpha_readbacks"],16383)
        self.assertFalse(d["full_native_acceptance"])
    def test_load_point_same_different_source(self):
        c,r=diag_fixture();r["mips"][0]["load_alpha"][0]=.8;r["mips"][0]["point_alpha"][0]=.8
        d=p.diagnostic(c,r,p.evaluate(c,r,True,0))
        self.assertEqual(d["interpretation"],"GPU_LOAD_AND_POINT_AGREE_BUT_SOURCE_ALPHA_DIFFERS")
    def test_wrong_mip_control_rejected(self):
        c,r=diag_fixture();r["calibration_wrong_mip"]=[p.blend(134)]
        self.assertNotEqual(p.diagnostic(c,r,p.evaluate(c,r,True,0))["status"],p.DIAGNOSTIC)
    def test_asymmetric_calibration_and_mip_drift(self):
        c,r=diag_fixture();r["calibration"][0]["point_alpha"].reverse()
        self.assertNotEqual(p.diagnostic(c,r,p.evaluate(c,r,True,0))["status"],p.DIAGNOSTIC)
    def test_original_sampler_mutation_rejected(self):
        c,r=diag_fixture();r["sampler_unchanged_after_draws"]=False
        self.assertNotEqual(p.diagnostic(c,r,p.evaluate(c,r,True,0))["status"],p.DIAGNOSTIC)
    def test_private_scope_and_unchanged_required(self):
        c,r=diag_fixture();self.assertNotEqual(p.diagnostic(c,r,p.evaluate(c,r,False,0))["status"],p.DIAGNOSTIC)
        r["private_log_guard"]=False
        self.assertNotEqual(p.diagnostic(c,r,p.evaluate(c,r,True,0))["status"],p.DIAGNOSTIC)
    def test_all_three_routes_and_no_identifiers(self):
        c,r=diag_fixture();d=p.diagnostic(c,r,p.evaluate(c,r,True,0))
        self.assertEqual(d["interpretation"],"ALL_THREE_GPU_ALPHA_ROUTES_MATCH_SOURCE")
        self.assertNotIn("authored",str(d));self.assertNotIn("cpu_sha256",str(d))
if __name__=="__main__":unittest.main()
