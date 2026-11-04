"""B09: source-only guard for the *authenticated* seven-pass Spectrum graph.

These constants come from W2's ZIP2 original stage topology and B17's
independent original resource-descriptor proof (CI 41920232173). This does
not reconstruct any ShaderLab, author a shader, or establish GPU pixels.
Unknown or changed source structure fails closed rather than padding passes.
"""
import hashlib
import json

TARGET = "UltimateWater/Spectrum/Water Spectrum"
OWNER = "sharedassets0.assets"
PATH_ID = 2432
PASSES = 7
SUBSHADERS = 1
KEYWORD_NAMES = 5
BLOB_SEQUENCES = {
    "progVertex": (1, 2, 1, 2, 1, 2, 1, 2, 14, 15, 1, 2, 1, 2),
    "progFragment": (5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19, 20, 21),
}
ORIGINAL_DESCRIPTORS = {
    "vertex_rows": 0,
    "fragment_rows": 13,
    "observed_table_fields": 42,
}


def _strict_int(value):
    return type(value) is int and value >= 0


def attest_spectrum(tree: dict, topology: dict, descriptors: dict) -> dict:
    """Validate original SHA-authenticated object metadata without revealing it.

    The caller *must* independently SHA-verify its ZIP2 owner and select the
    single original PathID before invoking this topology-level guard.
    """
    if not isinstance(tree, dict):
        raise ValueError("Original Spectrum parsed object missing")
    parsed = tree.get("m_ParsedForm")
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original Spectrum Shader identity changed")
    subshaders = parsed.get("m_SubShaders")
    if not isinstance(subshaders, list) or len(subshaders) != SUBSHADERS:
        raise ValueError("Original Spectrum subshader count changed")
    passes = subshaders[0].get("m_Passes") if isinstance(subshaders[0], dict) else None
    if not isinstance(passes, list) or len(passes) != PASSES or not all(isinstance(p, dict) for p in passes):
        raise ValueError("Original Spectrum seven-pass topology changed")
    keywords = parsed.get("m_KeywordNames")
    if not isinstance(keywords, list) or len(keywords) != KEYWORD_NAMES:
        raise ValueError("Original Spectrum keyword-table shape changed")

    if (not isinstance(topology, dict) or topology.get("gate") != "Spectrum-graph" or
            topology.get("subshaderCount") != SUBSHADERS or
            topology.get("passCount") != PASSES or
            topology.get("keywordNameCount") != KEYWORD_NAMES):
        raise ValueError("W2 authenticated Spectrum stage graph is unavailable")
    stages = topology.get("stages")
    if not isinstance(stages, dict) or set(stages) != set(BLOB_SEQUENCES):
        raise ValueError("Spectrum stage kinds changed")
    for stage_name, exact_sequence in BLOB_SEQUENCES.items():
        per_pass = stages[stage_name]
        if not isinstance(per_pass, list) or len(per_pass) != PASSES:
            raise ValueError("Spectrum per-pass stage count changed")
        observed_blob_sequence = []
        for index, record in enumerate(per_pass):
            if not isinstance(record, dict) or record.get("passIndex") != index:
                raise ValueError("Spectrum pass order changed")
            variants = record.get("variants")
            if not isinstance(variants, list) or len(variants) != 2:
                raise ValueError("Spectrum original stage variants changed")
            if [v.get("keywordIndices") for v in variants if isinstance(v, dict)] != [[], [4]]:
                raise ValueError("Spectrum original stage keyword selectors changed")
            for variant in variants:
                if not isinstance(variant, dict) or not _strict_int(variant.get("blobIndex")):
                    raise ValueError("Spectrum invalid original program index")
                observed_blob_sequence.append(variant["blobIndex"])
        if tuple(observed_blob_sequence) != exact_sequence:
            raise ValueError("Spectrum original program-blob order changed")

    if (not isinstance(descriptors, dict) or descriptors.get("original_pass_count") != PASSES or
            descriptors.get("stage_descriptor_table_counts") != ORIGINAL_DESCRIPTORS or
            descriptors.get("original_stage_resource_tables_observed") is not True):
        raise ValueError("B17 authenticated Spectrum resource topology changed")
    per_pass_descriptors = descriptors.get("per_pass_stage_numeric_contract")
    if not isinstance(per_pass_descriptors, list) or len(per_pass_descriptors) != PASSES:
        raise ValueError("Spectrum stage descriptor count changed")
    safe_commitment = hashlib.sha256(
        json.dumps(per_pass_descriptors, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return {
        "original_owner": OWNER,
        "original_path_id": PATH_ID,
        "authenticated_original_passes": PASSES,
        "authenticated_variant_stage_programs": sum(len(x["variants"]) for y in stages.values() for x in y),
        "numeric_descriptor_sha256": safe_commitment,
        "shaderlab_restored": False,
        "unity_or_device_verified": False,
    }
