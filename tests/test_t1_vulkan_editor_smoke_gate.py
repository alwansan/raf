"""Source-free adversarial parser controls for Unity Vulkan Editor test verdict."""
import unittest
from scripts.t1_vulkan_editor_smoke_gate import EXPECTED, evaluate, MAX_XML_BYTES


def report(names=None, *, result="Passed", passed=3, failed=0,
           skipped=0, inconclusive=0, size=None):
    names = sorted(EXPECTED) if names is None else names
    cases = "".join(
        '<test-case fullname="%s" result="%s"><failure><message>'
        'SECRET_UNTRUSTED_TEST_BODY'
        '</message></failure></test-case>' % (x,result) for x in names)
    count = len(names) if size is None else size
    return ('<test-run total="%d" testcasecount="%d" passed="%d" '
            'failed="%d" skipped="%d" inconclusive="%d" result="%s">%s</test-run>' %
            (count,count,passed,failed,skipped,inconclusive,result,cases)).encode()


class VulkanSmokeGateTests(unittest.TestCase):
    def test_exact_three_unity_tests_can_pass(self):
        v = evaluate(report(), 0)
        self.assertTrue(v["vulkan_editor_backend_and_synthetic_gpu_dispatch_verified"])
        self.assertEqual(v["synthetic_expected_float_texels_checked"], 64)
        self.assertFalse(v["original_fft_numeric_parity_proven"])

    def test_unity_failure_return_cannot_pass(self):
        self.assertFalse(evaluate(report(), 1)["vulkan_editor_backend_and_synthetic_gpu_dispatch_verified"])

    def test_wrong_case_or_duplicate_rejected(self):
        names = sorted(EXPECTED)
        for altered in (names[:2], names[:2]+[names[1]], names[:2]+["Spoof.Pass"]):
            self.assertFalse(evaluate(report(names=altered,passed=len(altered)),0)
                             ["vulkan_editor_backend_and_synthetic_gpu_dispatch_verified"])

    def test_skipped_failure_or_forged_root_not_pass(self):
        for blob in (report(result="Failed", passed=0, failed=3),
                     report(passed=2, skipped=1),
                     report(passed=2, failed=1),
                     report().replace(b' result="Passed">', b' result="Skipped">', 1)):
            self.assertFalse(evaluate(blob,0)
                             ["vulkan_editor_backend_and_synthetic_gpu_dispatch_verified"])

    def test_malformed_unbounded_and_wrong_root_rejected(self):
        for blob in (b"", b"<test-run", b"<results/>",
                     b"x"*(MAX_XML_BYTES+1),
                     b'<test-run total="1"/>'):
            with self.subTest(size=len(blob)):
                with self.assertRaises(ValueError):
                    evaluate(blob, 0)

    def test_never_disclose_private_test_messages(self):
        result = evaluate(report(result="Failed",passed=0,failed=3),1)
        self.assertNotIn("SECRET_UNTRUSTED_TEST_BODY",str(result))
        self.assertFalse(result["private_log_or_test_failure_text_disclosed"])


if __name__ == "__main__":
    unittest.main()
