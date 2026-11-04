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

[Dedicated CI run 41929367655](https://github.com/alwansan/raf/actions/runs/41929367655) **SUCCESS** (10 synthetic tests plus six SHA-pinned scenes and both 111–116MB selected original serialized owners). The owners' exact original size/SHA256 matched ZIP2 and source PPtrs were checked against actual Material class IDs: **1,609 verified**, **26 references to an unstaged but manifest-declared original owner**, **4 originally null slots**, **0 wrong/missing Material target objects**. This is verified original source graph evidence only; no Unity export or Android pixels.

## Residual 26 source targets fully verified

A third source-only experiment [scripts/b03_remaining_renderer_material_owners.py](../scripts/b03_remaining_renderer_material_owners.py), [negative controls](../tests/test_b03_remaining_renderer_material_owners.py), [isolated workflow](../.github/workflows/raft-b03-remaining-renderer-owners.yml) deterministically selected **one** remaining provider via actual six-scene PPtrs, then verified its original ZIP2 manifest file size/SHA256 **34,888,388 bytes**, without re-fetching the two prior authenticated owners. Original 26/26 target PathIDs resolve to actual serialized Material objects. [Final run 41930267873](https://github.com/alwansan/raf/actions/runs/41930267873) **SUCCESS**: 10 synthetic negative/positive checks, real six original scene SHA pins, 1 residual SHA-verified provider, 0 wrong/missing target objects, and only aggregate numeric output. This complements earlier [41929367655](https://github.com/alwansan/raf/actions/runs/41929367655) on the same immutable source commit; the latter's previously verified 1,609 references were **not** needlessly downloaded again.

[First residual attempt 41930090228](https://github.com/alwansan/raf/actions/runs/41930090228) failed during Git cone-mode sparse-checkout of an authentic **plain file**, not source/material resolution. The precise Git error was `is not a directory`; the fail-closed sparse selector was corrected to explicit `--no-cone` patterns at commit [03a6b89f](https://github.com/alwansan/raf/commit/03a6b89f9ac8de1e2d8f6ca670d775b0339aafb8). The corrected original-source job and all tests succeeded. The rejected cone-mode assumption is retained as an incident, not hidden or misreported as asset damage.

**Six original scenes only:** 1,495 original Renderer objects, 1,639 material slots; **1,635 of 1,635 non-null original external slots resolve to authenticated Material class objects across three SHA-verified source owners**, while 4 original slots are intentionally null. This verifies the bounded original source graph, **not** original-to-export renderer GUID/fileID retention or shader, texture, lighting and device pixels. B03's previous exported-YAML structural guard [41914562432](https://github.com/alwansan/raf/actions/runs/41914562432) still requires a real same-instance full game export before a source-to-export parity conclusion.

Next: correlate a real complete exported Unity project/renderer trace with the original source graph, then patch only evidenced lost Renderer material associations. Keep **RENDER-002 OPEN** and project **NOT_READY, 0/3**. Preserve sound, Settings, deferred touch, .meta/GUID, all original assets, local-world and .rgd systems.
