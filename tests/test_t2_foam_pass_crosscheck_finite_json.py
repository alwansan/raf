"""Source-free Foam CLI ingress regression: JSON exponent overflow is not parse_constant."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.t2_foam_pass_crosscheck import finite_float, main
from tests.test_t2_foam_pass_crosscheck_original_integration import full_safe_fixture, sites


class FoamFiniteJsonIngressTests(unittest.TestCase):
    def test_overflow_float_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonfinite_json"):
            finite_float("1e999")

    def test_finite_float_remains_finite(self):
        self.assertEqual(finite_float("1.25e2"), 125.0)

    def test_cli_rejects_overflow_in_original_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original.json"
            roles = Path(tmp) / "roles.json"
            data = json.dumps(full_safe_fixture())
            # A valid original numeric field replaced by a JSON exponent overflow.
            data = data.replace('"original_compiled_method_bodies_scanned": 19118',
                                '"original_compiled_method_bodies_scanned": 1e999')
            self.assertIn("1e999", data)
            original.write_text(data, encoding="utf-8")
            roles.write_text(json.dumps(sites("RenderTexture", "unknown",
                                             "RenderTexture", "unknown")), encoding="utf-8")
            with patch.object(sys, "argv", ["crosscheck", str(original), str(roles)]):
                with self.assertRaisesRegex(ValueError, "nonfinite_json"):
                    main()

    def test_cli_accepts_complete_safe_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original.json"
            roles = Path(tmp) / "roles.json"
            original.write_text(json.dumps(full_safe_fixture()), encoding="utf-8")
            roles.write_text(json.dumps(sites("RenderTexture", "unknown",
                                             "RenderTexture", "unknown")), encoding="utf-8")
            with patch.object(sys, "argv", ["crosscheck", str(original), str(roles)]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    main()
            self.assertTrue(json.loads(output.getvalue())["independent_summaries_agree"])


if __name__ == "__main__":
    unittest.main()
