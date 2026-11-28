import unittest
from tools.gt_fft_same_export import audit as same
from tools.gt_fft_exact_import import audit as a
class Controls(unittest.TestCase):
    def test_exact_pointer_text_and_absent_control(self):
        guid="abcdef0123456789abcdef0123456789"
        ptr=("{fileID: 7200000, guid: "+guid+", type: 3}").encode()
        body=b"MonoBehaviour:\n  array:\n  - "+ptr+b"\n"
        witness,exact=a.witness_body(body,same.digest(b"array"),(7200000,guid,"3"))
        self.assertEqual(exact,ptr)
        self.assertEqual(witness.count(ptr),1)
        self.assertIn(a.WRONG_GUID.encode(),witness)
        self.assertIn(b"selected:\n  - "+ptr,witness)
    def test_no_type_or_guid_guess(self):
        guid="abcdef0123456789abcdef0123456789"
        body=("MonoBehaviour:\n  array:\n  - {fileID: 7200000, guid: "+guid+", type: 2}\n").encode()
        with self.assertRaises(ValueError):a.witness_body(body,same.digest(b"array"),(7200000,guid,"3"))
if __name__=="__main__":unittest.main()
