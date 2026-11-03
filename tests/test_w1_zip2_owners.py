import csv
import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.w1_stage_zip2_owners import stage
from scripts.w1_probe_engine_shader_redirects import shader_key, classify


class Zip2Owners(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / 'zip2'
        self.checkout.mkdir()
        self.dest = self.root / 'output'
        self.relative = 'Raft_Data/synthetic.assets'
        self.parts = self.checkout / 'Raft' / self.relative
        self.parts.mkdir(parents=True)
        (self.parts / 'part-00000').write_bytes(b'abc')
        (self.parts / 'part-00001').write_bytes(b'def')
        self.pin = (6, hashlib.sha256(b'abcdef').hexdigest())
        with (self.checkout / 'RAFT_FILE_MANIFEST.tsv').open('w', newline='') as f:
            w = csv.writer(f, delimiter='\t')
            w.writerow(['kind','bytes','sha256','mode','relative_path_under_Raft'])
            w.writerow(['split',self.pin[0],self.pin[1],'660',self.relative])

    def stage(self): return stage(self.checkout, self.dest, {self.relative:self.pin})

    def test_verified_reassembly_and_cache(self):
        self.assertFalse(self.stage()['owners'][0]['cache_hit'])
        self.assertEqual((self.dest / self.relative).read_bytes(), b'abcdef')
        self.assertTrue(self.stage()['owners'][0]['cache_hit'])

    def test_wrong_same_size_bytes_rejected(self):
        (self.parts / 'part-00001').write_bytes(b'bad')
        with self.assertRaises(ValueError): self.stage()
        self.assertFalse((self.dest / self.relative).exists())

    def test_missing_chunk_rejected(self):
        (self.parts / 'part-00000').unlink()
        with self.assertRaises(ValueError): self.stage()

    def test_existing_changed_output_not_overwritten(self):
        self.stage()
        output = self.dest / self.relative
        output.write_bytes(b'changed')
        with self.assertRaises(ValueError): self.stage()
        self.assertEqual(output.read_bytes(), b'changed')

    def test_redirect_rejected(self):
        chunk = self.parts / 'part-00001'
        chunk.unlink()
        chunk.symlink_to(self.parts / 'part-00000')
        with self.assertRaises(ValueError): self.stage()

    def test_engine_property_order_and_ambiguity(self):
        def tree(names):
            return {'m_Name':'synthetic', 'm_ParsedForm':{'m_Name':'synthetic',
                    'm_PropInfo':{'m_Props':[{'m_Name':n} for n in names]}}}
        a, b = shader_key(tree(['a','b'])), shader_key(tree(['b','a']))
        self.assertNotEqual(a,b)
        self.assertEqual(classify([a,b],{a:[1]})['unique_engine_identity_candidates'],1)
        self.assertEqual(classify([a],{a:[1,2]})['ambiguous_engine_identity_candidates'],1)


if __name__ == '__main__': unittest.main()
