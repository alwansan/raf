# 20261111-GFX-chat-owner-gpu-unified-model-lab-66

origin=chat; role=GFX-LAB; resumed_from=20261111-GFX-chat-phase-one-input-lanes-65; base_sha=6a18eb47130d4e6dd20b4c578d132b21eeb1282b.

User tested GFX094 and requests merging model/geometry examples with prior CI42822853848 (GFX041 affine-reference synthetic GPU probe, success c51575cd9e0e16a7531cd8673bb86a78c2f56987). Scope and controls are in experiments/20261111-GFX-chat-owner-gpu-unified-model-lab-66.json. Owner ZIP stays private; safe counts only in Git. Phase-one source/rig/pixel gates remain open.

## GFX097 owner proof verified; GFX098 actual build running
- Owner ZIP CRC and SHA checked; SHA7daa48905a425dbdc4b3ec64c95873a984440f58c2740b5fb5fb57909a4daa47.
- 472 events:285 successful driver compiles (VS128/FS157),128 successful links,29 CPU-unavailable BaseInstance entries,0 GL errors,0 nonempty compiler/link logs. Source build66b2968673f410cbf58d5b255216c5e3c9c175ef. No original model/pixel parity from GFX094.
- Scope now GFX098: shared source-saved Standard candidate materials with6 material/18 texture aliases; original floats/colors/keywords/renderqueue/UV and instancing, official RGorAG normal candidate with red-unit guard, explicit regenerated mips. Legacy PBR retained as control. Both viewer and user referenced GFX041 affine probe are prepared as separate scenes with a persistent navigation toolbar and Screen.safeArea handling.
- 12 automatic camera readbacks (6 models x2 material modes), SHA-linked PNG/JSON and auto ZIP export. Original rig remains static/unrestored. PC exact-source recompilation requests include14 original stages; hardware tier missing in original player row is -1 UNKNOWN, so all3 compiler tier candidates are attempted and reported as candidates, never an invented source tier.
- Local source-free checks:922 tests passed. First unified build [CI42927645102](https://github.com/alwansan/raf/actions/runs/42927645102) at06ab8058e833146e78c81024d96980df2e3a39e1 in progress. No APK claimed until Unity import/compile/build/signature/artifact/purge verified. Legacy standalone GFX041 is retained manual-dispatch-only to avoid rebuilding it on shared-code changes; no other agent/workflow canceled.

## Build checkpoint
CI42927645102 passed source-free922 tests, original geometry/image sparse extraction, seven source Normal unit-red guards and saved material/alias/PC request staging. Unity Android compile/build started. GFX098 source schema preserves seven slots -> six Material aliases and21 texture links ->18 identities. Test captures are studio-camera960x540 PNGs, not claimed Raft game captures. Source normal conversion uses the official Unity2021.3.45f2 `UnpackNormalmapRGorAG` expression (R*A,G, reconstructed positive Z) under R==255, quantized to8-bit RGB for NormalMap importer; mips are regenerated and explicitly not source-chain parity.

Independent source baseline: SHA/size-manifest-authenticated original Raft_Data/globalgamemanagers (1914356bytes), PlayerSettings.m_ActiveColorSpace=1 (Unity ColorSpace.Linear). Safe evidence gfxlab/evidence/20261111_original_PC_color_baseline_safe.json. PC compile witness should set Linear before compilation and record it; source row hardware tiers remain unknown. Android final build already sets Linear; do not reinterpret a PC mismatch without matching this baseline.


## Verified delivery checkpoint — GFX097/098/099, 11 Nov 2026

Owner GFX094 evidence:285/285 actual Adreno compiles and128/128 links passed;0 GL errors.29 missing BaseInstance stages are CPU translation limits, not driver failures.

GFX098 CI42927645102 SUCCESS at06ab8058e833146e78c81024d96980df2e3a39e1;922 source-free tests passed. Signed ARM64 GLES3 APK independently checked:111020747bytes, SHA256 b314699c74eac39d89b7efb668a17519803f6ecd424c4f368cf17d378d726be6. Artifact13816395740 expires2026-11-18T00:16:44Z. Delivered GFX098-Unified-Models-GPU-Lab.apk, Library libfile_0f250cae03308191a0c2640452a337d7. Package com.alwansan.raft.graphicslab.unified098. Six models, source-saved Standard candidate and old PBR control,12 automatic camera captures, merged four-mode GFX041 affine GPU scene, combined ZIP export. Owner GFX098 execution is pending.

GFX099 CI42930674563 SUCCESS at19647a1f21832617fd9e9a83b4d0edc312885fed. Original PlayerSettings independently pinned Linear. Setting Linear BEFORE PC compilation produces14/14 representative original SHDR+ISGN+OSGN byte-exact requests,42/42 tier-candidate matches,0 exceptions/rejections. Source tier remains unknown; this does not validate every original variant or PC/Adreno pixels. Safe report gfxlab/evidence/20261111_gfx099_PC_linear_compile_safe.json. Supersedes GFX098 embedded PC witness9/14; Android098 already builds Linear and needs no rebuild for this CPU-only evidence update.

Skin source availability verified:14033 weighted vertices,213 bindposes across five skinned models, plus one static model; finite normalized weights and valid positive-weight bone indices. Hierarchy, pose and original full vertex stream are not restored. See safe skin report. Next: owner opens098, waits12 captures, selects AFFINE-GPU for4 tests, EXPORT ALL and returns latest GFXLAB-ALL-TEST-LOGS ZIP from /storage/emulated/0/Download/Games/cl/test/g/.

Phase one remains OPEN: original rig, original mip chain, exact GPU normal sampling and PC/device pixel comparison remain unproven. CPU normal XYZ conversion and regenerated mipmaps are candidates; CPU reconstruction before bilinear filtering is not equivalent to GPU AG unpack after filtering. Future rig work must preserve full vertex attributes/indices/weights/bindposes/hierarchy rather than attaching bones to merged OBJ vertices. No full-game build or other branch modified.
