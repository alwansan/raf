"""NEXT23b receipt byte consistency, not a signed attestation or render proof.

Inspect the same immutable byte snapshot that was fingerprinted. The caller
must still authenticate its producer and source and run the decoded route gate.
No original assets, Unity runtime, or network access is required by this module.
"""
from hashlib import sha256
import json
import stat

MAX_RECEIPT_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 16 * 1024 * 1024
MAX_SOURCE_BYTES = 128 * 1024 * 1024
MAX_BUNDLE_BYTES = 512 * 1024 * 1024


def read_snapshot(path, limit):
    """Bound private regular-file reads, rejecting empty or unstable sizes."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("next23b_receipt_input_not_regular_file")
    with path.open("rb") as stream:
        import os
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit:
            raise ValueError("next23b_receipt_input_size_invalid")
        data = stream.read(info.st_size + 1)
        if len(data) != info.st_size:
            raise ValueError("next23b_receipt_input_size_changed")
    return data


def strict_json(data):
    """Reject duplicate object keys rather than accept parser-dependent values."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("next23b_receipt_duplicate_json_key")
            result[key] = value
        return result

    def invalid_constant(_):
        raise ValueError("next23b_receipt_nonfinite_json")

    return json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=invalid_constant)


def verify_unity_receipt(receipt, shader_bytes, route_bytes, source_bytes, bundle_bytes):
    """Validate final editor receipt and exact four byte commitments.

    sourceManifestSha256 is the commitment carried by the engine manifest,
    not evidence that Unity independently read or authenticated the source.
    The producer can still fabricate an unsigned receipt; this contract checks
    consistency, not execution provenance.
    """
    expected = {
        "receiptSchemaVersion": 2,
        "unityVersion": "2021.3.45f2",
        "checkpoint": "verified",
        "failureType": "",
        "passCount": 4,
        "registeredRoutes": 1156,
        "errors": 0,
        "androidVulkanOnly": True,
        "privateBundleCompiled": True,
    }
    if type(receipt) is not dict or any(
        type(receipt.get(k)) is not type(v) or receipt[k] != v
        for k, v in expected.items()
    ):
        raise ValueError("next23b_unity_final_receipt_required")
    for data, limit in ((shader_bytes, MAX_SOURCE_BYTES),
                        (route_bytes, MAX_MANIFEST_BYTES),
                        (source_bytes, MAX_SOURCE_BYTES),
                        (bundle_bytes, MAX_BUNDLE_BYTES)):
        if type(data) is not bytes or not 0 < len(data) <= limit:
            raise ValueError("next23b_receipt_input_bytes_invalid")
    for field, data in (("candidateSha256", shader_bytes),
                        ("engineRouteManifestSha256", route_bytes),
                        ("sourceManifestSha256", source_bytes),
                        ("bundleSha256", bundle_bytes)):
        if receipt.get(field) != sha256(data).hexdigest():
            raise ValueError("next23b_unity_receipt_" + field + "_mismatch")
    if type(receipt.get("bundleBytes")) is not int or receipt["bundleBytes"] != len(bundle_bytes):
        raise ValueError("next23b_unity_receipt_bundle_size_mismatch")
    return {"unity_receipt_byte_commitments_verified": True,
            "unity_receipt_bundle_bytes": len(bundle_bytes),
            "unity_receipt_cryptographic_attestation_verified": False}
