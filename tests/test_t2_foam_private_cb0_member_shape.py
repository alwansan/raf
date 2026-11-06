"""Source-free adversarial controls for private two-pass Foam CB0 member reflection."""
import tempfile
from pathlib import Path
import unittest

from scripts.t2_foam_private_cb0_member_shape import (
    compare_private_cb0_geometry, inspect_private_candidate,
)
from scripts.t2_foam_private_shaderlab_candidate import assemble
from test_t2_foam_private_shaderlab_candidate import fixture, source_model_fixture


def member(offset=0, kind="vec4", array=None, stride=16, **extra):
    d = {"name": "PRIVATE_MEMBER_MUST_NEVER_BE_REPORTED", "offset": offset,
         "type": kind}
    if array is not None:
        d["array"] = array
        d["array_stride"] = stride
    d.update(extra)
    return d


def stage(mode, members=None, block=64, coord=(0, 0), **extra):
    d = {
        "entryPoints": [{"name": "main", "mode": mode}],
        "ubos": [{"set": coord[0], "binding": coord[1], "block_size": block,
                  "type": "_PRIVATE_TYPE", "name": "PRIVATE_UBO_IDENTIFIER"}],
        "types": {"_PRIVATE_TYPE": {"name": "PRIVATE_TYPE", "members":
                  members if members is not None else [member(array=[4])]}},
    }
    d.update(extra)
    return d


