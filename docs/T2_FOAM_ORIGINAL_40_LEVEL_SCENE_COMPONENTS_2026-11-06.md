# T2 — immutable original 40 Raft level scene component PPtr/Shader-host census

Date: **2026-11-06 UTC**; owner **T2**, origin `chat`, session `20261106T1753Z-T2-chat-original-levels-component-671a`; issue WATER-001 OPEN.

## Engineering question

The previous [full 40 sharedassets source Material scan](T2_FOAM_ORIGINAL_40_SHAREDASSETS_MATERIAL_HOST_2026-11-06.md) authenticated 474065455 original bytes / 1392 Material objects and found no direct `Material.m_Shader` reference to the SHA-original Foam Shader object in `Raft_Data/sharedassets0.assets` at PathID2420. A live water Shader could still be referenced by **serialized scene components** or script-created Materials.

This **distinct experiment** stages all 40 original `Raft_Data/level[0-9]+` Unity SerializedFiles from the independent immutable ZIP2 source, recursively parses **structurally typed `m_FileID,m_PathID` PPtrs** inside readable `MonoBehaviour` and render-component typetrees, and distinguishes same-file PathID from a **candidate external reference to the original Foam owner's filename+PathID**. `Material` objects, if any, are separately inspected for `m_Shader`. Opaque components are recorded as unparsed, **never treated as absent**. No raw byte scans or guessed GUIDs.

## Original provenance, controlled source output

- Immutable original checkout: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385` (read only).
- Validated original `RAFT_FILE_MANIFEST.tsv` with 366 entries and total declared data, then SHA-authenticated **all 40 level scene files**, **233237972 original bytes**; split files reassembled and independently SHA-verified against pinned manifest entries privately in GitHub Actions.
- Original Foam owner and raw PathID2420 SHA previously verified by [CI42264851712](https://github.com/alwansan/raf/actions/runs/42264851712) and [CI42262404131](https://github.com/alwansan/raf/actions/runs/42262404131). This new run **does not stage or rehash the original Foam Shader object**, and correctly exports `original_Foam_Shader_asset_SHA_authenticated_this_run=false` plus prior-provenance flag.
- Implementation: `scripts/t2_original_scene_foam_component_scan.py`; adversarial regression: `tests/test_t2_original_scene_foam_component_scan.py`; isolated CI: `.github/workflows/raft-t2-original-scene-foam-component.yml`, UnityPy==1.25.4, Ubuntu24.04, 23-min bounded runtime, separate no-cancel concurrency.
- No raw original bytecode/game objects, component field or class names, shader names or private file GUIDs/identifiers exported. Only finite aggregate integers/booleans left private source stage; entire original ZIP2 checkout and staging deleted before safe artifact upload.

## Genuine GitHub Actions result

[**CI 42266263645**](https://github.com/alwansan/raf/actions/runs/42266263645) **SUCCESS**, source commit **`ddf2011cdafacc7e18989f8eaed95ff3f4c812ad`**; job `128058868593`. **21/21** source-free tests pass, exact ZIP2 SHA check, all 40 original serialized scene bytes staged SHA and inspected, safe-shape assertions pass, source scratch removed. Finite safe artifact `13525944952` (`t2-original-40-level-scene-foam-safe-42266263645`, 664 bytes).

| Source-original category | Verified |
|---|---:|
| Original level scene files individually SHA-checked | **40/40** |
| Original level scene content bytes SHA-checked | **233237972** |
| Source scene `Material` objects | **0** |
| Source scene `MonoBehaviour`/render component objects selected | **240961** |
| Components whose typetree could be structurally parsed | **185633** |
| Components whose typetree was unsupported/opaque | **55328** |
| Structurally parsed component PPtr records examined | **1277371** |
| Scene `FileIdentifier` table entries naming Foam owner across all scenes | **40** |
| Parsed component PPtrs to that same source owner but **other PathIDs** | **24660** |
| Parsed component external Foam owner + exact Shader PathID2420 candidate | **0** |
| Scene Material Foam Shader candidate PPtrs | **0** (no scene Materials) |
| Foreign local `PathID2420` references, **not** Foam | **15** |
| Invalid external fileIDs in readable source tree | **0** |

**Interpretation:** The authenticated scene-component source contains no structurally parsed `PPtr` candidate to **the exact source-original Foam Shader PathID2420 via its owner filename**. But the scan did **not** inspect custom fields within the 55,328 unsupported/opaque component typetrees and does not cover dynamic `Shader.Find`, source code assignment, or other asset bundles. Thus **this does not establish 0 Foam references for all game scenes/runtime**. Basename+PathID itself would still be an external identity *candidate*, not a verified asset GUID or runtime binding even if a row had matched.

The 40 scene external table entries represent **entries, not 40 source Materials nor 40 resolved Shader references**. Count `24660` corresponds to other source-object PathIDs within the same owner, which is expected for scene renderers/components and cannot be relabeled Foam. The 15 same-number foreign local PPtrs must not be falsely linked to source Foam.

## Practical next step and phone-build vote

Prior T2 authentic managed IL [CI42229056366](https://github.com/alwansan/raf/actions/runs/42229056366) established a particular `Shader.Find` writer name does **not** equal original Foam serialized shader `m_Name`. Source-original water Shader may instead be assigned elsewhere at runtime, dynamically created, or referenced by custom MonoBehaviour layouts. Next produce a **focused original managed/source runtime trace** of Foam-related shader requests/Material allocation and/or extract the unsupported component typetrees by exact original script lineage, rather than repeating parsed scene and `sharedassets` scans. Integrate actual original Spectrum/Foam/Blur ShaderLab/CB0 and verify Unity/Adreno pixels only with substantive implementation.

Trial vote in [round trial-20261106-r1](../prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md) stays **T2 «لا يحتاج»**: source original graph diagnostics and regression tests are not a major integrated Android water rendering fix. T5 alone may consider a build once all five current workers independently meet owner-defined vote conditions. No native build, original ZIP2 branch modification, Raft shader/material/scene/.meta/GUID, audio, Settings, touch, input or other team workflows touched. WATER-001 remains **OPEN**; complete game remains **NOT_READY**.
