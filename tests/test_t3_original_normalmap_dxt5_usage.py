"""Synthetic-only T3 source type/normal-map usage tests, no proprietary assets."""
import unittest
from scripts import t3_original_normalmap_dxt5_usage as m

class NormalMapModeSource(unittest.TestCase):
    def cohort(self):
        records={}
        for i in range(1,31):
            records[("sharedassets6.assets",i)]={"m_TextureFormat":12,"m_ColorSpace":0,"m_LightmapFormat":3}
        for i in range(1,43):
            records[("sharedassets0.assets",i)]={"m_TextureFormat":12,"m_ColorSpace":1,"m_LightmapFormat":0}
        for i in range(1,35):
            records[("sharedassets1.assets",i)]={"m_TextureFormat":10,"m_ColorSpace":1,"m_LightmapFormat":0}
        return records
    def test_30_gamma_dxt5_originals_marked_normalmap(self):
        data=m.summarize(self.cohort())
        self.assertEqual(data["status"],"ALL_GAMMA_DXT5_ORIGINAL_NORMALMAP_DXT5NM")
        self.assertEqual(data["selected_original_Texture2D"],106)
        self.assertEqual(data["source_counts"]["Gamma_DXT5_NormalmapDXT5nm"],30)
        self.assertEqual(data["source_counts"]["format_DXT1"],34)
        self.assertEqual(data["source_counts"]["format_DXT5"],72)
        self.assertFalse(data["real_source_PNG_transform_equivalence_proven"])
    def test_one_different_usage_cannot_claim_all_30_normalmaps(self):
        source=self.cohort()
        source[("sharedassets6.assets",1)]["m_LightmapFormat"]=0
        data=m.summarize(source)
        self.assertEqual(data["status"],"SOURCE_NORMALMAP_HYPOTHESIS_UNCONFIRMED")
        self.assertEqual(data["source_counts"]["Gamma_DXT5_not_NormalmapDXT5nm"],1)
    def test_bool_or_string_usage_not_accepted_as_int(self):
        for usage in (True,"3",-1,999,None):
            src=self.cohort()
            src[("sharedassets6.assets",1)]["m_LightmapFormat"]=usage
            with self.subTest(usage=usage),self.assertRaisesRegex(ValueError,"format_color_usage"):
                m.summarize(src)
    def test_unknown_gamma_color_code_rejected(self):
        src=self.cohort()
        src[("sharedassets6.assets",1)]["m_ColorSpace"]=2
        with self.assertRaisesRegex(ValueError,"format_color_usage"):
            m.summarize(src)
    def test_wide_texture_format_labels_pooled_and_not_overfit(self):
        src=self.cohort()
        src[("sharedassets0.assets",1)]["m_TextureFormat"]=123
        data=m.summarize(src)
        self.assertEqual(data["source_counts"]["format_OTHER"],1)
        self.assertNotIn("123",str(data))
    def test_source_owner_alias_does_not_match_sha_pinned_roster(self):
        src=self.cohort()
        src[("outside/sharedassets6.assets",1)]=src.pop(("sharedassets6.assets",1))
        with self.assertRaisesRegex(ValueError,"untrusted_original_Texture2D_identity"):
            m.summarize(src)
    def test_missing_or_wrong_texture_type_field_fails_closed(self):
        src=self.cohort()
        del src[("sharedassets6.assets",1)]["m_LightmapFormat"]
        with self.assertRaisesRegex(ValueError,"format_color_usage"):
            m.summarize(src)
    def test_expected_source_object_count_required(self):
        src=self.cohort()
        src.pop(("sharedassets6.assets",1))
        with self.assertRaisesRegex(ValueError,"incomplete_authenticated"):
            m.summarize(src)
    def test_report_aggregates_only_no_ids_or_source_materials(self):
        summary=m.summarize(self.cohort())
        text=str(summary)
        self.assertNotIn("m_PathID",text)
        self.assertNotIn("sharedassets6.assets",text)
        self.assertNotIn("Raft_Data",text)
        self.assertFalse(summary["original_unity_pixels_or_android_device_verified"])
if __name__=="__main__":unittest.main()
