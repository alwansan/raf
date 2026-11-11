#!/usr/bin/env python3
"""GFX102 original-free code and analytical shader-version discrimination tests.

Runs in CI without Unity, private Raft source, phone data, or emulator.
"""
import unittest
from pathlib import Path

ROOT=Path("gfxlab/android-gles-qualifier-probe-v102")
JAVA=ROOT/"src/com/alwansan/gfx102/MainActivity.java"
MANIFEST=ROOT/"AndroidManifest.xml"
WORKFLOW=Path(".github/workflows/gfxlab-multi102-qualifier-version-matrix-apk.yml")
W=(.55,1.,2.7)
VERTICES=((-0.86,-.77),(0.86,-.77),(0.0,.86))
POINTS=((128,98),(104,108),(152,108))

def barycentric(x,y):
    X=2*(x+.5)/256.-1
    Y=2*(y+.5)/256.-1
    (x0,y0),(x1,y1),(x2,y2)=VERTICES
    den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
    a=((y1-y2)*(X-x2)+(x2-x1)*(Y-y2))/den
    b=((y2-y0)*(X-x2)+(x0-x2)*(Y-y2))/den
    return (a,b,1-a-b)

def smooth(a):
    raw=[x/w for x,w in zip(a,W)]
    k=sum(raw)
    return tuple(x/k for x in raw)

class GFX102Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=JAVA.read_text()
        cls.manifest=MANIFEST.read_text()
        cls.workflow=WORKFLOW.read_text()
    def test_exact_distinct_android_package(self):
        self.assertIn('package com.alwansan.gfx102;',self.src)
        self.assertIn('package="com.alwansan.gfx102"',self.manifest)
        self.assertIn('android:minSdkVersion="29"',self.manifest)
        self.assertIn('GFX-MULTI-102',self.src)
    def test_three_native_glsl_version_candidates_present(self):
        for n in (300,310,320):
            self.assertIn('NativeNoPerspectiveES'+str(n),self.src)
        self.assertIn('mode.endsWith("ES320")?320:mode.endsWith("ES310")?310:300',self.src)
        self.assertIn('String head="#version "+glslVersion+" es\\n"+',self.src)
        self.assertIn('int bestNativeVersion=-1;',self.src)
        self.assertIn('native_glsl_version_trials',self.src)
    def test_advertised_extension_required_and_native_fail_closed(self):
        self.assertIn('GL_NV_shader_noperspective_interpolation',self.src)
        self.assertIn('GLES30.glGetStringi(GLES30.GL_EXTENSIONS,i)',self.src)
        self.assertIn('" : require\\n"',self.src)
        self.assertIn('mode.startsWith("NativeNoPerspective")&&!nativeExtension',self.src)
        self.assertIn('NATIVE_EXTENSION_ADVERTISED_BUT_ALL_GLSL_VERSIONS_FAILED',self.src)
    def test_controls_independent_of_version_sweep(self):
        for mode in ('Smooth','Flat','AffineEmulated'):
            self.assertIn('"'+mode+'"',self.src)
        self.assertIn('control_flat_stable',self.src)
        self.assertIn('control_affine_emulated_matches_cpu',self.src)
        self.assertIn('cpu_affine_mad',self.src)
        self.assertIn('cpu_smooth_mad',self.src)
    def test_all_native_version_results_have_separate_filename(self):
        self.assertIn('String name="gpu-"+mode+".png";',self.src)
        self.assertIn('sha256(out.raw)',self.src)
        self.assertIn('summary.put("results",outputs)',self.src)
    def test_reference_triangle_separates_perspective_and_affine(self):
        for point in POINTS:
            lam=barycentric(*point)
            self.assertTrue(all(0<x<1 for x in lam))
            persp=smooth(lam)
            mad=sum(abs(x-y) for x,y in zip(lam,persp))/3
            self.assertGreater(mad,.12)
    def test_export_and_no_false_restore(self):
        for x in ('MediaStore.Downloads.RELATIVE_PATH',
                  'MediaStore.Downloads.SIZE',
                  '"Download/Games/cl/test/g/"',
                  '"originalShaderRestored",false',
                  '"originalAnimationRestored",false',
                  '"phase_closed",false'):
            self.assertIn(x,self.src)
        for x in ('Raft_Data','UnityShaderCache','source-zip2'):
            self.assertNotIn(x,self.src)
    def test_signing_workflow_safety(self):
        for x in ('apksigner','aapt2','zipalign','d8','com.alwansan.gfx102',
                  'gfx102-safe-delivery.json','cancel-in-progress: false',
                  'original_shader_restored'):
            self.assertIn(x,self.workflow)
        self.assertIn("python3 -m unittest discover",self.workflow)

if __name__=="__main__": unittest.main()
