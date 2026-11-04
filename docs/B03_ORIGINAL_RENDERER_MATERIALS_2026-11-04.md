# B03 — Authentic original scene Renderer→Material source graph (2026-11-04)

## Evidence boundaries

B03 resumed source-only RENDER-002 investigation in session `20261104T2243Z-B03-7c9e`. Immutable original source: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385` on protected `zip2`; six actual original `Raft_Data/level0..level5` blobs were validated by **original file byte count and SHA256**, before UnityPy typetree decoding. The existing B21 SHA pins were reused rather than inferred from file names.

Source audit program: [scripts/b03_original_renderer_materials.py](../scripts/b03_original_renderer_materials.py), tests [test_b03_original_renderer_materials.py](../tests/test_b03_original_renderer_materials.py), isolated [workflow](../.github/workflows/raft-b03-original-renderer-materials.yml). Original six-scene CI [41928128357](https://github.com/alwansan/raf/actions/runs/41928128357) SUCCESS; stronger ZIP2-manifest transport-name comparison [41928799663](https://github.com/alwansan/raf/actions/runs/41928799663) SUCCESS. No LFS, no Unity Editor or APK, no private source bytes or per-object identifiers published.

| Original scene | Serialized Renderer components | m_Materials slots | Declared external refs | Null slots |
|---|---:|---:|---:|---:|
| level0 | 1,369 | 1,500 | 1,500 | 0 |
| level1 | 20 | 33 | 29 | 4 |
| level2 | 25 | 25 | 25 | 0 |
| level3 | 22 | 22 | 22 | 0 |
| level4 | 38 | 38 | 38 | 0 |
| level5 | 21 | 21 | 21 | 0 |
| **6-scene total** | **1,495** | **1,639** | **1,635** | **4** |

All 1,495 target Renderer material arrays decoded structurally. The source owns 1,356 MeshRenderer, 110 ParticleSystemRenderer and 29 SkinnedMeshRenderer entries. All **1,635 external material slots** refer to distinct valid `m_FileID` indices whose declared provider basename appears exactly once in the immutable 366-file ZIP2 manifest; none was missing or ambiguous by name. This proves source-side *transport declaration* only, not that the referenced external file's bytes or target Material object is verified. Four null slots are genuinely present in these original scenes; a future exported project should not be “repaired” by blindly populating them.

The first proof is limited to **six of forty scenes**. It does not establish renderers' `m_Materials` parity with AssetRipper's same-instance Unity export, shader/material variants, texture/color values, original external owners' target object class, or device pixels. These outstanding links are distinct from B21 original light/lightmap analyses and other B-team material/texture checks.

## Target class validation extension

A second bounded experiment [scripts/b03_original_renderer_target_resolution.py](../scripts/b03_original_renderer_target_resolution.py) targets only two major source owners (`resources.assets`, `sharedassets0.assets`), reassembled from the original split parts at the fixed ZIP2 commit and checked against pinned **original bytes + SHA256**. It maps original six-scene non-null references to actual serialized `Material` class objects where their provider is one of those selected owners. Other providers remain unverified; source object IDs and original materials never enter public logs or artifacts.

[Dedicated CI run 41929367655](https://github.com/alwansan/raf/actions/runs/41929367655) was triggered for this separate experiment. Its result must be inspected live; no source-owner class match is claimed before final CI evidence. Initial expected budget: 18-minute public Linux runner, six original scenes plus two ~111–116MB source owners, **no 7.8GB full extraction, no LFS**.

Next after completed target check: correlate a real complete exported Unity project/renderer trace with the original source graph, then patch only evidenced lost Renderer material associations. Keep **RENDER-002 OPEN** and project **NOT_READY, 0/3**. Preserve sound, Settings, deferred touch, .meta/GUID, all original assets, local-world and .rgd systems.
