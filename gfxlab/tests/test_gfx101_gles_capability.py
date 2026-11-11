"""GFX101 source-free contracts and independent geometry controls.

Run with: python3 -m unittest gfxlab.tests.test_gfx101_gles_capability -v
Does not use proprietary Raft data, an owner APK or a device emulator.
"""
import math
import re
import unittest
from pathlib import Path

SOURCE=Path("gfxlab/android-gles-qualifier-probe/src/com/alwansan/gfx101/MainActivity.java")
MANIFEST=Path("gfxlab/android-gles-qualifier-probe/AndroidManifest.xml")
WORKFLOW=Path(".github/workflows/gfxlab-multi101-gles-native-interpolation-apk.yml")

W=(0.55,1.0,2.7)
XY=((-0.86,-0.77),(0.86,-0.77),(0.0,0.86))
SAMPLES=((128,98),(104,108),(152,108))

def barycentric(x,y):
    px=2*(x+.5)/256-1
    py=2*(y+.5)/256-1
    (x0,y0),(x1,y1),(x2,y2)=XY
    det=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
    a=((y1-y2)*(px-x2)+(x2-x1)*(py-y2))/det
    b=((y2-y0)*(px-x2)+(x0-x2)*(py-y2))/det
    return (a,b,1-a-b)

def colors(x,y,smooth):
    bc=barycentric(x,y)
    if not smooth:return bc
    vals=[c/w for c,w in zip(bc,W)]
    scale=sum(vals)
    return tuple(c/scale for c in vals)

class Gfx101GlesCapabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=SOURCE.read_text()
        cls.manifest=MANIFEST.read_text()
    def test_extensions_must_be_enumerated_on_real_gl_thread(self):
        self.assertIn("onDrawFrame(GL10 unused)",self.src)
        self.assertIn("GLES30.glGetStringi(GLES30.GL_EXTENSIONS,i)",self.src)
        self.assertIn("GL_NV_shader_noperspective_interpolation",self.src)
    def test_unadvertised_extension_never_compiled(self):
        self.assertRegex(self.src,r'if\(mode\.equals\("NativeNoPerspective"\)&&!nativeExtension\)')
        self.assertIn("capability_skip",self.src)
        self.assertIn(" : require",self.src)
    def test_controls_are_separate_native_affine_smooth_flat(self):
        for mode in ("Smooth","Flat","AffineEmulated","NativeNoPerspective"):
            self.assertIn('"'+mode+'"',self.src)
        self.assertIn("vWeighted/max(vClipW,0.00001)",self.src)
        self.assertIn("smooth out vec3 vWeighted",self.src)
        self.assertIn("flat out vec3 vColor",self.src)
        self.assertIn("noperspective out vec3 vColor",self.src)
    def test_triangle_has_interior_samples(self):
        for x,y in SAMPLES:
            bc=barycentric(x,y)
            self.assertTrue(all(0.0<c<1.0 for c in bc),str((x,y,bc)))
            self.assertAlmostEqual(sum(bc),1.0,places=12)
    def test_analytic_affine_and_perspective_differ_significantly(self):
        differences=[sum(abs(a-b) for a,b in zip(colors(x,y,False),colors(x,y,True)))/3
            for x,y in SAMPLES]
        self.assertTrue(all(x>0.08 for x in differences),str(differences))
    def test_identity_and_sha_evidence_fail_closed(self):
        for text in ("originalShaderRestored\",\"false","phase_closed\",\"false",
                     "pcAdrenoPixelParityVerified\",\"false","sha256(out.raw)",
                     "cpu_affine_mad","cpu_smooth_mad"):
            self.assertIn(text,self.src)
    def test_scoped_export_android_15(self):
        self.assertIn('\"Download/Games/cl/test/g/\"',self.src)
        self.assertIn("MediaStore.Downloads.RELATIVE_PATH",self.src)
        self.assertIn("MediaStore.Downloads.SIZE",self.src)
        self.assertIn("IS_PENDING",self.src)
        self.assertIn('android:minSdkVersion="29"',self.manifest)
        self.assertIn('package="com.alwansan.gfx101"',self.manifest)
    def test_never_bundle_original_raft_asset(self):
        for forbidden in ("/zip2/","Raft_Data","UnityShaderCache","source-zip2"):
            self.assertNotIn(forbidden,self.src)
        self.assertNotIn("READ_EXTERNAL_STORAGE",self.manifest)
        self.assertNotIn("INTERNET",self.manifest)
    def test_workflow_requires_apksigner_and_device_pending(self):
        workflow=WORKFLOW.read_text()
        self.assertIn("apksigner",workflow)
        self.assertIn("aapt2",workflow)
        self.assertIn("original_shader_restored",workflow)
        self.assertIn("original_shader_restored\":False",workflow)
        self.assertIn("cancel-in-progress: false",workflow)

if __name__=="__main__":
    unittest.main()
