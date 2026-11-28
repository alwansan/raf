import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from tools.gt_fft_compute_bundle import audit as a
class BundleTests(unittest.TestCase):
    def test_byte_fields(self):
        raw=bytes(range(32))
        self.assertEqual(list(a.byte_leaves({"code":list(raw),"other":[1,2]})),[(("code",),raw)])
        self.assertEqual(list(a.byte_leaves({"code":raw})),[(("code",),raw)])
    def test_reject_unbounded_field(self):
        with self.assertRaises(ValueError):list(a.byte_leaves({"x"*97:bytes(32)}))
    def test_missing_bundle_rejected(self):
        with self.assertRaises(ValueError):a.join_captures([],{},"RGHalf")
    def fixture(self):
        reports=[];modules=[]
        for i,slots in enumerate((list(range(20)),[6],[7],[16],[17])):
            rows=[]
            for slot in slots:
                pin=f"{i:02x}{slot:02x}"*16
                rows.append({"slot":slot,"module_candidates":[{"module":{"sha256":pin}}]})
                if slot in a.SLOTS:
                    modules.append({"slot":slot,"variant":"indexed" if i==0 else "standalone","capture":{"module":{"sha256":pin}}})
            reports.append(dict(bundle_index=i,status="OBSERVED_SERIALIZED_TOPOLOGY",all_routes_decoded=True,all_routes_expected_storage=True,serialized_variants=1,decoded_modules=len(rows),rows=rows))
        return reports,{"modules":modules}
    def test_direct_serialized_live_join(self):
        reports,receipt=self.fixture()
        self.assertEqual(len(a.join_captures(reports,receipt,"RGFloat")),8)
        receipt["modules"][0]["capture"]["module"]["sha256"]="0"*64
        with self.assertRaises(ValueError):a.join_captures(reports,receipt,"RGFloat")
    def test_duplicate_capture_rejected(self):
        reports,receipt=self.fixture()
        receipt["modules"][-1]=receipt["modules"][0]
        with self.assertRaises(ValueError):a.join_captures(reports,receipt,"RGFloat")
    def test_bounded_load_fields(self):
        self.assertEqual(a.bundle_load_fields({"bundle_load_index":2,"bundle_load_step":4,"bundle_opened":3,"bundle_named":True,"bundle_asset_count":100000,"raw_error":"private"}),{"bundle_load_index":2,"bundle_load_step":4,"bundle_opened":3})
    def test_log_categories_only(self):
        with TemporaryDirectory() as root:
            p=Path(root)
            (p/"editor.log").write_text("private token example\nUnable to open archive file: private-path\nCRC mismatch")
            result=a.log_categories(p)
            self.assertTrue(result["editor.log"]["archive_open"])
            self.assertTrue(result["editor.log"]["crc_mismatch"])
            self.assertNotIn("private-path",str(result))
    def test_missing_build_receipt_rejected(self):
        with TemporaryDirectory() as root:
            with self.assertRaises(ValueError):a.build_receipt(Path(root),"run")
if __name__=="__main__":unittest.main()
