"""T4 ledger identity regression: actual inherited JSON and independent synthetic cases.

Pure read-only test: never rewrites records or generates T_TEAM snapshot.
"""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.refresh_b_team import build, read_records
from scripts.refresh_t_team import build_t

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "prompt/coordination/B_TEAM"
TARGET = LEDGER / "events/T4/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.json"
EXPECTED_ID = "20261106T0130Z-T4-chat-touchpad-device-source-q4m7"


def write_event(root, name, event):
    directory = root / "events/T4"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(json.dumps(event, sort_keys=True), encoding="utf-8")


class LedgerEventIdentity(unittest.TestCase):
    def test_current_T4_event_has_exact_stable_id(self):
        event = json.loads(TARGET.read_text(encoding="utf-8"))
        self.assertEqual(event["id"], EXPECTED_ID)
        self.assertEqual(event["session_id"], EXPECTED_ID)
        self.assertEqual(event["owner"], "T4")
        self.assertEqual(event["issue_id"], "INPUT-005")
        self.assertTrue(event["summary"].strip())
        self.assertTrue(event["evidence"])
        self.assertEqual(event["at"], "2026-11-06T01:33:00Z")

    def test_actual_all_event_record_identities_unique(self):
        rows = read_records(LEDGER, "events")
        self.assertGreater(len(rows), 1)
        matching = [r for r in rows if r["id"] == EXPECTED_ID]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["_record_path"],
                         "events/T4/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.json")

    def test_actual_t_team_canonical_parser_is_read_only_and_open(self):
        before = TARGET.read_bytes()
        data = build_t(LEDGER)
        self.assertEqual(data["generation"], "T-2026-11-05")
        self.assertIn(EXPECTED_ID, {e["id"] for e in data["events"]})
        issues = [i for i in data["issues"] if i["id"] == "INPUT-005"]
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["status"], "OPEN")
        self.assertEqual(data["readiness"], "NOT_ASSESSED_BY_THIS_SUMMARY")
        self.assertEqual(TARGET.read_bytes(), before)

    def test_missing_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_event(root, "missing.json", {"session_id": "no-id", "owner": "T4"})
            with self.assertRaisesRegex(ValueError, "Missing record identity"):
                read_records(root, "events")

    def test_empty_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_event(root, "empty.json", {"id": "", "owner": "T4"})
            with self.assertRaisesRegex(ValueError, "Missing record identity"):
                read_records(root, "events")

    def test_duplicate_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("a.json", "b.json"):
                write_event(root, name, {"id": EXPECTED_ID, "owner": "T4"})
            with self.assertRaisesRegex(ValueError, "Duplicate events record identity"):
                read_records(root, "events")

    def test_linked_event_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_event(root, "real.json", {"id": EXPECTED_ID, "owner": "T4"})
            (root / "events/T4/linked.json").symlink_to(root / "events/T4/real.json")
            with self.assertRaisesRegex(ValueError, "Symlink record refused"):
                read_records(root, "events")


if __name__ == "__main__":
    unittest.main()
