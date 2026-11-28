import unittest
from tools.gt_fft_compiler_directive import audit as a
class DirectiveTests(unittest.TestCase):
    def test_exact_reversal(self):
        original=b"#pragma kernel main\n[numthreads(512,1,1)] void main(){}\n"
        changed=a.directive(original)
        self.assertEqual(changed,a.DIRECTIVE+original)
        self.assertEqual(a.strip_directive(changed),original)
    def test_refuse_duplicate_or_conflicting_directive(self):
        for text in (b"#pragma kernel main\n#pragma use_dxc\n",b"#pragma kernel main\n#pragma never_use_dxc\n",b"void main(){}",b"#pragma kernel main\n\x00"):
            with self.assertRaises(ValueError):a.directive(text)
    def test_refuse_unmodified_source(self):
        with self.assertRaises(ValueError):a.strip_directive(b"#pragma kernel main\n")
if __name__=="__main__":unittest.main()
