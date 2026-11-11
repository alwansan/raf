"""GFX139: source-free full 9-case / 51-capture owner-batch replay.

Fixtures are synthetic byte patterns, NOT original Raft assets or a signed APK.
The test uses the production private batch packer and owner-ZIP auditor.
"""
from __future__ import annotations

import io
import json
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image
from gfxlab.tools.gfx124_batch_pack import (
    CONTROLS, SLOTS, POSES, SHADOW_CONTROLS, DEFERRED_CAPTURES,
    REFERENCE_SIZE, inject,
)
from gfxlab.tools.gfx124_batch_zip_audit import audit

SIZE = 256
COVERED = 2008

def digest(data):
    return hashlib.sha256(data).hexdigest()


def rgba(rgb, count=COVERED):
    return bytes((*rgb, 255)) * count + bytes(4) * (SIZE * SIZE - count)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return digest(data)


def scene(folder, blocks, samplers, *, textured=False):
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(blocks):
        row = {"name": f"SYNTHETIC_BUFFER_{i}", "bytes": 16,
               "light": f"light-{i}.bin", "dark": f"dark-{i}.bin"}
        rows.append(row)
        save(folder / row["light"], bytes([i + 1]) * 16)
        save(folder / row["dark"], bytes([i + 2]) * 16)
    document = {"blocks": rows, "samplers": [{"name": f"SYNTHETIC_SAMPLER_{i}"} for i in range(samplers)]}
    if textured:
        document["textures"] = {
            role: {"width": 1, "height": 1, "levels": 1, "source_color_space": 0 if role == "normal" else 1}
            for role in ("basecolor", "normal", "metallic")}
        for role in document["textures"]:
            save(folder / (role + ".rgba"), b"\x10\x20\x30\xff")
    save(folder / "scene.json", json.dumps(document).encode())
    save(folder / "probe.vert", b"// source-free synthetic vertex fixture\n")
    save(folder / "probe.frag", b"// source-free synthetic fragment fixture\n")
    save(folder / "mesh.bin", bytes(48))
    save(folder / "indices.bin", bytes(6))


def deferred_images():
    out = {}
    for control in ("native", "flat", "nonmetal"):
        for target in range(4):
            values = bytearray()
            for pixel in range(SIZE * SIZE):
                valid = pixel < COVERED
                p = [40 + target, 60 + target, 80 + target, 255] if valid else [0, 0, 0, 0]
                if target == 3:
                    p = [0, 0, 0, 0]
                if valid and control == "flat" and target == 2:
                    p[1] += 10
                if valid and control == "nonmetal" and target == 0 and pixel < 20:
                    p[0] += 4
                if valid and control == "nonmetal" and target == 1:
                    p[2] += 9
                values.extend(p)
            out[f"{control}-rt{target}"] = bytes(values)
    return out


def png_from_gpu(raw):
    image = Image.frombytes("RGBA", (SIZE, SIZE), raw)
    output = io.BytesIO()
    image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(output, format="PNG")
    return output.getvalue()


class FullBatchReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = TemporaryDirectory()
        cls.root = Path(cls.work.name)
        cls.models = cls.root / "models"
        cls.m02 = cls.root / "M02-0"
        cls.additional = cls.root / "M02-0-add"
        cls.animation = cls.root / "M02-0-anim"
        cls.shadow = cls.root / "M02-0-shadow"
        cls.deferred = cls.root / "M02-0-deferred"
        cls.shell = cls.root / "synthetic-shell.apk"
        with ZipFile(cls.shell, "w") as pack:
            pack.writestr("AndroidManifest.xml", b"SYNTHETIC ONLY")
            pack.writestr("classes.dex", b"SYNTHETIC ONLY")
        extra = []
        base = {}
        for i, slot in enumerate(SLOTS):
            path = cls.m02 if slot == "M02-0" else cls.models / slot
            scene(path, 8, 7, textured=True)
            images = {
                "light": rgba((25 + 10 * i, 70, 100)),
                "dark": rgba((0, 0, 0)),
                "flat": rgba((25 + 10 * i, 90, 100)),
                "nonmetal": rgba((25 + 10 * i, 70, 120)),
            }
            for mode, raw in images.items():
                save(path / (mode + ".rgba"), raw)
            base[slot] = images
            if slot != "M02-0":
                draw = {"rgba_sha256": digest(images["light"])}
                if slot == "M03-0":
                    draw["two_slots_shared_depth_draw"] = {
                        "rgba_sha256": save(path / "combined.rgba", images["light"])}
                model, number = slot.split("-")
                extra.append({"model": model, "slot": int(number), "mesa_draw": draw})
        cls.evidence = cls.root / "model-evidence.json"
        save(cls.evidence, json.dumps({
            "m02_regression_rgba_sha256": digest(base["M02-0"]["light"]), "slots": extra
        }).encode())
        scene(cls.additional, 8, 4)
        cls.additional_evidence = cls.root / "add-evidence.json"
        add_raw = rgba((90, 80, 120))
        save(cls.additional / "combined.rgba", add_raw)
        save(cls.additional_evidence, json.dumps({"mesa": {"forward_add": {
            "composite_rgba_sha256": digest(add_raw)}}}).encode())
        scene(cls.animation, 8, 7)
        samples, captures = [], []
        for i, pose in enumerate(POSES):
            mesh = bytes([i + 1]) * 48
            rendered = rgba((50 + i, 75, 100))
            samples.append({"sample": pose, "vertex_sha256": save(cls.animation / (pose + ".bin"), mesh)})
            captures.append({"sample": pose, "rgba_sha256": save(cls.animation / (pose + ".rgba"), rendered)})
        cls.animation_evidence = cls.root / "animation-evidence.json"
        save(cls.animation_evidence, json.dumps({"samples": samples, "mesa": {"animation": {"samples": captures}}}).encode())
        scene(cls.shadow, 6, 1)
        shadow_data = {
            "native": rgba((80, 80, 80)), "solid": rgba((80, 80, 80)),
            "transparent": bytes(REFERENCE_SIZE), "depth-off": bytes(REFERENCE_SIZE),
        }
        cls.shadow_evidence = cls.root / "shadow-evidence.json"
        save(cls.shadow_evidence, json.dumps({"shadow_caster": {"reference_hashes": {
            control: save(cls.shadow / (control + ".rgba"), shadow_data[control])
            for control in SHADOW_CONTROLS}}}).encode())
        scene(cls.deferred, 5, 4)
        cls.deferred_evidence = cls.root / "deferred-evidence.json"
        deferred = deferred_images()
        save(cls.deferred_evidence, json.dumps({"deferred": {"reference_hashes": {
            control: save(cls.deferred / (control + ".rgba"), deferred[control])
            for control in DEFERRED_CAPTURES}}}).encode())
        cls.apk = cls.root / "private-synthetic-batch.apk"
        cls.pack_result = cls.assemble(cls.apk)

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    @classmethod
    def assemble(cls, out):
        return inject(cls.shell, cls.m02, cls.models, cls.evidence, out,
                      forward_add=cls.additional, add_evidence=cls.additional_evidence,
                      animation=cls.animation, animation_evidence=cls.animation_evidence,
                      shadow=cls.shadow, shadow_evidence=cls.shadow_evidence,
                      deferred=cls.deferred, deferred_evidence=cls.deferred_evidence)

    @classmethod
    def owner(cls, *, failed=None, forged=None, shuffled=False, omit=None):
        """Construct the identical summary schema produced by the Android runner."""
        report = {"experiment": "GFX124", "renderer": "synthetic-no-device",
                  "gles": "source-free-test", "phase_closed": False, "tests": []}
        exported = {}
        with ZipFile(cls.apk) as package:
            planned = json.loads(package.read("assets/batch.json"))["tests"]
            for test in planned:
                case = test["id"]
                run = {"id": case, "draw_completed": case != failed, "captures": []}
                if case == failed:
                    run["error"] = "synthetic forced per-case error"
                    report["tests"].append(run)
                    continue
                primary = test["primary"]
                merged = "secondary" in test
                add = "forward_add" in test
                anim = "animation" in test
                shadow = "shadow" in test
                deferred = "deferred" in test
                controls = (DEFERRED_CAPTURES if deferred else SHADOW_CONTROLS if shadow else
                            POSES if anim else ("lit", "off", "reject") if add else
                            ("combined",) if merged else CONTROLS)
                for control in controls:
                    capture = case if merged else f"{case}-{control}"
                    if deferred:
                        name = capture + ".rgba"
                        reference = package.read(f'assets/{test["deferred"]}/{control}.rgba')
                        raw = bytearray(reference)
                        if forged == capture:
                            raw[0] ^= 1  # Counter and hash are recomputed: only semantic test can reject it.
                        raw = bytes(raw)
                        differences = [abs(a-b) for a, b in zip(raw, reference, strict=True)]
                        row = {"name": capture, "raw": name,
                               "raw_rgba_sha256": digest(raw), "mesa_rgba_sha256": digest(reference),
                               "rgba_absolute_error_sum": sum(differences),
                               "max_rgba_channel_error": max(differences)}
                        exported[name] = raw
                    else:
                        folder = primary
                        reference_name = control
                        if anim:
                            folder = test["animation"]
                        if shadow:
                            folder = test["shadow"]
                        if add:
                            folder = test["forward_add"] if control == "lit" else primary
                            reference_name = "combined" if control == "lit" else "light"
                        reference = package.read(f"assets/{folder}/{reference_name}.rgba")
                        name = capture + ".png"
                        image = png_from_gpu(reference)
                        covered = reference[3::4].count(255)
                        row = {"name": capture, "image": name, "image_sha256": digest(image),
                               "raw_rgba_sha256": digest(reference), "mesa_rgba_sha256": digest(reference),
                               "covered_pixels": covered, "coverage_different_pixels": 0,
                               "rgb_channels": covered * 3, "rgb_absolute_error_sum": 0,
                               "max_rgb_channel_error": 0}
                        exported[name] = image
                    run["captures"].append(row)
                report["tests"].append(run)
        if shuffled:
            report["tests"].reverse()
        report["planned_tests"] = len(report["tests"])
        report["completed_tests"] = sum(x["draw_completed"] for x in report["tests"])
        result = io.BytesIO()
        with ZipFile(result, "w", ZIP_DEFLATED) as logs:
            logs.writestr("summary.json", json.dumps(report))
            for name, data in exported.items():
                if name != omit:
                    logs.writestr(name, data)
        result.seek(0)
        return result

    def test_complete_9_cases_51_captures(self):
        self.assertEqual(self.pack_result["tests"], 9)
        self.assertEqual(self.pack_result["expected_captures"], 51)
        with ZipFile(self.apk) as package:
            self.assertIsNone(package.testzip())
            self.assertEqual(len(json.loads(package.read("assets/batch.json"))["tests"]), 9)
        owner = self.owner()
        with ZipFile(owner) as report:
            self.assertEqual(len(report.namelist()) - 1, 51)
            self.assertEqual(sum(name.endswith('.png') for name in report.namelist()), 39)
            self.assertEqual(sum(name.endswith('.rgba') for name in report.namelist()), 12)
        owner.seek(0)
        safe = audit(owner, self.apk)
        self.assertEqual(safe["completed_tests"], 9)
        self.assertTrue(safe["tests"][-1]["deferred_semantics"]["coverage_matches_reference"])
        self.assertTrue(all(safe["tests"][-2]["shadow_controls"].values()))
        self.assertFalse(safe["phase_closed"])

    def test_partial_failure_retains_eight_cases(self):
        safe = audit(self.owner(failed="M02-deferred"), self.apk)
        self.assertEqual(safe["completed_tests"], 8)
        self.assertFalse(safe["tests"][-1]["draw_completed"])
        self.assertIn("error", safe["tests"][-1])

    def test_forged_self_consistent_deferred_channel_rejected(self):
        with self.assertRaisesRegex(ValueError, "unrelated render target"):
            audit(self.owner(forged="M02-deferred-flat-rt1"), self.apk)

    def test_missing_image_rejected(self):
        with self.assertRaises(KeyError):
            audit(self.owner(omit="M02-animation-C2P4.png"), self.apk)

    def test_reordered_summary_rejected(self):
        with self.assertRaisesRegex(ValueError, "order or identity"):
            audit(self.owner(shuffled=True), self.apk)

    def test_private_reference_tampering_rejected_by_packer(self):
        target = self.m02 / "light.rgba"
        original = target.read_bytes()
        try:
            target.write_bytes(bytes([original[0] ^ 1]) + original[1:])
            with self.assertRaisesRegex(ValueError, "Reference identity mismatch"):
                self.assemble(self.root / "bad-hash-batch.apk")
        finally:
            target.write_bytes(original)

    def test_extra_source_file_rejected_by_packer(self):
        extra = self.shadow / "unverified-original-hint.bin"
        try:
            extra.write_bytes(b"unexpected")
            with self.assertRaisesRegex(ValueError, "Unexpected private slot payload"):
                self.assemble(self.root / "bad-extra-batch.apk")
        finally:
            extra.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
