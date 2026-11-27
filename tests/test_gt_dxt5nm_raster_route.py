import unittest
from scripts import gt_dxt5nm_raster_route as v

class RasterOracleTests(unittest.TestCase):
    def test_geometry_known_pixel(self):
        kind,uv=v.geometry(0,0,0,"bottom_first")
        self.assertEqual(kind,"inside")
        self.assertAlmostEqual(uv[0],1/24);self.assertAlmostEqual(uv[1],1/32)
    def test_geometry_outside(self):
        self.assertEqual(v.geometry(0,31,15,"bottom_first"),("outside",None))
    def test_orientation_anchor(self):
        self.assertEqual(v.geometry(0,0,0,"bottom_first"),v.geometry(0,0,15,"top_first"))
        self.assertNotEqual(v.geometry(0,0,0,"bottom_first"),v.geometry(0,0,0,"top_first"))
    def test_transform_and_repeat_point(self):
        st=[2,.75,.25,.25]
        self.assertEqual(v.transformed((.5,.5),st),(1.25,.625))
        b=bytes((1,2,3,4,5,6,7,8))
        self.assertEqual(v.point_load((1.75,.25),2,1,b),tuple(x/255 for x in (5,6,7,8)))
    def test_texel_boundary_not_rounded(self):
        self.assertIsNone(v.point_load((.5,.25),2,1,bytes(8)))
    def test_DXT5nm_decode(self):
        self.assertEqual(v.unpack((1,.5,.5,.5),.25),(0,0,1,.25))
        self.assertEqual(v.unpack((1,1,1,1),.75),(1,1,0,.75))
    def test_V16_receipt_exact_mips(self):
        p=v.prior()
        self.assertEqual(len(p["rows"]),2)
        for r in p["rows"]:
            self.assertEqual([len(bytes.fromhex(x)) for x in r["actual_mip_RGBA_hex"]],[140,24,4])
            self.assertEqual([v.digest(bytes.fromhex(x)) for x in r["actual_mip_RGBA_hex"]],r["actual_mip_sha256"])
    def test_diagnostic_shader_distinct_markers(self):
        a,b=v.shader_bytes(0),v.shader_bytes(1)
        self.assertIn(b"const float marker=0.25",a);self.assertIn(b"const float marker=0.75",b)
        self.assertIn(b"_MainTex.Load",a);self.assertNotIn(b"tex2Dlod",a)
    def test_cpu_constructed_UV_oracle_rejects_wrong_orientation(self):
        st=[1,.75,.125,.25];values=[]
        for n in range(v.W*v.H):
            kind,uv=v.geometry(0,n%v.W,n//v.W,"bottom_first")
            values.extend((*uv,*v.transformed(uv,st)) if kind=="inside" else v.CLEAR)
        self.assertGreater(v.uv_oracle(0,st,"bottom_first",values)[0],70)
        with self.assertRaises(ValueError):v.uv_oracle(0,st,"top_first",values)
    def test_cpu_constructed_color_oracle_rejects_corruption(self):
        p=v.prior();data=bytes.fromhex(p["rows"][0]["actual_mip_RGBA_hex"][0]);st=[1,.75,.125,.25];values=[]
        for n in range(v.W*v.H):
            kind,uv=v.geometry(0,n%v.W,n//v.W,"bottom_first")
            q=v.point_load(v.transformed(uv,st),5,7,data) if kind=="inside" else None
            values.extend(q if q is not None else ((0.,)*4 if kind=="inside" else v.CLEAR))
        checked,_=v.color_oracle(0,st,"bottom_first",values,data,0)
        self.assertGreater(len(checked),40)
        values[4*checked[0]]=99
        with self.assertRaises(ValueError):v.color_oracle(0,st,"bottom_first",values,data,0)
if __name__=="__main__":unittest.main()
