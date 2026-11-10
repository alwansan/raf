"""GFX-MULTI-040 static contracts for a fully synthetic Android diagnostic.

Never treat successful APK packaging or synthetic GPU samples as authentic
Raft Shader48 resource mapping or PC/Adreno pixel parity.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"unity"/"Assets"


class TestSyntheticAndroidInterpolationProbe(unittest.TestCase):
    def test_all_three_shader_sources_are_authored_and_independent(self):
        modes={
            "Linear":"",
            "Flat":"nointerpolation float3 probe",
            "NoPerspective":"noperspective float3 probe"
        }
        for mode,qualifier in modes.items():
            with self.subTest(mode=mode):
                data=(ASSETS/"Shaders"/f"GfxLabInterpolation{mode}.shader").read_text()
                self.assertIn('Shader "Hidden/GfxLab/Interpolation'+mode+'"',data)
                self.assertIn("#pragma vertex vert",data)
                self.assertIn("#pragma fragment frag",data)
                self.assertIn("#pragma target 4.0",data)
                self.assertIn("v.vertex.xy * w",data)
                self.assertIn("v.color.rgb",data)
                self.assertIn("Fallback Off",data)
                self.assertIn("NOT Raft Shader48",data)
                if qualifier:self.assertIn(qualifier,data)
                if mode=="Linear":
                    self.assertNotIn("nointerpolation float3",data)
                    self.assertNotIn("noperspective float3",data)

    def test_android_probe_records_real_gpu_pixel_readback_not_fake_fps(self):
        code=(ASSETS/"Scripts"/"GfxInterpolationProbe.cs").read_text()
        for token in ("Graphics.ExecuteCommandBuffer(cmd)",
                      "pixels.ReadPixels(", "pixels.EncodeToPNG()",
                      "gpuReadbackCompleted=true",
                      "sampledColors","perspectiveVsNoPerspectiveDistinguishable",
                      "flatConstantAcrossInteriorSamples",
                      "GfxSessionRecorder", "ExportAll(out publicPath,out error)",
                      'Path.Combine(recorder.RootDirectory,"sessions",recorder.SessionId)',
                      "Download/Games/cl/test/g/",
                      "originalShaderRestored=false",
                      "originalPcPixelParityVerified=false",
                      "ORIGINAL", "INCONCLUSIVE_UNSUPPORTED_OR_NO_COLORED_PIXELS"):
            self.assertIn(token,code)
        self.assertNotIn("m_ProgramCode",code)

    def test_builder_uses_unique_package_and_no_zip2_original_assets(self):
        code=(ASSETS/"Editor"/"GfxInterpolationAndroidBuilder.cs").read_text()
        for token in (
                'com.alwansan.raft.graphicslab.interpolation',
                "GfxLab-Interpolation-GPUProbe.apk",
                "GfxInterpolationProbe.unity",
                "GfxInterpolationProbe",
                "GfxSessionRecorder",
                "OpenGLES3","AndroidArchitecture.ARM64",
                "UIOrientation.LandscapeLeft","ColorSpace.Linear",
                "original_shader_restored=false"):
            self.assertIn(token,code)
        self.assertNotIn("source-zip2",code)
        self.assertNotIn("Assets/MultiModels",code)
        self.assertNotIn("sourceShader",code)

    def test_public_mediastore_exporter_is_reused_and_scoped(self):
        c=(ASSETS/"Scripts"/"GfxDownloadsZipExporter.cs").read_text()
        bridge=(ASSETS/"Plugins"/"Android"/"GfxDownloadsBridge.java").read_text()
        self.assertIn('Download/Games/cl/test/g/',c)
        self.assertIn("sessions/",c)
        self.assertIn("ZipArchive(",c)
        self.assertIn("MediaStore.Downloads.EXTERNAL_CONTENT_URI",bridge)
        self.assertIn("MediaStore.MediaColumns.RELATIVE_PATH",bridge)
        self.assertNotIn("MANAGE_EXTERNAL_STORAGE",bridge)
