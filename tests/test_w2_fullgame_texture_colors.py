"""W2 fail-closed tests for the full-game per-owner texture color-space probe.

Synthetic (no original payload): identity kinds (LFS pointer vs tracked
regular blob vs unverified-local), unsafe owner names, engine-enum bounds,
and aggregate-only output all fail closed.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_fullgame_texture_colors import (
    SCHEMA_VERSION,
    VALID_TEXTURE_COLOR_SPACES,
    aggregate_owner,
    probe,
    validate_owner_names,
)


class Obj:
    def __init__(self, type_name, tree):
        self.type = type("T", (), {"name": type_name})()
        self._tree = tree

    def read_typetree(self):
        return self._tree


def _fake_env(objects):
    return type("Env", (), {"objects": objects})()


@contextlib.contextmanager
def fake_unitypy(env):
    fake = types.ModuleType("UnityPy")
    fake.load = lambda _path: env
    saved = sys.modules.get("UnityPy")
    sys.modules["UnityPy"] = fake
    try:
        yield
    finally:
        if saved is None:
            sys.modules.pop("UnityPy", None)
        else:
            sys.modules["UnityPy"] = saved


def _sample_env(textures=2):
    return _fake_env(
        [
            Obj("Texture2D", {"m_ColorSpace": 1, "m_TextureFormat": 12, "m_Width": 16, "m_Height": 16}),
            Obj("Texture2D", {"m_ColorSpace": 0, "m_TextureFormat": 12, "m_Width": 16, "m_Height": 16}),
        ][:textures]
    )


def _make_real_repo(root: Path, rel: str, committed: bytes, worktree: bytes) -> Path:
    """Create a real git repo committing ``committed`` at ``rel``, then set the
    worktree copy to ``worktree`` (simulating an LFS-hydrated worktree)."""
    import subprocess
    repo_dir = Path(root) / "repo"
    repo_dir.mkdir()
    blob_path = repo_dir / rel
    blob_path.parent.mkdir(parents=True, exist_ok=True)
    blob_path.write_bytes(committed)
    subprocess.run(["git", "-C", str(repo_dir), "init", "-q", "-b", "main"], check=True)
    subprocess.run(["git", "-C", str(repo_dir), "config", "user.email", "t@example"], check=True)
    subprocess.run(["git", "-C", str(repo_dir), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(repo_dir), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo_dir), "commit", "-q", "-m", "init"], check=True)
    blob_path.write_bytes(worktree)
    return repo_dir


class ContractTests(unittest.TestCase):
    def test_schema_and_enum(self):
        self.assertEqual(SCHEMA_VERSION, 1)
        self.assertEqual(VALID_TEXTURE_COLOR_SPACES, {0: "Gamma", 1: "Linear"})

    def test_unsafe_owner_name_rejected(self):
        for bad in ("../a.assets", "sub/a.assets", "a\\b.assets", "./a"):
            with self.assertRaises(ValueError):
                validate_owner_names([bad])
        self.assertEqual(validate_owner_names(["level0"]), ["level0"])

    def test_aggregate_owner_counts_and_splits(self):
        with tempfile.TemporaryDirectory() as td, fake_unitypy(_sample_env()):
            result = aggregate_owner(Path(td) / "x.assets")
        self.assertEqual(result["texture_count"], 2)
        self.assertEqual(result["colorspace_split"], {"Gamma": 1, "Linear": 1})
        self.assertEqual(result["distinct_formats"], 1)
        blob = json.dumps(result)
        for forbidden in ("m_Name", "m_PathID", "m_Shader", "m_ValidKeywords"):
            self.assertNotIn(forbidden, blob)

    def test_out_of_enum_colorspace_hard_fails(self):
        env = _fake_env([Obj("Texture2D", {"m_ColorSpace": 7, "m_TextureFormat": 1, "m_Width": 4, "m_Height": 4})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "x.assets")

    def test_non_int_format_hard_fails(self):
        env = _fake_env([Obj("Texture2D", {"m_ColorSpace": 1, "m_TextureFormat": "BC7", "m_Width": 4, "m_Height": 4})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "x.assets")

    def test_probe_refuses_unverified_local_without_repo(self):
        with tempfile.TemporaryDirectory() as td:
            owner = Path(td) / "x.assets"
            owner.write_bytes(b"")
            with fake_unitypy(_fake_env([])):
                result = probe([owner], None, "Raft/Raft_Data")
        self.assertEqual(result["owner_manifest"]["x.assets"]["identity_kind"], "unverified-local")

    def test_probe_mismatched_lfs_pointer_hard_fails(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            src.mkdir(parents=True)
            owner = src / "small.assets"
            owner.write_bytes(b"data")
            pointer = "version https://git-lfs\noid sha256:" + "0" * 64 + "\n"
            repo_dir = _make_real_repo(
                td,
                "Raft/Raft_Data/small.assets",
                pointer.encode(),
                pointer.encode(),
            )
            with fake_unitypy(_sample_env()):
                with self.assertRaises(ValueError):
                    probe([owner], repo_dir, "Raft/Raft_Data")

    def test_probe_lfs_pointer_match_passes_identity_even_hydrated(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            src.mkdir(parents=True)
            owner = src / "small.assets"
            owner.write_bytes(b"payload")
            import hashlib
            digest = hashlib.sha256(b"payload").hexdigest()
            pointer = f"version https://git-lfs\noid sha256:{digest}\n"
            repo_dir = _make_real_repo(
                td,
                "Raft/Raft_Data/small.assets",
                pointer.encode(),
                b"payload",
            )
            with fake_unitypy(_sample_env()):
                result = probe([owner], repo_dir, "Raft/Raft_Data")
        self.assertEqual(result["owner_manifest"]["small.assets"]["identity_kind"], "lfs-pointer-oid")

    def test_probe_regular_tracked_blob_match_and_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            src.mkdir(parents=True)
            owner = src / "small.assets"
            owner.write_bytes(b"payload")
            repo_dir = _make_real_repo(
                td,
                "Raft/Raft_Data/small.assets",
                b"payload",
                b"payload",
            )
            with fake_unitypy(_sample_env()):
                result = probe([owner], repo_dir, "Raft/Raft_Data")
            self.assertEqual(result["owner_manifest"]["small.assets"]["identity_kind"], "tracked-regular-blob")
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            src.mkdir(parents=True)
            owner = src / "small.assets"
            owner.write_bytes(b"different")
            repo_dir = _make_real_repo(
                td,
                "Raft/Raft_Data/small.assets",
                b"payload",
                b"payload",
            )
            with fake_unitypy(_sample_env()):
                with self.assertRaises(ValueError):
                    probe([owner], repo_dir, "Raft/Raft_Data")


if __name__ == "__main__":
    unittest.main()
