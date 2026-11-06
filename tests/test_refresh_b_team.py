import json
from pathlib import Path
import tempfile
import unittest
from scripts.refresh_b_team import build, render, STAGES


class BTeamSummaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, folder, name, row):
        p = self.root / folder / (name + ".json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(row), encoding="utf-8")

    def issue(self, status="OPEN"):
        return {"id": "WORLD", "title": "world", "status": status, "evidence": []}

    def test_event_cannot_close_issue_and_no_fake_percent(self):
        self.write("issues", "world", self.issue())
        self.write("events", "done", {"id": "done", "type": "closure", "issue_id": "WORLD"})
        d = build(self.root)
        self.assertEqual(d["issues"][0]["status"], "OPEN")
        self.assertIsNone(d["overall_percent"])

    def test_claimed_fix_requires_evidence(self):
        self.write("issues", "world", self.issue("SOURCE_FIXED"))
        with self.assertRaises(ValueError):
            build(self.root)

    def test_duplicate_issue_refused(self):
        self.write("issues", "a", self.issue())
        self.write("issues", "b", self.issue())
        with self.assertRaises(ValueError):
            build(self.root)

    def test_deterministic_and_unknown_resource_preserved(self):
        self.write("resources", "r", {"id": "r", "stages": {k: "UNKNOWN" for k in STAGES}})
        a, b = build(self.root), build(self.root)
        self.assertEqual(a, b)
        self.assertIn("device=UNKNOWN", render(a))

    def test_missing_stage_and_unknown_status_refused(self):
        self.write("issues", "world", self.issue("READY"))
        with self.assertRaises(ValueError):
            build(self.root)
        self.write("issues", "world", self.issue())
        self.write("resources", "r", {"id": "r", "stages": {"device": "UNKNOWN"}})
        with self.assertRaises(ValueError):
            build(self.root)

    def test_explicit_event_id_alias_is_preserved_without_touching_source(self):
        self.write("events/T4", "legacy-new", {
            "event_id": "T4-unambiguous", "origin": "scheduled",
            "issue_id": "INPUT-005", "updated_at": "2026-11-06T07:48:00Z",
        })
        path = self.root / "events/T4/legacy-new.json"
        original = path.read_bytes()
        rows = build(self.root)["events"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "T4-unambiguous")
        self.assertEqual(rows[0]["event_id"], "T4-unambiguous")
        self.assertEqual(rows[0]["_record_path"], "events/T4/legacy-new.json")
        self.assertEqual(original, path.read_bytes())

    def test_explicit_id_and_equal_event_id_are_accepted(self):
        self.write("events", "same", {"id": "unique", "event_id": "unique"})
        self.assertEqual(build(self.root)["events"][0]["id"], "unique")

    def test_conflicting_or_malformed_event_alias_fails_closed(self):
        for alias in ("", "  ", None, 10, [], {"identity": "untrusted"}):
            self.write("events", "bad", {"id": "stable", "event_id": alias})
            with self.subTest(alias=alias), self.assertRaises(ValueError):
                build(self.root)
        self.write("events", "bad", {"id": "stable", "event_id": "different"})
        with self.assertRaisesRegex(ValueError, "Conflicting event identities"):
            build(self.root)

    def test_duplicate_legacy_id_and_new_event_id_is_rejected(self):
        self.write("events/T4", "new", {"event_id": "same-event"})
        self.write("events/T5", "old", {"id": "same-event"})
        with self.assertRaisesRegex(ValueError, "Duplicate events record identity"):
            build(self.root)

    def test_session_id_only_never_becomes_event_identity(self):
        self.write("events/T5", "session-only", {"session_id": "not-a-unique-event"})
        with self.assertRaisesRegex(ValueError, "Missing record identity"):
            build(self.root)
        self.write("events/T5", "session-only", {"event_id": "safe-event"})
        self.write("issues", "bad", {"event_id": "not-an-issue-id", "status": "OPEN"})
        with self.assertRaisesRegex(ValueError, "Missing record identity"):
            build(self.root)

    def test_symlink_refused(self):
        self.write("issues", "world", self.issue())
        (self.root / "issues" / "link.json").symlink_to(self.root / "issues" / "world.json")
        with self.assertRaises(ValueError):
            build(self.root)


if __name__ == "__main__":
    unittest.main()
