"""T4 source-only exhaustive ledger record identity preflight regressions."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.t4_audit_team_event_identities import audit_events


class EventIdentityAudit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "events"
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def event(self, rel, payload):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_clean_id_and_event_id_accepted_without_mutation(self):
        self.event("T2/one.json", {"id": "one", "worker": "T2"})
        self.event("T3/two.json", {"event_id": "two", "session_id": "test"})
        v = audit_events(self.root)
        self.assertEqual(v["status"], "LEDGER_IDENTITY_CLEAN")
        self.assertEqual(v["finding_count"], 0)
        self.assertEqual(v["event_files_examined"], 2)
        self.assertFalse(v["canonical_summary_generation_proven"])

    def test_missing_event_id_reported_all_not_just_first(self):
        self.event("T2/a.json", {"session_id": "a"})
        self.event("T3/b.json", {"session_id": "b"})
        v = audit_events(self.root)
        self.assertEqual(v["finding_categories"], {"MISSING_RECORD_ID": 2})
        self.assertEqual([x["path"] for x in v["findings"]], ["T2/a.json", "T3/b.json"])

    def test_invalid_empty_event_id_rejected(self):
        self.event("T2/a.json", {"event_id": "  "})
        v = audit_events(self.root)
        self.assertEqual(v["finding_categories"], {"INVALID_EVENT_ID": 1})

    def test_conflicting_id_and_event_id_rejected(self):
        self.event("T2/a.json", {"id": "alpha", "event_id": "beta"})
        v = audit_events(self.root)
        self.assertEqual(v["finding_categories"], {"CONFLICTING_EVENT_IDS": 1})

    def test_matching_event_id_and_id_is_valid(self):
        self.event("T2/a.json", {"id": "alpha", "event_id": "alpha"})
        self.assertEqual(audit_events(self.root)["finding_count"], 0)

    def test_duplicate_ids_across_worker_files_reported_all(self):
        self.event("T2/a.json", {"id": "same"})
        self.event("T3/b.json", {"event_id": "same"})
        v = audit_events(self.root)
        self.assertEqual(v["finding_categories"], {"DUPLICATE_RECORD_ID": 2})

    def test_non_object_and_malformed_json_reported(self):
        self.event("T3/a.json", [])
        (self.root / "b.json").write_text("{bad", encoding="utf-8")
        v = audit_events(self.root)
        self.assertEqual(v["finding_categories"], {
            "NON_OBJECT_JSON": 1, "UNREADABLE_OR_INVALID_JSON": 1})

    def test_nested_duplicate_json_keys_flagged_even_when_id_valid(self):
        (self.root / "dupe.json").write_text('{"id":"only","metadata":{"a":1,"a":2}}')
        v = audit_events(self.root)
        self.assertEqual(v["finding_categories"], {"DUPLICATE_JSON_KEYS": 1})

    def test_symlinked_event_file_rejected(self):
        self.event("T2/original.json", {"id": "one"})
        (self.root / "T3").mkdir()
        try:
            (self.root / "T3/mirror.json").symlink_to("../T2/original.json")
        except OSError:
            self.skipTest("symlinks unsupported")
        v = audit_events(self.root)
        self.assertEqual(v["finding_categories"], {"NONREGULAR_OR_OVERSIZED": 1})

    def test_not_repairing_canonical_identity(self):
        path = self.event("T3/old.json", {"session_id": "old"})
        before = path.read_bytes()
        v = audit_events(self.root)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(v["repair_performed"])
        self.assertFalse(v["canonical_summary_generation_proven"])


if __name__ == "__main__":
    unittest.main()
