import json
import unittest
from scripts.t1_shared_fft_device_evidence import audit, SOURCE, PACK, APK

SID = "20261109-225506-552476830"
META = {"session": SID, "source": SOURCE, "pack_sha256": PACK, "apk": APK}
OBS = ("PASS fft_synthetic_two_pass_local512 checked_floats=1024 "
       "max_abs_error=2.3841858E-7 tolerance=3.0E-5 first_mismatch=-1 "
       "unmap=true gl_error=0x0 original_raft_compute_executed=false")


def fixture():
    summary = {"session": SID, "app_source": SOURCE, "pack_sha256": PACK,
               "pack_id": "raft-shared-t1-t5-v1", "results": []}
    events = [dict(META, time_ms=1000, event="auto_start",
                   detail="worker=T1 total=5 force=false")]
    for i in range(1, 6):
        case = f"T1-{i:02}"
        r = {"id": case, "worker": "T1", "status": "PASS",
             "fingerprint": str(i)*64, "observed": OBS if i == 5 else "PASS basic",
             "pack_sha256": PACK, "utc_ms": 1100+i*100, "image_uri": ""}
        summary["results"].append({"case_id": case, "worker": "T1", "result": r})
        events.append(dict(META, time_ms=1050+i*100, event="auto_case_start",
                           detail=case+" driver=t1_compute"))
        events.append(dict(META, time_ms=1100+i*100, event="case_result",
                           detail=json.dumps(r)))
    events.append(dict(META, time_ms=1700, event="auto_complete", detail="count=5"))
    events.append(dict(META, time_ms=1900, event="auto_reuse",
                       detail="T1-05 status=PASS "+"5"*64))
    return summary, events


def edit_observed(s, e, old, new):
    r = s["results"][4]["result"]
    r["observed"] = r["observed"].replace(old, new)
    for row in e:
        if row["event"] == "case_result" and '"T1-05"' in row["detail"]:
            row["detail"] = json.dumps(r)


class TestDeviceEvidence(unittest.TestCase):
    def reject(self, s, e):
        with self.assertRaises(ValueError):
            audit(s, e)

    def test_genuine_bounded_fixture(self):
        s, e = fixture()
        r = audit(s, e)
        self.assertEqual(r["verdict"], "PASS_SYNTHETIC_DEVICE_GLES_ONLY")
        self.assertFalse(r["original_raft_fft_proven"])
        self.assertTrue(r["later_reuse_is_not_second_execution"])

    def test_mixed_build(self):
        s, e = fixture()
        e[3]["source"] = "0"*40
        self.reject(s, e)

    def test_wrong_pack(self):
        s, e = fixture()
        s["pack_sha256"] = "0"*64
        self.reject(s, e)

    def test_stale_without_launch(self):
        s, e = fixture()
        e = [r for r in e if not (r["event"] == "auto_case_start" and r["detail"].startswith("T1-05"))]
        self.reject(s, e)

    def test_cached_alone_not_fresh(self):
        s, e = fixture()
        e = [r for r in e if not (r["event"] in ("auto_case_start", "case_result") and "T1-05" in r["detail"])]
        self.reject(s, e)

    def test_tampered_summary(self):
        s, e = fixture()
        s["results"][4]["result"]["fingerprint"] = "a"*64
        self.reject(s, e)

    def test_duplicate_case_result(self):
        s, e = fixture()
        e.insert(-2, dict(e[-3]))
        self.reject(s, e)

    def test_excessive_error(self):
        s, e = fixture()
        edit_observed(s, e, "2.3841858E-7", "9.99E-4")
        self.reject(s, e)

    def test_falsely_claims_original_shader(self):
        s, e = fixture()
        edit_observed(s, e, "executed=false", "executed=true")
        self.reject(s, e)

    def test_gpu_unmap_failure(self):
        s, e = fixture()
        edit_observed(s, e, "unmap=true", "unmap=false")
        self.reject(s, e)

    def test_wrong_gl_error(self):
        s, e = fixture()
        edit_observed(s, e, "gl_error=0x0", "gl_error=0x502")
        self.reject(s, e)

    def test_event_out_of_order(self):
        s, e = fixture()
        e[-3]["time_ms"] = 1
        self.reject(s, e)

    def test_missing_worker_completion(self):
        s, e = fixture()
        self.reject(s, [x for x in e if x["event"] != "auto_complete"])
