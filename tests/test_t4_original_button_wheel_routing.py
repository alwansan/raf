"""Synthetic-only controls for T4 original button/wheel lexical census."""
import tempfile
import unittest
from pathlib import Path
from scripts.t4_original_button_wheel_routing import KEYS, count_text, census, assert_original


class OriginalMouseRouting(unittest.TestCase):
    def test_legacy_and_custom_calls(self):
        x = """Input.GetMouseButtonDown(0); UnityEngine.Input.GetMouseButton(1);
               Input.GetMouseButtonUp(2); MyInput.GetMouseButtonDown(0);
               MyInput.GetMouseButton(1); MyInput.GetMouseButtonUp(index);"""
        c = count_text(x)
        self.assertEqual([c[k] for k in (
            "legacy_down", "legacy_held", "legacy_up",
            "myinput_down", "myinput_held", "myinput_up",
            "button_dynamic_argument")], [1, 1, 1, 1, 1, 1, 1])

    def test_wheel_and_new_input(self):
        c = count_text('''Input.GetAxis("Mouse ScrollWheel");
            Input.GetAxisRaw("Mouse ScrollWheel");
            MyInput.GetAxis("Mouse ScrollWheel");
            Input.mouseScrollDelta;
            Mouse.current.leftButton; Mouse.current?.rightButton;
            Mouse.current.middleButton; Mouse.current.scroll;''')
        self.assertEqual(c["legacy_wheel"], 2)
        self.assertEqual(c["myinput_wheel"], 1)
        self.assertEqual(c["legacy_scroll_delta"], 1)
        self.assertEqual(c["inputsystem_buttons"], 3)
        self.assertEqual(c["inputsystem_scroll"], 1)

    def test_comments_strings_not_source_calls(self):
        source = r'''
          // Input.GetMouseButtonDown(1)
          /* MyInput.GetAxis("Mouse ScrollWheel") */
          string x = "Input.GetMouseButtonUp(2)";
          string y = @"Mouse.current.scroll";
          Input.GetMouseButtonDown(0);
        '''
        c = count_text(source)
        self.assertEqual(sum(c.values()), 1)
        self.assertEqual(c["legacy_down"], 1)

    def test_unrelated_input_not_misidentified(self):
        c = count_text('Input.GetAxis("Mouse X"); Input.GetKeyDown(0);' +
                       ' Touchscreen.current.press; FakeInput.GetMouseButtonDown(2);')
        self.assertEqual(sum(c[k] for k in KEYS), 0)

    def test_bounded_private_directory_and_links(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.cs").write_text("Input.GetMouseButtonDown(0)")
            (root / "b.cs").write_text("Input.mouseScrollDelta;")
            result = census(root)
            self.assertEqual(result["source_files"], 2)
            self.assertEqual(result["counts"]["legacy_down"], 1)
            self.assertFalse(result["device_verified"])
            try:
                (root / "linked.cs").symlink_to(root / "a.cs")
            except OSError:
                return
            with self.assertRaises(ValueError):
                census(root)

    def test_fake_original_dll_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.dll"
            p.write_bytes(b"not Raft")
            with self.assertRaises(ValueError):
                assert_original(p)


if __name__ == "__main__":
    unittest.main()
