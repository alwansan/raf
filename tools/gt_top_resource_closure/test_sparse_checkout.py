from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.gt_top_resource_closure import sparse_checkout as s

class ExactSparseCheckoutTests(unittest.TestCase):
    def test_real_git_plain_and_split_provider_replace_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
            git("init", "-q")
            paths = ["RAFT_FILE_MANIFEST.tsv", "Raft/Raft_Data/old.assets",
                     "Raft/Raft_Data/mesh.resS/part-00000", "Raft/Raft_Data/mesh.resS/part-00001",
                     "Raft/Raft_Data/other.resS/part-00000", "Raft/Raft_Data/plain.assets"]
            for path in paths:
                f = root / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(path)
            git("add", ".")
            git("-c", "user.name=GT Test", "-c", "user.email=gt@example.invalid", "commit", "-qm", "authored")
            head = git("rev-parse", "HEAD").stdout
            git("sparse-checkout", "set", "--no-cone", "--", s.MANIFEST, "/Raft/Raft_Data/old.assets")
            s.select_provider(root, "Raft_Data/mesh.resS", "split")
            self.assertTrue(all((root / p).is_file() for p in (paths[0], paths[2], paths[3])))
            self.assertTrue(all(not (root / p).exists() for p in (paths[1], paths[4], paths[5])))
            s.select_provider(root, "Raft_Data/plain.assets", "plain")
            self.assertTrue(all((root / p).is_file() for p in (paths[0], paths[5])))
            self.assertTrue(all(not (root / p).exists() for p in paths[1:5]))
            self.assertEqual(git("rev-parse", "HEAD").stdout, head)
            self.assertEqual(git("status", "--porcelain").stdout, b"")

    def test_selector_rejects_wildcards_and_traversal(self):
        for rel, kind in (("Raft_Data/../x", "plain"), ("Raft_Data/*", "split"),
                          ("Raft_Data/..", "plain"), ("Raft_Data/x", "unknown")):
            with self.subTest(rel=rel, kind=kind), patch.object(s.subprocess, "run") as run:
                with self.assertRaisesRegex(s.SparseFailure, "invalid_sparse_provider_selector"):
                    s.select_provider(Path("."), rel, kind)
                run.assert_not_called()

    def test_stderr_is_classified_not_disclosed(self):
        cases = ((b"error: unknown option private-path", "cli"),
                 (b"fatal: Authentication failed private-path", "auth"),
                 (b"No space left on device private-path", "disk"),
                 (b"could not fetch private-path from promisor remote", "fetch"),
                 (b"private-path", "other"))
        for stderr, category in cases:
            with self.subTest(category=category), patch.object(s.subprocess, "run", return_value=subprocess.CompletedProcess([], 129, b"", stderr)):
                with self.assertRaisesRegex(s.SparseFailure, "^selected_dependency_sparse_checkout_" + category + "_error$"):
                    s.select_provider(Path("."), "Raft_Data/plain.assets", "plain")

if __name__ == "__main__":
    unittest.main()
