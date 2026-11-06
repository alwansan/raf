# T3 scheduled — Particle108 causal attribution checkpoint

session_id: 20261106T1532Z-T3-scheduled-particle108-causality-8f3a
origin: scheduled
issue_id: RENDER-002
resumed_from_sessions: 20261106T1515Z-T3-chat-5mat-yamlphase-e73b; 20261106T1429Z-T3-scheduled-native-dummy-audit-a83f; 20261106T1337Z-T3-chat-particle108-propstate-62fb
base_sha: 2c0c0af7023a9e0f157b12e615e1a8545cba915a
scope: prompt/coordination/work/RENDER-002/20261106T1532Z-T3-scheduled-particle108-causality-8f3a.json
status: completed_scope / RENDER-002 OPEN / NOT_READY

## Verified and differentiated evidence

- Owner phone feedback: original artifact 42058825739 entered/saved/reopened world; white raft/hand, square smoke and lighting still unresolved. The four owner screenshot URLs and immutable CL snapshot are indexed in docs/DEVICE_FEEDBACK_42058825739_AR.md. Phone source e9c358eda01785b65e4eb14f18723da426635628, **not** current branch HEAD.
- Native actual export CI42223071341: 126/126 exported custom ShaderLab files carry DummyShaderTextExporter; 511 custom-shader Material documents reference dummy targets. These are selected export-scope results, not installed APK shader-program identity.
- Later actual private same-instance export CI42243130856, immutable SHA 0cdab0cbd0e19c868261a3cbb556a3c4adacb19f, has **5/5 Particle108 materials; 15/15 RGBA and 145/145 float32 slots MATCH**; 10/10 UV scale-offset slots MATCH; 0 integer slots measured. 108 renderer uses and the selected Shader48 remains a dummy export. This **rejects** numeric Color/Float transport loss as explanation *within these five selected original materials*; does **not** rule out texture decode, GPU blend, sampler, missing keyword/program, other materials, or lighting.
- Earlier Particle108 original source establishes 13 authored properties (2 texture, 1 color, 4 float, 6 range), ColorMask RGB, alpha Blend, ZWrite Off, Cull Off; original 4 DXBC VS/FS keyword pairs still need source-authentic translation/interface/resource validation.
- T2 recent Shader/Material negative census (HEAD 2c0c0af7) is independent; do not reinterpret a source-name or PathID negative as positive identity of photographed emitter.
- Current live Actions recent completed T5 #42243852483 success and T2 #42243762570 success; no redundant heavy export dispatched. Existing T3 source-only #42243009945 and private export #42243130856 success already settle the selected numeric-transport hypothesis.

## Causal decision and next experiment

**Reject next action:** rewriting 5 selected Material color/float/UV values or blindly relinking GUIDs. Same-instance verified data matches; such patches would be unauthentic and risk making rendering worse.

**Next discriminating experiment:** in a separate private SHA-pinned disposable Unity render harness, compare four original Particle108 keyword-pair stage interfaces and resource bindings (VS/FS varying location+type, sampler bindings, CB offsets, blend/alpha, ColorMask) against a reconstructed candidate. Export only aggregate safe stage reason codes and screenshot-level render difference metrics, never proprietary HLSL/bytecode or original asset bytes. A successful stage/link compile does not establish GPU pixel parity. In parallel, match photographed emitter to a scene/prefab particle renderer identity via authenticated CL scene event/time and renderer/material trace; 108 uses are not emitter identification.

No original game assets, .meta, GUID, .rgd, audio, Settings, T4 mouse or T5 Resolution changed. No new Unity/native/APK/OBB build or release. Work scope closes as evidence triage; RENDER-002 remains OPEN / NOT_READY. Next T3 chat should start from this checkpoint and 1515Z chat genuine five-material result.
