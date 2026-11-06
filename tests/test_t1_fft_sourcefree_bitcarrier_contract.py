"""Regression contract for the source-free Unity FFT bitcarrier canary.

This validates the fixture's *interpretability*, not Unity/GPU correctness.
"""
import unittest

from scripts.t1_sourcefree_dispatch_fixture import (
    _DISPATCH_ASSERTIONS,
    _DISPATCH_COMPUTE,
)


class BitcarrierCanaryContractTests(unittest.TestCase):
    def test_six_distinct_lanes_and_read_paths(self):
        expected = (
            "Output[6 * x] = ViaGlobal();",
            "Output[6 * x + 1] = ViaArgument(x);",
            "Output[6 * x + 2] = address;",
            "Output[6 * x + 3] = asuint(asfloat(address));",
            "Output[6 * x + 4] = asuint(subnormal);",
            "Output[6 * x + 5] = asuint(normal);",
        )
        for statement in expected:
            self.assertEqual(_DISPATCH_COMPUTE.count(statement), 1, statement)
        self.assertIn("static uint3 DispatchId;", _DISPATCH_COMPUTE)
        self.assertIn("shader.SetInt(\"AddressOffset\", 11);", _DISPATCH_ASSERTIONS)
        self.assertIn("shader.SetFloat(\"CarrierScale\", 1.0f);", _DISPATCH_ASSERTIONS)

    def test_address_permutation_is_unique_and_not_constant(self):
        # Odd multiplier 5 is invertible modulo 64; a collapsed address
        # signal cannot be explained by duplicate fixture input addresses.
        addresses = [((x << 2) + x + 11) & 63 for x in range(64)]
        self.assertEqual(len(set(addresses)), 64)
        self.assertEqual(addresses[0], 11)
        self.assertEqual(addresses[-1], 6)
        self.assertIn("((x << 2) + x + AddressOffset) & 63u", _DISPATCH_COMPUTE)

    def test_positive_controls_are_asserted_diagnostic_lanes_are_reported(self):
        for control in (
            "Assert.That(integerMismatches, Is.Zero",
            "Assert.That(normalMismatches, Is.Zero",
            "Assert.That(viaArgumentMismatches, Is.Zero",
            "Assert.That(viaGlobalMismatches, Is.Zero",
        ):
            self.assertIn(control, _DISPATCH_ASSERTIONS)
        for diagnostic in ("bitcastMismatches", "subnormalMismatches"):
            self.assertIn(diagnostic + ".ToString()", _DISPATCH_ASSERTIONS)
            self.assertNotIn(
                "Assert.That(" + diagnostic + ", Is.Zero", _DISPATCH_ASSERTIONS
            )
        self.assertIn("dispatch-address-counts.txt", _DISPATCH_ASSERTIONS)


if __name__ == "__main__":
    unittest.main()
