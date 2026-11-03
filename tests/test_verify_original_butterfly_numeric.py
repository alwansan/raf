"""Fail-closed source handling with test-owned source, not original game code."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.verify_original_butterfly_numeric import generate

class NumericHarnessSourceTests(unittest.TestCase):
    def test_fingerprint_mismatch_never_creates_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source';source.mkdir();(source/'ButterflyFFTUtility.cs').write_text('class Owned {}')
            with self.assertRaisesRegex(ValueError,'fingerprint'):
                generate(source,root/'output')
            self.assertFalse((root/'output').exists())

    def test_ambiguous_source_and_output_inside_source_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source';source.mkdir();(source/'nested').mkdir()
            for path in (source/'ButterflyFFTUtility.cs',source/'nested/ButterflyFFTUtility.cs'):path.write_text('class Owned {}')
            with self.assertRaisesRegex(ValueError,'ambiguous'):generate(source,root/'output')
            with self.assertRaisesRegex(ValueError,'outside source'):generate(source,source/'output')
            self.assertFalse((root/'output').exists());self.assertFalse((source/'output').exists())

if __name__=='__main__':unittest.main()
