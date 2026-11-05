"""T1 synthetic fail-closed controls for actual Unity FFT GPU Dispatch XML."""
import unittest
from scripts.t1_fft_unity_gpu_result_gate import classify,KNOWN


def xml(names=None,*,result="Passed",failed=0,passed=2):
    names=sorted(KNOWN) if names is None else names
    cases="".join('<test-case fullname="%s" result="%s"><failure><message>PRIVATE SOURCE CONTENT</message></failure></test-case>'%(n,result) for n in names)
    return ('<test-run testcasecount="%d" total="%d" passed="%d" failed="%d" skipped="0" inconclusive="0" result="%s">%s</test-run>'%(len(names),len(names),passed,failed,result,cases)).encode()


class GPUReportControls(unittest.TestCase):
    def test_only_exact_two_expected_tests_pass(self):
        v=classify(xml(),0)
        self.assertTrue(v["all_private_unity_tests_passed"])
        self.assertTrue(v["fft_derived_two_pass_gpu_dispatch_with_observed_writes"])
        self.assertFalse(v["numeric_original_pixel_parity_proven"])
        self.assertFalse(v["android_adreno_water_pixels_proven"])
        self.assertFalse(v["original_author_kernel_names_or_runtime_mapping_proven"])

    def test_nonzero_process_fails(self):
        self.assertFalse(classify(xml(),3)["all_private_unity_tests_passed"])

    def test_missing_one_or_wrong_case_fails(self):
        names=sorted(KNOWN)
        for candidate in ([names[0]],[names[0],names[0]],[names[0],"T1Spoofed.Test"]):
            self.assertFalse(classify(xml(candidate),0)["all_private_unity_tests_passed"])

    def test_failure_cannot_be_concealed(self):
        for body in (xml(result="Failed",failed=2,passed=0),
                     xml(failed=1,passed=1),
                     xml(passed=1)):
            self.assertFalse(classify(body,0)["all_private_unity_tests_passed"])

    def test_reject_malformed_or_unbounded_nunit(self):
        for body in (b"",b"bad",b"<test-run",b"<tests/>",
                     b"<test-run testcasecount=\"2\"/>",
                     b"x"*(1024*1024+1)):
            with self.subTest(n=len(body)):
                with self.assertRaises(ValueError):classify(body,0)

    def test_never_echo_private_failure_message(self):
        record=classify(xml(result="Failed",passed=0,failed=2),1)
        self.assertNotIn("PRIVATE SOURCE CONTENT",str(record))
        self.assertFalse(record["private_original_names_shader_logs_or_pixel_values_exported"])


if __name__=="__main__":
    unittest.main()
