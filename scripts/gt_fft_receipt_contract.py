"""FFT v2 receipt commitments. Consistency, not a signed attestation.
Original source authorization and producer identity remain external requirements.
"""
from hashlib import sha256
import json
from scripts.gt_next23b_unity_receipt import strict_json, MAX_SOURCE_BYTES, MAX_RECEIPT_BYTES, MAX_BUNDLE_BYTES

SOURCE_STATUS = "GT_FFT_UTILITIES_AUTHENTIC_SEVEN_PASS_SOURCE_COMPILED"


def require_fields(packet, expected, prefix):
    if type(packet) is not dict:
        raise ValueError(prefix + "object")
    for key, value in expected.items():
        if type(packet.get(key)) is not type(value) or packet[key] != value:
            raise ValueError(prefix + key)


def digest(data):
    return sha256(data).hexdigest()


def checked_bytes(data, limit):
    if type(data) is not bytes or not 0 < len(data) <= limit:
        raise ValueError("fft_receipt_input_bytes")


def verify_commitments(candidate, source_raw, unity_raw, bundle):
    for data, limit in ((candidate, MAX_SOURCE_BYTES), (source_raw, MAX_RECEIPT_BYTES),
                        (unity_raw, MAX_RECEIPT_BYTES), (bundle, MAX_BUNDLE_BYTES)):
        checked_bytes(data, limit)
    source, unity = strict_json(source_raw), strict_json(unity_raw)
    if type(source) is not dict or type(unity) is not dict:
        raise ValueError("fft_receipt_object")
    require_fields(unity, {
        "receiptSchemaVersion": 2, "unityVersion": "2021.3.45f2",
        "checkpoint": "compiler_results", "failureType": "",
        "candidateSha256": digest(candidate), "candidateBytes": len(candidate),
        "sourceReceiptSha256": digest(source_raw),
        "bundleSha256": digest(bundle), "bundleBytes": len(bundle),
        "passCount": 7, "registeredKeywordVariants": 1, "errors": 0,
        "androidVulkanOnly": True, "privateBundleCompiled": True,
        "originalMaterialGuidProven": False, "gamePlayerBuilt": False,
        "devicePixelsProven": False,
    }, "fft_unity_receipt:")
    if unity.get("compilerControl") not in ("dxc", "hlslcc"):
        raise ValueError("fft_unity_receipt:compilerControl")
    return source, unity, {
        "receipt_schema_version": 2, "candidate_sha256": digest(candidate),
        "candidate_bytes": len(candidate), "source_receipt_sha256": digest(source_raw),
        "unity_receipt_sha256": digest(unity_raw), "bundle_sha256": digest(bundle),
        "bundle_bytes": len(bundle), "unity_receipt_byte_commitments_verified": True,
        "cryptographic_attestation_verified": False,
    }


def verify_original_commitments(candidate, source_raw, unity_raw, bundle):
    source, unity, proof = verify_commitments(candidate, source_raw, unity_raw, bundle)
    require_fields(source, {
        "status": SOURCE_STATUS, "candidate_shader_sha256": digest(candidate),
        "candidate_shader_bytes": len(candidate),
        "compiler_control": unity["compilerControl"],
        "original_SHA_owned_serialized_files": 2, "original_passes": 7,
        "original_normal_passes": 7, "original_empty_keyword_routes_verified": True,
        "original_keyword_pairs": 7, "original_orphan_stages": 0,
        "original_distinct_D3D11_programs": 12,
        "original_stages_roundtrip_validated": 12, "named_ShaderLab_entrypoints_compiled": 14,
        "Unity_import_proven": False, "Android_device_pixels_proven": False,
        "APK_OBB_XAPK_created": False, "source_bytes_or_IDs_published": False,
    }, "fft_source_receipt:")
    return dict(proof, original_source_receipt_contract_verified=True)


def require_same_decoded_receipt(actual, claimed):
    # Canonical JSON comparison preserves distinctions such as true vs 1.
    if json.dumps(actual, sort_keys=True, separators=(",", ":")) != json.dumps(
            claimed, sort_keys=True, separators=(",", ":")):
        raise ValueError("fft_decoded_receipt_does_not_match_actual_bundle")
