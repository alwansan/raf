# B21 — authenticated original scene lightmap evidence (4 November 2026)

**Scope:** P0 RENDER-002, independent original-scene lighting/lightmap lane; original ZIP2 pinned to `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. No gameplay, graphics export, Unity runtime, FMOD, Settings, touch, `.meta` or LFS changes.

## Reproducible source experiment

- Code: [`scripts/b21_scene_lightmap_links.py`](../scripts/b21_scene_lightmap_links.py), [16 synthetic and negative controls](../tests/test_b21_scene_lightmap_links.py), isolated [workflow](../.github/workflows/raft-b21-scene-lightmap-links.yml).
- [Run 41921259677](https://github.com/alwansan/raf/actions/runs/41921259677) **COMPLETED SUCCESS**, source `c4ab08d2f9d3fa7eb48a063ef27b26701ef13163`. Synthetic job 126894072692 **16/16 passed**; authenticated original scene job 126894149096 **passed**. Tool: Python 3.12 / UnityPy 1.23.0.
- Original `Raft/Raft_Data/level0..level5` are six regular Git files from ZIP2; each passed strict original-manifest byte-size and SHA256 checks **before** native Unity serialized object parsing. No 40-scene/full-export claim. Reports contain numeric aggregates and original SHA only, not proprietary raw data.
- Results: exactly one decoded `LightmapSettings` per scene, **0 serialized baked lightmap entries**, all **1,497** decoded renderer `m_LightmapIndex` entries unassigned (level0 1369; level1 22; level2 25; level3 22; level4 38; level5 21); **0 out-of-range indices**.
- Interpretation: the hypothesis “lost baked scene lightmap texture caused the reported white objects” is **unsupported for these six authenticated original scenes**; the original scenes had no such baked-lightmap slots. Do **not** infer missing meshes, absence of all lighting, intact dynamic lights, export fidelity, or anything about remaining 34 scenes. Shift investigation toward actual shader/material/texture/lighting interactions with preserved source identity.
- Test controls reject symlink sources, wrong size/digest, duplicate/null object pathID, duplicate LightmapSettings, out-of-range index; preserve unknown type-tree and external references rather than incorrectly declaring them missing or repaired.

## Failure history, not skipped

[41920993025](https://github.com/alwansan/raf/actions/runs/41920993025) failed one synthetic assertion: a `Counter` can explicitly contain zero-valued `renderer_indices_out_of_range`; test corrected at `f0cc646`. [41921086137](https://github.com/alwansan/raf/actions/runs/41921086137) then passed 16/16 synthetic, but refused original file due a copied level1 SHA typo in probe constants; the SHA was corrected directly from pinned `RAFT_FILE_MANIFEST.tsv` at `c4ab08d`. No original digest pin or source bytes were altered to conceal failure. No other run was repeated without a changed cause.

## Limits and next useful work

The water/FFT wrong-pass and zero-kernel failures (owner APK86) and Steam SaveGame exception remain open, untested on a newer Android build. This probe is **not** a water shader fix, an exported-material parity result, a device color result, or an APK. RENDER-002 and WATER-001 remain OPEN; project NOT_READY, independent full reviews **0/3**. A distinct follow-up is to inspect **original dynamic lighting/probe references vs same-instance exported scene**; only change export/render resources on authenticated mismatch with `.meta`/GUID preservation. Avoid repeating the existing B03/B05/B22/B44/B46 material and texture census.

Preserve B21 session `20261104T2153Z-B21-72ab`; see [coordination memory](../prompt/coordination/clients/B21/MEMORY.md).
