"""No commercial/game payload used by these tests."""
import unittest
from gfxlab.tools.shears_provenance_probe import resolve_pptr, texture_slot_rows, owner_basename

class ShearsSourceLinks(unittest.TestCase):
    def test_same_owner_local(self):
        kind,key=resolve_pptr({"m_FileID":0,"m_PathID":42},"resources.assets",[])
        self.assertEqual((kind,key),("local",("resources.assets",42)))
    def test_external_exact_basename(self):
        kind,key=resolve_pptr({"m_FileID":1,"m_PathID":19},"resources.assets",["archive:/path/sharedassets0.assets"])
        self.assertEqual((kind,key),("external_staged",("sharedassets0.assets",19)))
    def test_unstaged_external_not_guessed(self):
        kind,key=resolve_pptr({"m_FileID":1,"m_PathID":19},"resources.assets",["other.assets"])
        self.assertEqual((kind,key),("external_unstaged",None))
    def test_reject_external_out_of_range(self):
        kind,key=resolve_pptr({"m_FileID":2,"m_PathID":19},"resources.assets",["sharedassets0.assets"])
        self.assertEqual((kind,key),("malformed",None))
    def test_reject_null_external(self):
        self.assertEqual(resolve_pptr({"m_FileID":1,"m_PathID":0},"resources.assets",["sharedassets0.assets"])[0],"malformed")
    def test_reject_unknown_keys(self):
        self.assertEqual(resolve_pptr({"m_FileID":"0","m_PathID":1},"resources.assets",[])[0],"malformed")
    def test_no_confused_external_name(self):
        self.assertIsNone(owner_basename("someone/sharedassets0.assets.backup"))
        self.assertIsNone(owner_basename(""))
        self.assertEqual(owner_basename("sharedassets0.assets"),"sharedassets0.assets")
    def test_source_texenv_array(self):
        rows=texture_slot_rows([{"m_First":"secret-private-key","m_Second":{"m_Texture":{"m_FileID":0,"m_PathID":3}}}])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["m_Texture"]["m_PathID"],3)
    def test_source_pair_list(self):
        v={"m_Texture":{"m_FileID":0,"m_PathID":5}}
        self.assertEqual(texture_slot_rows([["_MainTex",v]])[0],v)
    def test_source_singleton_dict_entry(self):
        v={"m_Texture":{"m_FileID":0,"m_PathID":6}}
        self.assertEqual(texture_slot_rows([{"_MainTex":v}])[0],v)
    def test_source_reject_missing_texture_pointer(self):
        with self.assertRaises(ValueError):
            texture_slot_rows([{"_MainTex":{}}])
    def test_original_map_is_not_source_array(self):
        with self.assertRaises(ValueError):
            texture_slot_rows({"_MainTex":{"m_Texture":{"m_FileID":0,"m_PathID":4}}})
    def test_reject_bad_texenv(self):
        with self.assertRaises(ValueError):
            texture_slot_rows([{"not_the_right_key":1}])
        with self.assertRaises(ValueError):
            texture_slot_rows("bad")
if __name__=="__main__":
    unittest.main()
