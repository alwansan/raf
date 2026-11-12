"""Regression: W1 Depth Copy must read immutable SHA-pinned ZIP2 owners.

The reconstructed AssetRipper input is mutated by mesh range inlining; its
serialized owner hashes no longer match W1's authenticated source identities.
"""
from pathlib import Path
import unittest


class NativeDepthPristineSourceTests(unittest.TestCase):
    def test_depth_wrapper_reads_pristine_zip2_source(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/raft-unity-editor-android-import.yml").read_text()
        anchor = "timeout 600s python3 -m scripts.w1_build_depth_wrapper"
        self.assertEqual(workflow.count(anchor), 1)
        command = next(line.strip() for line in workflow.splitlines() if anchor in line)
        self.assertIn('--source "$RUNNER_TEMP/w1-original/Raft_Data"', command)
        self.assertNotIn('--source "$RUNNER_TEMP/input/Raft_Data"', command)

    def test_pristine_owners_are_authenticated_before_depth_stage(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/raft-unity-editor-android-import.yml").read_text()
        self.assertLess(workflow.index("python3 -m scripts.w1_full_engine_sources --zip2-checkout"),
                        workflow.index("timeout 600s python3 -m scripts.w1_build_depth_wrapper"))
        self.assertIn("w1-original/Raft_Data", workflow)


if __name__ == "__main__":
    unittest.main()
