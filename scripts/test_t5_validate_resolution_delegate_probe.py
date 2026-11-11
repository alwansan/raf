#!/usr/bin/env python3
"""Source-only regression for contradictory original Resolution IL evidence."""
import unittest
from copy import deepcopy
from scripts.t5_validate_resolution_delegate_probe import verify, COUNTERS, DISCLAIMERS

def fixture():
    ev = {key: 0 for key in COUNTERS}
    ev.update({key: False for key in DISCLAIMERS})
    ev.update(compiled_methods=12, delegate_instruction_sites=2,
              resolved_delegate_sites=2, unique_delegate_target_methods=2,
              option_population_call_sites=2, methods_populating_options=2,
              option_methods_with_delegate_sites=2,
              delegate_targets_with_int_parameter=2)
    return dict(schema_version=1, original_assembly_sha_verified=True,
                original_assembly_bytes=3211776, original_compiled_il=True,
                unique_original_graphics_settings_type=True, graph_method_limit=256,
                evidence=ev, no_original_methods_tokens_il_or_sources_emitted=True,
                event_registration_and_callback_dataflow_proven=False,
                android_render_scale_persistence_proven=False,
                actual_android_device_tested=False)

class OriginalDelegateGateTests(unittest.TestCase):
    def test_structurally_consistent_report_does_not_claim_runtime(self):
        result = verify(fixture())
        self.assertFalse(result["runtime_ui_callback_dataflow_verified"])
        self.assertFalse(result["persistent_android_render_scale_verified"])
        self.assertFalse(result["device_tested"])

    def test_option_delegate_method_count_cannot_exceed_sites(self):
        a = fixture()
        a["evidence"]["option_population_call_sites"] = 3
        a["evidence"]["methods_populating_options"] = 3
        a["evidence"]["option_methods_with_delegate_sites"] = 3
        with self.assertRaisesRegex(ValueError, "More option delegate methods"):
            verify(a)

    def test_negative_or_boolean_counters_rejected(self):
        for value in (-1, True):
            with self.subTest(value=value):
                a = fixture()
                a["evidence"]["compiled_methods"] = value
                with self.assertRaises(ValueError):
                    verify(a)

    def test_runtime_claim_rejected(self):
        a = fixture()
        a["event_registration_and_callback_dataflow_proven"] = True
        with self.assertRaises(ValueError):
            verify(a)

if __name__ == "__main__":
    unittest.main()
