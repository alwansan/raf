from datetime import datetime,timezone
import unittest
from scripts.check_shared_lab_votes import analyze
BASE="""**shared_round_id:** shared-test-r1
| العامل | القرار | السبب | الدليل | الوقت | الجولة |
|---|---|---|---|---|---|
{rows}
"""
NOW=datetime(2026,11,8,18,0,tzinfo=timezone.utc)
def doc(votes=None,ts=None,rounds=None):
    votes=votes or ["NO_BUILD"]*4+["NEED_BUILD"]
    ts=ts or ["2026-11-08T17:55:00Z"]*5
    rounds=rounds or ["shared-test-r1"]*5
    rows=[]
    for i in range(5):
        rows.append(f"| T{i+1} | {votes[i]} | Native driver change requires a new phone test | https://github.com/alwansan/raf/commit/0123456789012345678901234567890123456789 | {ts[i]} | {rounds[i]} |")
    return BASE.format(rows="\n".join(rows))
class GateTests(unittest.TestCase):
    def test_one_need_is_enough_for_review(self):
        x=analyze(doc(),NOW);self.assertTrue(x["eligible_for_T5_review"]);self.assertFalse(x["all_five_need"])
    def test_no_needs(self):
        x=analyze(doc(votes=["NO_BUILD"]*5),NOW);self.assertFalse(x["eligible_for_T5_review"])
    def test_stale_one_blocks(self):
        x=analyze(doc(ts=["2026-11-08T17:55:00Z"]*4+["2026-11-02T00:00:00Z"]),NOW)
        self.assertFalse(x["eligible_for_T5_review"])
    def test_different_round_blocks(self):
        x=analyze(doc(rounds=["shared-test-r1"]*4+["shared-old"]),NOW);self.assertFalse(x["eligible_for_T5_review"])
    def test_duplicate_or_missing_worker(self):
        with self.assertRaises(ValueError):analyze(doc().replace("| T5 |","| T4 |"),NOW)
if __name__=="__main__":unittest.main()
