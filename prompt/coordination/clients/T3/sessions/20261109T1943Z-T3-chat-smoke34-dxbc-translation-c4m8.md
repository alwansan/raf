# T3 chat session — authentic smoke34 original two-pair DXBC → SPIR-V private CPU translation

- session_id: `20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8`
- origin: `chat`
- branch: `feature/android-native-port` (only writable branch; no force)
- base_sha: `65e7b9c353c07927a63e405aaa8b49cd2a424460`
- resumed_from_sessions:
  - `20261109T1935Z-T3-scheduled-dxbc-handoff-k7m4`
  - `20261109T1924Z-T3-chat-smoke34-dxbc-source-p9n2`
  - `20261109T1913Z-T3-chat-smoke34-sameexport-v5m8`
  - `20261109T1857Z-T3-chat-smoke34-source-pass-q6n4`
- issue_id: `RENDER-002` — remains OPEN / NOT_READY 0/3
- scope_record: `prompt/coordination/work/RENDER-002/20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8.md`
- experiment_key: `t3-authentic-smoke34-two-keyword-paired-dxbc-vs-fs-private-vulkan11-spirv-roundtrip-sha15964-v1`
- resource_key: `original-zip2-6scene4owner-small-readonly-T3-two-pair-translation`

## Source evidence inherited without repeating a successful experiment

