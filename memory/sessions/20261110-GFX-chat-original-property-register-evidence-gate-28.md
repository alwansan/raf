# GFX-LAB 20261110-GFX-chat-original-property-register-evidence-gate-28
- session_id: 20261110-GFX-chat-original-property-register-evidence-gate-28; origin=chat; resumed_from=20261110-GFX-chat-authenticated-cb-byte-address-27.
- base_sha=38dc5882020d6f6c1932c130a711f92eeeaf8f2c, only writable experiment/android-graphics-rootcause. Read main, feature/android-native-port, ZIP2 without modifying. Source ZIP2 pinned SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385.
- experiment_key=GFX-MULTI-054; issue_id=RENDER-002; resource_key=authentic-original-Sh a der48-property-register-link-evidence-gate
## Baseline
- GFX-MULTI-053 CI42850106500 367 tests; original source b#/vec4 range 208/208 with actually loaded SPIR-V, source b-register name and strict vec4 UBO layout 66/66. No independent original Unity Material property→DXBC resource or CB member map.
- Earlier source-private GFX020/021/022/037 separately verified material parameter metadata, serialized source text, all 1435 source stage rows/1275 unique DX11 stage programs, RDEF/debug chunk availability. But they were not cross-gated in one run against source identity drift.
## Hypothesis / checks
- Cross-audit all four existing SHA-authenticated source metadata paths on one original ZIP2 staging; compare source identities 6 models, 7 Material slots, 27 original Shader48 property names, 7 passes, 524 exact keyword/tier pairs, 1435 variant link rows and 1275 referenced unique stages. Strictly guard contradictory counts and false positives.
- Only true directly source-proven per-variant serialized `m_Parameters` texture name→resource/sampler register+Material linkage may upgrade original property→t/s status; RDEF or debug chunks or embedded HLSL syntax markers alone only indicate potential witness and do not prove per-property mapping. No original CB byte offsets or Material values inferred from GPU resource register numeric alignment.
- Store count-only report and missing external/source witness contract. No source names, b/t/s registers, shader/GLSL/HLSL, private pointers/GUID exported. Synthetic negative fixtures test blocking, contradictions and one hypothetical directly authenticated source metadata edge. CI pending; do not assert blocked before actual original run.
## Files
- gfxlab/tools/multi_shader_property_register_evidence_gate.py
- gfxlab/tests/test_multi_shader_property_register_evidence_gate.py
- .github/workflows/gfxlab-multi054-source-property-register-gate.yml
- originalShaderRestored=false; G7–G12 blocked; no game APK or T-team edits.

## CI progress and negative control
- First [GFX054 CI42851989618](https://github.com/alwansan/raf/actions/runs/42851989618) failed **before private original source auditing** because sparse checkout omitted source-free mini-lab shader/Android script fixtures required by 9 existing Python regression cases. No original source evidence was used or interpreted in that failure.
- Workflow checkout fixed at commit `1dc6f8e346fe5155985fa7864b643b46a9ee2430` without changing proof checks or source input. Rerun [CI42852112971](https://github.com/alwansan/raf/actions/runs/42852112971) **started**; source-private cross-audits running; no correctness claim before terminal CI status, artifact and purge verified.

## Verified final outcome
- [CI42852112971](https://github.com/alwansan/raf/actions/runs/42852112971) SUCCESS, **377 Python tests**, SHA-locked ZIP2 private source staged and purged; `GFX054_ALL_PRIVATE_ORIGINAL_SOURCE_PURGED=true`.
- Four independently created source-private audits GFX020/GFX021/GFX022/GFX037 re-run under one origin and cross-checked. 6 models, 7 material slots, 27 source Shader48 properties, 21 bound material TexEnv slots, 7 passes, 524 source matched VS/FS pairs, 1435 linked subprogram rows, 1275 unique linked DXBC programs, no link/identity drift.
- Direct original Shader48 property→DXBC binding source witness **0**: serialized per-variant texture params 0 and CB binding params 0, RDEF across 1275 unique linked programs 0, alternate linked debug/reflection chunks 0, embedded authored `m_Script` absent. These source avenues cannot authenticate Material property→t/s/b or CB member byte offsets.
- This is an evidence-availability result restricted to checked SHA-pinned providers and metadata. No claim other source files/PC runtime are impossible to use. Compiler-translated SPIR-V b/t/s provenance and CB layout remains proven only for prior GFX049/GFX052/GFX053 scope, not Unity Material semantics.
- Safe count [artifact13781266865](https://github.com/alwansan/raf/actions/runs/42852112971/artifacts/13781266865), expires 2026-11-17T16:13:30Z. Private original code, property labels, register values not exported.
- Initial CI42851989618 failure = incomplete sparse checkout for source-free mini-lab tests; corrected workflow and reran full 377 tests successfully.
- Outcome `SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_CURRENT_PINNED_INPUTS`; source private `originalShaderRestored=false`, `phase_closed=false`, G7–G12 BLOCKED. Next require an independently authenticated **new** property-to-register source witness; `gfxlab/ORIGINAL_SHADER48_PROPERTY_REGISTER_CAPTURE_CONTRACT_AR.md`.
