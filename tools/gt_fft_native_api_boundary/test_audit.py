"""Authored values only, exercising the actual pinned logger envelope."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.gt_fft_native_api_boundary.audit import scan, read
from scripts.t1_fft_dispatch_pair_audit import audit as legacy_audit

P="t1_original_fft_"
DIG="a"*64
def row(f,p,n,g,*,thread=5,session="authored",site=0,pass_=0,arg=6,exp=8,frame=199,
        instance=-9,bank="source_bank0_candidate",groups="1,256,1",supported="True"):
    if f=="bind" and p=="before":
        detail=(f"sequence={n}; site={site}; pass={site//3}; shader_present=True; "
                f"shader_name_sha256={DIG}; shader_instance_session_local={instance}; frame={frame}; source_sha_prefix=8aa32937d423")
    elif f=="bind":
        detail=f"sequence={n}; gpu_result=unverified"
    elif p=="before":
        detail=(f"sequence={n}; source_sha_prefix=8aa32937d423; original_findkernel_callsite_present=false; "
                f"shader_instance_session_local={instance}; shader_present=True; original_exponent={exp}; inferred_bank_only={bank}; "
                f"pass_offset={pass_}; numeric_kernel_argument={arg}; group_xyz={groups}; unity_compute_supported={supported}; "
                f"frame={frame}; realtime_s=64.050; original_runtime_mapping=unverified; gpu_result=unverified")
    elif p=="returned":
        detail=f"sequence={n}; managed_dispatch_call_returned=true; unity_error_callback_may_follow=true; gpu_result=unverified; water_rendering=unverified"
    else:
        detail=f"sequence={n}; managed_dispatch_threw=true; exception_kind=argument; original_runtime_mapping=unverified; gpu_result=unverified; water_rendering=unverified"
    return {"utc":"2026-11-27T00:00:00Z","session":session,"sequence":g,"thread":thread,"area":"water","operation":P+f+"."+p,"detail":detail}

def window(start=1,base=1,dispatch=1,p=0,terminal="returned"):
    out=[]
    for j in range(3):
        out.extend([row("bind","before",base+j,start+2*j,site=p*3+j),
                    row("bind","returned",base+j,start+2*j+1)])
    out.extend([row("dispatch","before",dispatch,start+6,pass_=p,arg=6+p),
                row("dispatch",terminal,dispatch,start+7)])
    return out

def rewrite(rows,index,old,new):
    rows[index]["detail"]=rows[index]["detail"].replace(old,new)
    return rows

def scenarios():
    return {
      "two_pass_observed":window()+window(9,4,2,1),
      "dispatch_sync_throw":window(terminal="threw"),
      "binding_sync_throw":[row("bind","before",1,1),row("bind","threw",1,2)],
      "cross_thread":[row("dispatch","before",1,1),row("dispatch","returned",1,2,thread=6)],
      "missing_terminal":window()[:-1],
      "orphan_binding":[row("bind","returned",1,1)],
      "site_mismatch":rewrite(window(),2,"site=1","site=2"),
      "frame_mismatch":rewrite(window(),2,"frame=199","frame=200"),
      "instance_mismatch":rewrite(window(),2,"instance_session_local=-9","instance_session_local=-10"),
      "overflow":window()+[{"area":"logging","operation":"queue_overflow","dropped":1}],
      "global_gap":[dict(r,sequence=r["sequence"]+int(i>=4)) for i,r in enumerate(window())],
      "budget_exhausted":[row("bind","before",16,1),row("bind","returned",16,2),
                          row("dispatch","before",16,3),row("dispatch","returned",16,4)],
      "unrelated_callback":window()+[dict(row("bind","returned",1,9),operation="unity_error",area="unity",detail="authored error")],
      "unsupported_compute":rewrite(window(),6,"unity_compute_supported=True","unity_compute_supported=False"),
      "actual_unknown_numeric":rewrite(rewrite(window(),6,"numeric_kernel_argument=6","numeric_kernel_argument=99"),6,"source_bank0_candidate","outside_source_bank_candidates"),
      "interleaved_other_thread":[*window()[:4],
          row("bind","before",9,5,thread=7),row("bind","returned",9,6,thread=7),
          *[dict(r,sequence=r["sequence"]+2) for r in window()[4:]]],
    }

class Contract(unittest.TestCase):
    def result(self,name):
        got=scan(scenarios()[name])
        for k in ("runtime_invocation_identity_proven","actual_first_unity_failure_proven",
                  "original_bank_measured","original_runtime_kernel_mapping_proven",
                  "gpu_execution_proven","water_rendering_proven"):
            self.assertIs(got[k],False)
        return got
    def test_two_pass(self):
        x=self.result("two_pass_observed")
        self.assertEqual((x["source_order_compatible_windows"],x["numeric_6_source_compatible_windows"]),(2,1))
        self.assertEqual(x["api_calls"]["bind"]["returned"],6)
    def test_dispatch_throw(self):
        x=self.result("dispatch_sync_throw")
        self.assertEqual(x["first_observed_paired_synchronous_throw_api"],"Dispatch")
        self.assertEqual(x["windows_ending_dispatch_throw"],1)
    def test_bind_throw(self):
        x=self.result("binding_sync_throw")
        self.assertEqual(x["first_observed_paired_synchronous_throw_api"],"SetTexture")
        self.assertEqual(x["api_calls"]["bind"]["threw"],1)
        self.assertEqual(legacy_audit(scenarios()["binding_sync_throw"])["synchronous_thrown_count"],0)
    def test_cross_thread(self):
        x=self.result("cross_thread")
        self.assertEqual(x["api_calls"]["dispatch"]["invalid_pair"],1)
        self.assertEqual(x["api_calls"]["dispatch"]["returned"],0)
        self.assertEqual(legacy_audit(scenarios()["cross_thread"])["paired_count"],1)
    def test_missing_terminal(self):
        self.assertEqual(self.result("missing_terminal")["api_calls"]["dispatch"]["unresolved"],1)
    def test_orphan(self):
        self.assertEqual(self.result("orphan_binding")["api_calls"]["bind"]["orphan_terminal"],1)
    def test_window_negatives(self):
        for name in ("site_mismatch","frame_mismatch","instance_mismatch","overflow","global_gap","budget_exhausted","interleaved_other_thread"):
            with self.subTest(name=name):
                self.assertEqual(self.result(name)["source_order_compatible_windows"],0)
    def test_budget(self):
        x=self.result("budget_exhausted")
        self.assertTrue(x["binding_counter_budget_reached"] and x["dispatch_counter_budget_reached"])
    def test_async_callback_not_attributed(self):
        self.assertIsNone(self.result("unrelated_callback")["first_observed_paired_synchronous_throw_api"])
    def test_unsupported_and_outside_candidate(self):
        for name in ("unsupported_compute","actual_unknown_numeric"):
            self.assertEqual(self.result(name)["numeric_6_source_compatible_windows"],0)
    def test_reject_global_replay(self):
        for sequence in (1,0):
            rows=window()
            rows[1]["sequence"]=sequence
            with self.assertRaises(ValueError):scan(rows)
    def test_reject_mixed_sessions(self):
        rows=window()
        rows[-1]["session"]="another"
        with self.assertRaisesRegex(ValueError,"mixed_logger_sessions"):scan(rows)
    def test_reject_conflicting_terminal(self):
        with self.assertRaisesRegex(ValueError,"duplicate_or_conflicting"):scan(window()+[row("dispatch","threw",1,9)])
    def test_reject_duplicate_start(self):
        with self.assertRaisesRegex(ValueError,"duplicate_call_start"):scan(window()+[row("dispatch","before",1,9)])
    def test_reject_false_bank(self):
        with self.assertRaisesRegex(ValueError,"inferred_bank_marker_mismatch"):
            scan(rewrite(window(),6,"source_bank0_candidate","source_bank1_candidate"))
    def test_reject_invalid_site_pass(self):
        with self.assertRaisesRegex(ValueError,"binding_site_pass_mismatch"):scan(rewrite(window(),0,"pass=0","pass=1"))
    def test_reject_bad_provenance(self):
        with self.assertRaisesRegex(ValueError,"source_marker"):scan(rewrite(window(),0,"8aa32937d423","000000000000"))
    def test_reject_false_positive_marker(self):
        with self.assertRaisesRegex(ValueError,"dispatch_return_schema"):scan(rewrite(window(),7,"gpu_result=unverified","gpu_result=verified"))
    def test_reject_duplicate_detail(self):
        rows=window()
        rows[1]["detail"]+="; sequence=1"
        with self.assertRaisesRegex(ValueError,"duplicate_detail"):scan(rows)
    def test_legacy_target_not_silently_ignored(self):
        with self.assertRaisesRegex(ValueError,"legacy_fft"):scan([{"event":P+"bind.before","message":"sequence=1"}])
    def test_jsonl_duplicate_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"trace.jsonl"
            p.write_text('{"operation":"x","operation":"y"}\n')
            with self.assertRaisesRegex(ValueError,"duplicate_json_key"):read(p)
    def test_jsonl_actual_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"trace.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in window()))
            self.assertEqual(read(p),scan(window()))
    def test_reversed_terminal_is_invalid(self):
        rows=[row("dispatch","returned",1,1),row("dispatch","before",1,2)]
        self.assertEqual(scan(rows)["api_calls"]["dispatch"]["invalid_pair"],1)
    def test_unknown_unsequenced_row_blocks_windows(self):
        self.assertEqual(scan([{"other":"authored"}]+window())["source_order_compatible_windows"],0)

if __name__=="__main__":
    unittest.main()
