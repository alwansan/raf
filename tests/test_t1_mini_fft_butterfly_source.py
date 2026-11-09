"""T1-05 source-only boundaries. Does not claim actual Android GPU execution.

The original Raft water .compute/DXBC shader must NOT be staged in the shared
mini APK. This test only checks the fixed synthetic GLES driver contract,
correct 30-case pack routing, CPU-reference source and anti-spoof markers.
"""
import copy
import json
import re
import unittest
from pathlib import Path

from scripts.validate_unified_testpack import audit

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "apk-for-testing/host/app/src/main/java/com/alwansan/raftlab"
UNIFIED = ROOT / "apk-for-testing/unified"
PACK = UNIFIED / "pack/team-testpack.json"
BUTTERFLY = JAVA / "T1FftButterflyProbe.java"
DRIVER = JAVA / "T1ComputeProbe.java"
CHILD = JAVA / "MainActivity.java"
ROUTER = UNIFIED / "app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java"
ARABIC = UNIFIED / "app/src/main/java/com/alwansan/raftlab/ArabicLabStrings.java"
GRADLE = UNIFIED / "app/build.gradle"


def check_source(driver, builtin, child, shared, arabic, build):
    checks = [
        ("two fixed embedded 512-wide kernels", builtin.count("layout(local_size_x=512") == 2),
        ("two exact GPU dispatches", builtin.count("glDispatchCompute(1,1,1)") == 2),
        ("SSBO binding real", "GLES31.GL_SHADER_STORAGE_BUFFER" in builtin),
        ("barrier before second pass", builtin.count("GLES31.glMemoryBarrier(") == 2),
        ("mapped GPU byte buffer", "glMapBufferRange(" in builtin and "getFloat(" in builtin),
        ("all 1024 floats checked", "checked==N*2" in builtin and "N = 512" in builtin),
        ("CPU reference independent from SSBO", "float ar=(i%19)/19.0f" in builtin and
         "float br=(j%19)/19.0f" in builtin),
        ("fail on numeric mismatch or nonfinite", "Float.isFinite(actual)" in builtin and
         "error>TOL" in builtin),
        ("bounded numerical tolerance", "TOL = 0.00003f" in builtin),
        ("critical GPU evidence not fabricated", 'original_raft_compute_executed=false' in builtin and
         'original_raft_compute_executed=true' not in builtin),
        ("fixed-in-binary driver only", "T1FftButterflyProbe.run()" in driver and
         "glShaderSource(shader,source)" in builtin and "getIntent()" not in builtin),
        ("child case route", 'T1-0[1-5]' in child),
        ("unified case safe route", 'T1-0[1-5]' in shared),
        ("Arabic owner explanations", 'm.put("T1-05"' in arabic and "شيدر Raft الأصلي" in arabic),
        ("anti stale worker source fingerprint", "T1FftButterflyProbe.java" in build)
    ]
    return [why for why, ok in checks if not ok]


class MiniFftSourceGate(unittest.TestCase):
    def setUp(self):
        self.driver = DRIVER.read_text(encoding="utf-8")
        self.source = BUTTERFLY.read_text(encoding="utf-8")
        self.child = CHILD.read_text(encoding="utf-8")
        self.shared = ROUTER.read_text(encoding="utf-8")
        self.arabic = ARABIC.read_text(encoding="utf-8")
        self.gradle = GRADLE.read_text(encoding="utf-8")

    def gate(self, **kwargs):
        args=dict(driver=self.driver,builtin=self.source,child=self.child,
                  shared=self.shared,arabic=self.arabic,build=self.gradle)
        args.update(kwargs)
        return check_source(**args)

    def test_full_source_and_routes(self):
        self.assertEqual(self.gate(), [])

    def test_missing_barrier_rejected(self):
        x=self.source.replace("GLES31.glMemoryBarrier(", "noBarrier(",1)
        self.assertIn("barrier before second pass", self.gate(builtin=x))

    def test_downgraded_local_size_rejected(self):
        x=self.source.replace("layout(local_size_x=512","layout(local_size_x=4",1)
        self.assertIn("two fixed embedded 512-wide kernels", self.gate(builtin=x))

    def test_missing_cpu_all_float_gate_rejected(self):
        x=self.source.replace("checked==N*2","checked>0")
        self.assertIn("all 1024 floats checked",self.gate(builtin=x))

    def test_untrue_original_fft_claim_rejected(self):
        x=self.source.replace("original_raft_compute_executed=false",
                              "original_raft_compute_executed=true")
        self.assertIn("critical GPU evidence not fabricated",self.gate(builtin=x))

    def test_unaccounted_driver_fingerprint_rejected(self):
        x=self.gradle.replace("'../../host/app/src/main/java/com/alwansan/raftlab/T1FftButterflyProbe.java',", "")
        self.assertIn("anti stale worker source fingerprint",self.gate(build=x))

    def test_unified_testpack_has_one_new_safe_case(self):
        pack=json.loads(PACK.read_text(encoding="utf-8"))
        self.assertEqual(pack["revision"],2)
        self.assertEqual(len(pack["tests"]),30)
        results=[v for v in pack["tests"] if v["id"]=="T1-05"]
        self.assertEqual(len(results),1)
        one=results[0]
        self.assertEqual((one["driver"],one["mode"],one["worker"],one["screenshot"]),
                         ("t1_compute","auto","T1","none"))
        report=audit(PACK.read_bytes())
        self.assertEqual(report["per_worker"]["T1"],5)

    def test_imported_testpack_cannot_supply_shader_source(self):
        pack=json.loads(PACK.read_text(encoding="utf-8"))
        fake=copy.deepcopy(pack)
        t=next(x for x in fake["tests"] if x["id"]=="T1-05")
        t["glsl"]="#version 310 es\nvoid main(){}"
        with self.assertRaisesRegex(ValueError,"case fields"):
            audit(json.dumps(fake).encode("utf-8"))

    def test_untrusted_new_t1_code_route_rejected(self):
        pack=json.loads(PACK.read_text(encoding="utf-8"))
        fake=copy.deepcopy(pack)
        next(x for x in fake["tests"] if x["id"]=="T1-05")["id"]="T1-06"
        with self.assertRaisesRegex(ValueError,"T1 executable"):
            audit(json.dumps(fake).encode("utf-8"))

    def test_sample_cpu_values_are_finite_and_bounded(self):
        # Non-device independent arithmetic shape sanity, not GPU proof.
        import math
        twiddle=0.70710678
        for pair in range(256):
            i=pair*2;j=i+1
            a=(float(i%19)/19.0,float((i*7)%29)/29.0)
            b=(float(j%19)/19.0,float((j*7)%29)/29.0)
            t=((b[0]+b[1])*twiddle,(b[1]-b[0])*twiddle)
            out=(a[0]+t[0],a[1]+t[1],a[0]-t[0],a[1]-t[1])
            self.assertTrue(all(math.isfinite(x) and abs(x)<3 for x in out))


if __name__=="__main__":
    unittest.main()
