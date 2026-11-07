"""Source-free exhaustive partitions for the Foam Blit aggregate checker."""
import unittest
from scripts.t2_foam_pass_aggregate_consistency import check_counts

P = "field_api_Graphics_Blit_"
ROLES = {
    "source": ("Texture", "RenderTexture", "unknown"),
    "destination": ("RenderTexture", "null", "unknown"),
}

def fixture():
    report = {P + "explicit_sites_pass_" + x: 0 for x in
              ("literal0", "literal1", "other_literal", "unknown", "mixed")}
    report[P + "explicit_sites_pass_literal0"] = 1
    report[P + "explicit_sites_pass_literal1"] = 1
    for role, variants in ROLES.items():
        for variant in variants:
            for prefix in ("explicit_", "pass0_", "pass1_"):
                report[P + prefix + role + "_" + variant] = 0
    return report

def set_partition(report, role, first, second):
    for variant in ROLES[role]:
        report[P + "explicit_" + role + "_" + variant] = int(first == variant) + int(second == variant)
        report[P + "pass0_" + role + "_" + variant] = int(first == variant)
        report[P + "pass1_" + role + "_" + variant] = int(second == variant)

class ExhaustivePartitionTests(unittest.TestCase):
    def test_all_81_valid_combinations(self):
        for s0 in ROLES["source"]:
            for s1 in ROLES["source"]:
                for d0 in ROLES["destination"]:
                    for d1 in ROLES["destination"]:
                        with self.subTest(s0=s0, s1=s1, d0=d0, d1=d1):
                            report = fixture()
                            set_partition(report, "source", s0, s1)
                            set_partition(report, "destination", d0, d1)
                            self.assertEqual(check_counts(report), {
                                "classification_only": True,
                                "pass0": {"source": s0, "destination": d0},
                                "pass1": {"source": s1, "destination": d1},
                            })

    def test_all_single_category_aggregate_corruptions_fail(self):
        report = fixture()
        set_partition(report, "source", "Texture", "unknown")
        set_partition(report, "destination", "RenderTexture", "unknown")
        for role, variants in ROLES.items():
            for variant in variants:
                for delta in (-1, 1):
                    with self.subTest(role=role, variant=variant, delta=delta):
                        broken = report.copy()
                        key = P + "explicit_" + role + "_" + variant
                        broken[key] += delta
                        with self.assertRaises(ValueError):
                            check_counts(broken)

if __name__ == "__main__":
    unittest.main()
