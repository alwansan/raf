"""Exact manifest-provider sparse checkout; never report raw Git stderr."""
from pathlib import Path
import re
import subprocess

MANIFEST = "/RAFT_FILE_MANIFEST.tsv"

class SparseFailure(ValueError):
    pass

def select_provider(root: Path, rel: str, kind: str):
    if (type(rel) is not str or not re.fullmatch(r"Raft_Data/[A-Za-z0-9_.-]+", rel)
            or rel.split("/")[-1] in (".", "..") or kind not in ("plain", "split")):
        raise SparseFailure("invalid_sparse_provider_selector")
    pattern = "/Raft/" + rel + ("/*" if kind == "split" else "")
    # 'add' has no --no-cone option. 'set' selects the exact new provider
    # and retains the manifest; the original 12 owners are already staged.
    cp = subprocess.run(["git", "-C", str(root), "sparse-checkout", "set", "--no-cone", "--", MANIFEST, pattern],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600, check=False)
    if cp.returncode:
        msg = cp.stderr.lower()
        if b"unknown option" in msg or b"usage: git sparse-checkout" in msg:
            code = "selected_dependency_sparse_checkout_cli_error"
        elif b"authentication failed" in msg or b"could not read username" in msg or b"repository not found" in msg or b"permission denied" in msg:
            code = "selected_dependency_sparse_checkout_auth_error"
        elif b"no space left" in msg:
            code = "selected_dependency_sparse_checkout_disk_error"
        elif b"could not fetch" in msg or b"unable to access" in msg or b"promisor" in msg:
            code = "selected_dependency_sparse_checkout_fetch_error"
        else:
            code = "selected_dependency_sparse_checkout_other_error"
        raise SparseFailure(code)
