"""Source-free rejection tests for original runtime keyword bundle gate."""
import copy
from pathlib import Path
import unittest
from scripts.gt_verify_921_shader_bundle import validate_next23b_engine_manifest


def packet():
    return {"passes": [{"passType": "Normal", "variants": [
        {"keywords": ["SOURCE_%d" % i]} for i in range(n)]}
        for n in (512, 4, 128, 512)]}


class Next23bUnityGate(unittest.TestCase):
    def test_complete_original_engine_route_population(self):
        validate_next23b_engine_manifest(packet())

    def test_rejects_selector_fallback_collisions_and_population_drift(self):
        for mutate in (
            lambda p: p["passes"][0]["variants"].pop(),
            lambda p: p["passes"][1]["variants"][0].update(keywords=["GT_ORIGINAL_921_P1_V1"]),
            lambda p: p["passes"][2]["variants"].__setitem__(0, {"keywords": ["SOURCE_1"]}),
            lambda p: p["passes"][3].update(passType="Synthetic"),
        ):
            p = packet()
            mutate(p)
            with self.assertRaises(ValueError):
                validate_next23b_engine_manifest(p)

    def test_isolated_workflow_requires_engine_routes_decoding_and_no_installation(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / ".github/workflows/raft-gt-next23b-original-shader-unity.yml").read_text()
        for required in ("--engine-keywords", "--engine-route-manifest", "--smolv-decoder", "--next23b", "2021.3.45f2", "RaftGT.Next23bShaderValidation.Validate"):
            self.assertIn(required, text)
        self.assertNotIn("gt_install_", text)
        probe = (root / "android-port/Experiments/GT/Editor/Next23bShaderValidation.cs").read_text()
        self.assertIn("routes == null", probe)
        self.assertNotIn('variant == 0 ? Array.Empty', probe)
