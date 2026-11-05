"""Private GameCI Vulkan CLI logger: diagnostic booleans only, no text leakage."""
import unittest
from scripts.t1_unity_vulkan_cli_failure_classifier import classify, MAX_LOG


class VulkanCLIFailureControls(unittest.TestCase):
    def test_supported_local_image_failure_keeps_only_category(self):
        log = "docker: Error response from daemon: pull access denied for t1-fft-unity2021-lavapipe:local. SECRET_TOKEN_DO_NOT_PRINT"
        r = classify(log, 1)
        self.assertFalse(r["process_exit_zero"])
        self.assertTrue(r["observation_categories"]["docker_image_unavailable"])
        self.assertTrue(r["observation_categories"]["docker_container_launch_error"])
        self.assertTrue(r["observation_categories"]["explicit_custom_image_mentioned"])
        self.assertNotIn("SECRET_TOKEN_DO_NOT_PRINT", str(r))
        self.assertFalse(r["raw_log_or_secret_material_disclosed"])

    def test_known_cli_option_error_is_only_a_boolean(self):
        result = classify("error: Unknown argument: --dockerEnv PRIVATE_EMAIL", 1)
        self.assertTrue(result["observation_categories"]["cli_unknown_argument"])
        self.assertNotIn("PRIVATE_EMAIL", str(result))

    def test_started_editor_does_not_mean_vulkan_proven(self):
        r = classify("Unity test Using project path as synthetic. Vulkan not supported. editmode-results.xml", 1)
        self.assertTrue(r["observation_categories"]["unity_runner_start_seen"])
        self.assertTrue(r["observation_categories"]["unity_vulkan_device_error_category"])
        self.assertTrue(r["observation_categories"]["test_report_path_seen"])
        self.assertFalse(r["unity_vulkan_editor_or_fft_numeric_parity_proven"])

    def test_missing_or_excessive_rejected(self):
        for text in ("", "x" * (MAX_LOG + 1), None, b"secret"):
            with self.assertRaises(ValueError):
                classify(text, 1)

    def test_invalid_exit_rejected(self):
        for code in (-1, 256, "0", 0.0):
            with self.assertRaises(ValueError):
                classify("synthetic runner output", code)

    def test_success_process_does_not_prove_vulkan(self):
        row = classify("A tiny source-free synthetic Unity test finished", 0)
        self.assertTrue(row["process_exit_zero"])
        self.assertFalse(row["unity_vulkan_editor_or_fft_numeric_parity_proven"])
        self.assertFalse(row["original_raft_data_acquired"])


if __name__ == "__main__":
    unittest.main()
