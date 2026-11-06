import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from scripts.t1_fft_private_invocation_pair_report import analyze
from scripts.t1_fft_private_input_evidence import SCHEMA, input_hash
from scripts.t1_fft_trace_compare import INVOCATION_SIZE, INVOCATION_RECORD
from scripts.t1_fft_pass0_vulkan_trace import trace_host


def pack(coords=((1, 2, 0), (1, 2, 0), (1, 2, 0)),
         values=(11, 22, 33)):
    output = bytearray(INVOCATION_SIZE)
    struct.pack_into("<I", output, 0, 3)
    for site in range(3):
        data = INVOCATION_RECORD.pack(site, 9, 1, 0, 0, *coords[site],
                                      values[site], 0, 0, 0)
        offset = 4 + site * INVOCATION_RECORD.size
        output[offset:offset+INVOCATION_RECORD.size] = data
    return bytes(output)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ActualPrivatePairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.a, self.b = root/"a.bin", root/"b.bin"
        self.ma, self.mb = root/"a.json", root/"b.json"
        self.a.write_bytes(pack())
        self.b.write_bytes(pack())
        def contract(stage, path):
            return {
                "schema": SCHEMA, "stage": stage, "records_by_site": [1,1,1],
                "input_sha256": "a"*64, "dispatch_sha256": "b"*64,
                "shader_sha256": ("c" if stage == "original_spirv" else "d")*64,
                "trace_sha256": sha(path.read_bytes()),
            }
        self.oa=contract("original_spirv", self.a)
        self.ob=contract("hlsl_roundtrip_spirv", self.b)
        self.save()

    def save(self):
        self.ma.write_text(json.dumps(self.oa))
        self.mb.write_text(json.dumps(self.ob))

    def compare(self):
        return analyze(self.a,self.b,self.ma,self.mb)

    def test_independent_identical_synthetic_trace_can_match(self):
        result=self.compare()
        self.assertTrue(result["same_vulkan_fixture_numeric_match"])
        self.assertTrue(result["actual_GPU_input_bytes_match"])
        self.assertFalse(result["authored_Unity_kernel_runtime_identity_proven"])
        self.assertFalse(result["independent_source_authenticity_verified_by_manifest"])
        self.assertEqual(result["by_site_expected_reads"], [1,1,1])

    def test_actual_coordinate_difference_is_not_parity(self):
        blob=pack(coords=((1,2,0),(7,2,0),(1,2,0)))
        self.b.write_bytes(blob)
        self.ob["trace_sha256"]=sha(blob)
        self.save()
        result=self.compare()
        self.assertFalse(result["same_vulkan_fixture_numeric_match"])
        self.assertEqual(result["site_comparison"][1]["coordinate_mismatches"],1)

    def test_same_coordinate_different_value_is_not_parity(self):
        blob=pack(values=(11,90,33))
        self.b.write_bytes(blob)
        self.ob["trace_sha256"]=sha(blob)
        self.save()
        result=self.compare()
        self.assertFalse(result["same_vulkan_fixture_numeric_match"])
        self.assertEqual(result["site_comparison"][1]["same_coordinate_value_mismatches"],1)

    def test_actual_input_digest_must_match(self):
        self.ob["input_sha256"]="e"*64
        self.save()
        with self.assertRaisesRegex(ValueError,"input bytes differ"):
            self.compare()

    def test_dispatch_configuration_must_match(self):
        self.ob["dispatch_sha256"]="f"*64
        self.save()
        with self.assertRaisesRegex(ValueError,"dispatch config differs"):
            self.compare()

    def test_trace_sha_mismatch_rejected(self):
        self.ob["trace_sha256"]="0"*64
        self.save()
        with self.assertRaises(ValueError):
            self.compare()

    def test_same_underlying_file_is_not_independent(self):
        with self.assertRaisesRegex(ValueError,"identical underlying"):
            analyze(self.a,self.a,self.ma,self.mb)

    def test_producer_stage_role_mismatch_rejected(self):
        self.ob["stage"]="original_spirv"
        self.save()
        with self.assertRaisesRegex(ValueError,"producer stage"):
            self.compare()

    def test_incomplete_site_coverage_rejected(self):
        self.oa["records_by_site"]=[0,1,1]
        self.save()
        with self.assertRaisesRegex(ValueError,"site census"):
            self.compare()

    def test_oversized_or_duplicate_evidence_rejected(self):
        self.ma.write_bytes(b" " * 4097)
        with self.assertRaisesRegex(ValueError,"Oversized"):
            self.compare()
        self.ma.write_text('{"schema":"x","schema":"x"}')
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            self.compare()

    def test_private_hashes_not_in_public_report(self):
        result=self.compare()
        self.assertNotIn("a"*64,str(result))
        self.assertNotIn("b"*64,str(result))
        self.assertNotIn("c"*64,str(result))
        self.assertNotIn("9, 1, 0",str(result))

    def test_combined_input_hash_binds_order_and_bytes(self):
        self.assertNotEqual(input_hash(b"abc",b"def"),input_hash(b"def",b"abc"))
        self.assertNotEqual(input_hash(b"abc",b"def"),input_hash(b"abc",b"dez"))

    def test_optional_cxx_host_dump_keeps_exact_original_input_readback(self):
        source=Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text()
        plain=trace_host(source, INVOCATION_SIZE)
        keyed=trace_host(source, INVOCATION_SIZE,capture_inputs=True)
        self.assertNotIn("t1-source-input.rgba32f", plain)
        self.assertEqual(keyed.count("t1-source-input.rgba32f"),1)
        self.assertEqual(keyed.count("t1-butterfly-input.rgba32f"),1)
        self.assertIn("pixel(images[inputIndex],x,y,imageFormat)",keyed)


if __name__ == "__main__":
    unittest.main()
