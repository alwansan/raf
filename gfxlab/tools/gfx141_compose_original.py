"""GFX141: assemble and sign a staged owner-private, source-original 9-case APK.

Must be called only after source-pin verification and genuine Mesa draws.
Never upload the resulting APK or the private staged files from a public CI job.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from gfxlab.tools.original_model_probe import ZIP2_SHA
from gfxlab.tools.gfx124_batch_pack import inject, SLOTS, DEFERRED_CAPTURES
from gfxlab.tools.gfx140_signed_batch_smoke import checked, verify_asset_integrity, EXPECTED_PACKAGE


def load(path):
    return json.loads(path.read_text())


def compose(private, shell, tools, safe):
    work = private
    original = load(work / "m02-mesa.json")
    models = load(work / "model-stage.json")
    poses = load(work / "animation-stage.json")
    textures = load(work / "mip-stage.json")
    if models.get("source_sha") != ZIP2_SHA or poses.get("source_sha") != ZIP2_SHA or textures.get("source_sha") != ZIP2_SHA:
        raise ValueError("Original source provenance mismatch")
    if not original.get("original_translated_forward_draw_completed"):
        raise ValueError("Original Mesa Forward did not draw")
    if original["deferred"]["same_coverage_as_forward"] is not True:
        raise ValueError("Original source Deferred coverage differs")
    if len(poses["samples"]) != 15 or tuple(row["sample"] for row in poses["samples"]) != tuple(
        f"C{clip}P{pose}" for clip in range(3) for pose in range(5)
    ):
        raise ValueError("Original animation sample provenance differs")
    scenes = []
    for slot in ("M00-0", "M03-0", "M03-1"):
        name, index = slot.split("-")
        scenes.append({"model": name, "slot": int(index), "mesa_draw": load(work / f"{slot}-mesa.json")})
    (work / "models-evidence.json").write_text(json.dumps({
        "m02_regression_rgba_sha256": original["rgba_sha256"], "slots": scenes}))
    (work / "animation-evidence.json").write_text(json.dumps({
        "samples": poses["samples"], "mesa": {"animation": original["animation"]}}))
    unsigned = work / "GFX141-original-unsigned.apk"
    aligned = work / "GFX141-original-aligned.apk"
    signed = work / "GFX141-original-signed.apk"
    result = inject(
        shell, work / "M02-0", work / "models", work / "models-evidence.json", unsigned,
        forward_add=work / "M02-0-add", add_evidence=work / "m02-mesa.json",
        animation=work / "M02-0-anim", animation_evidence=work / "animation-evidence.json",
        shadow=work / "M02-0-shadow", shadow_evidence=work / "m02-mesa.json",
        deferred=work / "M02-0-deferred", deferred_evidence=work / "m02-mesa.json",
    )
    if (result["tests"], result["expected_captures"]) != (9, 51):
        raise ValueError("Original fixture did not supply all 9 cases and 51 references")
    checked([tools / "zipalign", "-f", "4", unsigned, aligned])
    store = work / "disposable-debug-keystore.jks"
    checked(["keytool", "-genkeypair", "-noprompt", "-storetype", "JKS",
             "-keystore", store, "-storepass", "temporary-gfx141-only",
             "-keypass", "temporary-gfx141-only", "-alias", "gfx141-debug",
             "-keyalg", "RSA", "-keysize", "2048", "-validity", "2",
             "-dname", "CN=GFX-LAB Temporary Test, O=Diagnostic Build, C=XX"])
    checked([tools / "apksigner", "sign", "--v2-signing-enabled", "true",
             "--v3-signing-enabled", "true", "--ks", store,
             "--ks-key-alias", "gfx141-debug",
             "--ks-pass", "pass:temporary-gfx141-only",
             "--key-pass", "pass:temporary-gfx141-only",
             "--out", signed, aligned])
    signature = checked([tools / "apksigner", "verify", "--verbose", signed])
    if "Verified using v3 scheme (APK Signature Scheme v3): true" not in signature:
        raise ValueError("Original owner APK v3 signature did not verify")
    if f"name='{EXPECTED_PACKAGE}'" not in checked([tools / "aapt2", "dump", "badging", signed]):
        raise ValueError("Android package name changed")
    count = verify_asset_integrity(unsigned, signed)
    with ZipFile(signed) as apk:
        entries = set(apk.namelist())
        planned = load_json = json.loads(apk.read("assets/batch.json"))["tests"]
        if len(planned) != 9 or any(f"assets/{slot}/scene.json" not in entries for slot in
            (*SLOTS, "M02-0-add", "M02-0-anim", "M02-0-shadow", "M02-0-deferred")
        ) or any(f"assets/M02-0-deferred/{control}.rgba" not in entries for control in DEFERRED_CAPTURES):
            raise ValueError("Original source private package incomplete")
    report = {
        "experiment": "GFX141", "source_sha": ZIP2_SHA,
        "original_source_pin_verified": True, "original_materials_models_mips": True,
        "original_mesa_forward_deferred_add_shadow_animation_prepared": True,
        "cases": result["tests"], "readbacks": result["expected_captures"],
        "apk_asset_count": count, "apk_size_bytes": signed.stat().st_size,
        "apk_sha256": sha256(signed.read_bytes()).hexdigest(),
        "android_package_name": EXPECTED_PACKAGE,
        "android_apk_v3_signature_verified": True, "post_signing_assets_unchanged": True,
        "public_original_assets_uploaded": False, "signed_apk_uploaded": False,
        "android_device_verified": False, "phase_closed": False
    }
    safe.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    signed.unlink()
    print(json.dumps(report, sort_keys=True))
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for key in ("private", "shell", "tools", "safe"):
        p.add_argument("--" + key, type=Path, required=True)
    args = p.parse_args()
    compose(args.private, args.shell, args.tools, args.safe)
