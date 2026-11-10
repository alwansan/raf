"""GFX-MULTI-041 source-free algebra and app contract tests.

Verifies smooth interpolation of (color*clipW) / (clipW) equals
screen-space affine interpolation without native noperspective support.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"unity"/"Assets"


def barycentric(px,py):
    x=(2*(px+0.5)/256)-1
    y=(2*(py+0.5)/256)-1
    ax,ay=-.86,-.77
    bx,by=.86,-.77
    cx,cy=0,.86
    den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    r=((by-cy)*(x-cx)+(cx-bx)*(y-cy))/den
    g=((cy-ay)*(x-cx)+(ax-cx)*(y-cy))/den
    return r,g,1-r-g


def reference_colors(px,py):
    affine=barycentric(px,py)
    w=(.55,1.,2.7)
    denom=sum(a/wi for a,wi in zip(affine,w))
    perspective=tuple(a/wi/denom for a,wi in zip(affine,w))
    weighted=tuple(a*wi for a,wi in zip(affine,w))
    # The GPU interpolates color_i*W_i and W_i using perspective correction.
    interp_colorw=tuple(affine[i]*1.0/denom for i in range(3))
    interp_w=sum(affine[i]*w[i]/w[i] for i in range(3))/denom
    emulated=tuple(p/interp_w for p in interp_colorw)
    return affine,perspective,emulated


class TestGfxMulti041AffineReference(unittest.TestCase):
    def test_screen_space_affine_emulation_is_exact_without_extension(self):
        for xy in ((128,98),(104,108),(152,108)):
            with self.subTest(pixel=xy):
                affine,smooth,emulated=reference_colors(*xy)
                for a,b in zip(affine,emulated):
                    self.assertAlmostEqual(a,b,places=12)
                self.assertGreater(sum(abs(x-y) for x,y in zip(affine,smooth))/3,.13)

    def test_no_native_noperspective_qualifier_in_affine_emulation(self):
        shader=(ASSETS/"Shaders"/"GfxLabInterpolationAffineEmulated.shader").read_text()
        for s in ("Hidden/GfxLab/InterpolationAffineEmulated",
                  "weightedProbe=v.color.rgb*w",
                  "o.clipW=w",
                  "i.weightedProbe/max(i.clipW,0.00001)",
                  "#pragma target 3.0"):
            self.assertIn(s,shader)
        self.assertNotIn("nointerpolation float3",shader)
        self.assertNotIn("noperspective float3",shader)

    def test_four_gpu_cases_cpu_reference_and_diagnostics(self):
        code=(ASSETS/"Scripts"/"GfxAffineReferenceProbe.cs").read_text()
        for token in (
            'experiment="GFX-MULTI-041"',
            '"Linear","Flat","NoPerspective","AffineEmulated"',
            "new Texture2D[4]", "new CaseResult[4]",
            "CpuExpected(", "MeanCpuError(",
            "gpuLinearVsCpuPerspectiveError",
            "gpuAffineEmulatedVsCpuAffineError",
            "gpuNativeVsCpuAffineError",
            "gpuNativeVsLinearError",
            "DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH",
            "DIAGNOSTIC_NATIVE_NOPERSPECTIVE_MATCHES_AFFINE",
            "Graphics.ExecuteCommandBuffer(cmd)",
            "pixels.ReadPixels(",
            "pixels.EncodeToPNG()",
            "GfxDownloadsZipExporter.ExpectedPublicDirectory",
            "originalRaftShaderBytecodeUsed=false",
            "originalPcPixelParityVerified=false",
        ):
            self.assertIn(token,code)
        self.assertNotIn("m_ProgramCode",code)

    def test_distinct_signed_android_build_and_shader_assets(self):
        code=(ASSETS/"Editor"/"GfxAffineReferenceAndroidBuilder.cs").read_text()
        for token in (
            "RaftGraphicsLabEditor",
            "GfxAffineReferenceAndroidBuilder",
            "GfxLab-AffineReference-GPUProbe.apk",
            "com.alwansan.raft.graphicslab.affinereference",
            'materials[3]=DiagnosticMaterial("AffineEmulated");',
            "root.AddComponent<GfxAffineReferenceProbe>()",
            "OpenGLES3","AndroidArchitecture.ARM64",
            "GfxSessionRecorder", "original_shader_restored=false",
        ):
            self.assertIn(token,code)
        self.assertNotIn("source-zip2",code)
        self.assertNotIn("Assets/MultiModels",code)
