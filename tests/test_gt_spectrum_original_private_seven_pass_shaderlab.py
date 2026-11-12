"""Source-free negative controls for source-authentic 7pass Spectrum candidates.

Only synthetic metadata and HLSL. No original source code, Shader text or GUID.
"""
from __future__ import annotations

import copy
import unittest

from scripts.b09_spectrum_topology_contract import PASSES
from scripts.gt_spectrum_original_private_seven_pass_shaderlab import (
    _pairs, assemble
)


def _prop(name, kind):
    return {
        "m_Name":name, "m_Description":name,
        "m_Attributes":[], "m_Type":kind, "m_Flags":0,
        "m_DefValue[0]":0., "m_DefValue[1]":0.,
        "m_DefValue[2]":0., "m_DefValue[3]":0.,
        "m_DefTexture":{"m_DefaultName":"white" if kind==4 else "",
                        "m_TexDim":2 if kind==4 else 0},
    }


def _parsed():
    props = [_prop("_Tex%d"%i, 4) for i in range(2)]
    props += [_prop("_Num%d"%i, 2) for i in range(4)]
    return {
        "m_Name":"UltimateWater/Spectrum/Water Spectrum",
        "m_PropInfo":{"m_Props": props},
        "m_SubShaders":[{"m_LOD":0,"m_Tags":{"tags":[]},
                         "m_Passes":[{"m_Type":0, "m_State":{}} for _ in range(7)]}],
        "m_FallbackName":"", "m_CustomEditorName":"",
    }


def _manifest():
    return {
        "original_subshader_pass_counts":[7],
        "original_passes":7,
        "source_topology_attestation":{
            "authenticated_variant_stage_programs":28},
        "stages":[
            {"subshader":0,"pass_index":i,
             "variant_pairs":[
                 {"pair_index":j,"stages":{"0":{},"1":{}}}
                 for j in range(2)]}
            for i in range(7)],
    }


def _programs():
    return {(pi, vi, st):
            "float4 main() : SV_Target { return float4(0,0,0,1); }"
            for pi in range(7) for vi in range(2) for st in (0,1)}


class PrivateSpectrumSevenPassTests(unittest.TestCase):
    def test_both_private_seven_pass_variants_are_structurally_complete(self):
        shaderlab, props = assemble(
            _parsed(), _manifest(), _programs(),
            ["ZWrite On\nCull Back" for _ in range(PASSES)])
        self.assertEqual(len(shaderlab), 2)
        self.assertEqual(props["original_authored_property_count"], 6)
        self.assertEqual(props["original_authored_texture_property_count"], 2)
        for text in shaderlab:
            self.assertEqual(text.count("HLSLPROGRAM"), 7)
            self.assertEqual(text.count("ENDHLSL"), 7)
            self.assertEqual(text.count("ZWrite On"), 7)
            self.assertIn("Shader \"UltimateWater/Spectrum/Water Spectrum\"", text)

    def test_spectrum_log_floor_six_cannot_replace_seven_original(self):
        candidate = _parsed()
        candidate["m_SubShaders"][0]["m_Passes"].pop()
        with self.assertRaisesRegex(ValueError, "subshader_topology_invalid"):
            assemble(candidate, _manifest(), _programs(),
                     ["ZWrite On" for _ in range(7)])

    def test_source_pass_order_and_variant_identity_rejected_when_malformed(self):
        for kind in ("order", "stage", "variant"):
            manifest = _manifest()
            if kind == "order":
                manifest["stages"][2]["pass_index"] = 3
            elif kind == "stage":
                del manifest["stages"][0]["variant_pairs"][0]["stages"]["0"]
            else:
                manifest["stages"][1]["variant_pairs"][0]["pair_index"] = 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                _pairs(manifest)

    def test_original_property_count_and_texture_types_required(self):
        for mutation in ("count", "textures", "attributes"):
            parsed = _parsed()
            if mutation == "count":
                parsed["m_PropInfo"]["m_Props"].pop()
            if mutation == "textures":
                parsed["m_PropInfo"]["m_Props"][0]["m_Type"] = 2
            if mutation == "attributes":
                parsed["m_PropInfo"]["m_Props"][2]["m_Attributes"] = ["Fake"]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                assemble(parsed, _manifest(), _programs(),
                         ["ZWrite On" for _ in range(7)])

    def test_partial_real_stage_bundle_not_admitted(self):
        programs=_programs()
        del programs[(6,1,0)]
        with self.assertRaisesRegex(ValueError, "pair_incomplete"):
            assemble(_parsed(), _manifest(), programs,
                     ["ZWrite On" for _ in range(7)])

    def test_states_cannot_be_silently_padded(self):
        with self.assertRaisesRegex(ValueError, "pair_incomplete"):
            assemble(_parsed(), _manifest(), _programs(),
                     ["ZWrite On" for _ in range(6)])

    def test_shaderlab_is_provisional_not_accepted_game_shader(self):
        from scripts.gt_spectrum_original_private_seven_pass_shaderlab import __doc__
        self.assertIn("NOT an original keyword routed", __doc__)
        self.assertIn("Unity import", __doc__)
        self.assertIn("Adreno pixel proof", __doc__)


if __name__ == "__main__":
    unittest.main()
