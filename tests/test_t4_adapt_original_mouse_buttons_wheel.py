"""T4 captured physical mouse -> original Raft Legacy button/wheel patch guards."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch as mock_patch
from scripts.t4_adapt_original_mouse_buttons_wheel import (
    EXPECTED, replacement_plan, patch, mask_comments_and_literals
)


def authentic_synthetic_text():
    # Synthetic replacement of private original caller counts only: NO game code.
    return "\n".join(
        ["Input.GetMouseButtonDown(0);"] * 4 +
        ["UnityEngine.Input.GetMouseButton(1);"] * 5 +
        ["Input.GetMouseButton(dynamicButton);"] +
        ["Input.GetMouseButtonUp(2);"] * 2 +
        ['Input.GetAxis("Mouse ScrollWheel");'] * 3 +
        ['UnityEngine.Input.GetAxisRaw("Mouse ScrollWheel");'] * 3 +
        ["Input.mouseScrollDelta.y;"] +
        ["UnityEngine.Input.mouseScrollDelta;"]
    )


class OriginalPhysicalInputPatchTest(unittest.TestCase):
    def test_expected_original_cardinality(self):
        self.assertEqual(EXPECTED, {
            "down": 4, "held": 6, "up": 2, "wheel_axis": 6, "scroll_delta": 2,
        })

    def test_comments_literals_masked_and_original_exact_cardinality(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "Original.cs"
            data = authentic_synthetic_text() + '''
              // Input.GetMouseButtonDown(2)
              /* Input.GetAxis("Mouse ScrollWheel") */
              string fake = "Input.GetMouseButtonUp(1)";
              string fake2 = @"Input.mouseScrollDelta";
              Input.GetAxis("Mouse X");
              Input.GetKeyDown(3);
            '''
            src.write_text(data)
            changed, counts = replacement_plan(root)
            self.assertEqual(counts, EXPECTED)
            result = changed[src]
            self.assertEqual(result.count(
                "RaftAndroid.Platform.AndroidPhysicalMouseCapture.GetMouseButtonDown("), 4)
            self.assertEqual(result.count(
                "RaftAndroid.Platform.AndroidPhysicalMouseCapture.GetMouseButton("), 6)
            self.assertEqual(result.count(
                "RaftAndroid.Platform.AndroidPhysicalMouseCapture.GetMouseButtonUp("), 2)
            self.assertEqual(result.count(
                "RaftAndroid.Platform.AndroidPhysicalMouseCapture.GetAxis"), 6)
            self.assertEqual(result.count(
                "RaftAndroid.Platform.AndroidPhysicalMouseCapture.GetMouseScrollDelta()"), 2)
            self.assertIn("Input.GetAxis(\"Mouse X\")", result)
            self.assertIn("Input.GetKeyDown(3)", result)
            self.assertIn("// Input.GetMouseButtonDown(2)", result)
            self.assertIn('string fake2 = @"Input.mouseScrollDelta";', result)
            self.assertEqual(src.read_text(), data,
                             "Plan mode must not edit original source")

    def test_patch_requires_actual_original_binary_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "Original.cs").write_text(authentic_synthetic_text())
            dll = root / "not_original.dll"
            dll.write_bytes(b"synthetic")
            with self.assertRaises(ValueError):
                patch(root, dll)

    def test_apply_reversible_byte_identical_backup(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "source"
            root.mkdir()
            original = root / "Original.cs"
            original.write_bytes(b"\xef\xbb\xbf" + authentic_synthetic_text().encode("utf-8"))
            before = original.read_bytes()
            backup = Path(d) / "original-backup"
            with mock_patch("scripts.t4_adapt_original_mouse_buttons_wheel.assert_original"):
                result = patch(root, Path(d)/"private.dll", apply=True, backup=backup)
            self.assertEqual(result["matched"], EXPECTED)
            self.assertTrue(result["applied"])
            self.assertEqual((backup / "Original.cs").read_bytes(), before)
            self.assertTrue(original.read_bytes().startswith(b"\xef\xbb\xbf"))
            self.assertIn(b"AndroidPhysicalMouseCapture.GetMouseScrollDelta()",
                          original.read_bytes())
            self.assertNotEqual(original.read_bytes(), before)
            original.write_bytes((backup / "Original.cs").read_bytes())
            self.assertEqual(original.read_bytes(), before, "Restoration is byte-identical")

    def test_missing_or_extra_original_sites_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "Original.cs"
            src.write_text(authentic_synthetic_text().replace(
                "Input.GetMouseButtonDown(0);", "", 1))
            with self.assertRaises(ValueError):
                replacement_plan(Path(d))
            src.write_text(authentic_synthetic_text() +
                           "\nInput.GetMouseButtonDown(0);")
            with self.assertRaises(ValueError):
                replacement_plan(Path(d))

    def test_no_linked_or_redirected_original_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "src"
            root.mkdir()
            data = root / "Original.cs"
            data.write_text(authentic_synthetic_text())
            symlink = root / "Redirected.cs"
            try:
                symlink.symlink_to(data)
            except (OSError, NotImplementedError):
                return
            with self.assertRaises(ValueError):
                replacement_plan(root)

    def test_project_assets_stage_is_limited_to_game_assembly(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            game = root / "Raft" / "Assembly-CSharp"
            game.mkdir(parents=True)
            original = game / "Original.cs"
            original.write_text(authentic_synthetic_text())
            untrusted = root / "RaftAndroid"
            untrusted.mkdir()
            (untrusted / "Other.cs").write_text(authentic_synthetic_text())
            changed, counts = replacement_plan(root, project_assets=True)
            self.assertEqual(counts, EXPECTED)
            self.assertEqual(set(changed), {original})

    def test_lexer_preserves_position_during_mask(self):
        x = 'Input.GetMouseButton(0); // fake\n"Input.GetMouseButton(1)"\n'
        masked = mask_comments_and_literals(x)
        self.assertEqual(len(masked), len(x))
        self.assertEqual(masked.count("\n"), x.count("\n"))
        self.assertIn("Input.GetMouseButton(0)", masked)
        self.assertNotIn("Input.GetMouseButton(1)", masked)

    def test_no_source_output_claims_device(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "Original.cs").write_text(authentic_synthetic_text())
            with mock_patch("scripts.t4_adapt_original_mouse_buttons_wheel.assert_original"):
                result = patch(root, Path(d) / "fake.dll")
            self.assertFalse(result["device_verified"])
            self.assertFalse(result["applied"])
            self.assertFalse(result["source_published"])


if __name__ == "__main__":
    unittest.main()
