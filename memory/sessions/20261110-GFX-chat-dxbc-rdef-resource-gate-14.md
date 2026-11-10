# 20261110-GFX-chat-dxbc-rdef-resource-gate-14
- session_id: 20261110-GFX-chat-dxbc-rdef-resource-gate-14; origin: chat
- resumed_from: 20261110-GFX-chat-all-seven-pass-gles-13
- base_sha: 557506f60fbea6481e4474ceee37b8b4f6112b4b
- experiment_key: GFX-MULTI-014-authentic-DXBC-RDEF-versus-SPIRV-resource-counts
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: one original Shader48 Pass 0 exact VS+FS DXBC source container RDEF resource/constant-buffer counts, reflected SPIRV resources, numeric safe report only; no source byte exports, full game, apk, or team branch edits.
- previous GFX-MULTI-013 CI42732808109 SUCCESS 71 tests: all seven authentic passes representative DXBC→SPIRV→GLSL ES310 offline compile and VS/FS stage IO location/type parity; only 7 of 524 pairs exercised; original Android Shader48 false.
- hypothesis: source DXBC RDEF resource declarations include shader globals not stored as per-Material textures, and SPIRV descriptor remaps require explicit register/CB/sampler semantic mapping rather than assuming Standard fallback binding.
- expected CI GFX-MULTI-014 after workflow push; source only; original shader phase OPEN.

- CI42733550704 FAILED pure synthetic fixture only: declared 1 resource binding at offset 40 in 56-byte RDEF payload, so strict parser correctly rejected truncated binding. No original Shader48 source was read. Enlarged synthetic test payload to 84 bytes, re-triggered CI. No change to proprietary source or runtime.


## CI final evidence / re-interpretation
- [Run 42733664716](https://github.com/alwansan/raf/actions/runs/42733664716) COMPLETED SUCCESS: 75 unit tests; actual original Pass0 VS+FS had no RDEF; original source CB/resource counts **unknown**, not zero. SPIR-V 5 VS UBO; 7 FS UBO, 7 images, 6 samplers. No source-to-SPIRV register parity.
- Fixed parser to output JSON null on absent RDEF, with strict negative test. Persistent plan: `gfxlab/OPEN_WORK_AND_IDEAS_AR.md`; next session `20261110-GFX-chat-persistent-roadmap-15`.
