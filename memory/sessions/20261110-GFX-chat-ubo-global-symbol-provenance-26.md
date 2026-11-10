# 20261110-GFX-chat-ubo-global-symbol-provenance-26 — GFX-MULTI-052
- session_id: 20261110-GFX-chat-ubo-global-symbol-provenance-26; origin: chat; resumed_from: 20261110-GFX-chat-cb-access-shape-25.
- base_sha 741acd1ca36288371f040edd46e7e79ac117aed2; only writable experiment/android-graphics-rootcause.
- source ZIP2 commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385, never export source.
- Prior GFX050 CI42843665847: 66/66 numeric b source to SPIRV UBO binding/byte-size candidates, 0/66 SPIRV-Cross reflected block-name-authenticated.
- Prior GFX051 CI42845677322: 208/208 original source static CB vector uses in supported subset overlap SPV numeric candidate, no independent CB identity.
- Goal: inspect only actual raw SPIR-V Uniform globals and their OpName plus Binding and DescriptorSet, never block types or local name. Compare with original source b-declarations and sizes. Counts only; duplicate globals/coords fail closed. Positive generated b symbol can indicate compiler provenance, not Material property or CB member offset. Test seven exact Shader48 source VS/FS keyword+tier pairs (14 stages). No APK or T-team changes.
- Files: gfxlab/tools/multi_shader_original_cb_global_opname.py, gfxlab/tests/test_multi_shader_original_cb_global_opname.py, .github/workflows/gfxlab-multi052-ubo-global-opname.yml.
- CI pending. originalShaderRestored=false, phase_closed=false.

## Final result
- [CI42847513772](https://github.com/alwansan/raf/actions/runs/42847513772) success, 356 source-free tests, original ZIP2 source SHA pinned; runner purge PASS.
- 14 representative original Shader48 stages, original DXBC b# declaration count 66, SPIRV-Cross reflected UBO count 66, real `OpVariable ... Uniform` with `OpName` count 66. All 66 names match original source b# and same numeric descriptor Binding and independent original declared byte size. 14/14 stages full matching, no name/coord ambiguity.
- 357 non-UBO-global OpName labels ignored. Diagnostic rejects duplicate global label IDs/decorations and source mismatch.
- Initial CI42847387051 failed synthetic-only raw-ID fixture, corrected; final CI passed source-private stage audit.
- [Safe aggregate artifact 13778128531](https://github.com/alwansan/raf/actions/runs/42847513772/artifacts/13778128531), expires 2026-11-17T15:45:13Z UTC; no private register names or source bytes exported.
- Proven: compiler-generated original DXBC b-register symbolic provenance and block-size alignment on representative 14 source stages. NOT proven: original Material property→CB/byte offset semantics, actual Shader48 Android GPU or PC parity; `originalShaderRestored=false`, `phase_closed=false`.
- Next GFX053 authenticate actual SPV CB member type shape/stride and vector byte address vs private source decoded b#/vec index with source register proven via actual raw Uniform global OpName, fail closed on unsupported instructions and dynamic indices.
