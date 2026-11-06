# T2 — source-original Unity external FileIdentifier GUID and reverse Foam Material evidence

Date: 2026-11-06 UTC. Agent T2, origin `chat`, issue `WATER-001`, session `20261106T1728Z-T2-chat-original-external-guid-4c81`.

## Distinct question

Earlier source-original [external Shader target census](T2_FOAM_EXTERNAL_MANIFEST_PPTR_2026-11-06.md) SHA-authenticated two previously unknown `Material.m_Shader` external typed Shader targets in one original asset. [Follow-up source-original name comparison](T2_FOAM_ORIGINAL_EXTERNAL_SHADER_NAME_RELATION_2026-11-06.md) verified **0/2 exact original Foam serialized Shader name matches**. Neither census authenticated the actual Unity external `FileIdentifier.guid` bytes or whether the target asset linked back to Foam.

This experiment reads **the original serialized external file table and target's own table** to distinguish nonzero GUID evidence, zero GUIDs, malformed GUIDs, inconsistent fileID/type values, and reciprocal original Foam-owner links. Original GUIDs, private file paths/names, raw Shader data and source binaries stay in temporary runner memory, not reports/artifacts.

## Immutable original source and tools

- Original provider: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385` (ZIP2; never modified).
- Original `Raft_Data/sharedassets0.assets`: **115978112** bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
- Original Foam Shader `PathID2420` raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1` checked in original staging.
- Same single external target as previous original experiment: **758412** bytes, exact original manifest SHA checked **privately**, without exposing target name or checksum.
- Original 366-row manifest schema and declared 7,789,295,609-byte total validated; **not** a SHA check of all 7.79GB.
- Code: `scripts/t2_original_external_guid_evidence.py`; source-free adversarial controls: `tests/test_t2_original_external_guid_evidence.py`; isolated GitHub Actions `.github/workflows/raft-t2-original-external-guid-evidence.yml`. UnityPy pinned to **1.25.4**, GitHub runner Ubuntu 24.04; 18-minute timeout, separate concurrency and bounded source staging.

## Authentic execution

[GitHub Actions 42262404131](https://github.com/alwansan/raf/actions/runs/42262404131) **SUCCESS**, code SHA `5f5ba4450209841993c8600534cdc63e097a5de9`. **11/11** independent GUID/reciprocal source-free controls and **11/11** inherited manifest controls succeeded. Original ZIP2 owner authentication, targeted SHA reconstruction, private GUID/Material graph analysis, exact-safe JSON assertions and scratch cleanup succeeded. Public count-only safe artifact `13525462480`, `t2-original-fileidentifier-guid-safe-42262404131` (621 bytes).

### Original two external Shader PPtrs

| Authenticated observation | Result |
|---|---:|
| Original two Shader PPtr rows examined | 2 |
| Unique original external fileIDs | 1 |
| Unique original target filename candidate | 1 |
| Zero 16-byte GUID rows | **2/2** |
| Nonzero GUID rows | **0/2** |
| Distinct nonzero GUIDs | **0** |
| Source file type=0 rows | **2/2** |
| Source file type=1,2,3 rows | 0 |
| Same-target GUID contradictions | 0 |

Both genuine `Material.m_Shader` references therefore use the **same single external `fileID`**, whose serialized `FileIdentifier.guid` value is the **all-zero 16-byte GUID** and whose `FileIdentifier.type` is **0**. The game source data is structurally valid in the tested scope and the target file is byte-authenticated. **Zero GUID is not proof of corruption:** compiled Unity SerializedFile references may rely on other source metadata/path resolution, which this experiment does not establish.

### Original target file

| Authenticated observation | Result |
|---|---:|
| Original target external FileIdentifier entries | 2 |
| Target Material objects | 1 |
| Target external entries naming original Foam owner | **0** |
| Target Material.m_Shader references to original Foam owner's PathID2420 via such entries | **0** |

This rules out a **direct reverse FileIdentifier/Material Shader PPtr** to this original Foam owner in the single staged target file. It does **not** prove the target is unused by water or no other source file references Foam.

## Proof boundary and next integration question

The actual original external identifier carries **no usable nonzero GUID** for these two pointers, so no independent GUID equality with the target file can be established from this field. The verified filename/manifest SHA and actual typed Shader target PathIDs remain **candidate associations**, not independently GUID-authenticated Unity runtime material binding. The earlier 0/2 Foam original Shader-name and raw equality findings remain valid and separate.

To identify a true original Foam Shader host, next inspect other source-pinned owners/scene/prefab or authored asset bundles with exact original Shader/Material PathIDs, external file identity and material properties, then trace real CB0/Spectrum/Blur usage. Preserve `.meta`/GUIDs and avoid invented aliases. Unity ShaderLab, graphics-device pixels and Android/Adreno water are **not** verified. Owner device [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) separately verified world enter/save/reopen, not water rendering. `WATER-001` stays **OPEN**, game **NOT_READY**.

No Raft game ShaderLab, shaders, scenes, Materials, .meta/GUID, APK/OBB, audio, Settings, touch or other workers' workflows were modified. No proprietary original names/GUIDs/raw data published.
