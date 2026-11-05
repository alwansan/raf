"""Classify a source-free GameCI Unity Vulkan startup failure without logs.

Never prints CLI stdout/stderr, option values, Unity license contents,
environment variables, private paths or exception bodies. This diagnoses
only the disposable synthetic Unity2021 runner; not original Raft data.
"""
import argparse
import json
import re
from pathlib import Path

MAX_LOG = 16 * 1024 * 1024

PATTERNS = {
    "cli_unknown_argument": r"(unknown argument|unknown option|unrecognized argument)",
    "docker_image_unavailable": r"(pull access denied|repository does not exist|no such image|manifest unknown)",
    "docker_container_launch_error": r"(error response from daemon|cannot connect to the docker daemon|failed to create task|OCI runtime create failed)",
    "unity_runner_start_seen": r"(Unity test|Using project path|Unity version.*to test|Start importing assets)",
    "unity_license_failure_category": r"(license.*(failed|invalid|denied)|failed to activate|no valid unity editor license)",
    "unity_vulkan_device_error_category": r"(vulkan.*(failed|error|not supported)|failed.*(vulkan|graphics device))",
    "unity_csharp_or_shader_error_category": r"(compilation failed|shader error|error CS[0-9]{4})",
    "gameci_test_command_mentioned": r"(game-ci test|Unity test)",
    "explicit_custom_image_mentioned": r"t1-fft-unity2021-lavapipe:local",
    "test_report_path_seen": r"editmode-results\.xml",
}


def classify(text: str, process_exit: int) -> dict:
    if type(text) is not str or not 0 < len(text.encode("utf8")) <= MAX_LOG:
        raise ValueError("Missing or excessive private CLI output")
    if type(process_exit) is not int or not 0 <= process_exit <= 255:
        raise ValueError("Invalid process result")
    found = {key: bool(re.search(pattern, text, re.I))
             for key, pattern in PATTERNS.items()}
    # Diagnostic fields, NOT proof of a real API/device. A passing synthetic
    # NUnit test is required independently for actual Vulkan execution.
    return {
        "source_free_cli_log_inspected": True,
        "process_exit_zero": process_exit == 0,
        "observation_categories": found,
        "unity_vulkan_editor_or_fft_numeric_parity_proven": False,
        "original_raft_data_acquired": False,
        "raw_log_or_secret_material_disclosed": False,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--log", type=Path, required=True)
    cli.add_argument("--process-exit", type=int, required=True)
    args = cli.parse_args()
    if args.log.is_symlink() or not args.log.is_file() or args.log.stat().st_size > MAX_LOG:
        raise SystemExit("RAFT_T1_VULKAN_CLI_DIAGNOSTIC private_log_missing_or_excessive=true")
    try:
        output = classify(args.log.read_text(encoding="utf8", errors="replace"),
                          args.process_exit)
    except (ValueError, OSError):
        raise SystemExit("RAFT_T1_VULKAN_CLI_DIAGNOSTIC invalid_private_log=true") from None
    print("RAFT_T1_VULKAN_CLI_DIAGNOSTIC " + json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
