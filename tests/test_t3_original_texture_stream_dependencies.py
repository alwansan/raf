"""Source-free T3 original Texture2D m_StreamData and immutable ZIP2 manifest controls."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts import t3_original_texture_stream_dependencies as m

class StreamEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.provider="sharedassets0.assets.resS"
        self.manifest={self.provider:(2048,"a"*64)}
    def records(self):
        return {
            ("sharedassets0.assets",1):{"m_StreamData":{"path":"archive:/"+self.provider,"offset":12,"size":120}},
            ("sharedassets1.assets",2):{"m_StreamData":{"path":"","offset":0,"size":0}},
            ("sharedassets6.assets",3):{"m_StreamData":{"path":"archive:/"+self.provider,"offset":0,"size":250}},
        }
    def evaluate(self,recs=None,providers=None):
        return m.evaluate(recs or self.records(),providers if providers is not None else self.manifest,self.root,expected=3)
    def test_authentic_external_extent_and_missing_staging_classified(self):
        report=self.evaluate()
        self.assertEqual(report["selected_original_linked_Texture2D_objects"],3)
        self.assertEqual(report["source_stream_classes"]["original_external_streamed_Texture2D"],2)
        self.assertEqual(report["source_stream_classes"]["required_original_stream_provider_not_staged"],2)
        self.assertEqual(report["required_streaming_provider_names"],{self.provider:2})
        self.assertEqual(report["original_stream_extents_by_provider_end_bytes"],{self.provider:250})
        self.assertFalse(report["full_original_stream_payloads_in_bounded_export_verified"])
    def test_stream_extent_does_not_claim_extra_bytes(self):
        records=self.records()
        records[("sharedassets0.assets",1)]["m_StreamData"]["offset"]=2000
        report=self.evaluate(records)
        self.assertEqual(report["source_stream_classes"]["original_StreamData_extent_beyond_manifest_provider"],1)
        self.assertEqual(report["original_manifest_declared_stream_objects_verified"],1)
    def test_staged_external_stream_without_sha_not_counted_as_proven(self):
        (self.root/self.provider).write_bytes(b"a"*2048)
        report=self.evaluate()
        self.assertEqual(report["source_stream_classes"]["staged_original_stream_provider_present_unhashed"],2)
        self.assertFalse(report["full_original_stream_payloads_in_bounded_export_verified"])
    def test_symlinked_staged_stream_refused(self):
        (self.root/self.provider).symlink_to(self.root/"outside")
        self.assertEqual(self.evaluate()["source_stream_classes"]["linked_staged_original_stream_provider_refused"],2)
    def test_invalid_offsets_do_not_count_as_missing_artifact(self):
        records=self.records()
        records[("sharedassets6.assets",3)]["m_StreamData"]["offset"]=-1
        r=self.evaluate(records)
        self.assertEqual(r["source_stream_classes"]["invalid_original_StreamData_values"],1)
        self.assertEqual(r["source_stream_classes"]["required_original_stream_provider_not_staged"],1)
    def test_zero_bytes_with_nonempty_stream_path_is_not_fake_inline_success(self):
        records=self.records()
        records[("sharedassets0.assets",1)]["m_StreamData"]["size"]=0
        r=self.evaluate(records)
        self.assertEqual(r["source_stream_classes"]["original_partial_StreamData"],1)
    def test_unpinned_stream_provider_cannot_be_claimed_available(self):
        r=self.evaluate(providers={})
        self.assertEqual(r["source_stream_classes"]["original_stream_provider_not_in_manifest"],2)
        self.assertEqual(r["original_manifest_declared_stream_objects_verified"],0)
    def test_duplicate_original_source_owner_id_refused(self):
        records=self.records()
        records[("wrong-asset",3)]=records.pop(("sharedassets6.assets",3))
        with self.assertRaisesRegex(ValueError,"unexpected_Texture2D"):
            self.evaluate(records)
    def test_expected_original_linked_population_is_mandatory(self):
        records=self.records()
        records.pop(("sharedassets6.assets",3))
        with self.assertRaisesRegex(ValueError,"missing_authenticated"):
            self.evaluate(records)
    def test_no_original_game_paths_or_ids_leak(self):
        r=str(self.evaluate())
        self.assertNotIn("archive:",r)
        self.assertNotIn("m_PathID",r)
        self.assertNotIn("offset",r)
if __name__=="__main__":unittest.main()
