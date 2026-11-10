import unittest
from types import SimpleNamespace
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED, EXPECTED_REFERENCED, EXPECTED_UNUSED,
    inspect_unused_programs,
)

def fake_programs():
    return [
        SimpleNamespace(
            m_ProgramType=SimpleNamespace(name="DX11Pixel"),
            m_ProgramCode=b"PRIVATE_PROGRAM_NOT_EXPORTED")
        for _ in range(EXPECTED_COMPILED)
    ]


class TestShader48UnreferencedCensus(unittest.TestCase):
    def test_exact_counts_bounded_rdef_absence(self):
        program = fake_programs()
        parsed=[]
        def parse(b):
            self.assertIn(b"PRIVATE_PROGRAM",b)
            return [b"DXBC_BOUND_BLOB"]
        d=inspect_unused_programs(
            program, set(range(EXPECTED_REFERENCED)),
            parse_containers=parse,
            inspect_rdef=lambda b: {"rdef_missing_in_source":True})
        self.assertEqual(d["unused_entries"],EXPECTED_UNUSED)
        self.assertEqual(d["unused_dx11_with_one_valid_dxbc"],EXPECTED_UNUSED)
        self.assertEqual(d["unused_dxbc_rdef_absent"],EXPECTED_UNUSED)
        self.assertEqual(d["unused_dxbc_rdef_present"],0)
        self.assertNotIn("PRIVATE_PROGRAM",str(d))

    def test_one_unused_rdef_is_only_candidate_evidence(self):
        programs=fake_programs()
        d=inspect_unused_programs(
            programs,set(range(EXPECTED_REFERENCED)),
            parse_containers=lambda b:[b"DXBC"],
            inspect_rdef=lambda b:{
                "rdef_structures_bounds_checked":True,
                "constant_buffers":2,"resource_binding_descriptors":3})
        self.assertEqual(d["unused_dxbc_rdef_present"],EXPECTED_UNUSED)
        self.assertEqual(d["unused_rdef_constant_buffer_descriptors"],2*EXPECTED_UNUSED)
        self.assertEqual(d["unused_rdef_resource_binding_descriptors"],3*EXPECTED_UNUSED)

    def test_wrong_reference_count_rejected(self):
        with self.assertRaisesRegex(ValueError,"REFERENCED_UNIQUE"):
            inspect_unused_programs(fake_programs(),{0})

    def test_duplicate_valid_dxbc_is_not_accepted(self):
        with self.assertRaisesRegex(ValueError,"DXBC_AMBIGUOUS"):
            inspect_unused_programs(fake_programs(),set(range(EXPECTED_REFERENCED)),
                                     parse_containers=lambda b:[b"A",b"B"])

    def test_reject_oversized_original_byte_payload(self):
        programs=fake_programs()
        programs[-1].m_ProgramCode=b"x"*(16*1024*1024+1)
        with self.assertRaisesRegex(ValueError,"UNBOUNDED"):
            inspect_unused_programs(programs,set(range(EXPECTED_REFERENCED)),
                                     parse_containers=lambda b:[])