- [Original Pass state CI42679312674](https://github.com/alwansan/raf/actions/runs/42679312674) SUCCESS: exact original 17 smoke-name ParticleSystemRenderers / 34 Material slots / one private Shader48, distinct from 34 fire-like and 108 particle-like shader. One NORMAL pass uses original alpha-dependent color and alpha, RGB ColorMask, ZWrite OFF, Cull OFF.
- [Same-instance export CI42681908313](https://github.com/alwansan/raf/actions/runs/42681908313) SUCCESS: W1/B02 genuine original export at same Shader48 identity emits ACTUAL_DUMMY_SHADER_TEXT_EXPORTER and no lexical RGB ColorMask. This does not prove installed phone identity/pixels.
- [Original D3D11 inventory CI42683328646](https://github.com/alwansan/raf/actions/runs/42683328646) SUCCESS: six SHA scenes / four shader owners, D3D11 table 8 records, exactly 2 VS + 2 FS variants, 2 original keyword matched VS/FS pairs and 0 unmatched. Source feasibility, not compiled SPIR-V or Unity.
- T3 scheduled 19:35 [handoff](20261109T1935Z-T3-scheduled-dxbc-handoff-k7m4.md) only documented next CPU translation; did not edit source or start CI. At reservation the latest observed Actions T4 Unity input, T2 Foam, T5 mini etc did not share this resource.

## Work implemented on separate files

1. Published scope/reservation FIRST at commit [81a3cef](https://github.com/alwansan/raf/commit/81a3cef1309d188f122b5fd83f3c06905a0a990e).
2. Added `scripts/t3_original_smoke34_spirv_translation.py` at [afba7ca](https://github.com/alwansan/raf/commit/afba7caa6f459f15f0dc6bdbb0e3cfd92147d6a5). The code authenticates exact original six scenes/four owners, one normal Pass/RGB mask/alpha-dependence/ZWrite OFF, immutable source SHA and unique Shader48. It rejects duplicate/changed/missing keyword or player-bucket pairs rather than choosing approximate VS/FS. It translates precisely two private original DXBC VS/FS pairs via existing vkd3d compiler → Vulkan1.1 SPIR-V → HLSL → SPIR-V roundtrip. Captures only bounded aggregate counts for stage validity, reflections, original/roundtrip I/O equality, resource-shape equality and VS/FS interface compatibility.
3. Added `tests/test_t3_original_smoke34_spirv_translation.py` at [dc1b855](https://github.com/alwansan/raf/commit/dc1b8551501580b1189deb494f63165dc2eae8d6), ten synthetic positive/negative controls: exact identity, swapped order, keyword mismatch, duplicates, changed stage/table, invalid translator schema, failed fragment, stage IO drift, invalid reflection, public-output privacy and untrusted interface checker.
4. Added isolated `.github/workflows/raft-t3-original-smoke34-spirv-translation.yml` at [40ed30b](https://github.com/alwansan/raf/commit/40ed30bd352eb37661e3f93f0891b59ee8bf38dd). This uses immutable ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, runner ubuntu-24.04, distinct concurrency cancel-in-progress:false, 35min job budget, 10min translation bound, original data only in disposable runner temp, public artifact ONLY safe JSON. Distro tools versions are logged at runtime, not asserted cross-run bit-reproducible. No source program, private file paths, shader names/GUIDs/PathIDs, per-program hashes, GLSL or HLSL published.
5. [GitHub Actions run 42687117806](https://github.com/alwansan/raf/actions/runs/42687117806) auto-triggered by dedicated workflow, head `40ed30b...`. **At initial checkpoint:** source-free synthetic tests PASS; ZIP2 checkout/sparse SHA-original scene + four owner reassembly PASS; apt tools installation in progress. Actual original translation not classified yet, DO NOT claim CPU SPIR-V success/pixel fix.

## Checkpoint acceptance boundary and next action

- `SOURCE_ONLY_TESTS_PASS` and `SHA_SOURCE_STAGE_PASS` do not imply that any of four authentic DXBC stage translations worked. A safe final JSON may classify toolchain limits or missing reflection without claiming Unity compatibility. Even four valid CPU SPIR-V programs would NOT establish reconstructed ShaderLab render states/keywords/pass resource bindings, correct Adreno pixels, or actual phone smoke-square identity.
- Review final CI job step statuses, inspect the sanitized JSON counters if accessible, and fix only T3-owned files on measured failure. Record run/result/artifact and boundary in own experiment/event/docs, mark work `completed` or `waiting_ci` as proven. If long-running, persist run link and resume from this session; do not repeat same ZIP2 experiment.
- No changes to game assets, .meta, GUID, .rgd, sound, Settings, input, unified mini APK, XAPK/OBB, Release, owner CL or any other agent's files.


## Verified FINAL — 2026-11-09 19:55 UTC

- Initial [CI42687117806](https://github.com/alwansan/raf/actions/runs/42687117806) **SUCCESS** on commit `40ed30bd352eb37661e3f93f0891b59ee8bf38dd`, actual original stage SHA-authenticated. 10/10 new synthetic tests and 7/7 inherited inventory tests PASS; six scene/four owners SHA PASS. 4/4 authentic original D3D11 vertex/fragment stages valid Vulkan1.1 SPIR-V, 4/4 HLSL recovered, 4/4 valid roundtrip. 2/2 original VS/FS and 2/2 roundtrip interfaces compatible; 4/4 resource slot shapes equal. However 0/4 original-to-roundtrip per-stage location/type signatures identical.
- Added separate **bounded drift classifier** with strict schema/value privacy gates and 2 more negative controls on [commit 7bc1b5430ca29eb5578bc8fb284e17b6107c3d4f](https://github.com/alwansan/raf/commit/7bc1b5430ca29eb5578bc8fb284e17b6107c3d4f). An earlier attempted commit based on a moving branch lost the CAS lease; it was NOT published and the two-file patch was safely rebased onto fresh HEAD before the successful single ref update. No other T work overwritten.
- [CI42687834153](https://github.com/alwansan/raf/actions/runs/42687834153) **COMPLETED SUCCESS** on `7bc1b543...`: 12/12 new source-free tests and 7/7 prior source tests PASS, SHA six scenes/four owners PASS, real 4/4 stage original + roundtrip SPIR-V valid, both 2/2 VS/FS pairs compatible. **Drift classified:** inputs 2 unchanged / 2 remap candidates; outputs 2 unchanged / 2 remap candidates; 2 removed and 2 added location entries on each side in aggregate; 0 same-location type changes; type multisets preserved for **all 4 input comparisons and all 4 output comparisons**; source↔roundtrip resource shapes 4/4 equal. Thus the observed mismatch is location-only candidate classification, not proven semantic mapping nor a restored Unity shader.
- [CI42687117806 safe artifact 13704513572](https://github.com/alwansan/raf/actions/runs/42687117806/artifacts/13704513572) and [CI42687834153 safe artifact 13705233370](https://github.com/alwansan/raf/actions/runs/42687834153/artifacts/13705233370) contain sanitized aggregate JSON only. The latter expires 2026-11-16T19:55:10Z. No proprietary shader data, original program hash or exported source shipped.
- Permanent report: `docs/T3_SMOKE34_AUTHENTIC_SPIRV_TRANSLATION_2026-11-09_AR.md`. Both CI runs prove **CPU compilation/structural reflection only**; they do NOT prove original executable HLSL fidelity, per-semantic stream mapping, texture-alpha sampling parity, ShaderLab blend/ColorMask state installed, Unity/Android runtime output, real square-smoke identity or device visual fix.
- T3 own source/CI experiment complete; release exclusive resource `original-zip2-6scene4owner-small-readonly-T3-two-pair-translation`. **RENDER-002 OPEN, NOT_READY 0/3**. No APK/XAPK, OBB, source game asset, Unity, audio, save, Settings or touch changes.
- **Next engineering gate:** authenticated stage-level source SPIR-V→roundtrip location map uniqueness and semantic/component widths (avoid falsely mapping repeated vec4), then restore the exact shader identity program+fixed Pass state into isolated Unity test and obtain a real in-game device screenshot. T5 shared Mini and T1/T2/T4 work remain independent.
