import copy
import json
import unittest
from t2_foam_pass_role_matrix import verify, unique
BASE = {"schema_version":1,"passes":[{"pass":0,"source":"RenderTexture","destination":"UNKNOWN"},{"pass":1,"source":"UNKNOWN","destination":"RenderTexture"}],"aggregates":{"source":{"Texture":0,"RenderTexture":1,"UNKNOWN":1},"destination":{"RenderTexture":1,"NULL":0,"UNKNOWN":1}}}
class TestGate(unittest.TestCase):
    def test_valid(self): self.assertEqual(verify(BASE)["status"], "SCHEMA_CONSISTENT_NOT_RUNTIME_PROVEN")
    def test_alternate_assignment(self):
        p=copy.deepcopy(BASE); p["passes"][0]["source"],p["passes"][1]["source"]=p["passes"][1]["source"],p["passes"][0]["source"]; verify(p)
    def test_duplicate_pass(self):
        p=copy.deepcopy(BASE); p["passes"][1]["pass"]=0
        with self.assertRaises(ValueError): verify(p)
    def test_bool_pass(self):
        p=copy.deepcopy(BASE); p["passes"][0]["pass"]=False
        with self.assertRaises(ValueError): verify(p)
    def test_bool_count(self):
        p=copy.deepcopy(BASE); p["aggregates"]["source"]["Texture"]=False
        with self.assertRaises(ValueError): verify(p)
    def test_count_mismatch(self):
        p=copy.deepcopy(BASE); p["aggregates"]["source"]["Texture"]=1
        with self.assertRaises(ValueError): verify(p)
    def test_extra_fields(self):
        p=copy.deepcopy(BASE); p["passes"][0]["original_field_name"]="secret"
        with self.assertRaises(ValueError): verify(p)
    def test_unknown_type(self):
        p=copy.deepcopy(BASE); p["passes"][0]["source"]="Texture2D"
        with self.assertRaises(ValueError): verify(p)
    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError): json.loads('{"pass":0,"pass":1}', object_pairs_hook=unique)
if __name__ == "__main__": unittest.main()
