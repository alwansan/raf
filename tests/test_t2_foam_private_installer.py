"""T2 original Foam transient installer synthetic, source-free negative controls.

Original game shader source, original MonoScript, private stage and real .meta
must never be embedded in test fixtures or published artifacts.
"""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.b24_original_foam_stage_translation import TARGET
from scripts.t2_foam_private_installer import (
    _read_safe_stage, install, require_attested_stage,
)
from scripts.b45_install_original_blur import _atomic_replace_bytes


META = b"fileFormatVersion: 2\nguid: " + b"a" * 32 + b"\n"
PLACEHOLDER = ('Shader "' + TARGET + '" { SubShader { Pass { } } }\n').encode()
CANDIDATE = ('Shader "' + TARGET + '" { '
             'Properties { _SyntheticTex ("Test", 2D) = "white" {} '
             '_SyntheticVector ("Vector", Vector) = (0,0,0,0) } '
             'SubShader { Pass { HLSLPROGRAM\nvoid main(){}\nENDHLSL } '
             'Pass { HLSLPROGRAM\nvoid main(){}\nENDHLSL } } }\n').encode()
SHA = hashlib.sha256(CANDIDATE).hexdigest()


def stage():
    return {
        "status": "original_private_foam_two_pass_shaderlab_structural_candidate",
        "private_candidate_bytes": len(CANDIDATE),
        "original_passes": 2,
        "original_program_stages": 4,
        "original_stage_models_verified": 4,
        "authentic_pass_states": 2,
        "complete_structural_passes": 2,
        "authored_properties": 2,
        "authored_texture_properties": 1,
        "original_DXBC_stage_model_SHA_verified": True,
        "shaderlab_target_derived_per_pass_not_guessed": True,
        "shaderlab_unity_import_verified": False,
        "original_cb0_name_or_data_upload_verified": False,
        "original_material_sampler_upload_verified": False,
        "original_numeric_or_device_pixels_verified": False,
        "private_shaderlab_published": False,
    }


def fixture(directory):
    root = Path(directory)
    project = root / "Project"
    shader_dir = project / "Assets" / "Water"
    shader_dir.mkdir(parents=True)
    target = shader_dir / "OriginalFoam.shader"
    target.write_bytes(PLACEHOLDER)
    Path(str(target) + ".meta").write_bytes(META)
    candidate = root / "private-candidate.shader"
    candidate.write_bytes(CANDIDATE)
    backup = root / "private-recovery"
    return project, target, candidate, backup


