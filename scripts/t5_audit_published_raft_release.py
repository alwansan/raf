"""Check public Raft GitHub Release transport metadata without downloading assets.

This is a release-manifest consistency check ONLY. API-reported SHA256 digest
strings are declarations, not cryptographic proof of actual APK/OBB/XAPK bytes,
Android APK signature, OBB mount, successful install or saved world.
"""
import argparse
import json
from pathlib import Path
import re

_SHA = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
_TAG = re.compile(r"^android-early-test-([1-9][0-9]*)-([1-9][0-9]*)$")
_PACKAGE = "com.alwansan.raft.androidtest"
_METADATA = {
    "delivery.json", "SHA256SUMS", "INSTALL_AR.md",
    "reassemble.py", "RECORDED_LIMITATIONS.json",
}
_ASSET_LIMIT = 2_147_483_648
_PART_LIMIT = 1_073_741_824


def _obj(value, name):
    if type(value) is not dict:
        raise ValueError(name + ": expected object")
    return value


def _required_sha(value, size, name):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{" + str(size) + "}", value):
        raise ValueError("Invalid " + name)
    return value


def audit(snapshot, *, expected_run_id, expected_sha):
    data = _obj(snapshot, "snapshot")
    run = _obj(data.get("run"), "workflow run")
    release = _obj(data.get("release"), "release")
    if type(expected_run_id) is not int or expected_run_id <= 0:
        raise ValueError("Invalid expected workflow id")
    if type(run.get("id")) is not int or run["id"] != expected_run_id:
        raise ValueError("Workflow run id mismatch")
    _required_sha(expected_sha, 40, "expected SHA")
    sha = _required_sha(run.get("head_sha"), 40, "native run source SHA")
    if sha != expected_sha:
        raise ValueError("Run source SHA does not match expected immutable source")
    if (run.get("name") != "Raft full native APK OBB XAPK build and delivery"
            or run.get("status") != "completed" or run.get("conclusion") != "success"):
        raise ValueError("No completed successful original native workflow evidence")

    tag = release.get("tag_name")
    match = _TAG.fullmatch(tag) if type(tag) is str else None
    if not match or int(match[1]) != expected_run_id:
        raise ValueError("Release tag does not identify same native run")
    # The second tag component is the Actions run attempt, not APK versionCode.
    # Check it when the workflow snapshot includes that API field.
    attempt = run.get("run_attempt")
    if attempt is not None and (type(attempt) is not int or attempt < 1
                                or int(match[2]) != attempt):
        raise ValueError("Release tag does not identify same native run attempt")
    if type(release.get("prerelease")) is not bool or not release["prerelease"]:
        raise ValueError("Missing early-test prerelease identity")
    if release.get("target_commitish") != sha or release.get("source_claim") != sha:
        raise ValueError("Release tag target/body source disagrees with native run")

    claims = _obj(release.get("logical_file_claims"), "logical file claims")
    if len(claims) != 3:
        raise ValueError("Expected exact APK/OBB/XAPK logical file claims")
    apk = "Raft-Android-Test.apk"
    xapk = "Raft-Android-Test.xapk"
    obbs = [x for x in claims if type(x) is str and re.fullmatch(
        r"main\.[1-9][0-9]*\.com\.alwansan\.raft\.androidtest\.obb", x)]
    if len(obbs) != 1 or set(claims) != {apk, xapk, obbs[0]}:
        raise ValueError("Malformed or incomplete APK/OBB/XAPK logical names")
    for key, row in claims.items():
        row = _obj(row, "logical claim")
        if type(row.get("bytes")) is not int or row["bytes"] <= 0:
            raise ValueError("Invalid logical file length")
        if type(row.get("sha256")) is not str or not _HEX.fullmatch(row["sha256"]):
            raise ValueError("Invalid logical file hash declaration")

    rows = release.get("assets")
    if type(rows) is not list or len(rows) > 100:
        raise ValueError("Missing or unbounded public release asset inventory")
    assets = {}
    for row in rows:
        row = _obj(row, "asset")
        name, size, digest = row.get("name"), row.get("size"), row.get("digest")
        if type(name) is not str or not name or len(name) > 256 or (
                "/" in name or "\\" in name or name in {".", ".."}):
            raise ValueError("Invalid public asset name")
        if name in assets:
            raise ValueError("Duplicate public asset name")
        if type(size) is not int or size <= 0 or size >= _ASSET_LIMIT:
            raise ValueError("Missing or oversized release asset")
        if type(digest) is not str or not _DIGEST.fullmatch(digest):
            raise ValueError("Missing or malformed API asset digest declaration")
        assets[name] = (size, digest.removeprefix("sha256:"))

    if not _METADATA.issubset(assets):
        raise ValueError("Missing required delivery or reassembly metadata")
    transport = {}
    for name, claim in claims.items():
        direct = name in assets
        part_prefix = re.compile(r"^" + re.escape(name) + r"\.part([0-9]{3})$")
        partrows = sorted(
            (int(m[1]), aname, size)
            for aname, (size, _digest) in assets.items()
            if (m := part_prefix.fullmatch(aname)) is not None
        )
        if direct and partrows:
            raise ValueError("Ambiguous both whole and multipart transport")
        if direct:
            if assets[name][0] != claim["bytes"]:
                raise ValueError("Direct published file size mismatches logical claim")
            if assets[name][1] != claim["sha256"]:
                raise ValueError("Direct published file API digest disagrees with declared whole hash")
            transport[name] = [name]
        else:
            if not partrows:
                raise ValueError("Missing published transport for logical file")
            if [n for n, _, _ in partrows] != list(range(1, len(partrows) + 1)):
                raise ValueError("Noncontiguous or duplicate multipart indices")
            if any(size > _PART_LIMIT for _, _, size in partrows):
                raise ValueError("Published transport part exceeds 1GiB limit")
            if sum(size for _, _, size in partrows) != claim["bytes"]:
                raise ValueError("Published multipart byte totals differ from logical claim")
            transport[name] = [name for _, name, _ in partrows]
    expected_names = _METADATA | {name for partnames in transport.values() for name in partnames}
    if set(assets) != expected_names:
        raise ValueError("Unexpected extra or disguised delivery asset")
    return {
        "native_run_id": expected_run_id,
        "native_source_sha": expected_sha,
        "release_tag": tag,
        "workflow_completed_successfully": True,
        "release_target_source_consistent": True,
        "published_asset_metadata_complete": True,
        "logical_apk_obb_xapk_declared": len(claims),
        "reported_transport_assets": sum(len(x) for x in transport.values()),
        "published_auxiliary_files": len(_METADATA),
        "reported_total_transport_bytes": sum(assets[n][0] for a in transport.values() for n in a),
        "actual_download_bytes_and_sha256_verified": False,
        "actual_apk_signature_verified": False,
        "real_obb_contents_and_mount_verified": False,
        "real_xapk_reassembly_verified": False,
        "android_device_install_or_gameplay_verified": False,
    }


def _read(path):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 1_000_000:
        raise ValueError("Missing or unbounded release metadata")
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot", required=True)
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--sha", required=True)
    a = p.parse_args()
    print(json.dumps(audit(_read(a.snapshot), expected_run_id=a.id, expected_sha=a.sha), sort_keys=True))


if __name__ == "__main__":
    main()
