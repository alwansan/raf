"""Verify real downloaded *small* Raft Release metadata bytes against GitHub API.

Never download or inspect actual proprietary APK, OBB, XAPK or multipart payloads.
Verifying delivery.json and SHA256SUMS bytes authenticates their API-declared
metadata, NOT the game-part hashes they merely list or the APK signature.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.t5_audit_published_raft_release import audit as audit_public_metadata

TAG = "android-early-test-41812889049-1"
RUN_ID = 41812889049
SOURCE_SHA = "d181ee7152580f49ee0b41dfd05fa2bfdacfafe5"
PACKAGE = "com.alwansan.raft.androidtest"
_HEX = re.compile(r"^[a-f0-9]{64}$")
_PART = re.compile(r"^[A-Za-z0-9_.-]+$")
_ROW = re.compile(r"^([a-f0-9]{64})  ([A-Za-z0-9_.-]+)$")


def _read_small(path, *, max_bytes):
    if not isinstance(path, Path) or not path.is_file() or path.is_symlink():
        raise ValueError("Missing or unsafe small published metadata")
    size = path.stat().st_size
    if not 0 < size <= max_bytes:
        raise ValueError("Small published metadata exceeds strict size bound")
    return path.read_bytes()


def _object(obj, what):
    if type(obj) is not dict:
        raise ValueError(what + " must be a JSON object")
    return obj


def _whole_hash(value, name):
    if type(value) is not str or not _HEX.fullmatch(value):
        raise ValueError("Invalid " + name + " digest")
    return value


def _live_assets(snapshot, live):
    baseline = _object(snapshot.get("release"), "baseline Release")
    public = _object(live, "current GitHub Release")
    for field in ("tag_name", "target_commitish", "prerelease"):
        if public.get(field) != baseline.get(field):
            raise ValueError("Current GitHub Release identity drift: " + field)
    def index(rows):
        if type(rows) is not list or not 1 <= len(rows) <= 100:
            raise ValueError("Invalid live/baseline Release asset inventory")
        found = {}
        for a in rows:
            _object(a, "Release asset")
            name, size, digest = a.get("name"), a.get("size"), a.get("digest")
            if (type(name) is not str or not _PART.fullmatch(name)
                    or name in found or type(size) is not int or size <= 0
                    or size >= 2_147_483_648 or type(digest) is not str
                    or not digest.startswith("sha256:")):
                raise ValueError("Invalid or duplicate Release asset record")
            _whole_hash(digest.removeprefix("sha256:"), "Release asset")
            found[name] = (size, digest.removeprefix("sha256:"))
        return found
    expected, actual = index(baseline.get("assets")), index(public.get("assets"))
    if actual != expected:
        raise ValueError("Current GitHub Release asset size/digest declarations drifted")
    return actual


def verify(snapshot, live_release, delivery_bytes, sums_bytes):
    baseline = _object(snapshot, "frozen provenance")
    identity = audit_public_metadata(
        baseline, expected_run_id=RUN_ID, expected_sha=SOURCE_SHA
    )
    if identity["release_tag"] != TAG:
        raise ValueError("Unrecognized verified Raft Release")
    assets = _live_assets(baseline, live_release)
    for name, content in (("delivery.json", delivery_bytes), ("SHA256SUMS", sums_bytes)):
        if type(content) is not bytes or len(content) != assets[name][0]:
            raise ValueError("Downloaded metadata length differs from GitHub API")
        if hashlib.sha256(content).hexdigest() != assets[name][1]:
            raise ValueError("Downloaded metadata SHA256 differs from GitHub API")
    try:
        meta = _object(json.loads(delivery_bytes.decode("utf-8")), "delivery.json")
        sums = sums_bytes.decode("ascii")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed downloaded release metadata") from exc
    if (type(meta.get("schema")) is not int or meta["schema"] != 1
            or meta.get("package") != PACKAGE or meta.get("version_code") != "86"
            or meta.get("companion_required") is not True
            or meta.get("transport_only_parts") is not True
            or meta.get("device_install_verified") is not False):
        raise ValueError("Delivery contract disagrees with APK86 native source")
    rows = meta.get("files")
    if type(rows) is not list or len(rows) != 3:
        raise ValueError("Delivery must retain exactly three logical files")
    claims = baseline["release"]["logical_file_claims"]
    seen = set()
    transport = []
    total = 0
    for row in rows:
        _object(row, "logical delivery file")
        name, count, sha = row.get("name"), row.get("bytes"), row.get("sha256")
        if (type(name) is not str or name not in claims or name in seen
                or type(count) is not int or count < 1):
            raise ValueError("Incorrect or duplicate logical delivery file")
        _whole_hash(sha, "logical whole")
        if (count, sha) != (claims[name]["bytes"], claims[name]["sha256"]):
            raise ValueError("Delivery logical size/SHA256 disagrees with published claim")
        seen.add(name)
        parts = row.get("parts")
        if type(parts) is not list or not 1 <= len(parts) <= 20:
            raise ValueError("Invalid logical file part list")
        part_sum = 0
        for i, part in enumerate(parts, 1):
            _object(part, "transport part")
            part_name, part_size, part_sha = part.get("name"), part.get("bytes"), part.get("sha256")
            expected_name = name if len(parts) == 1 else name + ".part" + str(i).zfill(3)
            if (part_name != expected_name or part_name not in assets
                    or type(part_size) is not int or part_size <= 0
                    or part_name in {n for n, _ in transport}):
                raise ValueError("Transport part absent, out of order or duplicated")
            _whole_hash(part_sha, "transport part")
            if (part_size, part_sha) != assets[part_name]:
                raise ValueError("Actual Release asset metadata differs from manifest transport part")
            part_sum += part_size
            transport.append((part_name, part_sha))
        if part_sum != count:
            raise ValueError("Transport byte sizes do not match logical whole")
        if len(parts) == 1 and parts[0]["sha256"] != sha:
            raise ValueError("Direct logical file hash disagrees with transport hash")
        total += count
    if seen != set(claims) or len(transport) != 7:
        raise ValueError("Incomplete APK/OBB/XAPK part manifest")
    if not sums.endswith("\n"):
        raise ValueError("SHA256SUMS must be newline terminated")
    parsed = []
    for line in sums.splitlines():
        match = _ROW.fullmatch(line)
        if match is None:
            raise ValueError("Malformed SHA256SUMS line")
        parsed.append((match[2], match[1]))
    if parsed != transport:
        raise ValueError("SHA256SUMS contents/order disagree with authenticated delivery manifest")
    return {
        "release_tag": TAG,
        "native_source_sha": SOURCE_SHA,
        "small_published_metadata_files_verified_by_actual_bytes": 2,
        "published_small_metadata_sha256_verified": True,
        "published_transport_part_records_bound_to_manifest": len(transport),
        "logical_file_declared_records_consistent": len(seen),
        "logical_transport_bytes_declared": total,
        "actual_game_part_bytes_sha256_verified": False,
        "apk_signature_verified": False,
        "obb_mounted_on_device": False,
        "xapk_reassembled_and_installed": False,
        "device_world_save_reopen_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--current-release", type=Path, required=True)
    parser.add_argument("--delivery", type=Path, required=True)
    parser.add_argument("--sums", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads(_read_small(args.snapshot, max_bytes=100_000).decode("utf-8"))
    current = json.loads(_read_small(args.current_release, max_bytes=200_000).decode("utf-8"))
    result = verify(
        baseline, current,
        _read_small(args.delivery, max_bytes=12_000),
        _read_small(args.sums, max_bytes=12_000),
    )
    print("T5_VERIFIED_SMALL_RELEASE_METADATA " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
