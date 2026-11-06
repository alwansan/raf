"""No-game-data guards for SHA-authentic Foam CB0→managed literal target staging."""
import hashlib
import unittest
from copy import deepcopy
from unittest.mock import patch

from scripts.b24_original_foam_stage_translation import TARGET
from scripts.t2_foam_private_cb0_managed_targets import _name, build_private_target_set


def fixture():
    ps = []
    for idx in range(2):
        name_rows = [
            ["PRIVATE_BUFFER_LITERAL", 1],
            ["PRIVATE_VECTOR_LITERAL", 2],
            ["PRIVATE_MATRIX_LITERAL", 3],
        ]
        def program():
            return {"m_CommonParameters": {"m_ConstantBuffers": [{
                "m_Size": 160, "m_NameIndex": 1,
                "m_VectorParams": [{"m_NameIndex": 2, "m_Index": 0}],
                "m_MatrixParams": [{"m_NameIndex": 3, "m_Index": 1}]
            }]}}
        ps.append({"m_NameIndices": name_rows,
                   "progVertex": program(), "progFragment": program()})
    return {"m_Name": TARGET, "m_SubShaders": [{"m_Passes": ps}]}


def audit(model):
    with patch("scripts.t2_foam_private_cb0_managed_targets.inspect_parsed",
               return_value={"matched_constant_buffer_bindings": 8}), \
         patch("scripts.t2_foam_private_cb0_managed_targets.validate_stage"):
        return build_private_target_set(model)


class OriginalCb0NameTargetTests(unittest.TestCase):
    def test_source_fake_four_stages_deduplicate_by_exact_strings(self):
        data = audit(fixture())
        self.assertEqual(data["original_stage_count"], 4)
        self.assertEqual(data["original_cb0_stage_bindings"], 4)
        self.assertEqual(data["original_cb0_vector_parameters"], 4)
        self.assertEqual(data["original_cb0_matrix_parameters"], 4)
        self.assertEqual(data["distinct_target_names"], 3)
        self.assertEqual(len(data["categories_sha256"]["buffer"]), 1)
        self.assertEqual(len(data["categories_sha256"]["vector"]), 1)
        self.assertEqual(len(data["categories_sha256"]["matrix"]), 1)
        self.assertNotIn("PRIVATE_", str(data))
        self.assertFalse(data["actual_Unity_upload_proven"])

    def test_digest_is_not_guess_or_plaintext(self):
        data = audit(fixture())
        self.assertEqual(data["categories_sha256"]["vector"],
                         [hashlib.sha256(b"PRIVATE_VECTOR_LITERAL").hexdigest()])
        self.assertNotIn("PRIVATE_VECTOR_LITERAL", str(data))

    def test_source_foam_shader_mname_digest_private_only(self):
        data = audit(fixture())
        self.assertEqual(
            data["original_Foam_Shader_mName_SHA256_private"],
            hashlib.sha256(TARGET.encode("utf8")).hexdigest())
        self.assertNotIn(TARGET, str(data))
        self.assertEqual(len(data["original_Foam_Shader_mName_SHA256_private"]), 64)

    def test_incomplete_original_name_reference_is_not_invented(self):
        data = fixture()
        data["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_CommonParameters"]["m_ConstantBuffers"][0]["m_VectorParams"][0]["m_NameIndex"] = 400
        result = audit(data)
        self.assertEqual(result["original_cb0_parameter_name_indices_unresolved"], 1)
        self.assertEqual(len(result["categories_sha256"]["vector"]), 1)

    def test_missing_cb_buffer_name_is_fatal(self):
        data = fixture()
        data["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_CommonParameters"]["m_ConstantBuffers"][0]["m_NameIndex"] = 999
        with self.assertRaises(ValueError):
            audit(data)

    def test_missing_source_target_fatal(self):
        data = fixture()
        data["m_Name"] = "WRONG_ORIGINAL"
        with self.assertRaises(ValueError):
            audit(data)

    def test_non_integer_bool_or_foreign_index_is_not_accepted(self):
        for idx in (True, "1", 12.0, None, -1, 999):
            with self.subTest(idx=idx):
                self.assertIsNone(_name({1: "PRIVATE"}, idx))
        self.assertEqual(_name({1: "PRIVATE"}, 1), "PRIVATE")

    def test_invalid_private_name_rejected(self):
        for value in ("", "x"*257, "nul\x00inside"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                _name({1: value}, 1)

    def test_duplicates_in_registry_rejected_by_original_B25(self):
        data = fixture()
        data["m_SubShaders"][0]["m_Passes"][0]["m_NameIndices"].append(
            ["PRIVATE_VECTOR_LITERAL", 99])
        with self.assertRaises(ValueError):
            audit(data)

    def test_unbounded_original_member_count_rejected(self):
        data = fixture()
        cb = data["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_CommonParameters"]["m_ConstantBuffers"][0]
        cb["m_VectorParams"] = [{"m_NameIndex": 2, "m_Index": i} for i in range(129)]
        with self.assertRaises(ValueError):
            audit(data)

    def test_missing_original_stage_is_not_ignored(self):
        data = fixture()
        data["m_SubShaders"][0]["m_Passes"][0].pop("progVertex")
        with self.assertRaises((KeyError, ValueError)):
            audit(data)

    def test_no_param_name_input_still_labels_unknown_not_upload_proof(self):
        data = fixture()
        for p in data["m_SubShaders"][0]["m_Passes"]:
            for k in ("progVertex", "progFragment"):
                cb = p[k]["m_CommonParameters"]["m_ConstantBuffers"][0]
                for row in cb["m_VectorParams"] + cb["m_MatrixParams"]:
                    row.pop("m_NameIndex")
        result = audit(data)
        self.assertEqual(result["original_cb0_parameter_name_indices_unresolved"], 8)
        self.assertEqual(len(result["categories_sha256"]["buffer"]), 1)
        self.assertEqual(len(result["categories_sha256"]["vector"]), 0)
        self.assertFalse(result["actual_Unity_upload_proven"])


if __name__ == "__main__":
    unittest.main()
