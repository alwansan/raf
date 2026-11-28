import unittest
from types import SimpleNamespace
from tools.gt_skybox_exact_provider import resolve as r
from tools.gt_ambient_same_export import audit as a
def env(*names):
    return SimpleNamespace(file=SimpleNamespace(externals=[SimpleNamespace(path=n) for n in names]))
def mat(file_id,path_id=-42):
    return {"m_SkyboxMaterial":{"m_FileID":file_id,"m_PathID":path_id}}
class TestExactProvider(unittest.TestCase):
    def setUp(self):self.rows=r.catalog()
    def test_metadata_population(self):
        self.assertEqual(len(self.rows),42)
        self.assertEqual(sum(x["kind"]=="split" for x in self.rows.values()),3)
    def test_exact_slot_not_first_name(self):
        self.assertEqual(r.external_owner(env("sharedassets2.assets","archive:/a/sharedassets3.assets"),mat(2),self.rows),("sharedassets3.assets",-42))
    def test_windows_basename(self):
        self.assertEqual(r.external_owner(env(r"archive:\x\resources.assets"),mat(1),self.rows),("resources.assets",-42))
    def test_not_staged_is_precise(self):
        with self.assertRaisesRegex(r.Rejected,"outside_exact_new_scope"):r.external_owner(env("sharedassets24.assets"),mat(1),self.rows)
    def test_unknown_external_not_fallback(self):
        with self.assertRaisesRegex(r.Rejected,"outside_exact_new_scope"):r.external_owner(env("unknown.assets","sharedassets3.assets"),mat(1),self.rows)
    def test_slot_out_of_range(self):
        with self.assertRaisesRegex(r.Rejected,"slot_missing"):r.external_owner(env("sharedassets3.assets"),mat(2),self.rows)
    def test_bad_path_injection(self):
        with self.assertRaisesRegex(r.Rejected,"path_schema"):r.external_owner(env("bad\nsharedassets3.assets"),mat(1),self.rows)
    def test_local_and_null_rejected(self):
        for p in (mat(0),mat(0,0)):
            with self.assertRaisesRegex(r.Rejected,"expected_unresolved"):r.external_owner(env("sharedassets3.assets"),p,self.rows)
    def test_provider_not_in_catalog(self):
        with self.assertRaisesRegex(r.Rejected,"outside_exact_new_scope"):r.external_owner(env("sharedassets999.assets"),mat(1),self.rows)
    def test_split_order_and_sizes(self):
        for p in self.rows.values():
            if p["kind"]=="split":
                self.assertEqual(sum(x["bytes"] for x in p["parts"]),p["bytes"])
                self.assertEqual([x["name"] for x in p["parts"]],[f"part-{i:05d}" for i in range(3)])
