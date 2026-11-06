"""T3 source-free Particle108 SPIR-V name-bridge negative/positive controls.

Synthetic compiler names only, never original private Shader, GUID, binary.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_particle108_reflected_name_bridge as t3
from scripts import t3_spirv_interface_name_drift as names


PAIRS=[(b"synthetic-private-vertex",b"synthetic-private-fragment") for _ in range(4)]


def fake_translate(code,stage,path):
    assert code.startswith(b"synthetic-private-")
    assert path.is_dir()
    return {"stage":stage,"vulkan11_valid":True,"hlsl_recovered":True,
            "roundtrip_vulkan11_valid":True,
            "dxbc_sha256":"ORIGINAL_SHADER_SHA_PRIVATE_SENTINEL",
            "hlsl_sha256":"PRIVATE_HLSL_SENTINEL"}


def row(name,loc,typ="vec4"):
    return {"name":name,"location":loc,"type":typ}


def raw_reflect(path):
    # Layout 0 on source; compiler-derived HLSL changes the VS output
    # Location but not the FS input on half the variants.
    name=path.parent.name
    stage=int(name.rsplit("-stage-",1)[1])
    variant=int(name.split("-")[1])
    derived=path.name.startswith("roundtrip")
    out={"inputs":[],"outputs":[]}
    if stage==1:
        out["outputs"]=[row("PRIVATE_INTERPOLATOR",1 if derived else 0)]
    else:
        out["inputs"]=[row("PRIVATE_INTERPOLATOR",
                            1 if derived and variant>=2 else 0)]
    return out


def sanitize(path):
    return {key:[{"location":r["location"],"type":r["type"]}
                 for r in raw_reflect(path).get(key,[])
                 if "location" in r] for key in ("inputs","outputs")} | {
                     "resource_slots":{}}


class Particle108NameBridge(unittest.TestCase):
    def test_true_per_stage_name_preservation_does_not_guarantee_four_compatible_pairs(self):
        with tempfile.TemporaryDirectory() as d:
            report=t3.evaluate(PAIRS,Path(d),translator=fake_translate,
                               safe_reflector=sanitize,raw_reflector=raw_reflect)
        c=report["counts"]
        self.assertEqual(c["stage_translation_attempts"],8)
        self.assertEqual(c["source_reflection_available"],8)
        self.assertEqual(c["roundtrip_reflection_available"],8)
        self.assertEqual(c["source_stage_pair_interfaces_compatible"],4)
        self.assertEqual(c["roundtrip_stage_pair_interfaces_compatible"],2)
        self.assertEqual(c["source_compatible_roundtrip_incompatible_pairs"],2)
        self.assertEqual(c["stages_full_located_name_type_preservation"],8)
        self.assertEqual(c["incompatible_pairs_with_both_stages_name_type_complete"],2)
        self.assertEqual(c["incompatible_pairs_with_all_located_name_and_no_unlocated_rows"],2)
        self.assertFalse(report["compiler_reflected_names_are_original_DXBC_semantics_verified"])
        self.assertFalse(report["compiler_reflected_names_sufficient_for_automatic_location_patch_verified"])
        public=json.dumps(report,sort_keys=True)
        for sentinel in ("PRIVATE_INTERPOLATOR","PRIVATE_HLSL_SENTINEL",
                         "ORIGINAL_SHADER_SHA_PRIVATE_SENTINEL","synthetic-private"):
            self.assertNotIn(sentinel,public)

    def test_changed_compiler_variable_names_block_named_repair_candidate(self):
        def renamed(path):
            d=raw_reflect(path)
            if path.name.startswith("roundtrip"):
                for side in ("inputs","outputs"):
                    for r in d[side]:
                        r["name"] += "_COMPILER_RENAMED"
            return d
        def safe(path):
            d=renamed(path)
            return {"inputs":[{"location":r["location"],"type":r["type"]}
                              for r in d["inputs"]],
                    "outputs":[{"location":r["location"],"type":r["type"]}
                               for r in d["outputs"]],
                    "resource_slots":{}}
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(PAIRS,Path(d),translator=fake_translate,
                          safe_reflector=safe,raw_reflector=renamed)
        c=r["counts"]
        self.assertEqual(c["stages_full_located_name_type_preservation"],0)
        self.assertEqual(c["incompatible_pairs_with_both_stages_name_type_complete"],0)
        self.assertGreater(c["name_outputs_source_only_names"],0)
        self.assertGreater(c["name_inputs_roundtrip_only_names"],0)
        self.assertFalse(r["compiler_reflected_names_sufficient_for_automatic_location_patch_verified"])

    def test_unlocated_builtin_entries_are_not_silent_semantic_proof(self):
        def builtins(path):
            d=raw_reflect(path)
            d["outputs"].append({"name":"gl_Position","builtin":"Position"})
            return d
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(PAIRS,Path(d),translator=fake_translate,
                          safe_reflector=sanitize,raw_reflector=builtins)
        c=r["counts"]
        self.assertEqual(c["stages_full_located_name_type_preservation"],8)
        self.assertEqual(c["stages_with_unlocated_builtin_or_other_rows"],8)
        self.assertEqual(c["incompatible_pairs_with_both_stages_name_type_complete"],2)
        self.assertEqual(c["incompatible_pairs_with_all_located_name_and_no_unlocated_rows"],0)

    def test_private_name_classifier_injection_and_bad_boolean_refused(self):
        def injected(*args):
            out=names.classify_reflected_names(*args)
            out["PRIVATE_SHADER_METADATA"]="secret"
            return out
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"schema_mismatch"):
                t3.evaluate(PAIRS,Path(d),translator=fake_translate,
                            safe_reflector=sanitize,raw_reflector=raw_reflect,
                            name_classifier=injected)
        def badbool(*args):
            out=names.classify_reflected_names(*args)
            out["inputs_name_type_complete_preservation"]=True
            return out
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"invalid_numeric"):
                t3.evaluate(PAIRS,Path(d),translator=fake_translate,
                            safe_reflector=sanitize,raw_reflector=raw_reflect,
                            name_classifier=badbool)

    def test_mismatched_sanitized_location_and_raw_name_refused_privately(self):
        def bad_safe(path):
            r=sanitize(path)
            if path.name.startswith("roundtrip") and r["outputs"]:
                r["outputs"][0]["location"]=123
            return r
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(PAIRS,Path(d),translator=fake_translate,
                          safe_reflector=bad_safe,raw_reflector=raw_reflect)
        self.assertEqual(r["counts"]["source_vs_roundtrip_stage_names_classified"],4)
        self.assertEqual(r["counts"]["roundtrip_stage_pair_interfaces_compatible"],2)
        self.assertNotIn("PRIVATE_INTERPOLATOR",json.dumps(r))

    def test_untrusted_translation_result_fails_closed_no_program_digests(self):
        def malformed(_code,stage,_path):
            return {"stage":stage,"vulkan11_valid":False,
                    "hlsl_recovered":True,"roundtrip_vulkan11_valid":True,
                    "secret":"NEVER_PUBLISH"}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"translation_result"):
                t3.evaluate(PAIRS,Path(d),translator=malformed,
                            safe_reflector=sanitize,raw_reflector=raw_reflect)

    def test_missing_original_fragment_stage_or_unbounded_pairs_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"name_bridge_scope"):
                t3.evaluate(PAIRS[:3],Path(d),translator=fake_translate,
                            safe_reflector=sanitize,raw_reflector=raw_reflect)
        with tempfile.TemporaryDirectory() as d:
            bad=list(PAIRS)
            bad[0]=(b"source-vertex",None)
            with self.assertRaisesRegex(ValueError,"DXBC_stage_pair"):
                t3.evaluate(bad,Path(d),translator=fake_translate,
                            safe_reflector=sanitize,raw_reflector=raw_reflect)


if __name__=="__main__":
    unittest.main()
