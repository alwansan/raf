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
