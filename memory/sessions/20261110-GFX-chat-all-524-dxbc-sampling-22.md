# GFX-LAB 20261110-GFX-chat-all-524-dxbc-sampling-22
- session_id: `20261110-GFX-chat-all-524-dxbc-sampling-22`, origin=`chat`, resumed_from=`20261110-GFX-chat-independent-dxbc-sample-pairs-21`.
- base_sha=`9ac91b8086ae4f3c75e727b93c3f5b051241499a`; experiment_key=`GFX-MULTI-048`; scope `experiment/android-graphics-rootcause` only, no T-team branches modified.
- source_ref original pinned ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- prior proof GFX047 [CI42838485544](https://github.com/alwansan/raf/actions/runs/42838485544): original DXBC independent 37/37 t/s opcode pairing to translated SPIR-V for 7 representative stage pairs, 314 tests.
## Question / controls
- Inspect all **524** original exact keyword/hardware-tier Shader48 matched VS/FS pair records and record confidential per-stage source DXBC sample/gather opcode t/s multisets. Determine how many anonymous sample-signature classes are present per Pass, sample-count histograms, unknown source dynamic indices and unique referenced program identities. Same sampled-count does NOT mean same t/s use pattern.
- Bound source/stage count, verify reference identity and opcode syntax, reject malformed dynamic/undeclared input, allow private cache but never output t/s values, shader bytes, keywords, GUID or pair fingerprints.
- This is a source-only census and **does not** translate all 524 pairs, execute original GLES shader on device, prove Material property identity or CB memory layout.
## Files/CI
- `gfxlab/tools/multi_shader_all_variant_dxbc_sample_census.py`
- `gfxlab/tests/test_multi_shader_all_variant_dxbc_sample_census.py`
- `.github/workflows/gfxlab-multi048-all-variant-samples.yml`
- CI pending; source-free tests + genuine SHA-pinned source audit + guaranteed purge. Never mark source equality until run terminal.
## Next
If all 524 source signatures are consistent within selected shaders, choose a bounded representative matrix for later 524-variant SPIR-V translation; still need genuine shader source or PC capture for property→t/s/b and CB byte layout. No originalShaderRestored, no APK.

## Final verified result
- [CI42839415657](https://github.com/alwansan/raf/actions/runs/42839415657) SUCCESS; 320 source-free tests, original private ZIP2 SHA pinned, purge PASS; safe aggregate artifact 13775750529 (expires 2026-11-17T14:58:26Z).
- **524 exact keyword/tier original VS/FS pairs / 1048 source stage references / 936 unique compiled stage programs / 58 combined source t/s sample-use signature classes**. 58 classes are sampled-resource patterns only, not complete shader program semantics.
- Pair counts by Pass: [80,156,32,80]+[40,120,16]. Per-Pass distinct fragment sample-use signatures: [12,25,4,6]+[9,22,2]. Fragment sample instruction count ranges [5–11,2–10,0–3,2–7]+[5–11,3–7,0–1]; vertex samples 0 across all pairs. No dynamic unresolved resource or sampler indices for recognized sample/gather instructions.
- Source-only result; no SPIR-V translation for all 524 variants, no PC↔Adreno GPU parity; no Shader48 property→register/CB proof. OriginalShaderRestored=false.
- Next: GFX049 representative each of 58 private sample-use classes with offline translation and independent DXBC→SPIR-V pair multiset validation, respecting that a sampling class is not full shader identity.
