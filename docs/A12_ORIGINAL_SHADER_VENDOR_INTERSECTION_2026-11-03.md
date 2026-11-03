# A12 RENDER-002 — authenticated original Shader-object / Unity vendor intersection

**Date:** 3 November 2026 (UTC). **Client:** A12, `raft-20261103T145700Z-12f4a8b3`. **Verdict:** bounded CPU-only original-data comparison **SUCCESS**, broader RENDER-002 and WATER-001 still OPEN; project **NOT_READY / 0 of 3** readiness reviews.

## Independent inputs and exact execution

[Workflow run 41659840282](https://github.com/alwansan/raf/actions/runs/41659840282) completed **SUCCESS** on exact source [4605ddca](https://github.com/alwansan/raf/commit/4605ddca31b21ba754b003f54ca5b2d0380d34a4) (job 125999820007): all **10/10** A12 synthetic identity/negative/privacy cases passed before resource access. The runner first checked Git LFS pointer identity, then hydrated and verified only two original W1-owned serialized resource files, totaling **227,511,628 bytes**. Reused the existing W1 two-owner cache key when available. The SHA-pinned official Unity 2021.3.45f2 built-in shader archive has **198** identities.

- `resources.assets`: 111,533,516 bytes; SHA256 `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c`.
- `sharedassets0.assets`: 115,978,112 bytes; SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
- Verified vendor archive SHA256 `5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5`.

New isolated files: [A12 source](../scripts/a12_probe_original_vendor_identity_overlap.py), [synthetic tests](../tests/test_a12_vendor_identity_overlap.py) and [CPU workflow](../.github/workflows/raft-a12-vendor-identity-overlap.yml). The source reads original Shader objects in the two owners using UnityPy, validates the selected owners **before** data inspection, and compares their serialized `m_ParsedForm.m_Name` / `m_Name` only to exact official vendor names. It publishes aggregate counts and a whole-inventory SHA only; never original names, programs, raw graphics bytes or per-object hashes.

## Verified aggregate result

| Signal | Value |
|---|---:|
| Original Shader objects in these **two** owners | **105** |
| Names usable for exact equality | **105** |
| Names absent or contradictory | **0** |
| Unique serialized names | **105** |
| Exact Unity built-in vendor name matches | **9** |
| Distinct exact vendor names matched | **9** |
| Nonvendor original Shader object names | **96** |
| Repeated original name occurrences | **0** |
| Matches supported by both parsed and top-level name simultaneously | **0** |
| Vendor matches from top-level fallback only | **0** |
| Complete Unity built-in vendor list | **198** |

The nine matches are derived from the original parsed-form field, not a second independent top-level-name comparison. Whole two-owner inventory SHA256 `8eb2144854bbd9c2bf8111c854914197f2110276ba64c7ac175d710d0e1d837b`. [Aggregate-only CI artifact 13239644796](https://github.com/alwansan/raf/actions/runs/41659840282/artifacts/13239644796) was published; no original materials or private ShaderLab text were retained.

## Relation to original native failure

[Native 41624581951](https://github.com/alwansan/raf/actions/runs/41624581951), old source `c7254f7d`, genuinely failed before Unity with `No exported built-in shader identities matched`. A11/A13 independently proved the local 107 ShaderLab file sample is **not authenticated** as that run's full 140-shader exported project. The new nine original serialized-name matches provide genuine missing evidence **upstream** of the AssetRipper ShaderLab stage: some original serialized Shader object names **are** official Unity built-in identities. However, the exact original-object→exported-shader path/GUID/name mapping at the failed run has not been validated; these 105 two-owner objects are not asserted to cover every game shader. Thus the old zero-match condition remains unresolved, not falsified or repaired.

## Boundaries and next engineering step

The controls reject exact-name aliases/case, contradictory serialized fields, duplicate original object keys, missing names and malformed inputs; owner size/SHA checks execute before UnityPy; official vendor SHA independently validates its data source. No Unity Editor, AssetRipper export, GPU, device, native build, APK/OBB/XAPK, release, new native request, original .meta/GUID/source edits or CL write were performed by A12.

**Next:** trace authenticated **same-stage complete export** object→file/.meta/GUID mapping (including any original built-in candidates) and compare to source object references without revealing private names or bypassing zero-match safety. Existing W1 program/pass recovery and A14 export investigation remain separate. Preserve full fidelity, WATER-001/RENDER-002 open and NOT_READY / 0-of-3.
