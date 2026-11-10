"""GFX-MULTI-041: private owner ZIP auditor synthetic regression tests."""
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path
from gfxlab.tools.affine_reference_owner_zip_audit import check_report,audit_zip
from gfxlab.tools.interpolation_owner_zip_audit import PNG_MAGIC


def report():
    return {
        "experiment":"GFX-MULTI-041",
        "originalShaderRestored":False,
        "originalRaftShaderBytecodeUsed":False,
        "originalPcPixelParityVerified":False,
        "sourceMaterialCbBindingsVerified":False,
        "diagnosticStatus":"DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH",
        "isGles3":True,
        "allFourGpuReadbacksComplete":True,
        "affineEmulatedMatchesCpu":True,
        "linearPerspectiveMatchesCpu":True,
        "nativeNoPerspectiveMatchesAffine":False,
        "nativeNoPerspectiveMatchesSmooth":True,
        "flatConstantAcrossInteriorSamples":True,
        "gpuLinearVsCpuPerspectiveError":.001,
        "gpuAffineEmulatedVsCpuAffineError":.002,
        "gpuNativeVsCpuAffineError":.163,
        "gpuNativeVsLinearError":0,
        "cpuExpectedPerspectiveAffineDifference":.163,
        "results":[{
            "name":mode,
            "shaderFound":True,
            "shaderSupportedOnDevice":True,
            "gpuReadbackCompleted":True,
            "allSamplePositionsHaveColor":True,
            "sampledColors":[{"r":.4,"g":.3,"b":.3,"a":1} for _ in range(3)]
        } for mode in ("Linear","Flat","NoPerspective","AffineEmulated")]
    }


def minimal_png():
    return (PNG_MAGIC+struct.pack(">I",13)+b"IHDR"+
            struct.pack(">II",256,256)+b"\x08\x06\0\0\0"+b"1234")


def fixture(path):
    prefix="sessions/001/"
    row={"kind":"state_snapshot","stateJson":json.dumps(report())}
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("README.txt","No original shader evidence")
        z.writestr(prefix+"snapshots.jsonl",json.dumps(row)+"\n")
        z.writestr(prefix+"summary.json",json.dumps({
            "originalShaderRestored":False,
            "unityErrors":0,"unityWarnings":0,"messagesDropped":0
        }))
        for name in ("linear","flat","noperspective","affineemulated"):
            z.writestr(prefix+"gpu-interpolation-"+name+".png",minimal_png())


class TestAffineOwnerZipAudit(unittest.TestCase):
    def test_four_case_source_only_collapse_is_a_valid_diagnostic_result(self):
        safe=check_report(report())
        self.assertEqual(safe["source_only_synthetic_mode_count"],4)
        self.assertTrue(safe["emulated_affine_matches_cpu"])
        self.assertTrue(safe["native_noperspective_matches_linear"])
        self.assertFalse(safe["source_original_shader48_restored"])

    def test_reject_native_success_without_real_gpu_and_cpu_reference(self):
        s=report()
        s["allFourGpuReadbacksComplete"]=False
        with self.assertRaisesRegex(ValueError,"COMPLETION_FLAG_CONTRADICTION"):
            check_report(s)
        s=report()
        s["affineEmulatedMatchesCpu"]=False
        with self.assertRaisesRegex(ValueError,"WITHOUT_REFERENCE"):
            check_report(s)

    def test_reject_fabricated_native_qualifier_classification(self):
        s=report()
        s["nativeNoPerspectiveMatchesSmooth"]=False
        with self.assertRaisesRegex(ValueError,"COLLAPSE_CLASSIFICATION"):
            check_report(s)
        s=report()
        s["diagnosticStatus"]="DIAGNOSTIC_NATIVE_NOPERSPECTIVE_MATCHES_AFFINE"
        with self.assertRaisesRegex(ValueError,"NATIVE_MATCH_CLASSIFICATION"):
            check_report(s)

    def test_reject_claim_original_shader_restored_and_malformed_mode(self):
        s=report()
        s["sourceMaterialCbBindingsVerified"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_AUTHENTIC_SHADER"):
            check_report(s)
        s=report()
        s["results"][3]["name"]="NotReal"
        with self.assertRaisesRegex(ValueError,"FOUR_MODES_REQUIRED"):
            check_report(s)

    def test_complete_synthetic_zip_is_only_private_safe_aggregate(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"original-private.zip"
            fixture(path)
            output=audit_zip(path)
            self.assertEqual(output["synthetic_gpu_256x256_png_count"],4)
            self.assertEqual(output["matching_gfx041_snapshots"],1)
            self.assertEqual(output["status"],"DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH")
            self.assertEqual(output["unity_errors"],0)
            self.assertFalse(output["source_owner_images_logs_device_identifiers_exported"])
            data=json.dumps(output)
            self.assertNotIn("sampledColors",data)
            self.assertNotIn("sessions/001",data)
            self.assertFalse(output["source_original_shader48_restored"])

    def test_reject_no_snapshots_or_missing_summary(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bad.zip"
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("README.txt","ok")
                z.writestr("sessions/a/snapshots.jsonl","")
            with self.assertRaisesRegex(ValueError,"GPU_SNAPSHOTS_ABSENT"):
                audit_zip(path)
