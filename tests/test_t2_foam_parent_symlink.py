#!/usr/bin/env python3
"""T2 Foam publisher: do not follow a symlinked destination directory."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t2_foam_publish_aggregate import publish


class ParentSymlinkTest(unittest.TestCase):
    def test_rejects_parent_symlink_without_writing_outside(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            outside = root / "outside"
            outside.mkdir()
            alias = root / "alias"
            try:
                alias.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("directory symlinks unavailable")
            source = root / "source.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                publish(source, alias / "aggregate.json")
            self.assertFalse((outside / "aggregate.json").exists())


if __name__ == "__main__":
    unittest.main()
