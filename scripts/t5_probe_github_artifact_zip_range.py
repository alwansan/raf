#!/usr/bin/env python3
"""T5: read-only bounded byte-range inventory for *real* owner GitHub Actions ZIPs.

Never downloads APK/OBB payloads, prints private member names or publishes a
GitHub/Azure redirect URL. This cannot verify inner-file hashes or signing.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

OWNER = "alwansan"
REPO = "raf"
SOURCE_RUN = 42058825739
SOURCE_SHA = "e9c358eda01785b65e4eb14f18723da426635628"
ARTIFACTS = (
    (13441227298, "raft-android-test-delivery", 5948243524,
     "sha256:29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6"),
    (13441766832, "raft-android-signed-output-checkpoint", 2974110506,
     "sha256:0e99e82c44af0fa21f613515ca0cb8eee2c04aa7911e9a001aabd1abdcde16bd"),
)
MAX_BYTES_PER_ARTIFACT = 4 * 1024 * 1024
MAX_RANGE_READ = 512 * 1024
MAX_MEMBERS = 40000
MAX_MANIFEST = 100_000
PACKAGE = "com.alwansan.raft.androidtest"
CONTENT_RANGE = re.compile(r"^bytes ([0-9]+)-([0-9]+)/([0-9]+)$")
ZIP_PART = re.compile(r"\\.part[0-9]{3,6}$")


class ProbeError(ValueError):
    pass


def unique_pairs(rows):
    result = {}
    for key, value in rows:
        if key in result:
            raise ProbeError("duplicate_json_key")
        result[key] = value
    return result


def _safe_json(content: bytes):
    if len(content) > MAX_MANIFEST:
        raise ProbeError("manifest_size")
    try:
        return json.loads(content.decode("utf-8"), object_pairs_hook=unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProbeError("manifest_encoding_or_json") from None


def _safe_member(name: str):
    if not name or name.startswith("/") or "\\\\" in name or ":" in name:
        raise ProbeError("unsafe_zip_member")
    segments = (name[:-1] if name.endswith("/") else name).split("/")
    if not segments or any(part in ("", ".", "..") for part in segments):
        raise ProbeError("unsafe_zip_member")
    if len(name.encode("utf-8")) > 4096:
        raise ProbeError("zip_member_name_too_long")


def _kind(name: str):
    base = name.lower()
    if ZIP_PART.search(base):
        base = ZIP_PART.sub("", base)
    if base.endswith(".apk"):
        return "apk"
    if base.endswith(".obb"):
        return "obb"
    if base.endswith(".xapk"):
        return "xapk"
    if name == "delivery.json":
        return "manifest"
    return "other"


def _sanitized_manifest(data):
    if type(data) is not dict:
        raise ProbeError("manifest_not_object")
    # Accept only source-known safe metadata fields; unknown additional payload
    # fields are ignored, never echoed to the log or returned.
    schema = data.get("schema")
    version = data.get("version_code")
    package = data.get("package")
    files = data.get("files")
    if (type(schema) is not int or schema != 1 or package != PACKAGE
            or type(version) is not str or not re.fullmatch(r"[1-9][0-9]{0,9}", version)
            or type(files) is not list or len(files) != 3):
        raise ProbeError("manifest_contract_unexpected")
    total = {"apk": 0, "obb": 0, "xapk": 0}
    parts = {"apk": 0, "obb": 0, "xapk": 0}
    for obj in files:
        if type(obj) is not dict:
            raise ProbeError("manifest_file_not_object")
        file_name = obj.get("name")
        bytes_count = obj.get("bytes")
        sha = obj.get("sha256")
        members = obj.get("parts")
        if (type(file_name) is not str or _kind(file_name) not in total
                or type(bytes_count) is not int or bytes_count <= 0
                or type(sha) is not str or not re.fullmatch("[0-9a-f]{64}", sha)
                or type(members) is not list or not 1 <= len(members) <= 200):
            raise ProbeError("manifest_logical_record_invalid")
        kind = _kind(file_name)
        if total[kind]:
            raise ProbeError("manifest_duplicate_logical_type")
        sum_bytes = 0
        for index, item in enumerate(members, 1):
            expected = file_name if len(members) == 1 else file_name + ".part" + str(index).zfill(3)
            if (type(item) is not dict or item.get("name") != expected
                    or type(item.get("bytes")) is not int or item["bytes"] <= 0
                    or type(item.get("sha256")) is not str
                    or not re.fullmatch("[0-9a-f]{64}", item["sha256"])):
                raise ProbeError("manifest_part_invalid")
            sum_bytes += item["bytes"]
        if sum_bytes != bytes_count:
            raise ProbeError("manifest_bytes_inconsistent")
        total[kind] = bytes_count
        parts[kind] = len(members)
    if any(total[k] == 0 for k in total):
        raise ProbeError("manifest_missing_logical_output")
    return {
        "schema": schema,
        "package": PACKAGE,
        "version_code": version,
        "logical_file_bytes": total,
        "logical_transport_part_counts": parts,
        "inner_file_digests_not_read_or_verified": True,
    }


class LimitedRangeIO(io.RawIOBase):
    """A seekable ZipFile-compatible reader without non-range/full-file fallback."""
    def __init__(self, length: int, fetcher, budget=MAX_BYTES_PER_ARTIFACT):
        super().__init__()
        if type(length) is not int or length <= 0:
            raise ProbeError("unknown_remote_length")
        self.length = length
        self.pos = 0
        self.fetcher = fetcher
        self.remaining = budget
        self.transferred = 0
        self.requests = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            new = offset
        elif whence == io.SEEK_CUR:
            new = self.pos + offset
        elif whence == io.SEEK_END:
            new = self.length + offset
        else:
            raise ValueError("unknown_whence")
        if type(new) is not int or new < 0 or new > self.length:
            raise ProbeError("range_seek_outside_archive")
        self.pos = new
        return self.pos

    def read(self, size=-1):
        if size is None or size < 0:
            size = self.length - self.pos
        size = min(size, self.length - self.pos)
        if size == 0:
            return b""
        if size > self.remaining:
            raise ProbeError("archive_range_read_budget_exhausted")
        blocks = []
        remaining = size
        while remaining:
            chunk_size = min(MAX_RANGE_READ, remaining)
            try:
                chunk = self.fetcher(self.pos, chunk_size)
            except ProbeError:
                raise
            except Exception:
                raise ProbeError("remote_range_request_failed") from None
            if type(chunk) is not bytes or len(chunk) != chunk_size:
                raise ProbeError("remote_range_incomplete")
            blocks.append(chunk)
            self.requests += 1
            self.transferred += len(chunk)
            self.remaining -= len(chunk)
            self.pos += len(chunk)
            remaining -= len(chunk)
        return b"".join(blocks)


def inspect_envelope(stream: LimitedRangeIO):
    try:
        with zipfile.ZipFile(stream, "r", allowZip64=True) as archive:
            members = archive.infolist()
            if not 1 <= len(members) <= MAX_MEMBERS:
                raise ProbeError("archive_member_count_out_of_bounds")
            names = set()
            counts = {k: 0 for k in ("apk", "obb", "xapk", "manifest", "other")}
            size_total = {k: 0 for k in counts}
            small_manifest = None
            for member in members:
                name = member.filename
                _safe_member(name)
                if name in names:
                    raise ProbeError("archive_duplicate_member")
                names.add(name)
                if member.flag_bits & 1:
                    raise ProbeError("archive_encrypted_member")
                mode = (member.external_attr >> 16) & 0xffff
                if member.create_system == 3 and (mode & 0o170000) == 0o120000:
                    raise ProbeError("archive_symlink_member")
                kind = _kind(name)
                if not member.is_dir():
                    counts[kind] += 1
                    size_total[kind] += member.file_size
                if kind == "manifest" and not member.is_dir():
                    if small_manifest is not None:
                        raise ProbeError("archive_duplicate_manifest")
                    if member.file_size > MAX_MANIFEST or member.compress_size > MAX_MANIFEST:
                        raise ProbeError("manifest_member_exceeds_limit")
                    small_manifest = member
            data = None
            if small_manifest is not None:
                with archive.open(small_manifest, "r") as member:
                    # A hard uncompressed cap prevents a crafted tiny ZIP entry
                    # from expanding to unbounded RAM.
                    content = member.read(MAX_MANIFEST + 1)
                    if len(content) > MAX_MANIFEST:
                        raise ProbeError("manifest_uncompressed_cap")
                data = _sanitized_manifest(_safe_json(content))
            return {
                "member_count": len(members),
                "file_type_counts": counts,
                "file_type_uncompressed_bytes": size_total,
                "delivery_manifest": data,
                "remote_range_requests": stream.requests,
                "remote_range_bytes": stream.transferred,
                "original_inner_file_hashes_verified": False,
                "apk_signature_verified": False,
                "obb_unity_guid_verified": False,
                "android_device_tested": False,
            }
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError, OSError) as exc:
        raise ProbeError("archive_zip_inventory_failed") from None


def _github_request(url, token: str, redirect=False):
    if not url.startswith("https://api.github.com/"):
        raise ProbeError("unexpected_github_api_host")
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "t5-signed-artifact-range-probe/1",
    })
    if not redirect:
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                if response.status != 200:
                    raise ProbeError("github_metadata_http_status")
                body = response.read(65537)
                if len(body) > 65536:
                    raise ProbeError("github_metadata_too_large")
                return _safe_json(body)
        except (urllib.error.URLError, OSError):
            raise ProbeError("github_metadata_request_unavailable") from None
    class RefuseRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None
    opener = urllib.request.build_opener(RefuseRedirect)
    try:
        with opener.open(req, timeout=25):
            raise ProbeError("github_archive_redirect_missing")
    except urllib.error.HTTPError as response:
        if response.code != 302:
            raise ProbeError("github_archive_redirect_unavailable") from None
        location = response.headers.get("Location", "")
        parsed = urllib.parse.urlsplit(location)
        host = (parsed.hostname or "").lower()
        trusted = host.endswith(".blob.core.windows.net") or host.endswith(".actions.githubusercontent.com")
        if parsed.scheme != "https" or not trusted or parsed.username or parsed.password:
            raise ProbeError("github_archive_untrusted_redirect")
        return location
    except (urllib.error.URLError, OSError):
        raise ProbeError("github_archive_redirect_unavailable") from None


def _http_range_fetcher(url: str, expected_size: int):
    def fetch(start: int, count: int):
        if not 0 <= start < expected_size or count <= 0 or start + count > expected_size:
            raise ProbeError("invalid_byte_range")
        req = urllib.request.Request(url, headers={
            "Range": "bytes=" + str(start) + "-" + str(start + count - 1),
            "Accept-Encoding": "identity",
            "User-Agent": "t5-signed-artifact-range-probe/1",
        })
        try:
            with urllib.request.urlopen(req, timeout=50) as response:
                if response.status != 206:
                    raise ProbeError("server_does_not_support_bounded_ranges")
                header = response.headers.get("Content-Range", "")
                match = CONTENT_RANGE.fullmatch(header)
                if (not match or tuple(int(x) for x in match.groups()) !=
                        (start, start + count - 1, expected_size)):
                    raise ProbeError("remote_range_content_mismatch")
                data = response.read(count + 1)
                if len(data) != count:
                    raise ProbeError("remote_range_length_mismatch")
                return data
        except ProbeError:
            raise
        except (urllib.error.URLError, OSError):
            raise ProbeError("remote_range_request_unavailable") from None
    return fetch


def probe_one(artifact, token):
    number, label, expected_bytes, digest = artifact
    base = "https://api.github.com/repos/" + OWNER + "/" + REPO + "/actions/artifacts/" + str(number)
    metadata = _github_request(base, token)
    if (metadata.get("id") != number or metadata.get("name") != label
            or metadata.get("size_in_bytes") != expected_bytes
            or metadata.get("digest") != digest or metadata.get("expired") is not False):
        raise ProbeError("pinned_artifact_metadata_changed")
    workflow = metadata.get("workflow_run")
    if workflow is not None and (type(workflow) is not dict or
                                 workflow.get("id") != SOURCE_RUN or
                                 workflow.get("head_sha") != SOURCE_SHA):
        raise ProbeError("original_source_run_link_mismatch")
    redirected = _github_request(base + "/zip", token, redirect=True)
    stream = LimitedRangeIO(expected_bytes, _http_range_fetcher(redirected, expected_bytes))
    result = inspect_envelope(stream)
    return {
        "artifact_id": number,
        "artifact_role": "delivery" if label == ARTIFACTS[0][1] else "signed_checkpoint",
        "source_workflow_run": SOURCE_RUN,
        "source_commit": SOURCE_SHA,
        "github_metadata_digest_recorded_not_fullstream_verified": digest,
        "github_artifact_zip_bytes": expected_bytes,
        "actual_remote_zip_central_directory_read": True,
        **result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        parser.error("Only explicitly bounded live artifact inspection is supported")
    token = os.environ.get("GITHUB_TOKEN", "")
    if len(token) < 8:
        print("T5_REMOTE_ARTIFACT_RANGE status=BLOCKED reason=token_not_available")
        raise SystemExit(2)
    try:
        for item in ARTIFACTS:
            result = probe_one(item, token)
            print("T5_REMOTE_ARTIFACT_RANGE " + json.dumps(result, sort_keys=True))
    except ProbeError as exc:
        # Only a closed vocabulary of local error labels ever reaches CI logs;
        # never print the signed blob redirect URL, private member names or
        # GitHub token from an HTTP exception.
        print("T5_REMOTE_ARTIFACT_RANGE status=BLOCKED reason=" + str(exc))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
