"""Synthetic-only original 82-owner Material to Shader PPtr closure tests."""
import unittest

from scripts.gt_stage_serialized_owners import OWNERS
from scripts.gt_spectrum_all82_original_material_closure import classify,summarize


KW="_SYNTHETIC_SPECTRUM_INDEX4"
NAMES=["K0","K1","K2","K3",KW]


def mat(fid=0,pid=2432,valid=None,invalid=None):
    return {"m_Shader":{"m_FileID":fid,"m_PathID":pid},
            "m_ValidKeywords":[] if valid is None else valid,
            "m_InvalidKeywords":[] if invalid is None else invalid}


def synthetic_rows():
    rows=[{"owner":o, "external":[], "materials":[]} for o in OWNERS]
    # Exactly 1556 synthetic Material documents across 82 source owners.
    for row in rows:
        if row["owner"]=="sharedassets0.assets":
            row["materials"].append(mat(valid=[KW]))
        if row["owner"]=="level2":
            row["external"]=["foo/sharedassets0.assets"]
            row["materials"].append(mat(1,2432,invalid=[KW]))
        if row["owner"]=="resources.assets":
            row["materials"].append(mat(0,2432,valid=[KW]))  # Wrong owner.
    filler=1556-sum(len(r["materials"]) for r in rows)
    rows[3]["materials"].extend(mat(0,100,[],[]) for _ in range(filler))
    return rows


class SourceSpectrum82ClosureTests(unittest.TestCase):
    def test_local_identity_requires_owner_and_pathid(self):
        self.assertEqual(classify("sharedassets0.assets",[],{"m_FileID":0,"m_PathID":2432}),"local")
        self.assertEqual(classify("level1",[],{"m_FileID":0,"m_PathID":2432}),"other")

    def test_external_pptr_one_based(self):
        self.assertEqual(classify("resources.assets",["sharedassets0.assets"],
                                  {"m_FileID":1,"m_PathID":2432}),"external")
        self.assertEqual(classify("resources.assets",["sharedassets00.assets"],
                                  {"m_FileID":1,"m_PathID":2432}),"other")

    def test_82_and_1556_exact_closure(self):
        summary=summarize(synthetic_rows(),KW,NAMES)
        self.assertEqual(summary["original_serialized_owners_SHA_verified"],82)
        self.assertEqual(summary["original_material_documents_inspected"],1556)
        self.assertEqual(summary["exact_material_references_total"],2)
        self.assertEqual(summary["exact_material_references_local"],1)
        self.assertEqual(summary["exact_material_references_external"],1)
        self.assertEqual(summary["target_keyword_enabled"],1)
        self.assertEqual(summary["target_keyword_invalid"],1)
        self.assertFalse(summary["runtime_materials_or_Shader_Find_scanned"])
        self.assertFalse(summary["exported_Unity_GUID_or_RT_CB0_sampler_verified"])
        self.assertNotIn(KW,str(summary))

    def test_missing_owner_rejected(self):
        rows=synthetic_rows()
        rows.pop()
        with self.assertRaisesRegex(ValueError,"scope_untrusted"):
            summarize(rows,KW,NAMES)

    def test_1556_accounting_mismatch_rejected(self):
        rows=synthetic_rows()
        rows[3]["materials"].pop()
        with self.assertRaisesRegex(ValueError,"incomplete"):
            summarize(rows,KW,NAMES)

    def test_shader_pptr_wrong_source_fileid_rejected(self):
        with self.assertRaisesRegex(ValueError,"out_of_range"):
            classify("level12",[],{"m_FileID":3,"m_PathID":2432})

    def test_invalid_pointer_type_rejected(self):
        with self.assertRaises(ValueError):
            classify("level3",[],{"m_FileID":True,"m_PathID":2432})
        with self.assertRaises(ValueError):
            classify("level3",[],{"m_FileID":-1,"m_PathID":2432})

    def test_invalid_keyword_arrays_rejected(self):
        rows=synthetic_rows()
        target=next(r for r in rows if r["owner"]=="sharedassets0.assets")
        target["materials"][0]["m_ValidKeywords"]=[True]
        with self.assertRaisesRegex(ValueError,"source_keyword_array_invalid"):
            summarize(rows,KW,NAMES)

    def test_duplicate_owner_rejected(self):
        rows=synthetic_rows()
        rows[0]["owner"]=rows[1]["owner"]
        with self.assertRaisesRegex(ValueError,"dup_or_missing"):
            summarize(rows,KW,NAMES)


if __name__=="__main__":
    unittest.main()
