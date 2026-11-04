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

    def test_symlink_refused(self):
        self.write("issues", "world", self.issue())
        (self.root / "issues" / "link.json").symlink_to(self.root / "issues" / "world.json")
        with self.assertRaises(ValueError):
            build(self.root)


if __name__ == "__main__":
    unittest.main()
