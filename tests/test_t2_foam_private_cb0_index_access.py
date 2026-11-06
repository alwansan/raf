"""Source-free adversarial controls; no original source/program/descriptor IDs."""
import struct
import tempfile
from pathlib import Path
import unittest

from scripts.t2_foam_private_cb0_index_access import (
    compiled_cb0_load_paths, private_shared_ubo, inspect_candidate
)
from scripts.t2_foam_private_shaderlab_candidate import assemble
from test_t2_foam_private_shaderlab_candidate import fixture, source_model_fixture


def reflection(mode, length=8, coord=(0, 0), kind="vec4", offset=0):
    return {
        "entryPoints": [{"name": "main", "mode": mode}],
        "ubos": [{"set": coord[0], "binding": coord[1],
                  "block_size": 16*length, "type": "_private", "id": 5}],
        "types": {"_private": {"members": [{
            "name": "PRIVATE_CB0_MEMBER", "offset": offset, "type": kind,
            "array": [length], "array_stride": 16
        }]}},
    }


def inst(op, *args):
    return [(len(args)+1) << 16 | op, *args]


def spirv(index=2, *, dynamic=False, no_load=False, pointer_copy=False,
          negative=False, extra=None, mode="vert"):
    if mode not in ("vert", "frag"):
        raise ValueError("invalid synthetic stage")
    body = (
        inst(15, 0 if mode == "vert" else 4, 17, 0x6e69616d, 0)
        + inst(71, 5, 33, 0) + inst(71, 5, 34, 0)
        + inst(21, 6, 32, 1 if negative else 0)
        + inst(43, 6, 7, 0)
        + inst(43, 6, 8, 0xffffffff if negative else index)
        + inst(59, 3, 5, 2)
    )
    if dynamic:
        # Synthetic undefined SSA index deliberately tests cautious classification.
        index_id = 40
    else:
        index_id = 8
    body += inst(65, 9, 21, 5, 7, index_id)
    ptr = 21
    if pointer_copy:
        body += inst(83, 9, 23, 21)
        ptr = 23
    if extra:
        body += extra
    if not no_load:
        body += inst(61, 10, 22, ptr)
    header = [0x07230203, 0x00010300, 0, 64, 0]
    return struct.pack("<%dI" % (len(header)+len(body)), *(header+body))


