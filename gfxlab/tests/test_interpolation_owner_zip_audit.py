import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from gfxlab.tools.interpolation_owner_zip_audit import (
    validate_snapshot,png_synthetic_shape,audit_zip,PNG_MAGIC,
)


def original_free_status(status="DIAGNOSTIC_INTERPOLATION_PASS"):
    return {
        "experiment":"GFX-MULTI-040",
        "originalShaderRestored":False,
        "originalRaftShaderBytecodeUsed":False,
        "originalPcPixelParityVerified":False,
        "sourceMaterialCbBindingsVerified":False,
        "diagnosticStatus":status,
        "isGles3":True,
        "allThreeGpuReadbacksComplete":True,
        "flatConstantAcrossInteriorSamples":True,
        "perspectiveVsNoPerspectiveDistinguishable":True,
        "results":[{
            "name":name,"shaderFound":True,
            "shaderSupportedOnDevice":True,
            "gpuReadbackCompleted":True,
            "allSamplePositionsHaveColor":True,
            "sampledColors":[{"r":.3,"g":.3,"b":.4,"a":1.0} for _ in range(3)]
        } for name in ("Linear","Flat","NoPerspective")]
    }


def dummy_png():
    return PNG_MAGIC + struct.pack(">I",13) + b"IHDR" + struct.pack(">II",256,256) + b"\x08\x06\x00\x00\x00" + b"xxxx"


def make_fixture(path,status="DIAGNOSTIC_INTERPOLATION_PASS"):
    snap=original_free_status(status)
    state=json.dumps(snap)
    row={"kind":"state_snapshot","stateJson":state}
    folder="sessions/synthetic-session-01/"
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("README.txt","original shader not restored\n")
        z.writestr(folder+"snapshots.jsonl",json.dumps(row)+"\n")
        z.writestr(folder+"summary.json",json.dumps({
            "originalShaderRestored":False,
            "unityErrors":0,"messagesDropped":0
        }))
        for mode in ("linear","flat","noperspective"):
            z.writestr(folder+"gpu-interpolation-"+mode+".png",dummy_png())


class TestSyntheticGfx040OwnerExportAuditor(unittest.TestCase):
    def test_strict_no_original_shader_gpu_pass_gate(self):
        status=validate_snapshot(original_free_status())
        self.assertTrue(status["all_three_gpu_readbacks_completed"])
        self.assertEqual(status["cases_with_gpu_readback"],3)
        self.assertFalse(status["original_shader48_restored"])
        self.assertFalse(status["original_gpu_pc_parity_verified"])

    def test_unknown_or_faked_shaders_rejected(self):
        s=original_free_status()
        s["originalShaderRestored"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_PROOF"):
            validate_snapshot(s)
        s=original_free_status()
        s["results"][1]["shaderSupportedOnDevice"]=False
        with self.assertRaisesRegex(ValueError,"WITHOUT_SHADER_SUPPORT"):
            validate_snapshot(s)
        s=original_free_status()
        s["allThreeGpuReadbacksComplete"]=False
        with self.assertRaisesRegex(ValueError,"INCONSISTENT"):
            validate_snapshot(s)

    def test_non_gles3_cannot_claim_qualifier_pass(self):
        s=original_free_status()
        s["isGles3"]=False
        with self.assertRaisesRegex(ValueError,"WITHOUT_REQUIRED_EVIDENCE"):
            validate_snapshot(s)

    def test_png_exact_256_ihdr_dimensions(self):
        self.assertTrue(png_synthetic_shape(dummy_png()))
        self.assertFalse(png_synthetic_shape(PNG_MAGIC+struct.pack(">I",13)+b"IHDR"+struct.pack(">II",1,1)+b"x"*8))
        self.assertFalse(png_synthetic_shape(b"invalid"))

    def test_private_zip_scan_outputs_only_counts_not_samples_device_or_names(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"owner-private.zip"
            make_fixture(p)
            summary=audit_zip(p)
            self.assertEqual(summary["synthetic_pngs_256x256_verified"],3)
            self.assertEqual(summary["test_logs_unity_errors"],0)
            self.assertEqual(summary["gfx040_state_snapshots_examined"],1)
            self.assertEqual(summary["synthetic_gpu_probe_status"],"DIAGNOSTIC_INTERPOLATION_PASS")
            encoded=json.dumps(summary,sort_keys=True)
            self.assertNotIn("synthetic-session-01",encoded)
            self.assertNotIn("sampledColors",encoded)
            self.assertNotIn('"r":',encoded)
            self.assertFalse(summary["source_owner_data_text_published"])

    def test_incomplete_export_does_not_assert_gpu_runtime_pass(self):
        snap=original_free_status("INCONCLUSIVE_UNSUPPORTED_OR_NO_COLORED_PIXELS")
        snap["results"][1]["gpuReadbackCompleted"]=False
        snap["results"][1]["allSamplePositionsHaveColor"]=False
        snap["allThreeGpuReadbacksComplete"]=False
        x=validate_snapshot(snap)
        self.assertFalse(x["all_three_gpu_readbacks_completed"])
        self.assertEqual(x["synthetic_gpu_probe_status"],"INCONCLUSIVE_UNSUPPORTED_OR_NO_COLORED_PIXELS")

    def test_missing_or_wrong_experiment_snapshots_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"bad.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("README.txt","ok")
                z.writestr("sessions/test/snapshots.jsonl",
                           json.dumps({"kind":"state_snapshot","stateJson":'{"experiment":"OTHER"}'}))
                z.writestr("sessions/test/summary.json",'{"originalShaderRestored":false}')
            with self.assertRaisesRegex(ValueError,"NO_EXPERIMENT"):
                audit_zip(p)
