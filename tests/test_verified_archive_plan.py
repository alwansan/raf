import hashlib
import unittest
from scripts.extract_verified_raft_sources import extraction_plan


class VerifiedArchivePlanTests(unittest.TestCase):
    def test_git_blob_and_lfs_pointer_identities_are_distinct(self):
        name = 'Raft/Raft_Data/resources.assets'
        pointer = 'version https://git-lfs.github.com/spec/v1\noid sha256:' + 'a' * 64 + '\nsize 1234\n'
        encoded = pointer.encode()
        sha = hashlib.sha1(b'blob ' + str(len(encoded)).encode() + b'\0' + encoded).hexdigest()
        plan = extraction_plan({'files': [{'path': name, 'sha': sha, 'size': len(encoded)}],
                                'pointers': [{'path': name, 'pointer': pointer}]})
        self.assertEqual(plan[name]['size'], 1234)
        self.assertEqual(plan[name]['algorithm'], 'sha256')
        self.assertEqual(plan[name]['digest'], 'a' * 64)

    def test_modified_pointer_is_rejected_before_archive_extraction(self):
        with self.assertRaisesRegex(ValueError, 'Pointer does not match'):
            extraction_plan({'files': [{'path': 'Raft/Raft_Data/resources.assets', 'sha': 'b' * 40, 'size': 5}],
                             'pointers': [{'path': 'Raft/Raft_Data/resources.assets', 'pointer': 'fake'}]})

    def test_windows_native_programs_and_parent_paths_are_rejected(self):
        for path in ['Raft/Raft.exe', 'Raft/Raft_Data/Plugins/OnlineFix64.dll', 'Raft/Raft_Data/../native.dll']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                extraction_plan({'files': [{'path': path, 'sha': 'a' * 40, 'size': 3}], 'pointers': []})
