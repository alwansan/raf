# 20261111-GFX-chat-gfx107-108-original-indexed-skinning-75 — GFX107/GFX108 original-source indexed CPU skinning proof

**role=GFX-LAB · origin=chat · only writable branch=experiment/android-graphics-rootcause**. Resumed from `20261111-GFX-chat-verified-siv-rig-source-74`. ZIP2 immutable source SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Source files and raw bone/mesh parameters remained in disposable private GitHub CI runner; safe aggregate only and source purge logged.

## Actual CI 107
- Run [42951739739](https://github.com/alwansan/raf/actions/runs/42951739739) **SUCCESS**, 12 tests, artifact 13825760281. Source-authentic computed **213/213** bone world × Mesh.bindpose matrices across five Skinned samples.
- Relative to first bone matrix product, consistency ≤1e-4: M00 3/3 (max 9.6e-7); M01 74/100 (0.26967712); M02 8/8 (7.878e-5); M04 74/100 (0.26967712); M05 2/2 (2e-8). Combined coherent 161/213. Only a test of **serialized Transform snapshot**, not assertion of bind rest pose; M01/M04 mismatch could be animated snapshot or another coordinate difference. Do not overwrite source bones.
- Implementation `gfxlab/tools/gfx107_source_bindpose_math.py`, `gfxlab/tools/gfx107_original_bindpose_matrix_audit.py`. Source-safe `gfxlab/evidence/20261111_gfx107_original_bindpose_cpu_safe.json`.

## Actual CI 108
- Initial GFX108 direct Mesh attribute `m_Vertices` was unavailable in UnityPy generated mesh. Recovered authoritative `UnityPy.helpers.MeshHelper.MeshHandler(mesh).process()` which supplies **same-source-index** positions, weight tuples and bone-index tuples BEFORE OBJ axis mirror or welded importer. No OBJ fallback.
- CI proved exactly two original influences for each M00/M05 vertex (375+4452 rows); four for M01/M02/M04. Current code allows **only** authentic source widths 2 or 4, zero-pads 2 with mathematically inert zeros, rejects mismatched/unobserved widths, nonfinite/nonunit weights, and out-of-range weighted bone indices. Synthetic regression ensures identical positions with different original weights are not welded.
- Final [GFX108 run 42953322197](https://github.com/alwansan/raf/actions/runs/42953322197) **SUCCESS, 18 tests, artifact 13826002534**, private original source purged. **14,033/14,033** true original indexed vertices CPU LBS computed with original bones/bindposes:
  - M00 375 vertices; different from first-bone matrix reference at >1e-4: 0; max distance 3e-7.
  - M01 5095; different 695; max distance 0.0228293.
  - M02 1666; different 0; max distance 4.65e-5.
  - M04 2445; different 679; max distance 0.0228293.
  - M05 4452; different 0; max distance 3.1e-5.
  - Total **1374/14033** differ from first bone reference in synthetic CPU numeric comparison, not a verified original GPU animation/per-frame pose.
- Implementation `gfxlab/tools/gfx108_indexed_skinning_cpu.py` + `gfxlab/tools/gfx108_original_indexed_skin_cpu.py`; source-safe evidence `gfxlab/evidence/20261111_gfx108_original_indexed_cpu_skin_safe.json`; Arabic report `gfxlab/GFX107_GFX108_INDEXED_SKINNING_AR.md`.

## Phase-one truth and priorities
**What is proven:** exact source pointer/weight/index and bone matrix data available; 5/5 source skinned original Mesh examples can be evaluated through CPU linear blend skinning without OBJ welding, source loss or fabricated weights. **What is NOT proven:** CPU pose identity with original Windows runtime; original AnimationClips/Animator; Android GPU skinned pose; original 7-pass Shader48 runtime, exact materials/CB/samplers/normal/mips, PC↔Adreno pixel parity. The source snapshot may not be bind pose (especially M01/M04). M00/M05 can have multiple root ancestry chains; original bones are not missing.

**Next:** build original-source GPU pose probe for one simple M02 and one complex M01 or M04 using same index+weight+bindpose streams and explicit CPU/GPU witnesses; generate signed test APK only when variant is source-authentic and GPU evidence can be interpreted. Continue original Shader48 Material CB/Normal/RenderState proof independently; do not touch T1–T5.

**Flags:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `original_rig_restored=false`, `pcAdrenoPixelParityVerified=false`, `phase_closed=false`.
