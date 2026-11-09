from pathlib import Path
import json, unittest
from scripts.validate_unified_testpack import audit

P=Path(__file__).resolve().parents[1]/"apk-for-testing/unified/pack/team-testpack.json"
BASE=json.loads(P.read_text("utf-8"))

def raw(x):return json.dumps(x,ensure_ascii=False).encode("utf-8")
class UnifiedManifestTests(unittest.TestCase):
    def test_provided_pack(self):
        out=audit(P.read_bytes())
        self.assertEqual(out["cases"],30)
        self.assertEqual(out["per_worker"],{"T1":5,"T2":4,"T3":6,"T4":9,"T5":6})
    def test_no_injected_driver(self):
        x=json.loads(json.dumps(BASE));x["tests"][0]["driver"]="execute_dex"
        with self.assertRaisesRegex(ValueError,"routing"):audit(raw(x))
    def test_mouse_no_silent_auto(self):
        x=json.loads(json.dumps(BASE));x["tests"][15]["mode"]="auto"
        with self.assertRaises(ValueError):audit(raw(x))
    def test_duplicate_id(self):
        x=json.loads(json.dumps(BASE));x["tests"][1]["id"]=x["tests"][0]["id"]
        with self.assertRaises(ValueError):audit(raw(x))
    def test_no_cross_worker(self):
        x=json.loads(json.dumps(BASE));x["tests"][0]["worker"]="T5"
        with self.assertRaises(ValueError):audit(raw(x))
    def test_untrusted_gpu_case_cannot_execute(self):
        x=json.loads(json.dumps(BASE));x["tests"][0]["id"]="T1-91"
        with self.assertRaises(ValueError):audit(raw(x))
    def test_oversize(self):
        with self.assertRaisesRegex(ValueError,"256KiB"):audit(b" "+b"a"*262144)
if __name__=="__main__":unittest.main()
