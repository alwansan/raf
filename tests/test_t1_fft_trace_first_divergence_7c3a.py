import json
import tempfile
import unittest
from pathlib import Path
from scripts.t1_fft_trace_first_divergence_7c3a import compare, load

BASE = {"source_sha":"vulkan","fixture_sha256":"fixture","input_sha256":"input","kernel":"FFT","dispatch":[1,1,1],"pass":0,"invocation":0,"read_site":0,"coordinate":[0,1],"value":[1.0]}
class TraceTests(unittest.TestCase):
    def check(self, left, right):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/"a",Path(d)/"b"
            a.write_text(json.dumps(left)+"\n"); b.write_text(json.dumps(right)+"\n")
            return compare(a,b)["status"]
    def test_match(self): self.assertEqual(self.check(BASE, BASE),"matched")
    def test_coordinate(self): self.assertEqual(self.check(BASE,{**BASE,"coordinate":[1,0]}),"coordinate_mismatch")
    def test_distinct_programs(self): self.assertEqual(self.check(BASE,{**BASE,"source_sha":"unity"}),"matched")
    def test_input(self): self.assertEqual(self.check(BASE,{**BASE,"input_sha256":"other"}),"provenance_mismatch")
    def test_numeric(self): self.assertEqual(self.check(BASE,{**BASE,"value":[2.0]}),"numeric_mismatch")
    def test_unpaired(self): self.assertEqual(self.check(BASE,{**BASE,"read_site":1}),"unpaired")
    def test_boolean_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a";p.write_text(json.dumps({**BASE,"invocation":True})+"\n")
            with self.assertRaises(ValueError): load(p)
    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a";p.write_text(json.dumps(BASE)[:-1]+',"kernel":"other"}\n')
            with self.assertRaises(ValueError): load(p)
    def test_numeric_order(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/"a",Path(d)/"b"
            rows=[{**BASE,"pass":v} for v in (10,2)]
            a.write_text("".join(json.dumps(x)+"\n" for x in rows))
            b.write_text("".join(json.dumps({**x,"coordinate":[9,9]})+"\n" for x in rows))
            self.assertEqual(compare(a,b)["key"][0],2)
    def test_late_provenance_conflict_precedes_early_coordinate_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/"a", Path(d)/"b"
            left = [{**BASE, "read_site":0}, {**BASE, "read_site":1}]
            right = [{**BASE, "read_site":0, "coordinate":[9,9]},
                     {**BASE, "read_site":1, "input_sha256":"different"}]
            a.write_text("".join(json.dumps(row)+"\n" for row in left))
            b.write_text("".join(json.dumps(row)+"\n" for row in right))
            result = compare(a,b)
            self.assertEqual(result["status"], "provenance_mismatch")
            self.assertEqual(result["key"], (0,0,1))
            self.assertEqual(result["field"], "input_sha256")
    def test_intra_trace_mixed_inputs_rejected_even_when_both_sides_match(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/"a", Path(d)/"b"
            rows = [{**BASE, "read_site":0},
                    {**BASE, "read_site":1, "input_sha256":"other"}]
            for path in (a, b):
                path.write_text("".join(json.dumps(row)+"\n" for row in rows))
            with self.assertRaisesRegex(ValueError, "inconsistent input_sha256"):
                compare(a, b)
    def test_intra_trace_mixed_compiled_sources_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/"a", Path(d)/"b"
            left = [{**BASE, "read_site":0},
                    {**BASE, "read_site":1, "source_sha":"different-program"}]
            right = [{**row, "source_sha":("unity" if i == 0 else "unity-other")}
                     for i, row in enumerate(left)]
            for path, rows in ((a, left), (b, right)):
                path.write_text("".join(json.dumps(row)+"\n" for row in rows))
            with self.assertRaisesRegex(ValueError, "inconsistent source_sha"):
                compare(a, b)
    def test_intra_trace_dispatch_drift_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"trace"
            rows = [{**BASE, "read_site":0},
                    {**BASE, "read_site":1, "dispatch":[2,1,1]}]
            p.write_text("".join(json.dumps(row)+"\n" for row in rows))
            with self.assertRaisesRegex(ValueError, "inconsistent dispatch"):
                load(p)
if __name__=="__main__": unittest.main()
