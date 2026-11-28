import unittest
from tools.gt_fft_same_export import audit as a
class Controls(unittest.TestCase):
    def setUp(self):
        self.guid="abcdef0123456789abcdef0123456789"
        self.body=("MonoBehaviour:\n  computeArray:\n  - {fileID: 7200000, guid: "+self.guid+", type: 2}\n").encode()
        self.field=a.digest(b"computeArray")
    def test_exact(self):
        self.assertTrue(a.verify_field(self.body,self.field,(7200000,self.guid,"2")))
    def test_wrong_guid_type_file_id_and_field(self):
        for p in [(7200001,self.guid,"2"),(7200000,"0"*32,"2"),(7200000,self.guid,"3")]:
            with self.assertRaises(ValueError):a.verify_field(self.body,self.field,p)
        with self.assertRaises(ValueError):a.verify_field(self.body,a.digest(b"wrong"),(7200000,self.guid,"2"))
    def test_duplicate_and_extra(self):
        for body in [self.body+b"  computeArray: []\n",self.body+b"  - {fileID: 0}\n"]:
            with self.assertRaises(ValueError):a.verify_field(body,self.field,(7200000,self.guid,"2"))
if __name__=="__main__":unittest.main()
