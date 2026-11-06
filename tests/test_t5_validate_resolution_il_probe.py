"""Synthetic negative and positive controls; never contains original game IL."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.t5_validate_resolution_il_probe import COUNTS, load, verify


def baseline():
    settings = {key: 0 for key in COUNTS}
    dynamic = {key: 0 for key in COUNTS}
    settings.update(method_bodies=12, call_sites=20, screen_set_resolution=1)
    dynamic.update(method_bodies=5, call_sites=7, scalable_resize_buffers=2)
    return dict(
        schema_version=1, original_assembly_sha_verified=True,
        original_assembly_bytes=3211776, original_classes_unique=True,
        settings=settings, dynamic=dynamic, compiled_il_inspected=True,
        option_to_callback_dataflow_proven=False,
        persisted_android_render_scale_proven=False,
        equal_axis_render_scale_proven=False, phone_tested=False,
        original_game_modified=False,
    )


class OriginalResolutionILGateTests(unittest.TestCase):
    def test_positive_is_only_original_structural_evidence(self):
        result = verify(baseline())
        self.assertTrue(result["original_compiled_display_calls_source_verified"])
        self.assertFalse(result["persisted_android_render_scale_proven"])
        self.assertFalse(result["option_to_callback_dataflow_proven"])

    def test_display_option_without_listener_is_not_claimed_bound(self):
        data = baseline()
        data["settings"]["screen_resolutions_read"] = 5
        data["settings"]["event_add_listener"] = 0
        self.assertFalse(verify(data)["option_to_callback_dataflow_proven"])

    def test_legacy_screen_setresolution_is_not_android_scale(self):
        data = baseline()
        data["settings"]["local_apply_resolution_calls"] = 3
        data["settings"]["playerprefs_writes"] = 2
        self.assertFalse(verify(data)["persisted_android_render_scale_proven"])

    def test_original_api_site_drift_rejected(self):
        for field, path, bad in (
            ("set", ("settings", "screen_set_resolution"), 0),
            ("resize", ("dynamic", "scalable_resize_buffers"), 1),
        ):
            with self.subTest(field=field):
                data = baseline()
                data[path[0]][path[1]] = bad
                with self.assertRaises(ValueError):
                    verify(data)

    def test_missing_or_boolean_numeric_and_extra_fields_rejected(self):
        for field, bad in (("method_bodies", True), ("call_sites", -1),
                           ("screen_set_resolution", 100001)):
            with self.subTest(field=field):
                data = baseline()
                data["settings"][field] = bad
                with self.assertRaises(ValueError):
                    verify(data)
        data = baseline()
        data["settings"]["original_method_name"] = "forbidden"
        with self.assertRaises(ValueError):
            verify(data)

    def test_proof_overstatement_rejected(self):
        for key in ("option_to_callback_dataflow_proven",
                    "persisted_android_render_scale_proven",
                    "equal_axis_render_scale_proven",
                    "phone_tested", "original_game_modified"):
            data = baseline()
            data[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(data)

    def test_nonoriginal_source_and_bad_bytes_rejected(self):
        for key, bad in (("original_assembly_sha_verified", False),
                         ("original_assembly_bytes", 3211777),
                         ("compiled_il_inspected", False)):
            data = baseline()
            data[key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(data)

    def test_duplicate_json_symlink_and_oversized_report_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "report.json"
            p.write_text(json.dumps(baseline()), encoding="utf-8")
            self.assertEqual(load(p)["settings_set_resolution_sites"], 1)
            p.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_text("x" * 8193, encoding="utf-8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_text(json.dumps(baseline()), encoding="utf-8")
            link = Path(root) / "link.json"
            link.symlink_to(p)
            with self.assertRaises(ValueError):
                load(link)


if __name__ == "__main__":
    unittest.main()
