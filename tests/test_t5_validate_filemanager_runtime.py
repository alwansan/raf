"""Source-free tests for original FileManager synthetic runtime result gate."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.t5_validate_filemanager_runtime import main, verify

def good():
    return {
        "schema_version": 1, "status": "MANAGED_SYNTHETIC_ROUNDTRIP",
        "original_sha_verified": True, "static_compiled_call_safety_guard": True,
        "original_managed_methods_invoked": True,
        "synthetic_bytes_exact_readback": True,
        "failed_phase": "NONE", "failure_category": "NONE",
        "original_rgd_serialization_proven": False,
        "original_world_or_unity_or_android_proven": False,
        "private_method_names_or_original_bytes_disclosed": False,
    }

class TestOriginalFilemanagerRuntimeGate(unittest.TestCase):
    def assert_reject(self, doc):
        with self.assertRaises(ValueError):
            verify(doc)

    def test_valid_synthetic_report_not_device(self):
        r=verify(good())
        self.assertTrue(r["original_compiled_filemanager_synthetic_managed_roundtrip"])
        self.assertFalse(r["android_device_or_original_rgd_proven"])

    def test_refuse_false_green_with_zero_bytes(self):
        r=good();r["synthetic_bytes_exact_readback"]=False;self.assert_reject(r)

    def test_refuse_unverified_original_binary(self):
        r=good();r["original_sha_verified"]=False;self.assert_reject(r)

    def test_refuse_missing_static_compiled_guard(self):
        r=good();r["static_compiled_call_safety_guard"]=False;self.assert_reject(r)

    def test_refuse_not_invoked(self):
        r=good();r["original_managed_methods_invoked"]=False;self.assert_reject(r)

    def test_refuse_inconclusive_sandbox(self):
        for val in ("INCONCLUSIVE","UNSUPPORTED_READ_RETURN","FILE_NOT_CREATED","BYTES_MISMATCH"):
            r=good();r["status"]=val;self.assert_reject(r)

    def test_refuse_hidden_failure(self):
        for k,val in (("failed_phase","ORIGINAL_MANAGED_INVOCATION"),("failure_category","DEPENDENCY_UNRESOLVED")):
            r=good();r[k]=val;self.assert_reject(r)

    def test_refuse_claims_of_real_rgd_or_android(self):
        for k in ("original_rgd_serialization_proven", "original_world_or_unity_or_android_proven",
                  "private_method_names_or_original_bytes_disclosed"):
            r=good();r[k]=True;self.assert_reject(r)

    def test_refuse_privacy_identifier_injection(self):
        r=good();r["private_original_method_name"]="SomePrivateName";self.assert_reject(r)

    def test_refuse_bool_disguised_as_other_types(self):
        for k in ("original_sha_verified","synthetic_bytes_exact_readback"):
            r=good();r[k]=1;self.assert_reject(r)

    def test_refuse_unsupported_schema(self):
        r=good();r["schema_version"]=True;self.assert_reject(r)

    def test_cli_safe_json_and_unparseable(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"safe.json"
            p.write_text(json.dumps(good()))
            self.assertEqual(main(["--report",str(p)]),0)
            p.write_text("{bad json")
            self.assertEqual(main(["--report",str(p)]),2)

    def test_refuse_symlink_report(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"safe.json";p.write_text(json.dumps(good()))
            link=Path(t)/"link";link.symlink_to(p)
            self.assertEqual(main(["--report",str(link)]),2)

if __name__=="__main__":
    unittest.main()
