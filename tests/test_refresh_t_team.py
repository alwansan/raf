import json
from pathlib import Path
import tempfile
import unittest
from scripts.refresh_t_team import build_t, render_t


class TTeamMigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, folder, name, row):
        p = self.root / folder / (name + ".json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(row), encoding="utf-8")
        return p

    def test_preserves_legacy_fix_provenance_and_stage_without_writing_source(self):
        p = self.write("issues", "world", {"id": "LOCAL", "status": "SOURCE_FIXED",
                        "updated_by": "B50", "evidence": ["original-ci"]})
        before = p.read_bytes()
        d = build_t(self.root)
        self.assertEqual(d["issues"][0]["status"], "SOURCE_FIXED")
        self.assertEqual(d["issues"][0]["updated_by"], "B50")
        self.assertEqual(p.read_bytes(), before)
        self.assertIn("../B_TEAM/issues/world.json", render_t(d))

    def test_new_team_event_does_not_close_old_issue(self):
        self.write("issues", "water", {"id": "WATER", "status": "OPEN"})
        self.write("events/T1", "result", {"id": "t1-result", "owner": "T1", "type": "closure"})
        d = build_t(self.root)
        self.assertEqual(d["issues"][0]["status"], "OPEN")
        self.assertIsNone(d["overall_percent"])
        self.assertIn("فريق T1–T5", render_t(d))

    def test_deterministic_and_rejects_unsupported_readiness(self):
        self.write("issues", "water", {"id": "WATER", "status": "OPEN"})
        self.assertEqual(build_t(self.root), build_t(self.root))
        self.write("issues", "water", {"id": "WATER", "status": "READY"})
        with self.assertRaises(ValueError):
            build_t(self.root)


if __name__ == "__main__":
    unittest.main()
