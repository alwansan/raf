import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class TestGpuChannelProbeContract(unittest.TestCase):
    def test_original_shader_never_claimed_in_probe(self):
        viewer=(ROOT/"gfxlab/unity/Assets/Scripts/GfxMultiViewer.cs").read_text()
        self.assertIn('DIAGNOSTIC_SHADER_NOT_SOURCE_SHADER48',viewer)
        self.assertIn('coloredPixelsAutomaticallyVerified=false',viewer)
        self.assertIn('originalShaderRestored=m.exactShaderRestored',viewer)
        self.assertIn('diagnosticShaderSupported',viewer)
        self.assertIn('GFX-MULTI-026',viewer)
    def test_probed_texture_roles_and_sampling_controls(self):
        builder=(ROOT/"gfxlab/unity/Assets/Editor/GfxMultiAndroidBuilder.cs").read_text()
        viewer=(ROOT/"gfxlab/unity/Assets/Scripts/GfxMultiViewer.cs").read_text()
        for x in ("basecolorSource","basecolorLinear","normalSource","normalLinear","metallicSource","metallicLinear"):
            self.assertIn(x,builder)
            self.assertIn(x,viewer)
        self.assertIn('importer.sRGBTexture=!forceLinear && role!="normal"',builder)
        self.assertIn('imp.textureType=role=="normal" ? TextureImporterType.NormalMap',builder)
        self.assertIn("FORCE_LINEAR_IMPORT",viewer)
        self.assertIn("SOURCE_TEXTURE_COLORSPACE_IMPORT",viewer)
    def test_probe_shader_is_not_original(self):
        shader=(ROOT/"gfxlab/unity/Assets/Shaders/GfxLabChannelProbe.shader").read_text()
        for fragment in ("Hidden/GfxLab/ChannelProbe","ZWrite Off","ZTest Always","Cull Off","tex2D(_MainTex","sampled.aaa","sampled.rrr","sampled.ggg","sampled.bbb"):
            self.assertIn(fragment,shader)
        self.assertNotIn("Shader48",shader)
    def test_only_diagnostic_package_produced(self):
        builder=(ROOT/"gfxlab/unity/Assets/Editor/GfxMultiAndroidBuilder.cs").read_text()
        self.assertIn("com.alwansan.raft.graphicslab.channels",builder)
        self.assertIn("GfxLab-Multi-Six-Channel-Probe.apk",builder)
        self.assertIn("original_shader_exact=false",builder)
        self.assertIn("GFX_MULTI_SOURCE_TRIANGLE_PARITY_FAIL_",builder)
