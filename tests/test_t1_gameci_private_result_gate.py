"""Adversarial, source-free controls for the private Unity NUnit result boundary."""
import unittest
from scripts.t1_gameci_private_result_gate import classify, KNOWN


def xml_report(stage="synthetic", *, result="Passed", case_result="Passed",
               total=None, passed=None, failed=0, skipped=0, inconclusive=0,
               names=None):
    entries = sorted(KNOWN[stage]) if names is None else names
    count = len(entries)
    total = count if total is None else total
    passed = count if passed is None else passed
    cases = "".join(
        '<test-case fullname="%s" result="%s"><failure><message>PRIVATE SECRET, NEVER DISCLOSE</message></failure></test-case>' %
        (name, case_result) for name in entries
    )
    return ('<test-run testcasecount="%d" total="%d" passed="%d" failed="%d" '
            'skipped="%d" inconclusive="%d" result="%s">%s</test-run>' %
            (count,total,passed,failed,skipped,inconclusive,result,cases)).encode()


class T1PrivateReportGateTests(unittest.TestCase):
    def test_bounded_synthetic_two_actual_tests(self):
        row = classify(xml_report(),0,"synthetic")
        self.assertTrue(row["all_expected_tests_passed"])
        self.assertTrue(row["synthetic_unity_compute_test_verified"])
        self.assertFalse(row["original_derived_twenty_compute_import_groups_verified"])

    def test_real_derived_requires_its_own_single_import_test(self):
        row = classify(xml_report("original_derived"),0,"original_derived")
        self.assertTrue(row["all_expected_tests_passed"])
        self.assertTrue(row["original_derived_twenty_compute_import_groups_verified"])
        self.assertFalse(row["original_authored_compute_source_restored"])
        self.assertFalse(row["original_runtime_kernel_identity_mapping_proven"])
        self.assertFalse(row["android_adreno_or_water_pixels_proven"])

    def test_nonzero_process_cannot_be_passed(self):
        self.assertFalse(classify(xml_report(),3,"synthetic")["all_expected_tests_passed"])

    def test_failure_or_skipped_case_not_hidden(self):
        for report in (xml_report(result="Failed",passed=1,failed=1),
                       xml_report(case_result="Failed"),
                       xml_report(passed=1,skipped=1),
                       xml_report(passed=0,inconclusive=2)):
            with self.subTest(report=report[:70]):
                self.assertFalse(classify(report,0,"synthetic")["all_expected_tests_passed"])

    def test_wrong_test_identity_and_duplicates_fail(self):
        required = sorted(KNOWN["synthetic"])
        for names in ([required[0],"Unexpected.EditMode"],
                      [required[0],required[0]]):
            self.assertFalse(classify(xml_report(names=names),0,"synthetic")["all_expected_tests_passed"])

    def test_malformed_xml_and_header_rejected(self):
        for xml in (b"", b"<test-run", b"<not-a-test/>",
                    b"<test-run testcasecount=\"2\" total=\"2\"/>",
                    b"x"*(1024*1024+1)):
            with self.subTest(size=len(xml)):
                with self.assertRaises(ValueError):
                    classify(xml,0,"synthetic")

    def test_faked_original_result_cannot_pass_synthetic(self):
        self.assertFalse(classify(xml_report("original_derived"),0,"synthetic")["all_expected_tests_passed"])

    def test_no_private_test_messages_in_public_result(self):
        value=classify(xml_report(),0,"synthetic")
        self.assertNotIn("PRIVATE SECRET",str(value))
        self.assertNotIn("test-case",str(value))
        self.assertFalse(value["private_compiler_logs_or_shader_contents_disclosed"])


if __name__ == "__main__":
    unittest.main()
