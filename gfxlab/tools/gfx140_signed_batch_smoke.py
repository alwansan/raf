"""GFX140: build, align, sign, inspect & replay a synthetic 51-readback APK.

This intentionally never publishes a signed APK or fixture assets.  The source
Raft materials are NOT inputs.  A disposable test keystore lives in TemporaryDirectory.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from gfxlab.tests.test_gfx139_full_batch_replay import FullBatchReplay
from gfxlab.tools.gfx124_batch_zip_audit import audit

EXPECTED_PACKAGE = "com.alwansan.gfx124"


def checked(args):
    result = subprocess.run([str(x) for x in args], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            check=True)
    return result.stdout


def checksum(data):
    return sha256(data).hexdigest()


def verify_asset_integrity(before, after):
    with ZipFile(before) as unsigned, ZipFile(after) as signed:
        originals = {name for name in unsigned.namelist() if name.startswith("assets/")}
        finals = {name for name in signed.namelist() if name.startswith("assets/")}
        if originals != finals or len(originals) < 100:
            raise ValueError("APK source-free fixture assets changed after signing")
        if unsigned.testzip() or signed.testzip():
            raise ValueError("APK CRC failed")
        for name in sorted(originals):
            if checksum(unsigned.read(name)) != checksum(signed.read(name)):
                raise ValueError("Post-signing fixture asset payload mismatch")
        tests = json.loads(signed.read("assets/batch.json"))["tests"]
        if len(tests) != 9:
            raise ValueError("Wrong signed APK batch size")
        return len(originals)


def smoke(shell, tools, safe):
    with TemporaryDirectory(prefix="gfx140-private-synthetic-") as folder:
        work = Path(folder)
        FullBatchReplay.setUpClass()
        try:
            unpacked = work / "synthetic-batch-unsigned.apk"
            aligned = work / "synthetic-batch-aligned.apk"
            signed = work / "synthetic-batch-signed.apk"
            assert FullBatchReplay.pack_result["expected_captures"] == 51
            aggregate = FullBatchReplay.assemble(unpacked)
            if aggregate["tests"] != 9 or aggregate["expected_captures"] != 51:
                raise ValueError("Full synthetic batch assembly failed")
            checked([tools / "zipalign", "-f", "4", unpacked, aligned])
            store = work / "throwaway-synthetic.jks"
            checked(["keytool", "-genkeypair", "-noprompt", "-storetype", "JKS",
                     "-keystore", store, "-storepass", "synthetic-smoke-only",
                     "-keypass", "synthetic-smoke-only", "-alias", "gfx140-synthetic",
                     "-keyalg", "RSA", "-keysize", "2048", "-validity", "2",
                     "-dname", "CN=Source-Free Test, O=GFX-LAB, C=XX"])
            checked([tools / "apksigner", "sign", "--ks", store, "--ks-key-alias",
                     "gfx140-synthetic", "--ks-pass", "pass:synthetic-smoke-only",
                     "--key-pass", "pass:synthetic-smoke-only", "--out", signed, aligned])
            signature = checked([tools / "apksigner", "verify", "--verbose", signed])
            if "Verified using v2 scheme (APK Signature Scheme v2): true" not in signature:
                raise ValueError("APK v2 signature missing")
            if "Verified using v3 scheme (APK Signature Scheme v3): true" not in signature:
                raise ValueError("APK v3 signature missing")
            badging = checked([tools / "aapt2", "dump", "badging", signed])
            if f"name='{EXPECTED_PACKAGE}'" not in badging:
                raise ValueError("Signed APK package name mismatch")
            count = verify_asset_integrity(unpacked, signed)
            FullBatchReplay.apk = signed
            owner = FullBatchReplay.owner()
            with ZipFile(owner) as report:
                if len(report.namelist()) != 52:
                    raise ValueError("Signed APK replay did not produce 51 readbacks")
            owner.seek(0)
            checked_log = audit(owner, signed)
            if checked_log["completed_tests"] != 9 or len(checked_log["tests"]) != 9:
                raise ValueError("Owner ZIP audit against signed APK failed")
            out = {
                "experiment": "GFX140",
                "signed_apk_synthetic_only": True,
                "real_production_android_java_and_manifest_compiled": True,
                "signed_package_name": EXPECTED_PACKAGE,
                "zipaligned_before_signing": True,
                "apk_signature_v2_verified": True,
                "apk_signature_v3_verified": True,
                "post_signing_fixture_asset_count": count,
                "post_signing_asset_hash_parity": True,
                "owner_log_complete_tests": 9,
                "owner_log_verified_readbacks": 51,
                "fixture_original_raft_assets": False,
                "apk_or_original_assets_uploaded": False,
                "apk_or_original_assets_written_to_public_repository": False,
                "real_android_device_draw_verified": False,
                "phase_closed": False,
            }
            safe.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
            print(json.dumps(out, sort_keys=True))
            return out
        finally:
            FullBatchReplay.tearDownClass()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--shell", required=True, type=Path)
    p.add_argument("--tools", required=True, type=Path)
    p.add_argument("--safe", required=True, type=Path)
    args = p.parse_args()
    smoke(args.shell, args.tools, args.safe)
