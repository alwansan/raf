#!/usr/bin/env python3
"""Synthetic-only tests: no owner ZIP or source game assets in CI."""
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from gfxlab.tools.unified098_owner_zip_audit import analyze, PREFIX

PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000b49444154789c636000020000050001a5f645400000000049454e44ae426082"
)
# PNG bytes serve only as a synthetic fixed sample; visual validity is not a claim.

def fake_archive(path, *, bad_hash=False, restore_claim=False, bad_summary=False):
    sid="synthetic-session"
    base=PREFIX+sid+"/"
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        meta={
            "session":sid,"originalShaderRestored":restore_claim,
            "devicePixelParityVerified":False,
            "eventsWritten":0,"snapshotsWritten":0,
            "unityErrors":0,"unityWarnings":0,"messagesDropped":0,
        }
        if bad_summary:
            meta["eventsWritten"]=1
        z.writestr(base+"summary.json",json.dumps(meta))
        z.writestr(base+"events.jsonl","")
        z.writestr(base+"snapshots.jsonl","")
        digest=hashlib.sha256(PNG).hexdigest()
        for model in range(6):
            for mode in (3,4):
                stem=f"M{model:02}_mode{mode}_synthetic"
                z.writestr(base+"model-matrix098/"+stem+".png",PNG)
                z.writestr(base+"model-matrix098/"+stem+".json",json.dumps({
                    "model":f"M{model:02}","materialMode":mode,
                    "pngFile":stem+".png",
                    "pngSha256":("0"*64 if bad_hash else digest),
                }))

class GFX098OwnerZipAuditTests(unittest.TestCase):
    def run_case(self,**kwargs):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"synthetic.zip"
            fake_archive(path,**kwargs)
            return analyze(path)
    def test_accept_synthetic_complete_matrix(self):
        result=self.run_case()
        self.assertEqual(result["capture_png_sha_verified"],12)
        self.assertEqual(result["unique_model_mode_cases"],12)
        self.assertFalse(result["originalShaderRestored"])
        self.assertFalse(result["phase_closed"])
        self.assertEqual(result["unity_errors"],0)
    def test_reject_wrong_capture_sha(self):
        with self.assertRaisesRegex(ValueError,"CAPTURE_IMAGE_SHA_MISMATCH"):
            self.run_case(bad_hash=True)
    def test_reject_false_original_shader_claim(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_SHADER_FALSE_PROOF"):
            self.run_case(restore_claim=True)
    def test_reject_counter_mismatch(self):
        with self.assertRaisesRegex(ValueError,"SESSION_COUNTS_MISMATCH"):
            self.run_case(bad_summary=True)

if __name__=="__main__":
    unittest.main()
