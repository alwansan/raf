"""Source-free byte-commitment tests; no Unity bundle or game data is used."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from scripts.gt_next23b_unity_receipt import read_snapshot, strict_json, verify_unity_receipt


def receipt_for(shader, routes, source, bundle):
    return {
        "receiptSchemaVersion": 2,
        "unityVersion": "2021.3.45f2",
        "checkpoint": "verified",
        "failureType": "",
        "passCount": 4,
        "registeredRoutes": 1156,
        "errors": 0,
        "androidVulkanOnly": True,
        "privateBundleCompiled": True,
        "candidateSha256": sha256(shader).hexdigest(),
        "engineRouteManifestSha256": sha256(routes).hexdigest(),
        "sourceManifestSha256": sha256(source).hexdigest(),
        "bundleSha256": sha256(bundle).hexdigest(),
        "bundleBytes": len(bundle),
    }


class Next23bReceiptProvenance(unittest.TestCase):
    def setUp(self):
        self.inputs = [b"authored shader", b'{"passes":[]}', b'{"source":1}', b"authored bundle"]
        self.receipt = receipt_for(*self.inputs)

    def test_exact_bytes_are_accepted_without_attestation_claim(self):
        report = verify_unity_receipt(self.receipt, *self.inputs)
        self.assertTrue(report["unity_receipt_byte_commitments_verified"])
        self.assertFalse(report["unity_receipt_cryptographic_attestation_verified"])
        self.assertEqual(report["unity_receipt_bundle_bytes"], len(self.inputs[-1]))

    def test_every_input_is_bound_even_when_length_is_preserved(self):
        fields = ("candidateSha256", "engineRouteManifestSha256", "sourceManifestSha256", "bundleSha256")
        for index, field in enumerate(fields):
            with self.subTest(field=field):
                data = self.inputs[:]
                data[index] = bytes([data[index][0] ^ 1]) + data[index][1:]
                with self.assertRaisesRegex(ValueError, field + "_mismatch"):
                    verify_unity_receipt(self.receipt, *data)

    def test_equivalent_json_is_not_same_consumed_manifest_bytes(self):
        data = self.inputs[:]
        data[1] = b'{ "passes": [] }'
        self.assertEqual(json.loads(data[1]), json.loads(self.inputs[1]))
        with self.assertRaisesRegex(ValueError, "engineRouteManifestSha256_mismatch"):
            verify_unity_receipt(self.receipt, *data)

    def test_legacy_or_incomplete_receipt_fails_closed(self):
        for key in self.receipt:
            with self.subTest(key=key):
                stale = self.receipt.copy()
                stale.pop(key)
                with self.assertRaises(ValueError):
                    verify_unity_receipt(stale, *self.inputs)

    def test_failed_or_not_final_receipts_cannot_pass(self):
        for key, value in (("receiptSchemaVersion", 1), ("checkpoint", "compiler_results"),
                           ("failureType", "InvalidOperationException"), ("errors", 1),
                           ("privateBundleCompiled", False), ("androidVulkanOnly", False),
                           ("unityVersion", "2022.3.0f1"), ("registeredRoutes", 1155)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_unity_receipt(dict(self.receipt, **{key: value}), *self.inputs)

    def test_bool_float_and_string_are_not_numeric_receipt_fields(self):
        for key, value in (("receiptSchemaVersion", 2.0), ("passCount", "4"),
                           ("registeredRoutes", 1156.0), ("errors", False),
                           ("privateBundleCompiled", 1), ("bundleBytes", True),
                           ("bundleBytes", float(len(self.inputs[-1])))):
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_unity_receipt(dict(self.receipt, **{key: value}), *self.inputs)

    def test_bundle_size_mismatch_rejected_even_with_correct_digest(self):
        with self.assertRaisesRegex(ValueError, "bundle_size_mismatch"):
            verify_unity_receipt(dict(self.receipt, bundleBytes=len(self.inputs[-1]) + 1), *self.inputs)

    def test_empty_bundle_is_not_accepted_even_when_receipt_matches(self):
        data = self.inputs[:]
        data[-1] = b""
        with self.assertRaisesRegex(ValueError, "input_bytes_invalid"):
            verify_unity_receipt(receipt_for(*data), *data)

    def test_duplicate_and_nonfinite_json_fail_closed(self):
        for data in (b'{"x":0,"x":1}', b'{"nested":{"a":1,"a":1}}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                strict_json(data)
        self.assertEqual(strict_json(b'{"x":0,"nested":{"x":1}}'), {"x": 0, "nested": {"x": 1}})

    def test_snapshot_rejects_empty_oversize_nonfile_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / "input"
            for data in (b"", b"12345"):
                path.write_bytes(data)
                with self.assertRaisesRegex(ValueError, "input_size_invalid"):
                    read_snapshot(path, 4)
            path.write_bytes(b"1234")
            self.assertEqual(read_snapshot(path, 4), b"1234")
            link = root / "alias"
            link.symlink_to(path)
            for bad in (link, root, root / "missing"):
                with self.assertRaisesRegex(ValueError, "not_regular_file"):
                    read_snapshot(bad, 4)

    def test_editor_source_hashes_consumed_manifest_and_fresh_bundle_before_success(self):
        # Static source contract only: no C# compiler/Unity API is executed.
        root = Path(__file__).resolve().parents[1]
        code = (root / "android-port/Experiments/GT/Editor/Next23bShaderValidation.cs").read_text()
        self.assertIn("receiptSchemaVersion = 2", code)
        self.assertIn("File.Exists(receiptPath) || Directory.Exists(bundleDirectory)", code)
        self.assertNotIn("File.ReadAllText(routePath)", code)
        steps = (
            'result.checkpoint = "fresh_output"',
            "result.candidateSha256 = HashFile(candidatePath)",
            "var routeBytes = File.ReadAllBytes(routePath)",
            "result.engineRouteManifestSha256 = HashBytes(routeBytes)",
            "new UTF8Encoding(false, true).GetString(routeBytes)",
            "routeManifest.candidate_sha256 != result.candidateSha256",
            "result.sourceManifestSha256 = routeManifest.source_manifest_sha256",
            "BuildPipeline.BuildAssetBundles(",
            "HashFile(candidatePath) != result.candidateSha256",
            "HashFile(routePath) != result.engineRouteManifestSha256",
            "result.bundleSha256 = HashFile(artifact.FullName, out result.bundleBytes)",
            'result.checkpoint = "verified"',
            "result.privateBundleCompiled = true",
            "exitCode = 0",
            "File.WriteAllText(receiptPath,",
        )
        offsets = [code.index(step) for step in steps]
        self.assertEqual(offsets, sorted(offsets))
        self.assertIn("result.privateBundleCompiled = false;\n                exitCode = 1;", code)
        self.assertIn("public long bundleBytes;", code)
        self.assertEqual(code.count("File.ReadAllBytes(routePath)"), 1)
