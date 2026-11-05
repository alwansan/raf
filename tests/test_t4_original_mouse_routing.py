"""Source-free adverse controls for the T4 original mouse routing census."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.t4_original_mouse_routing import (
    without_comments, count_sources, assert_original, report,
    MAX_FILE_BYTES, ORIGINAL_SIZE,
)


class OriginalMouseRoutingTests(unittest.TestCase):
    def test_comment_only_calls_are_not_considered(self):
        source = """
        // Input.GetAxis("Mouse X");
        /* MyInput.GetAxis("Mouse Y"); */
        class CameraLook {
          string url = "https://example.invalid/input";
          string comment = "/* not a comment */";
          float x = Input.GetAxis("Mouse X");
          float y = MyInput.GetAxisRaw("Mouse Y");
        }
        """
        filtered = without_comments(source)
        self.assertNotIn("// Input.GetAxis", filtered)
        self.assertNotIn("MyInput.GetAxis", filtered.split("class CameraLook")[0])
        self.assertIn('"/* not a comment */"', filtered)
        self.assertIn('Input.GetAxis("Mouse X")', filtered)

    def test_original_route_categories_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "MainCamera.cs").write_text(
                'float x=Input.GetAxis("Mouse X"); float y=Input.GetAxisRaw("Mouse Y");\n'
                'float z=MyInput.GetAxis("Mouse X"); Cursor.lockState = mode;\n')
            (root / "UserInterface.cs").write_text(
                'float y=MyInput.GetAxisRaw("Mouse Y");\n'
                'float z=Mouse.current.delta.ReadValue().x;\n'
                '/* Input.GetAxis("Mouse X"); */\n')
            got = count_sources(root)
            self.assertEqual(got["source_files"], 2)
            self.assertEqual((got["direct_mouse_x"], got["direct_mouse_y"]), (1, 1))
            self.assertEqual((got["wrapped_mouse_x"], got["wrapped_mouse_y"]), (1, 1))
            self.assertEqual(got["camera_named_direct_sites"], 2)
            self.assertEqual(got["camera_named_wrapped_sites"], 1)
            self.assertEqual(got["input_system_delta_syntax_sites"], 1)
            self.assertEqual(got["cursor_lock_assignment_syntax_sites"], 1)
            self.assertEqual(got["all_axis_call_syntax_sites"], 4)

    def test_verbatim_string_comment_marker_is_not_a_comment(self):
        self.assertIn('@"/* not a comment */"',
                      without_comments('var s=@"/* not a comment */"; // end'))

    def test_symlink_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            real = root / "real.cs"
            real.write_text("class A {}")
            (root / "linked.cs").symlink_to(real)
            with self.assertRaises(ValueError):
                count_sources(root)

    def test_bounded_individual_file_and_no_empty_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                count_sources(root)
            (root / "huge.cs").write_bytes(b" " * (MAX_FILE_BYTES + 1))
            with self.assertRaises(ValueError):
                count_sources(root)

    def test_wrong_binary_is_rejected_before_decomp_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dll = root / "Assembly-CSharp.dll"
            dll.write_bytes(b"wrong")
            with self.assertRaises(ValueError):
                assert_original(dll)
            (root / "Camera.cs").write_text('Input.GetAxis("Mouse X")')
            with self.assertRaises(ValueError):
                report(dll, root)
            self.assertEqual(dll.stat().st_size, len(b"wrong"))

    def test_no_original_code_or_names_in_result_keys(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "SecretNamedCamera.cs").write_text('Input.GetAxis("Mouse X")')
            public = json.dumps(count_sources(root))
            self.assertNotIn("SecretNamed", public)
            self.assertNotIn("Input.GetAxis", public)


if __name__ == "__main__":
    unittest.main()
