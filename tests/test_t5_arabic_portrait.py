"""Source-level owner requirements: portrait unified lab, Arabic human guidance, stable pack."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"apk-for-testing/unified/app/src/main/AndroidManifest.xml"
ACTIVITY=ROOT/"apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java"
ARABIC=ROOT/"apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/ArabicLabStrings.java"
PACK=ROOT/"apk-for-testing/unified/pack/team-testpack.json"
DIRECTIVE=ROOT/"prompt/coordination/T_TEAM/OWNER_ARABIC_PORTRAIT_CL_UPLOADS_20261108.md"


class ArabicPortraitLabContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=MANIFEST.read_text(encoding="utf-8")
        cls.activity=ACTIVITY.read_text(encoding="utf-8")
        cls.translations=ARABIC.read_text(encoding="utf-8")
        cls.pack=json.loads(PACK.read_text(encoding="utf-8"))

    def test_four_activities_portrait(self):
        self.assertEqual(self.manifest.count('android:screenOrientation="portrait"'),4)
        self.assertNotIn('android:screenOrientation="landscape"',self.manifest)

    def test_all_test_descriptions_translated_without_editing_pack(self):
        expected={x["id"] for x in self.pack["tests"]}
        actual=set(re.findall(r'\bm\.put\("(T[1-5]-\d{2,3})", new String\[\]',self.translations))
        self.assertEqual(actual,expected)
        self.assertEqual(len(expected),29)
        for line in self.translations.splitlines():
            if "m.put(" in line:
                self.assertRegex(line,"[\u0600-\u06ff]")

    def test_owner_navigation_rtl_and_cl_upload_path(self):
        self.assertIn("View.LAYOUT_DIRECTION_RTL",self.activity)
        self.assertIn("ArabicLabStrings.title",self.activity)
        self.assertIn("ArabicLabStrings.instructions",self.activity)
        self.assertIn("ArabicLabStrings.expected",self.activity)
        self.assertIn("github.com/alwansan/CL/tree/main/test",self.activity)
        self.assertLess(self.activity.index("content.addView(pendingButtons)"),self.activity.index("caseDetail=text("))
        self.assertIn('manualResult("USER_PASS")',self.activity)
        self.assertIn("اكتب أولًا ما شاهدته",self.activity)

    def test_original_machine_drivers_and_pack_schema_stable(self):
        self.assertEqual(self.pack["schema_version"],2)
        self.assertEqual(self.pack["pack_id"],"raft-shared-t1-t5-v1")
        self.assertEqual(self.pack["revision"],1)
        self.assertTrue(all(t["id"].startswith(t["worker"]+"-") for t in self.pack["tests"]))
        self.assertIn('"EVIDENCE_READY"',self.activity)
        self.assertIn('"BLOCKED"',self.activity)
        self.assertIn("alwansan/CL/tree/main/test",DIRECTIVE.read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
