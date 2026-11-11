"""Synthetic GFX101 owner ZIP audit guards; no private data or original Raft assets."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from gfxlab.tools.gfx101_owner_zip_audit import audit

# Header only, intentionally artificial bytes; not presented as real phone pixel data.
PNG=b"\x89PNG\r\n\x1a\n"+b"\x00\x00\x00\x0dIHDR"+(256).to_bytes(4,"big")*2+b"\x08\x06\x00\x00\x00"+b"fake_crc"
MODES=("Smooth","Flat","AffineEmulated","NativeNoPerspective")

def create_zip(path,*,extension=False,claim_success=False,shader_restored=False,
               corrupt_png=False,missing_png=False):
    modes=MODES if extension else MODES[:3]
    results=[]
    for mode in modes:
        results.append({
            "mode":mode,"gpu_readback":True,
            "cpu_smooth_mad":0.02,"cpu_affine_mad":0.02,
            "png_filename":"gpu-"+mode+".png",
            "png_sha256":("0"*64 if corrupt_png else hashlib.sha256(PNG).hexdigest()),
        })
    summary={
        "experiment":"GFX-MULTI-101",
        "originalShaderRestored":shader_restored,
        "originalRaftShaderBytecodeUsed":False,
        "originalAnimationRestored":False,
        "pcAdrenoPixelParityVerified":False,"phase_closed":False,
        "nv_noperspective_extension_advertised":extension,
        "control_smooth_matches_cpu":True,
        "control_affine_emulated_matches_cpu":True,
        "control_flat_stable":True,
        "native_extension_shader_compiled_and_linked":extension,
        "native_gpu_matches_cpu_affine":extension,
        "native_gpu_matches_cpu_smooth_only":False,
        "diagnostic_status":("NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE"
            if claim_success else ("NATIVE_GPU_UNEXPECTED_INTERPOLATION" if extension else
                                   "NATIVE_EXTENSION_NOT_ADVERTISED")),
        "gpu_readbacks":len(modes),"results":results,
    }
    events=[{"event":"environment"}]+[{"event":"gpu_readback","result":row} for row in results]
    with ZipFile(path,"w",ZIP_DEFLATED) as z:
        z.writestr("summary.json",json.dumps(summary))
        z.writestr("events.jsonl","".join(json.dumps(row)+"\n" for row in events))
        z.writestr("LIMITS.txt","SYNTHETIC ONLY")
        for mode in modes:
            if missing_png and mode==modes[-1]: continue
            z.writestr("captures/gpu-"+mode+".png",PNG)

class GFX101OwnerZIPTests(unittest.TestCase):
    def run_case(self,**kwargs):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"synthetic.zip"
            create_zip(p,**kwargs)
            return audit(p)
    def test_no_extension_valid_decline(self):
        got=self.run_case()
        self.assertEqual(got["gpu_capture_png_sha_verified"],3)
        self.assertFalse(got["supported_optional_extension"])
        self.assertFalse(got["original_shader_restored"])
    def test_extension_native_success_requires_real_evidence_fields(self):
        got=self.run_case(extension=True,claim_success=True)
        self.assertEqual(got["diagnostic_status"],"NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE")
        self.assertEqual(got["gpu_capture_png_sha_verified"],4)
    def test_false_original_shader_claim_rejected(self):
        with self.assertRaisesRegex(ValueError,"FALSE_ORIGINAL_SOURCE_PROOF"):
            self.run_case(shader_restored=True)
    def test_corrupt_sha_rejected(self):
        with self.assertRaisesRegex(ValueError,"GPU_PNG_HASH_MISMATCH"):
            self.run_case(corrupt_png=True)
    def test_missing_capture_rejected(self):
        with self.assertRaisesRegex(ValueError,"GPU_PNG_NOT_FOUND"):
            self.run_case(missing_png=True)
    def test_forged_native_pass_without_extension_rejected(self):
        with self.assertRaisesRegex(ValueError,"NATIVE_SUCCESS_LACKS_REQUIRED_GPU_EVIDENCE"):
            self.run_case(extension=False,claim_success=True)

if __name__=="__main__":
    unittest.main()
