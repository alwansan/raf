"""Authored keyword fixtures; exercise the real C preprocessor, not game pixels."""
import itertools
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from scripts.gt_runtime_keyword_contract import (
    exact_independent_toggle_plan, keyword_set, strict_bundle_route_key,
    strict_engine_router,
)


def lattice(n):
    names = [f"SOURCE_{i}" for i in range(n)]
    return [tuple(name for name, enabled in zip(names, bits) if enabled)
            for bits in itertools.product((False, True), repeat=n)]


class RuntimeKeywordContract(unittest.TestCase):
    def test_full_lattice_route_order_and_pragmas(self):
        keys = [("B",), (), ("A", "B"), ("A",)]
        names, sets = exact_independent_toggle_plan(keys)
        self.assertEqual(names, ["A", "B"])
        self.assertEqual(sets, list(map(frozenset, keys)))
        pragmas, code = strict_engine_router(keys, dict(enumerate("abcd")))
        self.assertEqual(pragmas, ["#pragma multi_compile __ A", "#pragma multi_compile __ B"])
        self.assertTrue(code.endswith("#else\n#error Unmapped_original_keyword_set\n#endif\n"))
        self.assertIn("#if !defined(A) && defined(B)\na\n", code)

    def test_sparse_or_missing_empty_route_fails_before_emission(self):
        for keys in ([(), ("A", "B")], [("A",)], [("A",), ("B",)], []):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                strict_engine_router(keys, dict(enumerate("abcd"[:len(keys)])))

    def test_bad_names_and_collisions_fail(self):
        for keys in ([(), ()], [("A", "A")], [("GT_ORIGINAL_921_P0_V1",)],
                     [("A B",)], [("",)], [(True,)], [("Ä",)]):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                exact_independent_toggle_plan(keys)

    def test_program_table_requires_exact_nonempty_route_slots(self):
        for programs in ({0: "a"}, {0: "a", 1: ""}, {0: "a", 1: "b", 2: "c"},
                         {False: "a", True: "b"}):
            with self.subTest(programs=programs), self.assertRaises(ValueError):
                strict_engine_router([(), ("A",)], programs)

    def test_instancing_directive_and_empty_lattice(self):
        pragmas, code = strict_engine_router([(), ("INSTANCING_ON",)], {0: "a", 1: "b"})
        self.assertEqual(pragmas, ["#pragma multi_compile_instancing"])
        self.assertIn("#elif defined(INSTANCING_ON)\nb", code)
        pragmas, code = strict_engine_router([()], {0: "only"})
        self.assertEqual(pragmas, [])
        self.assertIn("#if 1\nonly", code)

    @unittest.skipUnless(shutil.which("cpp"), "requires actual C preprocessor")
    def test_all_1156_authored_route_selections_in_real_cpp(self):
        total = 0
        for p, n in enumerate((9, 2, 7, 9)):
            keys = lattice(n)
            # Deliberately make route zero nonempty: route index is not a keyword default.
            keys = keys[1:] + keys[:1]
            markers = {i: f"GT_MARKER_P{p}_R{i}" for i in range(len(keys))}
            _, code = strict_engine_router(keys, markers)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "router.h").write_text(code, encoding="utf-8")
                blocks = []
                for key in keys:
                    blocks.extend(f"#define {name} 1" for name in key)
                    blocks.append('#include "router.h"')
                    blocks.extend(f"#undef {name}" for name in key)
                result = subprocess.run(["cpp", "-P", "-undef", "-nostdinc", "-I", directory,
                                         "-x", "c", "-"], input="\n".join(blocks) + "\n",
                                        text=True, capture_output=True, timeout=30, check=True)
            self.assertEqual(result.stdout.split(), list(markers.values()))
            total += len(keys)
        self.assertEqual(total, 1156)

    @unittest.skipUnless(shutil.which("cpp"), "requires actual C preprocessor")
    def test_unmapped_branch_is_error_not_route_zero(self):
        _, code = strict_engine_router([(), ("A",)], {0: "ZERO", 1: "ONE"})
        broken = code.replace("#elif defined(A)\nONE\n", "")
        result = subprocess.run(["cpp", "-P", "-undef", "-nostdinc", "-DA=1", "-x", "c", "-"],
                                input=broken, text=True, capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unmapped_original_keyword_set", result.stderr)
        self.assertNotIn("ZERO", result.stdout)

    def test_bundle_exact_key_and_other_pass_names(self):
        expected = {frozenset(), frozenset({"A"})}
        self.assertEqual(strict_bundle_route_key(["A", "OTHER_PASS"], {"m_KeywordIndices": [0]},
                                                expected), frozenset({"A"}))
        self.assertEqual(strict_bundle_route_key(["A"], {"m_KeywordIndices": []}, expected), frozenset())

    def test_bundle_rejects_projection_wrong_scope_and_bad_indices(self):
        expected = {frozenset(), frozenset({"A"})}
        for names, row in (
            (["A", "OTHER_PASS"], {"m_KeywordIndices": [0, 1]}),
            (["A", "OTHER_PASS"], {"m_KeywordIndices": [1]}),
            (["A", "GT_ORIGINAL_921_P0_V1"], {"m_KeywordIndices": [0]}),
            (["A"], {"m_KeywordIndices": [0], "m_LocalKeywordIndices": [0]}),
            (["A"], {"m_KeywordIndices": [0], "m_GlobalKeywordIndices": [0]}),
            (["A"], {"m_KeywordIndices": [0], "m_LocalKeywordIndices": None}),
            (["A"], {"m_KeywordIndices": [0, 0]}),
            (["A"], {"m_KeywordIndices": [True]}),
            (["A"], {"m_KeywordIndices": [1]}),
            (["A", "A"], {"m_KeywordIndices": [0]}),
            (["A"], {}),
        ):
            with self.subTest(names=names, row=row), self.assertRaises(ValueError):
                strict_bundle_route_key(names, row, expected)


if __name__ == "__main__":
    unittest.main()
