"""Synthetic privacy and negative controls for compiler-reflected I/O names.

These names are not claimed to be original D3D11 semantic signatures.
"""
import json
import unittest

from scripts import t3_spirv_interface_name_drift as t3


def raw(inputs=(), outputs=()):
    return {"inputs": list(inputs), "outputs": list(outputs), "entryPoints": []}


def row(name, location, typ="vec4"):
    return {"name": name, "location": location, "type": typ}


def safe(full):
    return {side: [{"location": v["location"], "type": v["type"]}
                   for v in full.get(side, []) if "location" in v]
            for side in ("inputs", "outputs")}


class ReflectedNameDriftTests(unittest.TestCase):
    def test_complete_name_type_preservation_with_location_remap(self):
        src = raw([row("PRIVATE_COLOR", 0), row("PRIVATE_UV", 1, "vec2")],
                  [row("PRIVATE_VERTEX_POSITION", 0)])
        dst = raw([row("PRIVATE_COLOR", 4), row("PRIVATE_UV", 7, "vec2")],
                  [row("PRIVATE_VERTEX_POSITION", 3)])
        report = t3.classify_reflected_names(src, dst, safe(src), safe(dst))
        self.assertEqual(report["inputs_source_located"], 2)
        self.assertEqual(report["inputs_source_name_type_matches"], 2)
        self.assertEqual(report["inputs_source_name_type_relocated"], 2)
        self.assertEqual(report["inputs_source_name_type_same_location"], 0)
        self.assertEqual(report["inputs_name_type_complete_preservation"], 1)
        self.assertEqual(report["inputs_name_type_relocation_only_candidate"], 1)
        self.assertEqual(report["outputs_name_type_relocation_only_candidate"], 1)
        self.assertNotIn("PRIVATE_COLOR", json.dumps(report))
        self.assertNotIn("PRIVATE_UV", json.dumps(report))

    def test_renamed_variable_does_not_become_semantic_proof(self):
        src = raw([row("SOURCE_PRIVATE_NAME", 0)])
        dst = raw([row("GENERATED_OTHER_NAME", 6)])
        result = t3.classify_reflected_names(src, dst, safe(src), safe(dst))
        self.assertEqual(result["inputs_source_name_type_matches"], 0)
        self.assertEqual(result["inputs_source_only_names"], 1)
        self.assertEqual(result["inputs_roundtrip_only_names"], 1)
        self.assertEqual(result["inputs_name_type_complete_preservation"], 0)
        self.assertEqual(result["inputs_name_type_relocation_only_candidate"], 0)
        self.assertNotIn("GENERATED_OTHER_NAME", json.dumps(result))

    def test_same_name_but_changed_type_not_equal(self):
        src = raw([row("PRIVATE_SEMANTIC", 3, "float")])
        dst = raw([row("PRIVATE_SEMANTIC", 4, "vec4")])
        result = t3.classify_reflected_names(src, dst, safe(src), safe(dst))
        self.assertEqual(result["inputs_same_name_different_type"], 1)
        self.assertEqual(result["inputs_source_name_type_matches"], 0)
        self.assertEqual(result["inputs_name_type_complete_preservation"], 0)

    def test_missing_name_means_inconclusive_even_if_locations_equal(self):
        src = raw([{"location": 3, "type": "float"}])
        dst = raw([row("DERIVED_PRIVATE_NAME", 3, "float")])
        result = t3.classify_reflected_names(src, dst, safe(src), safe(dst))
        self.assertEqual(result["inputs_source_located_without_name"], 1)
        self.assertEqual(result["inputs_name_comparison_incomplete"], 1)
        self.assertEqual(result["inputs_name_type_complete_preservation"], 0)

    def test_same_locations_and_types_without_remap(self):
        src = raw([row("PRIVATE_IDENT", 0)], [row("PRIVATE_RESULT", 3)])
        result = t3.classify_reflected_names(src, src, safe(src), safe(src))
        self.assertEqual(result["inputs_name_type_complete_preservation"], 1)
        self.assertEqual(result["inputs_name_type_relocation_only_candidate"], 0)
        self.assertEqual(result["outputs_name_type_relocation_only_candidate"], 0)

    def test_unlocated_builtin_rows_counted_without_disclosure(self):
        src = raw([{"name": "gl_VertexIndex", "builtin": "VertexIndex"},
                   row("PRIVATE", 1)])
        dest = raw([{"name": "gl_VertexIndex", "builtin": "VertexIndex"},
                    row("PRIVATE", 2)])
        result = t3.classify_reflected_names(src, dest, safe(src), safe(dest))
        self.assertEqual(result["inputs_source_unlocated_entries"], 1)
        self.assertEqual(result["inputs_roundtrip_unlocated_entries"], 1)
        self.assertNotIn("gl_VertexIndex", json.dumps(result))

    def test_duplicate_name_or_location_rejected(self):
        duplicate = raw([row("PRIVATE_DUP", 0), row("PRIVATE_DUP", 1)])
        with self.assertRaisesRegex(ValueError, "duplicate_private_spirv_reflection_name"):
            t3.classify_reflected_names(duplicate, duplicate, safe(duplicate), safe(duplicate))
        duplicate_loc = raw([row("PRIVATE_A", 0), row("PRIVATE_B", 0)])
        with self.assertRaisesRegex(ValueError, "duplicate_private_spirv_location"):
            t3.classify_reflected_names(duplicate_loc, duplicate_loc,
                                        safe(duplicate_loc), safe(duplicate_loc))

    def test_reject_raw_and_sanitized_original_reflection_disagreement(self):
        src = raw([row("PRIVATE", 2, "vec3")])
        dst = raw([row("PRIVATE", 3, "vec3")])
        original_safe = safe(src)
        original_safe["inputs"][0]["type"] = "vec4"
        with self.assertRaisesRegex(ValueError, "disagrees_with_safe_IO_baseline"):
            t3.classify_reflected_names(src, dst, original_safe, safe(dst))

    def test_reject_boolean_location_and_untrusted_name_control_chars(self):
        source = raw([row("PRIVATE", True)])
        with self.assertRaisesRegex(ValueError, "invalid_or_duplicate_private_spirv_location_type"):
            t3.classify_reflected_names(source, source, safe(source), safe(source))
        unsafe = raw([row("PRIVATE\ndata", 0)])
        with self.assertRaisesRegex(ValueError, "invalid_or_duplicate_private_spirv_reflection_name"):
            t3.classify_reflected_names(unsafe, unsafe, safe(unsafe), safe(unsafe))

    def test_no_private_per_stage_source_name_or_hash_in_safe_result(self):
        src = raw([row("SUPER_SECRET_SOURCE_DXBC_SEMANTIC", 0)])
        dst = raw([row("SUPER_SECRET_SOURCE_DXBC_SEMANTIC", 1)])
        result = t3.classify_reflected_names(src, dst, safe(src), safe(dst))
        payload = json.dumps(result, sort_keys=True)
        self.assertNotIn("SUPER_SECRET_SOURCE_DXBC_SEMANTIC", payload)
        self.assertTrue(all(type(v) is int for v in result.values()))
        self.assertEqual(set(result), {side + "_" + key
                         for side in t3.SIDES for key in t3.FIELDS})


if __name__ == "__main__":
    unittest.main()
