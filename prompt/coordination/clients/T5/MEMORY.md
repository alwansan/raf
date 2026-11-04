# T5 — integration and execution validation memory

Session: 20261104T2357Z-T5-b12-fixture-7e2. Generation T-2026-11-05, branch feature/android-native-port (only writable). This is a new T5 identity, not B12/B18.

## Live handoff and provenance
Read T_TEAM/PROMPT_AR, README, OPERATING_MODEL_AR, SOURCES_AND_ACTIONS_AR, MIGRATION, LEGACY_HANDOFF, TEMPLATES; AGENTS, ZIP2 provider and source context. Baseline known audited SHA 58047d3b293f04547e36536518fd936ad328f4d1; branch has additional commits, so use fresh file blob SHA and update/ref leases before writes. Canonical evidence B_TEAM/issues, T_TEAM index. Legacy B12 bounded snapshot CI41929419050 PASS, B18 new loaded compute helper later merged, B12 latest CI41933025319 FAILED. Last actual game APK86 from d181ee7152580f49ee0b41dfd05fa2bfdacfafe5; no new phone confirmation, NOT_READY 0/3. Original ZIP2 source pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385. CL review 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29 (historical evidence).

## Active work
Work INTEGRATION-001/T5-20261104T2357Z-b12-fixture. Exact production scene snapshot harness scripts/b12_scene_render_harness.py extracts everything from OriginalQualityStateSnapshot to ReportSceneShaderSnapshot. New B18 LoadedComputeShaderSnapshot helper occurs in between; exact production coroutine invokes it. CI41933025319 failed on missing C# stub ComputeShader, Resources, Encoding, not a proved Unity or gameplay bug. B12 previous production bounded coroutine passed 8 synthetic .NET cases, before new helper insertion. Correct the harness to execute BOTH original production methods with stand-in read-only Resource API, capture water and render logs separately, preserve bounds assertions and add negative/no-dispatch checks. Production code must remain unchanged. No LFS/raw original assets, audio, working Settings, deferred touch, native request or gameplay rewrite.

## Checkpoint
Status: plan registered before implementation. Next: patch harness with C# stub and explicit helper assertions; run local Python controls; use independent isolated CI (existing B12 workflow trigger via path if available); record errors and evidence, never claim device success from managed tests.
