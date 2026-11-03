import hashlib
from pathlib import Path
import unittest
from scripts.probe_original_fft_target_formats import analyze
class TargetFormatTests(unittest.TestCase):
    def test_fingerprint_rejects_unknown_source(self):
        with self.assertRaisesRegex(ValueError,'fingerprint'):analyze('class Owned {}')
    def test_missing_method_and_wrong_contract_fail_closed(self):
        for source in ('class Owned {}','class Owned { private void RetrieveRenderTexturesSet() { int size = 2; } }'):
            with self.assertRaises(ValueError):analyze(source,hashlib.sha256(source.encode()).hexdigest())
if __name__=='__main__':unittest.main()
