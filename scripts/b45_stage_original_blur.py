"""Stage exact private original Blur candidate after two-pass CPU Vulkan proof.

All original text/program bytes stay in an isolated runner scratch folder.
Only hashes, counts and safe aggregate comparisons are emitted as JSON. Never
publish the staged shader in a GitHub artifact or git commit.
"""
import argparse
import json
import os
from pathlib import Path
import tempfile

from scripts.b45_install_original_blur import CANDIDATE_BYTES, CANDIDATE_SHA256, check_safe_ancestors
from scripts.w5_blur_recovery import recover


def stage(root, repo, runner, candidate, report_path):
    repo = check_safe_ancestors(repo)
    candidate, report_path = check_safe_ancestors(candidate), check_safe_ancestors(report_path)
    if candidate.is_relative_to(repo) or report_path.is_relative_to(repo):
        raise ValueError("Private original-derived source and report must stay outside checkout")
    if candidate.exists() or candidate.is_symlink() or report_path.exists():
        raise ValueError("Refusing to overwrite private or aggregate output")
    if not candidate.parent.is_dir() or not report_path.parent.is_dir():
        raise ValueError("Private scratch directory missing")
    with tempfile.TemporaryDirectory(prefix="b45-private-authentic-", dir=candidate.parent) as folder:
        private = Path(folder)
        result = recover(root, repo, runner, private, {})
        body = private / "candidate.shader"
        if not body.is_file() or body.is_symlink():
            raise ValueError("Original two-pass privately constructed source missing")
        import hashlib
        source = body.read_bytes()
        if (result.get("private_shaderlab_constructed") is not True or
                result.get("shaderlab_passes") != 2 or
                result.get("shaderlab_bytes") != CANDIDATE_BYTES or
                result.get("shaderlab_sha256") != CANDIDATE_SHA256 or
                len(source) != CANDIDATE_BYTES or
                hashlib.sha256(source).hexdigest() != CANDIDATE_SHA256 or
                not all(all(p["within_tolerance"] for p in row["positive"]) and
                        all(row["negative"].values()) for row in result["raster"])):
            raise ValueError("Private source fingerprint or original raster proof changed")
        with candidate.open("xb") as stream:
            stream.write(source)
            stream.flush()
            os.fsync(stream.fileno())
        if candidate.read_bytes() != source:
            candidate.unlink(missing_ok=True)
            raise ValueError("Private staged candidate write mismatch")
        del source
    result.update(private_shader_staged=True, private_shader_sha256=CANDIDATE_SHA256,
                  private_shader_bytes=CANDIDATE_BYTES, private_shader_published=False,
                  original_exported_guid_modified=False, game_source_modified=False,
                  unity_compiled=False, phone_render_verified=False)
    report_path.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--runner", required=True, type=Path)
    parser.add_argument("--private-shader", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    a = parser.parse_args()
    try:
        result = stage(a.source, a.repo, a.runner, a.private_shader, a.out)
        print("RAFT_B45_STAGED_BLUR " + json.dumps(result, sort_keys=True))
    except BaseException as exc:
        # Generic error class only; original source paths or names are never logged.
        safe = {"status": "blocked", "failure_type": type(exc).__name__,
                "private_shader_published": False, "original_guid_modified": False}
        a.out.write_text(json.dumps(safe, sort_keys=True) + "\n", encoding="utf-8")
        print("RAFT_B45_STAGED_BLUR " + json.dumps(safe, sort_keys=True))
        raise SystemExit(1)
