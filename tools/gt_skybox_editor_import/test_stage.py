import unittest
from tools.gt_skybox_editor_import import stage as a
from tools.gt_light_same_export.audit import Rejected

def good():
    out={k:True for k in a.BOOL_FIELDS}
    out["playerBuilt"]=False
    out.update({k:0 for k in a.COUNT_FIELDS})
    out.update(status="PASS",version=a.VERSION,errorCategory="none",candidateSha256=a.CANDIDATE_SHA,
               colorSlots=6,colorMatches=6,floatSlots=20,floatMatches=20,passCount=1,privateBundleBytes=100)
    return out

class EditorControls(unittest.TestCase):
    def test_good(self): self.assertTrue(a.verify_editor(good()))
    def test_digest_drift(self):
        x=good();x["candidateSha256"]=""
        self.assertFalse(a.verify_editor(x))
    def test_same_counts_wrong_values(self):
        x=good();x["floatMatches"]=19
        self.assertFalse(a.verify_editor(x))
    def test_wrong_color(self):
        x=good();x["colorMatches"]=5
        self.assertFalse(a.verify_editor(x))
    def test_wrong_reference(self):
        x=good();x["materialShaderReference"]=False
        self.assertFalse(a.verify_editor(x))
    def test_not_vulkan_only(self):
        x=good();x["androidVulkanOnly"]=False
        self.assertFalse(a.verify_editor(x))
    def test_compiler_error(self):
        x=good();x["shaderErrorsAfter"]=1
        self.assertFalse(a.verify_editor(x))
    def test_no_bundle(self):
        x=good();x["privateBundleBytes"]=0
        self.assertFalse(a.verify_editor(x))
    def test_player_not_allowed(self):
        x=good();x["playerBuilt"]=True
        self.assertFalse(a.verify_editor(x))
    def test_bad_schema(self):
        with self.assertRaises(Rejected): a.verify_editor(dict(good(),rawName="AUTHORED"))
    def test_binary32_signed_zero(self):
        self.assertEqual(a.bits(-0.0),"80000000")

if __name__=="__main__": unittest.main()
