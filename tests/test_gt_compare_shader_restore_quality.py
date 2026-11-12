"""GT shader quality comparisons: source-only conservative contract controls."""
import unittest
from scripts.gt_compare_shader_restore_quality import compare, STATUS


def sample(dummy=20, custom=3, builtin=10, unknown=0, material_docs=33, files=25):
    return {
        "status":STATUS,
        "counts":{
            "material_documents":material_docs,
            "material_docs_using_dummy_Shader":dummy,
            "material_docs_using_non_dummy_Shader":custom,
            "material_docs_using_Unity_builtin_Shader":builtin,
            "material_docs_with_unknown_or_broken_Shader":unknown,
            "shader_files":files,
            "shader_files_with_dummy_exporter_marker":files,
            "shader_files_with_complete_program_pass":files,
        },
    }


class QualityTest(unittest.TestCase):
    def test_vendor_material_restore_reports_actual_delta_not_device_success(self):
        r=compare(sample(),sample(dummy=12,custom=11,files=27),True)
        self.assertEqual(r["dummy_material_documents_decreased_by"],8)
        self.assertTrue(r["original_exported_meta_bytes_unchanged"])
        self.assertFalse(r["original_shader_variant_parity_proven"])
        self.assertFalse(r["android_shader_compilation_or_pixels_verified"])

    def test_no_change_is_not_misrepresented_as_full_shader_recovery(self):
        r=compare(sample(),sample(),True)
        self.assertEqual(r["dummy_material_documents_decreased_by"],0)
        self.assertEqual(r["postrestore_custom_dummy_material_documents"],20)

    def test_existing_meta_change_rejected(self):
        with self.assertRaisesRegex(ValueError,"original_meta_guid_modified"):
            compare(sample(),sample(),False)

    def test_unresolved_shader_regression_rejected(self):
        with self.assertRaisesRegex(ValueError,"vendor_restore_introduced_unresolved"):
            compare(sample(),sample(unknown=1,dummy=19),True)

    def test_missing_quality_report_rejected(self):
        with self.assertRaises(ValueError):
            compare(sample(),{"counts":sample()["counts"]},True)

    def test_material_count_drift_rejected(self):
        with self.assertRaisesRegex(ValueError,"changed_exported_material_document_count"):
            compare(sample(),sample(material_docs=34),True)

    def test_count_inconsistency_rejected(self):
        with self.assertRaisesRegex(ValueError,"shader_material_count_inconsistent"):
            compare(sample(),sample(dummy=50),True)


if __name__=="__main__":
    unittest.main()
