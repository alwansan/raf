import copy
import unittest
from tools.gt_particle108_native_import import probe as p

def fixture():
    s=dict(m_FilterMode=1,m_Aniso=1,m_MipBias=0,m_WrapU=0,m_WrapV=0,m_WrapW=0)
    cfg=dict(run_id="test",guid="authored",file_id=2800000,source_color_space=1,source_sampler=s,mips=[])
    r=dict(status="OBSERVED",run_id="test",unity_version="2021.3.45f2",backend="Vulkan",color_space="Linear",device="fixture",
           guid="authored",file_id=2800000,native_importer=True,width=64,height=64,mip_count=7,texture_format="RGBA32",
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
if __name__=="__main__":unittest.main()
