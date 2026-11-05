"""Guard authentic pixel diagnostic failures from being disguised as decoder failures."""
import ast
from pathlib import Path
import unittest


class DiagnosticBoundaryTests(unittest.TestCase):
    def test_diagnostic_not_inside_unsupported_decoder_handler(self):
        source = Path(__file__).resolve().parents[1] / "scripts/t3_authentic_decoded_pixel_export.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
        calls = [n for n in ast.walk(run) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == "diagnose_pair"]
        self.assertEqual(len(calls), 1)
        diagnostic = calls[0]
        for node in ast.walk(run):
            if not isinstance(node, ast.Try):
                continue
            for handler in node.handlers:
                if not any(isinstance(child, ast.Constant) and child.value == "UNSUPPORTED_MODE"
                           for child in ast.walk(handler)):
                    continue
                self.assertFalse(any(child is diagnostic for child in ast.walk(node)),
                                 "diagnostic exception must not be swallowed as unsupported decoder")

    def test_export_png_and_parity_errors_are_not_decoder_errors(self):
        source = Path(__file__).resolve().parents[1] / "scripts/t3_authentic_decoded_pixel_export.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
        compare_calls = [n for n in ast.walk(run) if isinstance(n, ast.Call)
                         and isinstance(n.func, ast.Name) and n.func.id == "compare_pair"]
        # Raw comparison is preserved; exact DXT5nm semantic comparison adds
        # one more source-authenticated pair, both outside decoder handlers.
        self.assertEqual(len(compare_calls), 2)
        png_calls = [n for n in ast.walk(run) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute)
                     and isinstance(n.func.value, ast.Name)
                     and n.func.value.id == "Image" and n.func.attr == "open"]
        self.assertEqual(len(png_calls), 1)
        for node in ast.walk(run):
            if not isinstance(node, ast.Try):
                continue
            if not any(isinstance(child, ast.Constant) and child.value == "UNSUPPORTED_MODE"
                       for handler in node.handlers for child in ast.walk(handler)):
                continue
            for comparison in compare_calls:
                self.assertFalse(any(child is comparison for child in ast.walk(node)))
            self.assertFalse(any(child is png_calls[0] for child in ast.walk(node)))

    def test_inconclusive_top_level_remains_fail_closed(self):
        source = Path(__file__).resolve().parents[1] / "scripts/t3_authentic_decoded_pixel_export.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        self.assertTrue(any(isinstance(n, ast.Constant) and n.value == "INCONCLUSIVE"
                            for n in ast.walk(main)))
        self.assertTrue(any(isinstance(n, ast.Constant) and n.value == 2
                            for n in ast.walk(main)))


if __name__ == "__main__":
    unittest.main()