class FoamInstallTests(unittest.TestCase):
    def test_real_transaction_preserves_export_and_guid_in_external_backup(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            r = install(project, candidate, backup, SHA, stage())
            self.assertEqual(r["unique_original_foam_exported_target_installed"], 1)
            self.assertEqual(target.read_bytes(), CANDIDATE)
            self.assertEqual(Path(str(target) + ".meta").read_bytes(), META)
            self.assertEqual((backup / "original.shader").read_bytes(), PLACEHOLDER)
            self.assertEqual((backup / "original.shader.meta").read_bytes(), META)
            self.assertFalse(r["Unity_2021_import_verified"])
            self.assertFalse(r["original_Material_CB0_runtime_binding_verified"])
            self.assertFalse(r["Android_water_pixels_verified"])

    def test_tampered_candidate_fails_before_backup(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            candidate.write_bytes(CANDIDATE + b"mismatch")
            with self.assertRaises(ValueError):
                install(project, candidate, backup, SHA, stage())
            self.assertEqual(target.read_bytes(), PLACEHOLDER)
            self.assertFalse(backup.exists())

    def test_stage_forged_positive_runtime_flag_fails_closed(self):
        for key in ("shaderlab_unity_import_verified",
                    "original_cb0_name_or_data_upload_verified",
                    "original_material_sampler_upload_verified",
                    "original_numeric_or_device_pixels_verified",
                    "private_shaderlab_published"):
            with tempfile.TemporaryDirectory() as d:
                project, target, candidate, backup = fixture(d)
                a = stage()
                a[key] = True
                with self.subTest(key=key), self.assertRaises(ValueError):
                    install(project, candidate, backup, SHA, a)
                self.assertFalse(backup.exists())
                self.assertEqual(target.read_bytes(), PLACEHOLDER)

    def test_missing_and_wrong_type_stage_fields_rejected(self):
        for mutate in (lambda s: s.pop("authentic_pass_states"),
                       lambda s: s.__setitem__("original_passes", True),
                       lambda s: s.__setitem__("original_stage_models_verified", 3),
                       lambda s: s.__setitem__("authored_texture_properties", 0),
                       lambda s: s.__setitem__("private_candidate_bytes", 0),
                       lambda s: s.__setitem__("original_DXBC_stage_model_SHA_verified", 1)):
            a = stage()
            mutate(a)
            with self.subTest(stage=a), self.assertRaises(ValueError):
                require_attested_stage(a, len(CANDIDATE))

    def test_no_shaderlab_topology_bypass_from_attestation(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            body = CANDIDATE.replace(b"ENDHLSL } Pass {", b"ENDHLSL } Stage {")
            candidate.write_bytes(body)
            a = stage()
            a["private_candidate_bytes"] = len(body)
            with self.assertRaises(ValueError):
                install(project, candidate, backup, hashlib.sha256(body).hexdigest(), a)
            self.assertFalse(backup.exists())

    def test_extra_shader_header_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            body = CANDIDATE + PLACEHOLDER
            candidate.write_bytes(body)
            a = stage()
            a["private_candidate_bytes"] = len(body)
            with self.assertRaises(ValueError):
                install(project, candidate, backup, hashlib.sha256(body).hexdigest(), a)
            self.assertFalse(backup.exists())

    def test_export_requires_one_target(self):
        for mode in ("missing", "duplicate"):
            with tempfile.TemporaryDirectory() as d:
                project, target, candidate, backup = fixture(d)
                if mode == "missing":
                    target.write_text('Shader "Synthetic/NotFoam" { SubShader {} }')
                else:
                    (target.parent / "DuplicateFoam.shader").write_bytes(PLACEHOLDER)
                with self.subTest(mode=mode), self.assertRaises(ValueError):
                    install(project, candidate, backup, SHA, stage())
                self.assertFalse(backup.exists())

    def test_metadata_malformed_or_missing(self):
        for value in (None, b"guid: not-a-guid\n", b"guid: " + b"a" * 32 + b"\nguid: " + b"b" * 32):
            with tempfile.TemporaryDirectory() as d:
                project, target, candidate, backup = fixture(d)
                meta = Path(str(target) + ".meta")
                if value is None:
                    meta.unlink()
                else:
                    meta.write_bytes(value)
                with self.subTest(value=value is None), self.assertRaises(ValueError):
                    install(project, candidate, backup, SHA, stage())
                self.assertEqual(target.read_bytes(), PLACEHOLDER)
                self.assertFalse(backup.exists())

    def test_backup_must_be_external_and_fresh(self):
        for within in (True, False):
            with tempfile.TemporaryDirectory() as d:
                project, target, candidate, backup = fixture(d)
                where = project / "Assets" / "Water" / "backup" if within else backup
                if not within:
                    where.mkdir()
                with self.subTest(within=within), self.assertRaises(ValueError):
                    install(project, candidate, where, SHA, stage())
                self.assertEqual(target.read_bytes(), PLACEHOLDER)

    def test_candidate_and_original_symlinks_rejected(self):
        for which in ("candidate", "target", "meta"):
            with tempfile.TemporaryDirectory() as d:
                project, target, candidate, backup = fixture(d)
                selected = {"candidate": candidate, "target": target,
                            "meta": Path(str(target) + ".meta")}[which]
                outside = Path(d) / (which + "-outside")
                outside.write_bytes(selected.read_bytes())
                selected.unlink()
                selected.symlink_to(outside)
                with self.subTest(which=which), self.assertRaises(ValueError):
                    install(project, candidate, backup, SHA, stage())
                self.assertFalse(backup.exists())

    def test_atomic_failure_keeps_external_verified_backup(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            with mock.patch("scripts.t2_foam_private_installer._atomic_replace_bytes",
                            side_effect=OSError("synthetic write fail")):
                with self.assertRaises(OSError):
                    install(project, candidate, backup, SHA, stage())
            self.assertEqual(target.read_bytes(), PLACEHOLDER)
            self.assertEqual((backup / "original.shader").read_bytes(), PLACEHOLDER)
            self.assertFalse(list(target.parent.glob(".t2-foam-install-*")))

    def test_post_promotion_corruption_rolls_back_atomically(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            def corrupt(path, data, prefix):
                _atomic_replace_bytes(path, data, prefix)
                if prefix == ".t2-foam-install-":
                    path.write_bytes(b"damaged-synthetic")
            with mock.patch("scripts.t2_foam_private_installer._atomic_replace_bytes",
                            side_effect=corrupt):
                with self.assertRaises(ValueError):
                    install(project, candidate, backup, SHA, stage())
            self.assertEqual(target.read_bytes(), PLACEHOLDER)
            self.assertEqual((backup / "original.shader").read_bytes(), PLACEHOLDER)
            self.assertEqual(Path(str(target) + ".meta").read_bytes(), META)

    def test_rollback_failure_refuses_success_and_retains_pristine_backup(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            def fail_rollback(path, data, prefix):
                if prefix == ".t2-foam-install-":
                    _atomic_replace_bytes(path, b"damaged-synthetic", prefix)
                else:
                    raise OSError("synthetic rollback error")
            with mock.patch("scripts.t2_foam_private_installer._atomic_replace_bytes",
                            side_effect=fail_rollback):
                with self.assertRaises(RuntimeError):
                    install(project, candidate, backup, SHA, stage())
            self.assertEqual((backup / "original.shader").read_bytes(), PLACEHOLDER)
            self.assertEqual((backup / "original.shader.meta").read_bytes(), META)

    def test_duplicate_stage_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text('{"status":"good","status":"evil"}')
            with self.assertRaises(ValueError):
                _read_safe_stage(p)

    def test_symlinked_backup_parent_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project, target, candidate, backup = fixture(d)
            real = Path(d) / "real"
            real.mkdir()
            linked = Path(d) / "linked"
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaises(ValueError):
                install(project, candidate, linked / "backup", SHA, stage())
            self.assertEqual(target.read_bytes(), PLACEHOLDER)


if __name__ == "__main__":
    unittest.main()
