"""Regression tests for the advisory T-team vote gate (no native workflow)."""
from datetime import datetime, timedelta, timezone
import unittest

from scripts.t_team_trial_votes import audit

NOW = datetime(2026, 11, 6, 17, 0, tzinfo=timezone.utc)
BASE = """**round_id:** trial-test-r1
**round_state:** COLLECTING
<!-- TRIAL_VOTES_BEGIN -->
| العامل | القرار | السبب | الدليل | الوقت | الجولة |
|---|---|---|---|---|---|
{rows}
<!-- TRIAL_VOTES_END -->
"""


def doc(votes=None, stamps=None, rounds=None, state="COLLECTING"):
    votes = votes or ["يحتاج"] * 5
    stamps = stamps or ["2026-11-06T16:30:00Z"] * 5
    rounds = rounds or ["trial-test-r1"] * 5
    entries = []
    for i, name in enumerate(("T1", "T2", "T3", "T4", "T5")):
        entries.append(
            f"| {name} | {votes[i]} | اختبار جهاز كبير مطلوب للعالم والماء | "
            f"https://github.com/alwansan/raf/actions/runs/42058825739 | "
            f"{stamps[i]} | {rounds[i]} |"
        )
    return BASE.format(rows="\n".join(entries)).replace("COLLECTING", state, 1)


class TrialVoteGateTests(unittest.TestCase):
    def test_five_fresh_yes_is_review_only(self):
        got = audit(doc(), now=NOW)
        self.assertTrue(got["eligible_for_T5_manual_review"])
        self.assertIn("NOT", got["note"])

    def test_one_no_blocks(self):
        votes = ["يحتاج"] * 5
        votes[2] = "لا يحتاج"
        self.assertFalse(audit(doc(votes=votes), now=NOW)["all_five_fresh_yes"])

    def test_missing_vote_blocks(self):
        votes = ["يحتاج"] * 5
        votes[1] = "لم يحدد"
        self.assertFalse(audit(doc(votes=votes), now=NOW)["all_five_fresh_yes"])

    def test_old_round_blocks(self):
        r = ["trial-test-r1"] * 5
        r[4] = "trial-old"
        got = audit(doc(rounds=r), now=NOW)
        self.assertEqual(got["votes"]["T5"]["reason"], "different_round")

    def test_stale_vote_blocks(self):
        times = ["2026-11-06T16:30:00Z"] * 5
        times[0] = "2026-11-03T16:00:00Z"
        self.assertFalse(audit(doc(stamps=times), now=NOW)["all_five_fresh_yes"])

    def test_already_requested_blocks_duplicate(self):
        self.assertFalse(audit(doc(state="REQUESTED"), now=NOW)["all_five_fresh_yes"])

    def test_duplicate_worker_rejected(self):
        bad = doc().replace("<!-- TRIAL_VOTES_END -->",
            "| T1 | يحتاج | duplicate too long | test | 2026-11-06T16:30:00Z | trial-test-r1 |\n<!-- TRIAL_VOTES_END -->")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(bad, now=NOW)

    def test_missing_worker_rejected(self):
        bad = doc().replace("| T5 | يحتاج |", "| T6 | يحتاج |")
        with self.assertRaisesRegex(ValueError, "exactly"):
            audit(bad, now=NOW)


if __name__ == "__main__":
    unittest.main()
