# GT Chat-24 — SHA-original Spectrum m_KeywordFlags index4, source-only real CI

**Date:** 2026-11-12; **branch writable:** `feature/android-native-port`; **original:** `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385` READ ONLY, no Git LFS.

## Work completed

- Verified parent baseline [43288288144](https://github.com/alwansan/raf/actions/runs/43288288144) THREE jobs SUCCESS: one private original-index4-keyword 7-pass Spectrum shader, two Unity2021 Android Vulkan ShaderVariantCollection variants, 14,492-byte PRIVATE bundle, zero final GLSL/import/internal-variant/compile failures. This is not game integration.
- Introduced `scripts/gt_spectrum_original_keyword_flags.py` and `tests/test_gt_spectrum_original_keyword_flags.py` with fail-closed exact five-row flag and source shader checks, uint8-only schema, 7-pass guard, SHA-verified B09 source object, and no original keyword spelling/program publication.
- Added independent source-only CI `.github/workflows/raft-gt-spectrum-keyword-flags-source.yml`; original input staged from immutable ZIP2 into TEMP, no LFS, no original .meta or game code changed.
- [CI 43296468683 SUCCESS](https://github.com/alwansan/raf/actions/runs/43296468683): real owner `sharedassets0.assets` exactly **115,978,112 bytes**, original source `m_KeywordNames` **5**, source `m_KeywordFlags` **5 uint8 flags**; `m_KeywordFlags[4] == 0`, all five byte values identical (distinct count **1**), source flags-byte SHA256 `8855508aade16ec573d21e6a485dfd0a7624085c1a14b5ecdd6485de0c6839a4`. Synthetic negative tests PASS.
- Strict significance: byte value zero is **observed serialized metadata only**. Exact `flag-byte -> global/local/overridable` mapping for the source editor version still UNPROVEN, and original Material runtime keyword branch, GUID, sampler filtering/wrapping, CB0, RT and Adreno pixels remain UNPROVEN. No production Shader or Material install.

## Next P06/M2 actions

1. Establish the byte-flag semantic mapping with a version-matched independent Unity 2021 keyword-space control (compare global and local synthetic keyword declarations and serialized flags) before changing any source-index4 ShaderLab pragma. The single private candidate currently uses a **provisional** `multi_compile`.
2. Locate the exact source Material -> Shader PathID2432/owner PPtr references across authentic 82 serialized owners, then same AssetRipper-export GUID/Material/keyword selection. No assumed cross-owner identity.
3. Verify original Sampler/Texture/CB0/RT binding and actual selected keyword ON/OFF under a disposable Unity water rendering experiment, then consider full APK/XAPK and new Adreno logs/screenshots.
4. Foam Global original 2 passes; compute kernel6 provenance; 770 still Dummy Material docs. Continue source-only tasks while full-game assets are not yet safe to replace.

## Recovery

Read `clients/GT/RESTORE_AR.md`, `RESTORATION_PLAN_AR.md` + JSON, `state.json`, `SUMMARY_AR.md`, `MEMORY.md`, and Chat23/Chat24 sessions. Do NOT confuse CI SUCCESS with in-game water pixel acceptance. Keep source ZIP2 read only and no Git LFS.
