# GT Chat-23 — Spectrum variant1 hidden GLSL linker errors / fail-closed true Unity console gate

**Date:** 2026-11-12. **Writable only:** `feature/android-native-port`. **Original ZIP2:** `15964ea8f246b6e076ce26b60931ee2e1a9a2385` read-only, no Git LFS, no Raft .meta/GUID/Material mutations. Owner discontinued T1–T5; reuse their evidence rather than wait.

## Verified source/probe baseline

- [43273276394](https://github.com/alwansan/raf/actions/runs/43273276394) source original 7 Spectrum Passes, 14 original VS/FS pairs and 28/28 Vulkan1.1 paired-stage compiles, 13 distinct DXBC-derived program translations.
- [43273958426](https://github.com/alwansan/raf/actions/runs/43273958426): original 7 distinct render states, 6 authored properties (2 textures, 3 floats, 1 vector).
- [43274729958](https://github.com/alwansan/raf/actions/runs/43274729958): two private source-authentic seven-pass *structural* ShaderLab candidates; NOT source-original runtime keyword shader.
- [43279249696](https://github.com/alwansan/raf/actions/runs/43279249696): exact original names from DXBC+Unity resource register parity, 26 texture and 26 sampler symbolic mappings across 28 original stages; real Unity 2021.3.45f2 Android Vulkan isolated variant0 imported 7 passes, shader errors=0, produced 12,079 byte private bundle. **Only variant0 source-derived private compilation proven.** Original game Material, GUID, sampler filter/wrap, RT, CB upload and phone pixel parity FALSE.

## Variant1 important false-green warning

- Initial synthetic variant1 CI failure [43280517999](https://github.com/alwansan/raf/actions/runs/43280517999) was a fixture mismatch: assertion asked for literal `\\n`, private text file contains real newline. Fixed in commit `9220038bf08db4bc8adb208dd0cf0c5eaceb8c57`.
- [43282759870 — GitHub SUCCESS but NOT visual/shader acceptance](https://github.com/alwansan/raf/actions/runs/43282759870):
  - Variant0 real Unity 2021: 7 Passes, ShaderUtil errors 0, 12,080B isolated Android Vulkan bundle.
  - Variant1 real Unity 2021: 7 Passes, ShaderUtil errors 0, 12,418B isolated Android Vulkan bundle, BUT **12 `GLSL link error` lines** and **12 `Creation of internal variant of shader ... failed`** lines in same finished job console. Cause: **cross-stage incompatible uniform block `cb4_struct` definitions**. This is hidden error in Unity ShaderUtil; NEVER classify as shader compile success.
  - Original Shader and real game still unchanged. No Adreno pixel evidence.
- Introduced `scripts/gt_spectrum_private_stage_buffer_isolation.py` optional `stage_uniform_blocks=True`, disambiguates HLSL stage-local `cbN_struct` and `cbN` symbols solely on disposable private ShaderLab candidate, with bytewise reverse and unchanged `register(bN)`; NOT original Material parity.
- Introduced `scripts/gt_spectrum_ci_console_gate.py` + tests. **Critical:** this check must run in a **second GitHub Actions job** after Unity exits, fetch finalized first job logs with authenticated GitHub Actions REST `actions:read`, reject any GLSL link errors, internal variant failures, shader importer errors; successful ShaderUtil counts and AssetBundle bytes alone are not acceptance. Script matches timestamped runtime markers so echoed shell source cannot fake pass.
- [43285251243](https://github.com/alwansan/raf/actions/runs/43285251243) runs private uniform block rename for variant1 and the secondary log checker. **In progress at this checkpoint**, not yet proven. If it fails inspect BOTH job conclusions and safe numeric failure class. For source-authentic CBuffer symbols inspect only counters or source metadata, never print or commit private HLSL.

## Next actions (P06/M2 not complete)

1. Verify full [43285251243](https://github.com/alwansan/raf/actions/runs/43285251243) especially **strict-final-unity-console** job, do not accept first job SUCCESS alone; if checker cannot fetch logs, fail closed and fix evidence pipeline.
2. If cross-stage `cb4_struct` block still mismatches, derive exact original CB layout and stage-specific bindings from source ZIP2, implement only reversible private symbolic transform. Never guess buffer sizes or original material register bindings.
3. After *both* variant0 and variant1 Unity private compilations truly clean, test source-original index4 `m_KeywordIndices` metadata and a **single provisional seven-pass keyword-routed ShaderLab** with 2 variants per pass; current prototype `scripts/gt_spectrum_private_keyword_routed_shaderlab.py` is unvalidated; scope global/local Keyword flags unproven.
4. Verify original material GUID, texture, sampler, CB0, render-target and runtime keyword usage in same instance; integrate only after original proof, then Android full APK+OBB+XAPK and device pixels.
5. Foam Global 2 original Passes and water compute kernel index6 still missing source-to-phone proof; 770 material Dummy documents remain and phone invalid-pass baseline is still open. The full native [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) older snapshot was in Unity at last check; check live status before building/duplicating.

## Recovery

Read `clients/GT/RESTORE_AR.md`, `RESTORATION_PLAN_AR.md` + JSON, `state.json`, `SUMMARY_AR.md`, `MEMORY.md`, this session. Work only on `feature/android-native-port`. Update all after each proved milestone and accurately separate source validation, private Unity acceptance, game integration and phone pixel evidence.