class PrivateCB0MemberGeometryTests(unittest.TestCase):
    def test_matching_members_and_extents_do_not_prove_upload(self):
        r = compare_private_cb0_geometry(stage("vert"), stage("frag"))
        self.assertEqual(r["shared_uniform_buffer_coordinate_count"], 1)
        self.assertEqual(r["same_offset_exact_reflected_geometry_count"], 1)
        self.assertFalse(r["different_reflected_block_byte_extent"])
        self.assertTrue(r["reflected_member_shape_is_not_Unity_CB0_upload_evidence"])
        self.assertNotIn("PRIVATE_", str(r))

    def test_real_style_different_block_extents_and_array_length(self):
        r = compare_private_cb0_geometry(
            stage("vert", [member(array=[4])], 64),
            stage("frag", [member(array=[6])], 96))
        self.assertEqual(r["same_offset_same_type_token_count"], 1)
        self.assertEqual(r["same_offset_exact_reflected_geometry_count"], 0)
        self.assertEqual(r["same_offset_array_shape_difference_count"], 1)
        self.assertTrue(r["different_reflected_block_byte_extent"])

    def test_same_offset_incompatible_token_or_matrix_stride(self):
        a = stage("vert", [member(kind="mat4", matrix_stride=16)])
        b = stage("frag", [member(kind="vec4", matrix_stride=16)])
        r = compare_private_cb0_geometry(a, b)
        self.assertEqual(r["same_offset_same_type_token_count"], 0)
        self.assertEqual(r["same_offset_exact_reflected_geometry_count"], 0)
        b = stage("frag", [member(kind="mat4", matrix_stride=32)])
        r = compare_private_cb0_geometry(a, b)
        self.assertEqual(r["same_offset_stride_or_major_difference_count"], 1)

    def test_different_member_starts_never_fake_matching(self):
        a = stage("vert", [member(offset=0), member(offset=16)])
        b = stage("frag", [member(offset=0), member(offset=32)])
        r = compare_private_cb0_geometry(a, b)
        self.assertEqual(r["same_offset_member_count"], 1)
        self.assertEqual(r["vertex_reflected_member_count"], 2)
        self.assertEqual(r["fragment_reflected_member_count"], 2)

    def test_member_symbols_are_not_published_or_matched(self):
        a = stage("vert")
        b = stage("frag")
        b["types"]["_PRIVATE_TYPE"]["members"][0]["name"] = "ANOTHER_PRIVATE_NAME"
        r = compare_private_cb0_geometry(a, b)
        self.assertEqual(r["same_offset_exact_reflected_geometry_count"], 1)
        self.assertNotIn("ANOTHER_PRIVATE", str(r))

    def test_missing_shared_ubo_or_ambiguous_shared_ubos_rejected(self):
        with self.assertRaises(ValueError):
            compare_private_cb0_geometry(stage("vert"), stage("frag", coord=(0, 5)))
        a = stage("vert")
        b = stage("frag")
        a["ubos"].append({"set": 0, "binding": 5, "type": "_PRIVATE_TYPE",
                          "block_size": 64})
        b["ubos"].append({"set": 0, "binding": 5, "type": "_PRIVATE_TYPE",
                          "block_size": 64})
        with self.assertRaises(ValueError):
            compare_private_cb0_geometry(a, b)

    def test_duplicate_descriptor_and_missing_private_type_rejected(self):
        a = stage("vert")
        a["ubos"].append(dict(a["ubos"][0]))
        with self.assertRaises(ValueError):
            compare_private_cb0_geometry(a, stage("frag"))
        a = stage("vert")
        a["types"] = {}
        with self.assertRaises(ValueError):
            compare_private_cb0_geometry(a, stage("frag"))

    def test_boolean_float_negative_offset_and_oversized_extent_rejected(self):
        for offset in (True, -1, 64, 0.5, None):
            with self.subTest(offset=offset):
                with self.assertRaises(ValueError):
                    compare_private_cb0_geometry(
                        stage("vert", [member(offset=offset)]), stage("frag"))
        for block in (True, 0, -1, 16*1024*1024+1, 64.0):
            with self.subTest(block=block), self.assertRaises(ValueError):
                compare_private_cb0_geometry(stage("vert", block=block),
                                             stage("frag"))

    def test_nonliteral_array_stride_and_major_forgery_rejected(self):
        bad = [
            member(array=[False]),
            member(array=[0]),
            member(array=[65537]),
            member(array=[4], array_size_is_literal=[False]),
            member(array=[4], array_size_is_literal=[True, True]),
            member(array=[4], array_stride=True),
            member(array=[4], array_stride=-1),
            member(row_major=1),
        ]
        for row in bad:
            with self.subTest(row=row), self.assertRaises(ValueError):
                compare_private_cb0_geometry(stage("vert", [row]),
                                             stage("frag"))

    def test_same_block_duplicate_offset_and_oversize_count_rejected(self):
        with self.assertRaises(ValueError):
            compare_private_cb0_geometry(
                stage("vert", [member(), member()]), stage("frag"))
        with self.assertRaises(ValueError):
            compare_private_cb0_geometry(
                stage("vert", [member(offset=i*16) for i in range(65)], 2048),
                stage("frag"))

    def test_no_original_program_compiled_by_synthetic_negative(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "private.shader"
            parsed, stages, states = fixture()
            path.write_text(assemble(parsed, stages, states,
                                     source_model_fixture())[0], encoding="utf-8")
            r = []
            def stop_before_original(cmd):
                r.append(cmd)
                return False
            with self.assertRaises(ValueError):
                inspect_private_candidate(path, Path(temp), invoke=stop_before_original)
            self.assertTrue(r)
            self.assertEqual(r[0][0], "glslangValidator")

    def test_private_two_pass_reflection_is_compiled_not_just_staged(self):
        with tempfile.TemporaryDirectory() as temp:
            parsed, stages, states = fixture()
            path = Path(temp) / "private.shader"
            path.write_text(assemble(parsed, stages, states,
                                     source_model_fixture())[0], encoding="utf-8")
            def fake_invoke(cmd):
                if cmd[0] == "glslangValidator":
                    Path(cmd[cmd.index("-o")+1]).write_bytes(b"q" * 20)
                return True
            def fake_reflect(path):
                return stage("vert" if "-vert" in path.name else "frag",
                             block=64 if "-vert" in path.name else 96)
            r = inspect_private_candidate(path, Path(temp),
                                          invoke=fake_invoke, reflect=fake_reflect)
            self.assertEqual(r["pass_count"], 2)
            self.assertEqual(r["compiled_stage_variants"], 4)
            self.assertTrue(all(x["different_reflected_block_byte_extent"]
                                for x in r["per_pass_CB0_member_geometry"]))
            self.assertFalse(r["original_member_semantics_or_CBuffer_upload_verified"])
            self.assertNotIn("PRIVATE_", str(r))


if __name__ == "__main__":
    unittest.main()