class CB0CompiledLoadIndexTests(unittest.TestCase):
    def test_source_free_two_stage_capacity_direction_is_private(self):
        coord, vs, fs = private_shared_ubo(
            reflection("vert", length=10), reflection("frag", length=6))
        self.assertEqual(coord, (0, 0))
        self.assertEqual((vs, fs), (10, 6))
        with self.assertRaises(ValueError):
            private_shared_ubo(reflection("vert", 6), reflection("frag", 6))
        with self.assertRaises(ValueError):
            private_shared_ubo(reflection("vert", 10),
                               reflection("frag", 6, kind="mat4"))

    def test_literal_in_both_own_and_other_reflected_arrays(self):
        r = compiled_cb0_load_paths(spirv(index=2), reflection("vert"), (0, 0), 8, 6)
        self.assertEqual(r["observed_static_index_load_count"], 1)
        self.assertEqual(r["static_index_in_common_reflected_prefix_count"], 1)
        self.assertEqual(r["static_index_exceeds_other_stage_array_count"], 0)
        self.assertTrue(r["observed_load_index_paths_not_runtime_access_proof"])
        self.assertNotIn("PRIVATE_", str(r))

    def test_literal_in_own_but_outside_other_array_is_counted(self):
        r = compiled_cb0_load_paths(spirv(index=7), reflection("vert"), (0, 0), 8, 6)
        self.assertEqual(r["observed_static_index_load_count"], 1)
        self.assertEqual(r["static_index_exceeds_own_reflected_array_count"], 0)
        self.assertEqual(r["static_index_exceeds_other_stage_array_count"], 1)
        self.assertEqual(r["static_index_in_common_reflected_prefix_count"], 0)

    def test_literal_outside_own_reflected_capacity_is_not_declared_safe(self):
        r = compiled_cb0_load_paths(spirv(index=9), reflection("vert"), (0, 0), 8, 6)
        self.assertEqual(r["static_index_exceeds_own_reflected_array_count"], 1)
        self.assertEqual(r["static_index_exceeds_other_stage_array_count"], 1)

    def test_dynamic_and_negative_index_never_count_as_known_static(self):
        for blob in (spirv(dynamic=True), spirv(negative=True)):
            with self.subTest(blob=blob[:8]):
                r = compiled_cb0_load_paths(blob, reflection("vert"), (0, 0), 8, 6)
                self.assertEqual(r["observed_static_index_load_count"], 0)
                self.assertEqual(r["observed_dynamic_or_unknown_index_load_count"], 1)

    def test_copy_object_preserves_pointer_provenance(self):
        r = compiled_cb0_load_paths(
            spirv(index=7, pointer_copy=True), reflection("vert"), (0, 0), 8, 6)
        self.assertEqual(r["static_index_exceeds_other_stage_array_count"], 1)

    def test_duplicate_or_invalid_pointer_ssa_result_fails_closed(self):
        # Synthetic conflicting result IDs must never overwrite tracked CB0
        # provenance, including when a second alias comes from a phi/select.
        for extra in (
            inst(83, 9, 21, 21),  # CopyObject overwrites AccessChain ID
            inst(83, 9, 64, 21),  # CopyObject result outside SPIR-V bound
            inst(245, 9, 21, 21, 44),  # Phi overwrites tracked ID
            inst(169, 9, 21, 40, 21, 42),  # Select overwrites tracked ID
            inst(67, 9, 21, 5, 8),  # PtrAccessChain overwrites tracked ID
        ):
            with self.subTest(op=extra[0] & 0xffff), self.assertRaises(ValueError):
                compiled_cb0_load_paths(
                    spirv(no_load=True, extra=extra),
                    reflection("vert"), (0, 0), 8, 6)

    def test_unrelated_pointer_load_is_ignored_not_falsely_attributed(self):
        blob = spirv(index=2, extra=inst(61, 10, 32, 42))
        r = compiled_cb0_load_paths(blob, reflection("vert"), (0, 0), 8, 6)
        self.assertEqual(r["observed_static_index_load_count"], 1)

    def test_zero_observed_oploads_proves_no_runtime_absence(self):
        r = compiled_cb0_load_paths(spirv(no_load=True), reflection("vert"), (0, 0), 8, 6)
        self.assertEqual(r["observed_static_index_load_count"], 0)
        self.assertFalse(r["no_trace_means_no_reads_proven"])

    def test_direct_root_ubo_load_is_unresolved(self):
        blob = spirv(index=1, no_load=True, extra=inst(61, 10, 22, 5))
        r = compiled_cb0_load_paths(blob, reflection("vert"), (0, 0), 8, 6)
        self.assertEqual(r["observed_unresolved_pointer_or_whole_load_count"], 1)
        self.assertEqual(r["observed_static_index_load_count"], 0)

    def test_ambiguous_ptr_access_and_phi_alias_fail_conservatively(self):
        for op in (
            inst(67, 9, 23, 5, 8),  # pointer arithmetic
            inst(245, 9, 23, 5, 44),  # pointer phi
        ):
            blob = spirv(no_load=True, extra=op+inst(61, 10, 22, 23))
            r = compiled_cb0_load_paths(blob, reflection("vert"), (0, 0), 8, 6)
            self.assertGreater(r["observed_unresolved_pointer_or_whole_load_count"], 0)
            self.assertEqual(r["observed_static_index_load_count"], 0)

    def test_incomplete_spirv_and_mismatched_binary_reflection_fail(self):
        for blob in (b"", spirv()[:-4], spirv()[:17]):
            with self.subTest(length=len(blob)), self.assertRaises(ValueError):
                compiled_cb0_load_paths(blob, reflection("vert"), (0, 0), 8, 6)
        with self.assertRaises(ValueError):
            compiled_cb0_load_paths(spirv(), reflection("vert", coord=(0, 4)),
                                    (0, 0), 8, 6)
        with self.assertRaises(ValueError):
            compiled_cb0_load_paths(spirv(), reflection("frag"), (0, 0), 8, 6)

    def test_fragment_stage_binary_matches_fragment_reflection(self):
        r = compiled_cb0_load_paths(spirv(index=2, mode="frag"),
                                    reflection("frag"), (0, 0), 8, 6)
        self.assertEqual(r["observed_static_index_load_count"], 1)
        with self.assertRaises(ValueError):
            compiled_cb0_load_paths(spirv(index=2, mode="frag"),
                                    reflection("vert"), (0, 0), 8, 6)

    def test_unknown_array_capacity_is_not_rounded_or_assumed(self):
        for x in (True, 0, -1, 8.0, 65537, None):
            with self.subTest(x=x), self.assertRaises(ValueError):
                compiled_cb0_load_paths(spirv(), reflection("vert"),
                                        (0, 0), x, 6)

    def test_real_style_two_pass_diagnostic_requires_compiled_stage_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            parsed, stages, states = fixture()
            candidate = Path(temp) / "private.shader"
            candidate.write_text(
                assemble(parsed, stages, states, source_model_fixture())[0])
            def fake_invoke(cmd):
                if cmd[0] == "glslangValidator":
                    out = Path(cmd[cmd.index("-o")+1])
                    out.write_bytes(spirv(index=7, mode=(
                        "frag" if "-frag" in out.name else "vert")))
                return True
            def fake_reflect(path):
                return reflection("vert" if "-vert" in path.name else "frag",
                                  length=8 if "-vert" in path.name else 6)
            r = inspect_candidate(candidate, Path(temp), invoke=fake_invoke,
                                  reflect=fake_reflect)
            self.assertEqual(r["original_compiled_stage_count"], 4)
            self.assertEqual(r["original_pass_count"], 2)
            self.assertEqual(len(r["per_pass_relative_loads"]), 2)
            self.assertTrue(all(p["relative_array_capacity"] == "vertex_larger"
                                for p in r["per_pass_relative_loads"]))
            self.assertTrue(all(
                p["vertex_compiled_loads"]["static_index_exceeds_other_stage_array_count"] == 1
                for p in r["per_pass_relative_loads"]))
            self.assertFalse(r["Unity_original_CB0_upload_verified"])
            self.assertNotIn("PRIVATE_", str(r))


if __name__ == "__main__":
    unittest.main()
