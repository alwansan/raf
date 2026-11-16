"""Protect source original-name ownership from later real same-export install census.

Source SHA/PathID selection for NEXT18/NEXT17 is authenticated against post14
216/46. Install eligibility requires an independent later same-export quality
report. This test costs no ZIP2 download, LFS, game files or Unity license.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/".github"/"workflows"

NEXT18="raft-gt-next18-original-full-export.yml"
NEXT17="raft-gt-next17-original-full-export.yml"


def step(content, step_name):
    marker="      - name: "+step_name+"\n"
    start=content.find(marker)
    if start<0:
        raise ValueError("missing_required_original_shader_workflow_step:"+step_name)
    end=content.find("      - name: ",start+len(marker))
    if end<0:
        raise ValueError("unbounded_required_original_shader_workflow_step:"+step_name)
    return content[start:end]


def quality_path(segment):
    return {s.strip() for s in segment.splitlines()
            if s.strip().startswith('--quality "$RUNNER_TEMP/')}


def validate_workflow_text(name,content):
    source18=step(content,"Restore authentic NEXT18 original 58 D3D11 stages and 33 VSFS 4-pass ShaderLab privately")
    install18=step(content,"Install NEXT18 original Shader48 only on its genuine AssetRipper same-export Shader GUID")
    if quality_path(source18)!={'--quality "$RUNNER_TEMP/gt-fourteen-shader-postrestore-quality.json" \\' }:
        raise ValueError("invalid_NEXT18_original_source_quality_must_be_post14_216_46")
    if quality_path(install18)!={'--quality "$RUNNER_TEMP/gt-fifteen-shader-postrestore-quality.json" \\' }:
        raise ValueError("invalid_NEXT18_same_export_guid_install_quality_must_be_post15_193_45")
    if "assert c[\"material_docs_using_dummy_Shader\"]==175" not in content:
        raise ValueError("missing_original_NEXT18_post16_175_real_audit")
    if 'assert source_sha==before,"next18_unexpected_original_material_or_meta_sha_drift"' not in content:
        raise ValueError("missing_NEXT18_full_sha_meta_gate")
    if name==NEXT17:
        source17=step(content,"Recover NEXT17 43 original D3D11 programs from ZIP2 with exact post14 216-source identity")
        install17=step(content,"Install NEXT17 original Shader48 on same-export original GUID using actual post16 audit")
        if quality_path(source17)!={'--quality "$RUNNER_TEMP/gt-fourteen-shader-postrestore-quality.json" \\' }:
            raise ValueError("invalid_NEXT17_original_source_quality_must_be_post14")
        if quality_path(install17)!={'--quality "$RUNNER_TEMP/gt-sixteen-shader-postrestore-quality.json" \\' }:
            raise ValueError("invalid_NEXT17_same_export_guid_install_quality_must_be_post16")
        if '--smolv-decoder "$smolv/decode" --next17 \\' not in content:
            raise ValueError("NEXT17_serialized_vulkan_23route_profile_missing")
        if 'assert c["material_docs_using_dummy_Shader"]==158' not in content or 'assert c["material_docs_using_non_dummy_Shader"]==628' not in content:
            raise ValueError("NEXT17_post17_original_quality_audit_missing")
        if 'assert sha==before,"next17_original_Material_meta_YAML_sha_drift"' not in content:
            raise ValueError("NEXT17_original_same_export_29213_file_sha_guard_missing")
    return True


class GenuineOriginalShaderQualityProvenanceTests(unittest.TestCase):
    def test_FULL_workflows_keep_source_and_install_quality_separate(self):
        for name in (NEXT18,NEXT17):
            with self.subTest(name=name):
                self.assertTrue(validate_workflow_text(name,(DIR/name).read_text()))

    def test_detect_misrouted_SOURCE_census_before_any_expensive_export(self):
        for name in (NEXT18,NEXT17):
            real=(DIR/name).read_text()
            changed=real.replace('--quality "$RUNNER_TEMP/gt-fourteen-shader-postrestore-quality.json"',
                '--quality "$RUNNER_TEMP/gt-fifteen-shader-postrestore-quality.json"')
            self.assertNotEqual(real,changed)
            with self.assertRaisesRegex(ValueError, "original_source_quality"):
                validate_workflow_text(name,changed)

    def test_detect_NEXT17_wrong_install_census_or_Vulkan_profile(self):
        real=(DIR/NEXT17).read_text()
        changed=real.replace('--quality "$RUNNER_TEMP/gt-sixteen-shader-postrestore-quality.json"',
            '--quality "$RUNNER_TEMP/gt-fifteen-shader-postrestore-quality.json"')
        self.assertNotEqual(real,changed)
        with self.assertRaisesRegex(ValueError, "same_export_guid_install_quality"):
            validate_workflow_text(NEXT17,changed)
        changed=real.replace('--smolv-decoder "$smolv/decode" --next17',
                             '--smolv-decoder "$smolv/decode" --next30')
        self.assertNotEqual(real,changed)
        with self.assertRaisesRegex(ValueError,"serialized_vulkan_23route"):
            validate_workflow_text(NEXT17,changed)

    def test_translator_and_installer_definitions_remain_original_source_bound(self):
        for index,prior in [(18,193),(17,175)]:
            translator=(ROOT/"scripts"/f"gt_translate_next_remaining_{index}_shader48.py").read_text()
            installer=(ROOT/"scripts"/f"gt_install_next{index}_original_shader48.py").read_text()
            with self.subTest(shader=index):
                self.assertIn('get("material_docs_using_dummy_Shader")!=216',translator)
                self.assertIn('get("distinct_dummy_Shader_targets_referenced")!=46',translator)
                self.assertIn(f'c.get("material_docs_using_dummy_Shader") != {prior}',installer)
                self.assertIn("traced_shader(project / \"Assets\", trace, source_key)",installer)
                self.assertIn("meta.read_bytes() != metadata",installer)


if __name__=="__main__":
    unittest.main()
