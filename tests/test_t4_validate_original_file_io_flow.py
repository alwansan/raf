"""T4 adversarial public-data controls for private original compiled IO flow report."""
import copy
import tempfile
import unittest
from pathlib import Path

from scripts.t4_validate_original_file_io_flow import validate, main


def groups(io=0, core=0, local=0, external=0):
    return dict(system_io=io, system_non_io=core,
                same_original_filemanager=local,
                other_original_or_external=external)


def edge(n, intent, categories):
    return dict(
        parameter_count=n, parameter_categories=categories, return_category="stream",
        direct_io_intent=intent, direct_io_call_count=1, catch_handler_count=1,
        finally_handler_count=0, catch_contains_leave=True,
        catch_contains_explicit_throw=False, catch_contains_null_literal=True,
        catch_can_exit_normally=True, exception_swallow_on_device_proven=False,
        original_try_calls=groups(io=1, local=1),
        original_catch_calls=groups(core=1, external=1),
        original_outside_handler_calls=groups(),
        original_transitive_callees_executed=False)


def valid():
    return dict(
        schema_version=1, source="IMMUTABLE_ORIGINAL_COMPILED_IL",
        exact_dll_size_sha_verified=True, read_target_unique=True,
        write_target_unique=True, original_methods_distinct=True,
        read=edge(2, "file_open", ["string", "io_enum"]),
        write=edge(1, "file_create", ["string"]),
        actual_file_io_invoked=False, real_rgd_reopened=False,
        android_or_unity_executed=False,
        original_source_or_private_symbols_published=False)


class T4IoFlowSchemaTests(unittest.TestCase):
    def test_valid_bounded_original_structural_proof(self):
        result = validate(valid())
        self.assertEqual(result["status"], "AUTHENTIC_COMPILED_IO_CONTROL_FLOW_CLASSIFIED")
        self.assertFalse(result["original_device_file_io_executed"])

    def test_unknown_original_source(self):
        x = valid(); x["source"] = "ANONYMOUS"
        with self.assertRaises(ValueError): validate(x)

    def test_omitted_original_binary_sha_claim(self):
        x = valid(); x["exact_dll_size_sha_verified"] = False
        with self.assertRaises(ValueError): validate(x)

    def test_fake_rgd_roundtrip(self):
        x = valid(); x["real_rgd_reopened"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_fake_android_test(self):
        x = valid(); x["android_or_unity_executed"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_private_method_name_disclosure_rejected(self):
        x = valid(); x["read"]["private_method_name"] = "NeverPublish"
        with self.assertRaises(ValueError): validate(x)

    def test_fabricated_exception_swallow_proof(self):
        x = valid(); x["read"]["exception_swallow_on_device_proven"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_unsupported_original_parameter_count(self):
        x = valid(); x["write"]["parameter_count"] = 2
        with self.assertRaises(ValueError): validate(x)

    def test_unknown_bcl_call_intent(self):
        x = valid(); x["read"]["direct_io_intent"] = "private_game_method_name"
        with self.assertRaises(ValueError): validate(x)

    def test_incoherent_leave_and_throw(self):
        x = valid(); x["read"]["catch_contains_explicit_throw"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_missing_handler_rejected(self):
        x = valid(); x["write"]["catch_handler_count"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_bool_cannot_pass_as_signed_count(self):
        x = valid(); x["write"]["direct_io_call_count"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_unrecognized_data_type_category(self):
        x = valid(); x["read"]["parameter_categories"][0] = "private_type_name"
        with self.assertRaises(ValueError): validate(x)

    def test_extra_root_text_rejected(self):
        x = valid(); x["original_private_il"] = "do not publish"
        with self.assertRaises(ValueError): validate(x)

    def test_original_transitive_callee_execution_not_claimed(self):
        x = valid(); x["read"]["original_transitive_callees_executed"] = True
        with self.assertRaisesRegex(ValueError, "transitive"):
            validate(x)

    def test_original_callee_group_cardinality_rejected(self):
        x = valid(); x["read"]["original_try_calls"]["system_io"] = 2
        with self.assertRaisesRegex(ValueError, "call_group_cardinality"):
            validate(x)

    def test_public_callee_group_schema_rejects_private_names(self):
        x = valid(); x["write"]["original_catch_calls"]["private_method_name"] = 1
        with self.assertRaisesRegex(ValueError, "call_phase_schema"):
            validate(x)

    def test_phase_specific_handler_calls_preserved(self):
        x = valid()
        x["read"]["original_try_calls"] = groups(io=1, core=1)
        x["read"]["original_catch_calls"] = groups(local=1, external=1)
        summary = validate(x)
        self.assertEqual(summary["read_catch_local_and_external_calls"], 2)
        self.assertFalse(summary["original_device_file_io_executed"])

    def test_untrusted_file_path_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "missing.json"
            self.assertEqual(main(["--report", str(p)]), 2)


if __name__ == "__main__":
    unittest.main()
