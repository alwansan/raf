#!/usr/bin/env python3
"""Reject an ancestor symlink even if the immediate output parent is real."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t2_foam_publish_aggregate import publish


class AncestorSymlinkTest(unittest.TestCase):
    def test_rejects_ancestor_alias_without_external_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            (outside / "nested").mkdir(parents=True)
            alias = root / "alias"
            try:
                alias.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("directory symlinks unavailable")
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            target = alias / "nested" / "aggregate.json"
            self.assertFalse(target.parent.is_symlink())  # Previous guard missed this.
            with self.assertRaises(ValueError):
                publish(source, target)
            self.assertFalse((outside / "nested" / "aggregate.json").exists())


if __name__ == "__main__":
    unittest.main()
