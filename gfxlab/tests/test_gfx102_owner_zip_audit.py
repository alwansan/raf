"""GFX102 purely synthetic source-free negative controls for the owner ZIP audit."""
import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from gfxlab.tools.gfx102_owner_zip_audit import audit,validate_png_rgba8_256

MODES=("Smooth","Flat","AffineEmulated","NativeNoPerspectiveES300",
       "NativeNoPerspectiveES310","NativeNoPerspectiveES320")

def png_fixture():
    def chunk(tag,payload):
        return (struct.pack(">I",len(payload))+tag+payload+
                struct.pack(">I",zlib.crc32(tag+payload)&0xffffffff))
    hdr=struct.pack(">IIBBBBB",256,256,8,6,0,0,0)
    row=b"\x00"+b"\x33\x66\xcc\xff"*256
    data=row*256
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",hdr)+chunk(b"IDAT",zlib.compress(data,9))+chunk(b"IEND",b"")

PNG=png_fixture()

def make_zip(path,*,extension=False,native=None,claim_success=False,
             bad_hash=False,bad_png=False,bad_original=False,wrong_trial=False,
             flat_failed=False):
    if native is not None and native not in (300,310,320):
        raise ValueError("fixture")
    modes=list(MODES[:3])
    if native is not None: modes.append("NativeNoPerspectiveES"+str(native))
    results=[]
    for mode in modes:
        results.append({
            "mode":mode,"gpu_readback":True,"cpu_affine_mad":0.005,
            "cpu_smooth_mad":0.005,"png_filename":"gpu-"+mode+".png",
            "png_sha256":"0"*64 if bad_hash else hashlib.sha256(PNG).hexdigest(),
        })
    status=("NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE" if claim_success else
            "NATIVE_EXTENSION_NOT_ADVERTISED" if not extension else
            "NATIVE_EXTENSION_ADVERTISED_BUT_ALL_GLSL_VERSIONS_FAILED" if native is None else
            "NATIVE_GPU_UNEXPECTED_INTERPOLATION")
    trial=[{"glsl_es_version":v,"gpu_readback":v==native,
            "affine_cpu_mad":.005 if v==native else None}
           for v in (300,310,320)]
    if wrong_trial:trial[0]["glsl_es_version"]=320
    summary={
        "experiment":"GFX-MULTI-102","originalShaderRestored":bad_original,
        "originalRaftShaderBytecodeUsed":False,"originalAnimationRestored":False,
        "pcAdrenoPixelParityVerified":False,"phase_closed":False,
        "nv_noperspective_extension_advertised":extension,
        "control_smooth_matches_cpu":True,
        "control_flat_stable":not flat_failed,
        "control_affine_emulated_matches_cpu":True,
        "native_extension_shader_compiled_and_linked":native is not None,
        "native_glsl_version_trials":trial,
        "native_best_glsl_es_version":native if native is not None else -1,
        "native_gpu_matches_cpu_affine":native is not None and claim_success,
        "native_gpu_matches_cpu_smooth_only":False,
        "diagnostic_status":status,
        "gpu_readbacks":len(modes),"results":results,
    }
    events=[{"event":"environment"}]+[{"event":"gpu_readback","result":row} for row in results]
    with ZipFile(path,"w",ZIP_DEFLATED) as zipf:
        zipf.writestr("summary.json",json.dumps(summary))
        zipf.writestr("events.jsonl","".join(json.dumps(e)+"\n" for e in events))
        zipf.writestr("LIMITS.txt","Original Shader48 not restored.")
        for mode in modes:
            raw=PNG[:-1]+b"x" if bad_png else PNG
            zipf.writestr("captures/gpu-"+mode+".png",raw)

class GFX102OwnerAuditTests(unittest.TestCase):
    def run_case(self,**kwargs):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"synthetic.zip"
            make_zip(p,**kwargs)
            return audit(p)
    def test_valid_png_fixture(self):
        self.assertTrue(validate_png_rgba8_256(PNG))
    def test_no_nv_extension_is_explicit_nonfailure(self):
        v=self.run_case()
        self.assertEqual(v["diagnostic_status"],"NATIVE_EXTENSION_NOT_ADVERTISED")
        self.assertEqual(v["gpu_capture_hashes_verified"],3)
    def test_three_versions_failed_explicit(self):
        v=self.run_case(extension=True)
        self.assertEqual(v["best_native_glsl_version"],-1)
        self.assertEqual(v["glsl_versions_tried"],[300,310,320])
    def test_glsl_320_native_gpu_verified(self):
        v=self.run_case(extension=True,native=320,claim_success=True)
        self.assertEqual(v["best_native_glsl_version"],320)
        self.assertTrue(v["native_gpu_affine_parity"])
        self.assertEqual(v["gpu_capture_hashes_verified"],4)
    def test_bad_original_shader_restored_claim_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNSAFE_ORIGINAL_SOURCE_SUCCESS"):
            self.run_case(bad_original=True)
    def test_bad_png_hash_rejected(self):
        with self.assertRaisesRegex(ValueError,"RESULT_PNG_INTEGRITY_FAILURE"):
            self.run_case(bad_hash=True)
    def test_corrupted_png_crc_rejected(self):
        with self.assertRaisesRegex(ValueError,"PNG_CHUNK_CRC_INVALID"):
            self.run_case(bad_png=True)
    def test_duplicate_version_trial_rejected(self):
        with self.assertRaisesRegex(ValueError,"TRIAL_VERSION_INVALID_OR_DUPLICATE"):
            self.run_case(wrong_trial=True)
    def test_native_pass_without_flat_control_rejected(self):
        with self.assertRaisesRegex(ValueError,"FORGED_NATIVE_SUCCESS"):
            self.run_case(extension=True,native=320,claim_success=True,flat_failed=True)
    def test_claimed_native_without_extension_rejected(self):
        with self.assertRaises(ValueError):
            self.run_case(extension=False,native=320,claim_success=True)

if __name__=="__main__":
    unittest.main()
