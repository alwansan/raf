"""Source-free negative controls and structural tests for private glslang IO options."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.t3_particle108_glslang_io_map_experiment import (
    PAIRS, CONFIGS, COUNT_FIELDS, compile_alternative, compare_pair, evaluate,
)

def stage(inputs=(),outputs=()):
    return {"inputs":[{"location":loc,"type":typ} for loc,typ in inputs],
            "outputs":[{"location":loc,"type":typ} for loc,typ in outputs],
            "resource_slots":{}}

class Particle108GlslangIOMapTests(unittest.TestCase):
    def test_compiler_variants_explicit_and_no_baseline_flag(self):
        self.assertEqual(CONFIGS["baseline"],())
        self.assertEqual(CONFIGS["iomap"],("--hlsl-iomap",))
        self.assertEqual(CONFIGS["aml"],("--auto-map-locations",))
        self.assertEqual(CONFIGS["iomap_aml"],("--hlsl-iomap","--auto-map-locations"))

    def test_pair_full_link(self):
        d=compare_pair({1:stage(outputs=[(2,"vec3")]),0:stage(inputs=[(2,"vec3")])})
        self.assertEqual(d,{"linked":1,"missing":0,"type_mismatch":0})

    def test_pair_fragment_missing_location(self):
        d=compare_pair({1:stage(outputs=[(2,"vec3")]),0:stage(inputs=[(3,"vec3")])})
        self.assertEqual(d["linked"],0)
        self.assertEqual(d["missing"],1)
        self.assertEqual(d["type_mismatch"],0)

    def test_pair_same_location_type_mismatch(self):
        d=compare_pair({1:stage(outputs=[(2,"vec2")]),0:stage(inputs=[(2,"vec3")])})
        self.assertEqual(d["linked"],0)
        self.assertEqual(d["missing"],0)
        self.assertEqual(d["type_mismatch"],1)

    def test_pair_duplicate_location_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"duplicate_private_SPIRV_IO_location"):
            compare_pair({1:stage(outputs=[(0,"vec4"),(0,"vec2")]),0:stage(inputs=[])})

    def test_unsafe_compilation_scope_rejected_before_subprocess(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)
            src=folder/"private.hlsl"
            src.write_text("float4 main() : SV_Position { return 0; }")
            with self.assertRaisesRegex(ValueError,"unsafe_private_hlsl_alternative_compiler_scope"):
                compile_alternative(src,folder/"safe.spv",1,("--hlsl-iomap","--unapproved-flag"))
            with self.assertRaisesRegex(ValueError,"unsafe_private_hlsl_alternative_compiler_scope"):
                compile_alternative(src,src,1,())

    def test_fake_four_pairs_preserve_per_variant_success_and_failure(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)
            pairs=[(b"private VS",b"private FS") for _ in range(PAIRS)]
            def translator(code,kind,directory):
                for fn in ("original.spv","roundtrip.spv","private.hlsl"):
                    (directory/fn).write_text("private stub only")
                return {"vulkan11_valid":True,
                        "hlsl_recovered":True,
                        "roundtrip_vulkan11_valid":True}
            def reflector(path):
                isvertex=path.parent.name.endswith("stage-1")
                name=path.name
                # Base original link all four; baseline roundtrip mismatches all
                # four. Only iomap option restores fake locations.
                vertex_type="vec3" if name=="roundtrip.spv" else "vec4"
                if isvertex:
                    return stage(outputs=[(1,vertex_type)])
                return stage(inputs=[(1,"vec4")])
            def compiler(hlsl,spv,kind,flags):
                return flags==("--hlsl-iomap",)
            d=evaluate(pairs,folder,translator=translator,reflector=reflector,
                       compiler=compiler)
            c=d["counts"]
            self.assertEqual(set(c),set(COUNT_FIELDS))
            self.assertEqual(c["source_pairs_linked"],4)
            self.assertEqual(c["baseline_pairs_compared"],4)
            self.assertEqual(c["baseline_pairs_linked"],0)
            self.assertEqual(c["baseline_fragment_same_location_type_mismatch"],4)
            self.assertEqual(c["iomap_stage_compiles_valid"],8)
            self.assertEqual(c["iomap_pairs_linked"],4)
            self.assertEqual(c["aml_pairs_compared"],0)
            self.assertEqual(c["iomap_aml_pairs_compared"],0)

    def test_untrusted_original_pair_count_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError,"unverified_original_private_four_pairs"):
                evaluate([(b"VS",b"FS")],Path(root))
            with self.assertRaisesRegex(ValueError,"unverified_original_private_four_pairs"):
                evaluate([(b"VS",b"FS")]*(PAIRS-1)+[(b"",b"FS")],Path(root))

if __name__=="__main__":
    unittest.main()
