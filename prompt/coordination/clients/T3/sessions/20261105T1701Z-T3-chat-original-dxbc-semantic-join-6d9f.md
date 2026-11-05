# T3 chat — genuine compiled DXBC semantic/index/mask linkage

- session_id: `20261105T1701Z-T3-chat-original-dxbc-semantic-join-6d9f`; owner **T3**, origin **chat**.
- Branch: `feature/android-native-port` **only**; scope RENDER-002 OPEN, NOT_READY 0/3.
- base_sha: `f81f2bfb8ad8be058fd3079fb1f0291e712e5a9f`; work plan registered BEFORE code edits in `prompt/coordination/work/RENDER-002/20261105T1701Z-T3-chat-original-dxbc-semantic-join-6d9f.json` at `33ab7672e2fd919e4560c9ab4c60fe64caadda70`.
- resumed_from_sessions: `20261105T1642Z-T3-chat-original-vf-component-bridge-d42e` (genuine CI42068915602) and `20261105T1625Z-T3-scheduled-dxbc-contract-8f2c` (six source-free checks).
- Experiment: `T3-originalZIP2-15964ea8-sixscene-fourshaderowners-top921-Shader48-exact-4pass-DXBC-ISGN-OSGN-ISG1-OSG1-OSG5-VF-semantic-mask-private`.
- Resource: `T3-921-fourpass-original-DXBC-CPU`; no Unity/APK build.

## Reason for distinct scope

Authentic source [CI42068915602](https://github.com/alwansan/raf/actions/runs/42068915602) proved same structural SPIR-V Location+Component scalar families across four exact V/F pairs/Pass both before and after HLSL roundtrip, with no 44 input component deficits. That did **not** establish original compiled DXBC SemanticName/Index/type/register/mask identity; generated names had 0/34 and 0/29 retention [CI42062573338](https://github.com/alwansan/raf/actions/runs/42062573338). Scheduled T3 `t3_dxbc_signature_contract.py` validates pre-extracted component occupancy only. This chat integrates and preserves that unchanged code, independently parsing real compiled DXBC signature chunks and privately comparing original semantics.

## Implementation and controls

- `scripts/t3_original_921_dxbc_semantic_join.py` [commit 7ee50d74](https://github.com/alwansan/raf/commit/7ee50d746d7b35302081328a0e93469a10d57675): strictly bounded original DXBC container/chunk sizes and offsets, one ISGN/ISG1 and OSGN/OSG5/OSG1 side, 24/28/32-byte record layouts, chunk-relative semantic string offsets, register masks and source system values. Returns only safe aggregate counters, no private semantic name, bytecode, GUID or hash. Uses scheduled validator as-is, with explicit original source class48 921-use selected by six scene/four owner pins. Does **not** assert original→SPIR-V Location mapping.
- `tests/test_t3_original_921_dxbc_semantic_join.py` [commit ab49613e](https://github.com/alwansan/raf/commit/ab49613e0f16ac86853e2b7f33b4ea858739f50d): 21 synthetic format and privacy controls (including malformed chunks/names, duplicate registers, separate semantic names, mask deficits, system values, all 3 signature record widths).
- `.github/workflows/raft-t3-original-921-dxbc-semantic-join.yml` commit `059d85fd`, corrected to execute exact 21 new source-free tests at `b5beec2c`; existing scheduled six tests retained and source reader not edited. Source input ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original 6 scene/four owner SHA staging, no LFS; opt-in heavy private job only for exact scoped marker push + SHA lock.
- [CI42070932298](https://github.com/alwansan/raf/actions/runs/42070932298) **SUCCESS**, 21 new + 6 scheduled = **27/27** source-free checks; original job intentionally skipped.
- One genuine original private request marker at `f0a02d6e634e3f93ea34f82343f51e5223f07ef0`, `.github/t3-dxbc-semantic-requests/20261105T1701Z-T3-chat-original-dxbc-semantic-join-6d9f.json`. The explicitly authorized source original [CI42071059741](https://github.com/alwansan/raf/actions/runs/42071059741) was queued at checkpoint; need inspect its private job and safe aggregate result, never treat synthetic tests alone as source proof.

## Required handoff

If CI42071059741 succeeds, report **only aggregate** semantic/index mismatches, missing components, type changes and system value counts across four original pairs. A real source semantic match is neither SPIR-V location proof nor correct shading on Android. If failed, read stage/categorized output, repair precise serializer assumption without lowering source/authenticity restrictions. Preserve any unsuccessful hypothesis and no false device/P0 closure. Do not issue duplicate original job unchanged.

No game or other clients' files changed, no sound/Settings/touch development, no Actions cancelled, no source names copied into artifacts. T5 native [CI42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) and T1 Vulkan activities were left untouched.
