# T3 chat 2026-11-09 — original smoke34 → same-instance ShaderLab comparison

- session_id: `20261109T1913Z-T3-chat-smoke34-sameexport-v5m8`
- origin: `chat`
- resumed_from_sessions: `20261109T1857Z-T3-chat-smoke34-source-pass-q6n4`, `20261109T1829Z-T3-scheduled-smoke-extraction-contract-v6p2`.
- initial base_sha: `fd8cd4603f77c0f80560afc232875db200db58dd`
- sole writable branch: `feature/android-native-port`.
- work claim: `prompt/coordination/work/RENDER-002/20261109T1913Z-T3-chat-smoke34-sameexport-v5m8.md` commit `a485ac30016f22f7f864dfc0b1d39192ae8a39f5`.
- issue: `RENDER-002`, still OPEN/NOT_READY 0/3.
- experiment_key: `t3-authentic-smoke34-unique-private-shader48-w1b02-sameinstance-shaderlab-quality-sha15964ea8-6scenes4owners-v1`.
- resource_key: `asset-ripper-source-export-T3-smoke34-12-provider-readonly-standalone`.
- intended_files: only new T3 script/test/workflow, own session/work/event/experiment/report.

## Restored original verified baseline
[Original SHA-pinned Pass CI42679312674](https://github.com/alwansan/raf/actions/runs/42679312674) PASS (not Android): six original scenes, four SHA owners, 17 smoke-name GameObject ParticleSystemRenderers -> 34 original Material slots -> one source-authenticated Shader48 distinct from equal-rank fire Shader48. One SubShader/one Pass: Color Blend ALPHA_DEPENDENT, Alpha Blend ALPHA_DEPENDENT, ColorMask RGB, ZWrite OFF, ZTest ENABLED_NUMERIC, Cull OFF; regular translation rejected selective RGB, opt-in accepted. The phone's actual square-smoke Shader identity and runtime program remain UNKNOWN.

## Team/dependency scan
At start 2026-11-09 19:10 UTC latest 25 Actions had no running same-export smoke experiment; T3 scheduled 18:29 scope wrote independent extraction contract but no CI. T1 FFT, T2 Foam, T4 mouse, T5 owner SAF on other paths. New workflow uses separate concurrency/resource; no Unity, no full-game or shared mini build, and no touch to T1/T2/T4/T5 files. Single immutable ZIP2 source @15964ea8f246b6e076ce26b60931ee2e1a9a2385 and public AssetRipperCLI source @036098ab525a3f9f693dc101edeb21faad4d32d8, no proprietary output published.

## New actual engineering
- `scripts/t3_smoke34_sameexport_shaderlab.py` introduced [2c4abf6](https://github.com/alwansan/raf/commit/2c4abf6c3165a350442d85c9f17102d925bcdafc), with private original six-scene source graph selection by class199→class21→class48 and W1/B02 one export-instance exact Shader48→GUID→.shader.meta→.shader. Generic classification records dummy/no programs/Pass count and lexical ColorMask tokens only, marks active Pass and Android pixels NOT proven.
- `tests/test_t3_smoke34_sameexport_shaderlab.py` [3f5586e](https://github.com/alwansan/raf/commit/3f5586ee26d28c167adb324cd5045497cf0d24b2) contains ten source-free negative/positive controls for exact W1/B02 trace, duplicate GUID, equal-rank wrong-target, missing shader text, dummy exporter, incomplete program, lexical RGB and no visual assertions.
- `.github/workflows/raft-t3-smoke34-sameexport.yml` [e48685f](https://github.com/alwansan/raf/commit/e48685ffd5faf4ee0594602649a1dc4736e736e9): SHA-pinned 12 original providers (6 scenes/4 shader owners/2 globals), real AssetRipper optional W1+B02 trace, 43-minute isolated runner, only JSON safe artifact, fail-closed result status.
- Initial [CI42681627370](https://github.com/alwansan/raf/actions/runs/42681627370) failed before export: source script syntax `if` missing close parenthesis. Fixed in [8da47b9](https://github.com/alwansan/raf/commit/8da47b91e569b77d6b0fbfc46e7cb532cf8a0206). It was a T3 scripting bug, not original data evidence.
- [CI42681729932](https://github.com/alwansan/raf/actions/runs/42681729932) failed source-free 2/10 lexical parser fixtures: ShaderLab directive immediately after `{` was missed by line-only matcher. Corrected scope-sensitive lexical scanner and raw escaping in [78826ae](https://github.com/alwansan/raf/commit/78826ae4333b0b401c7170350a7aeaa67b13583d). An intermediate uncorrected double escape CI42681869909 failed; not source-export evidence.
- [CURRENT CI42681908313](https://github.com/alwansan/raf/actions/runs/42681908313) on **78826ae**: source-free identity/export tests PASS, checkout public tool PASS; compiling pinned W1/B02 exporter in_progress at last look. Later original SHA, actual source exporter and same-ShaderLab output are still pending. Do not call READY/PASS on original export until inspected.

## Safety / next steps
Monitor current 42681908313 job steps. If successful, take bounded report `export_shader_status` (ACTUAL_DUMMY_SHADER_TEXT_EXPORTER vs PROGRAMMED_STRUCTURAL_PASS_NOT_AUTHENTICITY etc.), number of real ShaderLab Passes, lexical ColorMask presence with active Pass still UNKNOWN, compare evidence to actual original pass. If export fails, record exact stage without raw error/asset paths, then adjust only own script/workflow if warranted. Preserve installed shared lab and full Unity game; do not publish original shader or guess repair. Save final status in this session + experiment + B_TEAM event; mark work completed/waiting_ci appropriately for scheduled T3 pickup.
