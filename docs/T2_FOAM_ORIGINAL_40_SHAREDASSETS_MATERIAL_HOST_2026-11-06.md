# T2 — immutable ZIP2 original 40-sharedassets Foam material host census

Date: 2026-11-06 UTC. Agent T2; `origin=chat`, session `20261106T1743Z-T2-chat-trial-vote-foam-host-83a2`, issue `WATER-001`.

## Goal and trial-build policy

Per [trial build policy](../prompt/coordination/T_TEAM/TRIAL_BUILD_POLICY_AR.md), T2 currently votes **«لا يحتاج»** in round `trial-20261106-r1`: the original Shader/Material graph remains source diagnostic; no substantial integrated actual Android Spectrum/Foam/Blur ShaderLab/CB0 fix is ready for a new phone test. T2 edits its own voting row only; no native APK/OBB/XAPK request or T5's round state changed.

Earlier source-original [CI42262404131](https://github.com/alwansan/raf/actions/runs/42262404131) proved two unknown external typed Shader Material references from one original owner use a single type0 FileIdentifier with zero 16-byte GUID and do **not** match original Foam Shader exact name. Original actual Foam-host Material identities stayed unknown.

This experiment asks a distinct, broader question: **Does any original `Material.m_Shader` in all 40 original `Raft_Data/sharedassets[0-9]+.assets` files directly reference original Foam Shader at `sharedassets0:PathID2420`?** Unlike arbitrary foreign same-number PathIDs, correct local and external owner resolution is mandatory. External basename matching is only a candidate until independent GUID/Unity runtime mapping.

## Immutable provider, tools, privacy

- Read-only ZIP2 provider SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- Original `RAFT_FILE_MANIFEST.tsv` parsed and all 366 rows/total declarations validated; the **40** exact original sharedassets files selected by stable path pattern are **474,065,455 bytes**, including 2 split and 38 plain.
- Every staged sharedassets file independently verified against manifest SHA256 after reconstruction. Original Foam owner's `sharedassets0.assets` 115978112 bytes matches public independently pinned SHA `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; original Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1` checked again.
- UnityPy **1.25.4** on Ubuntu24.04, Python source `scripts/t2_original_foam_material_host_scan.py`, **18 source-free controls** `tests/test_t2_original_foam_material_host_scan.py`, isolated 24min GH Actions `.github/workflows/raft-t2-original-foam-material-host-scan.yml`.
- No private material names, original private GUIDs, raw asset data, other original file paths, Shader bytes or scripts uploaded; original source checkout/staged 474MB deleted before artifact publishing.

## Actual original-data outcome

[Actions run **42264851712**](https://github.com/alwansan/raf/actions/runs/42264851712) **SUCCESS** on source commit `980d8a9b0b3c04d3eb8136954e7c106675654a32`. **18/18** adversarial synthetic controls plus authentic full original-source SHA stage and result assertion passed. Final safe aggregate artifact ID **13526981272**, name `t2-original-40-sharedassets-foam-host-safe-42264851712` (554 bytes).

| Verified original-data category | Result |
|---|---:|
| Original sharedassets SHA-authenticated file count | **40/40** |
| Original sharedassets SHA-authenticated content bytes | **474,065,455** |
| Source-authentic original `Material` objects scanned | **1,392** |
| `Material.m_Shader` pointers parsed | **1,392/1,392** |
| Unparsed original Material Shader pointers | **0** |
| Malformed external Shader FileIDs | **0** |
| Serialized external FileIdentifier entries naming original Foam owner, across source owners | **39** |
| Original Material external references to same Foam owner but **other Shader PathIDs** | **885** |
| Same-owner `Material.m_Shader=(fileID0,PathID2420)` actual original Foam refs | **0** |
| Foreign-owner local `PathID2420` incorrectly masquerading as original Foam | **0** |
| Other-owner external basename + original Foam `PathID2420` candidate refs | **0** |
| Original owners with at least one direct Foam Shader Material PPtr candidate | **0** |

### What this proves—and does not

The 40 original files contain **zero directly matching Material Shader PPtrs** to source-original Foam Shader `PathID2420`, although other shaders in its source owner have hundreds of actual Material pointers and the parser covered all 1,392 original Material objects in this source class. This is **not** a source omission from failed material deserialization or failed SHA reconstruction.

The original Foam Shader still demonstrably exists as a SHA-authenticated Shader object, and source-original Foam compiled programs/texture and CB numeric ABI were separately verified in prior B20/T2 experiments. A Material PPtr need not be the only way a water shader is bound: source `MonoBehaviour`, `Shader.Find`, script-assigned runtime materials, prefabs/scenes or other bundled resources may provide identity. **We have not proven the original Foam Shader is never used or that the original game is corrupt**. The 39 external table entries are not 39 material references; the independently counted 885 Material references target different PathIDs.

It is now inappropriate to invent an original Material/GUID based on `sharedassets0`, `PathID2420`, a zero GUID or a shader name alias. Next original-data work should inspect serialized `MonoBehaviour`/water component links, prefabs/level scenes/asset bundles or game code's runtime material/Shader assignments for authenticated references, then connect real ShaderLab/CB0 and compile/render test on Unity and Adreno. Maintain `WATER-001` **OPEN**, full project **NOT_READY**. Owner's earlier world/save/reopen phone proof does not establish water visuals.

No Unity game material/ShaderLab/.meta/GUID, audio, Settings, input/touch, native build request, other client files or original ZIP2 branch modified.
