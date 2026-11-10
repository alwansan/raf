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
