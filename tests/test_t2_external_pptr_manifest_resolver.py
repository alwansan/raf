import unittest
from t2_external_pptr_manifest_resolver import resolve_external_target as resolve
H = 'a' * 64

class ResolverTests(unittest.TestCase):
    def test_unique_pinned_candidate(self):
        self.assertEqual(resolve('owner.assets', [{'path':'Raft_Data/owner.assets','sha256':H}]), ('Raft_Data/owner.assets',H))
    def test_missing(self):
        self.assertIsNone(resolve('other.assets', [{'path':'Raft_Data/owner.assets','sha256':H}]))
    def test_ambiguous(self):
        self.assertIsNone(resolve('owner.assets', [{'path':'a/owner.assets','sha256':H},{'path':'b/owner.assets','sha256':H}]))
    def test_unpinned(self):
        self.assertIsNone(resolve('owner.assets', [{'path':'a/owner.assets','sha256':'invalid'}]))
    def test_traversal(self):
        self.assertIsNone(resolve('owner.assets', [{'path':'../owner.assets','sha256':H}]))
    def test_reference_path(self):
        self.assertIsNone(resolve('../owner.assets', []))
    def test_bad_unrelated_entry(self):
        self.assertIsNone(resolve('owner.assets', [{'path':'a/owner.assets','sha256':H},{'path':'b/bad.assets','sha256':None}]))

if __name__ == '__main__':
    unittest.main()
