"""B22 source-free Material scalar value parity regression tests."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.b22_verify_material_scalars import _float_bits, normalize, compare, exported_scalars

GUID = "a" * 32
SRC = ("sharedassets0.assets", 7)
DST = (2100000, GUID)


def sample(floats=None, ints=None):
    return normalize({"m_Floats": list((floats or {}).items()), "m_Ints": list((ints or {}).items())})


def trace(*, guid=GUID, path_id=7, file_id=2100000):
    return {"schema_version": 1, "export_instance": "b" * 32, "objects": [
        {"class_id": 21,
         "source": {"owner": SRC[0], "path_id": path_id},
         "export": {"file_id": file_id, "guid": guid, "type": 2},
         "exportable": True}]}


class B22ScalarTests(unittest.TestCase):
    def test_float32_canonical_roundtrip(self):
        self.assertEqual(_float_bits(0.1), _float_bits(0.10000000149011612))
        orig = {SRC: sample({"_Cutoff": 0.1, "_SrcBlend": 1, "_ZWrite": 0})}
        exp = {DST: sample({"_Cutoff": 0.10000000149011612, "_SrcBlend": 1.0, "_ZWrite": 0.0})}
        report = compare(trace(), orig, exp)
        self.assertTrue(report["scalar_values_preserved"])
        self.assertEqual(report["float_slots_compared"], 3)

    def test_cutoff_mutation_rejected(self):
        report = compare(trace(), {SRC: sample({"_Cutoff": 0.4})},
                         {DST: sample({"_Cutoff": 0.9})})
        self.assertEqual((report["changed_float32_values"], report["mismatched_materials"]), (1, 1))
        self.assertFalse(report["scalar_values_preserved"])

    def test_blend_mode_mutation_rejected(self):
        before = {SRC: sample({"_SrcBlend": 1, "_DstBlend": 0, "_ZWrite": 1})}
        after = {DST: sample({"_SrcBlend": 1, "_DstBlend": 5, "_ZWrite": 0})}
        self.assertEqual(compare(trace(), before, after)["changed_float32_values"], 2)

    def test_missing_extra_slots_rejected(self):
        before = {SRC: sample({"_Cutoff": 0.25, "_ZWrite": 1})}
        after = {DST: sample({"_Cutoff": 0.25, "_Metallic": 0.7})}
        r = compare(trace(), before, after)
        self.assertEqual((r["missing_scalar_slots"], r["extra_scalar_slots"]), (1, 1))

    def test_ints_mutation_independent(self):
        a = {SRC: sample({"_Cutoff": 0.2}, {"_Stencil": 5})}
        b = {DST: sample({"_Cutoff": 0.2}, {"_Stencil": 6})}
        r = compare(trace(), a, b)
        self.assertEqual((r["int_slots_compared"], r["changed_int32_values"]), (1, 1))

    def test_invalid_float_types_and_nonfinite_rejected(self):
        for bad in (True, "0.5", None, float("nan"), float("inf"), -float("inf"), 1e100):
            with self.subTest(type=str(bad)), self.assertRaises(ValueError):
                sample({"_Cutoff": bad})

    def test_invalid_int_types_and_range_rejected(self):
        for bad in (False, 0.0, "1", 2**40):
            with self.subTest(type=str(bad)), self.assertRaises(ValueError):
                sample({}, {"_Stencil": bad})

    def test_duplicate_slot_and_shape_rejected(self):
        with self.assertRaises(ValueError):
            normalize({"m_Floats": [("_Cutoff", 0.1), ("_Cutoff", 0.2)], "m_Ints": []})
        with self.assertRaises(ValueError):
            normalize({"m_Floats": [{"_Cutoff": 0.1}, {"_Cutoff": 0.2}], "m_Ints": []}, exported=True)
        with self.assertRaises(ValueError):
            normalize({"m_Floats": [{"bad": 1, "another": 2}], "m_Ints": []}, exported=True)

    def test_supported_yaml_pair_encodings(self):
        props = {"m_Floats": [{"_Cutoff": 0.5}, {"m_First": "_Mode", "m_Second": 0.0}], "m_Ints": []}
        self.assertEqual(len(normalize(props, exported=True)["m_Floats"]), 2)

    def test_swapped_identity_and_missing_material_fail_closed(self):
        original = {SRC: sample({"_Cutoff": 0.4})}
        actual = {DST: sample({"_Cutoff": 0.4})}
        with self.assertRaises(ValueError):
            compare(trace(guid="c" * 32), original, actual)
        with self.assertRaises(ValueError):
            compare(trace(path_id=99), original, actual)
        with self.assertRaises(ValueError):
            compare(trace(), original, {})
        with self.assertRaises(ValueError):
            compare(trace(), {}, actual)

    def test_duplicate_and_missing_trace_fail_closed(self):
        original = {SRC: sample({"_Cutoff": 0.2})}
        actual = {DST: sample({"_Cutoff": 0.2})}
        t = trace()
        t["objects"] += [dict(t["objects"][0])]
        with self.assertRaises(ValueError):
            compare(t, original, actual)
        t = trace()
        t["export_instance"] = "invalid"
        with self.assertRaises(ValueError):
            compare(t, original, actual)

    def test_report_hides_proprietary_values_and_identity(self):
        r = compare(trace(), {SRC: sample({"_Cutoff": 0.314159})},
                    {DST: sample({"_Cutoff": 0.8})})
        output = json.dumps(r)
        for fragment in ("_Cutoff", "0.314159", "0.8", "sharedassets", GUID, "b"*32, "path_id"):
            self.assertNotIn(fragment, output)

    def test_actual_yaml_import_and_duplicate_yaml_keys(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            assets = root / "Assets"
            assets.mkdir()
            meta = assets / "one.mat.meta"
            meta.write_text("fileFormatVersion: 2\nguid: " + GUID + "\n")
            mat = assets / "one.mat"
            prefix = ("%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
                      "--- !u!21 &2100000\nMaterial:\n  m_SavedProperties:\n")
            mat.write_text(prefix + "    m_Floats:\n      - _Cutoff: 0.5\n    m_Ints: []\n")
            self.assertEqual(exported_scalars(root)[DST]["m_Floats"]["_Cutoff"], _float_bits(0.5))
            mat.write_text(prefix + "    m_Floats:\n      - _Cutoff: 0.5\n"
                           "    m_Floats:\n      - _Cutoff: 0.7\n    m_Ints: []\n")
            with self.assertRaises(ValueError):
                exported_scalars(root)

    def test_symlinked_assets_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "real").mkdir()
            (root / "Assets").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaises(ValueError):
                exported_scalars(root)


if __name__ == "__main__":
    unittest.main()
