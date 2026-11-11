"""Adversarial public synthetic assertions; no original game code or IL data."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.t5_validate_resolution_delegate_probe import COUNTERS, DISCLAIMERS, load, verify


def baseline():
    ev = {key: 0 for key in COUNTERS}
    ev.update(compiled_methods=42, delegate_instruction_sites=2,
              resolved_delegate_sites=2, unique_delegate_target_methods=2,
              option_population_call_sites=1, methods_populating_options=1,
              internal_direct_call_edges=15)
    ev.update({key: False for key in DISCLAIMERS})
    return {
        "schema_version": 1, "original_assembly_sha_verified": True,
        "original_assembly_bytes": 3211776, "original_compiled_il": True,
        "unique_original_graphics_settings_type": True,
        "graph_method_limit": 256, "evidence": ev,
        "no_original_methods_tokens_il_or_sources_emitted": True,
        "event_registration_and_callback_dataflow_proven": False,
        "android_render_scale_persistence_proven": False,
        "actual_android_device_tested": False,
    }


class T5DelegateGraphGateTests(unittest.TestCase):
    def test_legacy_delegate_count_proven_not_android_callback(self):
        report = verify(baseline())
        self.assertEqual(report["original_compiled_delegate_sites_authenticated"], 2)
        self.assertFalse(report["runtime_ui_callback_dataflow_verified"])
        self.assertFalse(report["persistent_android_render_scale_verified"])

    def test_graph_target_can_reach_legacy_set_resolution_without_ui_proof(self):
        x = baseline()
        x["evidence"]["delegate_targets_reach_screen_setresolution"] = 1
        x["evidence"]["delegate_targets_direct_screen_setresolution"] = 1
        self.assertEqual(verify(x)["delegate_targets_reach_legacy_setresolution"], 1)
        self.assertFalse(verify(x)["runtime_ui_callback_dataflow_verified"])

    def test_options_unbound_to_handler_or_setter_stays_unproven(self):
        x = baseline()
        x["evidence"]["option_population_call_sites"] = 8
        x["evidence"]["methods_populating_options"] = 3
        self.assertEqual(verify(x)["option_population_methods_reach_setresolution"], 0)
        self.assertEqual(verify(x)["option_population_methods_contain_delegate_site"], 0)

    def test_original_missing_duplicate_or_unresolved_delegates_rejected(self):
        for key, value in [
            ("delegate_instruction_sites", 1), ("delegate_instruction_sites", 3),
            ("resolved_delegate_sites", 1), ("unresolved_delegate_sites", 1),
            ("unique_delegate_target_methods", 0), ("unique_delegate_target_methods", 3),
        ]:
            with self.subTest(key=key, value=value):
                x = baseline()
                x["evidence"][key] = value
                with self.assertRaises(ValueError):
                    verify(x)

    def test_distinct_methods_cannot_exceed_compiled_graph(self):
        for key in ("unique_delegate_target_methods", "methods_populating_options"):
            x = baseline()
            x["evidence"]["compiled_methods"] = 1
            if key == "unique_delegate_target_methods":
                x["evidence"]["unique_delegate_target_methods"] = 2
            else:
                x["evidence"]["unique_delegate_target_methods"] = 1
                x["evidence"]["option_population_call_sites"] = 2
                x["evidence"]["methods_populating_options"] = 2
            with self.subTest(key=key), self.assertRaisesRegex(
                ValueError, "Method population exceeds compiled"
            ):
                verify(x)

    def test_unknown_callsite_rejected_rather_than_false_no_path(self):
        x = baseline()
        x["evidence"]["unresolved_internal_call_sites"] = 1
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            verify(x)

    def test_direct_cannot_exceed_reachable_and_subsets_are_bounded(self):
        for key, value in [
            ("delegate_targets_direct_apply_calls", 1),
            ("delegate_targets_direct_screen_setresolution", 1),
            ("option_methods_direct_apply_calls", 1),
            ("delegate_targets_with_int_parameter", 3),
            ("option_methods_with_delegate_sites", 2),
        ]:
            with self.subTest(key=key):
                x = baseline()
                x["evidence"][key] = value
                with self.assertRaises(ValueError):
                    verify(x)

    def test_direct_apply_requires_internal_call_edge(self):
        for key in ("delegate_targets_direct_apply_calls",
                    "option_methods_direct_apply_calls"):
            x = baseline()
            x["evidence"]["internal_direct_call_edges"] = 0
            x["evidence"][key] = 1
            if key == "delegate_targets_direct_apply_calls":
                x["evidence"]["delegate_targets_reach_apply"] = 1
            else:
                x["evidence"]["option_methods_reach_apply"] = 1
            with self.subTest(key=key), self.assertRaisesRegex(
                ValueError, "Direct Apply calls exceed internal call edges"
            ):
                verify(x)

    def test_runtime_proof_unsupported(self):
        for top in ("event_registration_and_callback_dataflow_proven",
                    "android_render_scale_persistence_proven", "actual_android_device_tested"):
            x = baseline()
            x[top] = True
            with self.subTest(top=top), self.assertRaises(ValueError):
                verify(x)
        for nested in DISCLAIMERS:
            x = baseline()
            x["evidence"][nested] = True
            with self.subTest(nested=nested), self.assertRaises(ValueError):
                verify(x)

    def test_malformed_numeric_extra_fields_or_bad_original_pin_rejected(self):
        for name, value in [
            ("compiled_methods", True),
            ("internal_direct_call_edges", -1),
            ("delegate_targets_reach_apply", 100001),
        ]:
            x = baseline()
            x["evidence"][name] = value
            with self.subTest(name=name), self.assertRaises(ValueError):
                verify(x)
        x = baseline()
        x["evidence"]["original_method_token"] = "prohibited"
        with self.assertRaises(ValueError):
            verify(x)
        for top, bad in [("original_assembly_bytes", 3211775),
                         ("original_assembly_sha_verified", False),
                         ("original_compiled_il", False),
                         ("graph_method_limit", 9999)]:
            x = baseline()
            x[top] = bad
            with self.subTest(top=top), self.assertRaises(ValueError):
                verify(x)

    def test_file_bound_symlink_duplicate_json_and_utf8(self):
        with tempfile.TemporaryDirectory() as dir:
            p = Path(dir) / "report.json"
            p.write_text(json.dumps(baseline()), encoding="utf-8")
            self.assertEqual(load(p)["unique_targets"], 2)
            p.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_bytes(b"\xff\xfe")
            with self.assertRaises(UnicodeDecodeError):
                load(p)
            p.write_text("x" * 16385, encoding="utf-8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_text(json.dumps(baseline()), encoding="utf-8")
            link = Path(dir) / "alias.json"
            link.symlink_to(p)
            with self.assertRaises(ValueError):
                load(link)


if __name__ == "__main__":
    unittest.main()
