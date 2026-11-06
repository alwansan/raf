# T3 scheduled — native shader dummy audit

session_id: 20261106T1429Z-T3-scheduled-native-dummy-audit-a83f
origin: scheduled
resumed_from_sessions: 20261106T1332Z-T3-scheduled-particle108-handoff-6c9e; 20261106T1230Z-T3-scheduled-source-gate-7e4c
track: RENDER-002
status: OPEN / NOT_READY

## Evidence newly inspected
- Owner device feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: actual phone entered/saved/reloaded world on artifact 42058825739; square smoke, white raft/hand and lighting remain uncorrected. This is not proof of an individual emitter identity.
- Read live scripts/t3_shader_identity_gate.py and tests/test_t3_shader_identity_gate.py; 13 tests exist; workflow 42218286983 structural-gate completed success, not shader authenticity.
- Independently inspected completed GitHub Actions job 127909618354 logs for run 42223071341 (not only its success status). Native post-restorer audit reports 731 exported Material docs, 511 custom shader material docs, all 511 linking dummy shader, 220 Unity built-in material docs, 126 exported ShaderLab files all 126 with DummyShaderTextExporter marker, 54 distinct referenced custom shader targets all dummy, and zero material docs using non-dummy shader. These are selected exported scope counts, NOT whole installed APK and NOT proof of GPU pixels.
- The same run's original 41 Material source/export comparison matched 41 shader pointers and 10 typed shader targets; 9 custom ShaderLab targets and 1 engine transport target. The 9 selected shader files have balanced braces and program-shaped passes, but program shape is not authenticity.
- Particle108 joined to original Shader48 from six scenes: 108 renderer slots; dummy before and after TMP/PostFX/volumetric restorers. The 108 slots are not proven to be the phone square-smoke emitter.

## Engineering decision
Do not spend another cycle on the structural-link regex or redo same-source parity. Existing evidence makes replacement of original compiled shader programs/variants (with preserved GUID, blend/alpha and texture semantics) the next substantive target; no random material re-linking. Prior 89/89 internal TexEnv pointers and 150 RGBA slots matched in their authenticated 41-material subset, with 25 external references unverified. T1/T2 handle water shaders; T3 handles non-water material/particle shader authenticity and phone image mapping. No Unity build, release, or code changes initiated here.

## Limits / next executable action
No current artifact payload or private original compiled shader programs available to this run for a proven shader replacement; no source asset edited. Next cycle: inspect existing private Particle108 Vertex/Fragment pair mismatch trace and use SHA-pinned private source staging to identify missing semantic/resource bindings for 2/4 incompatible pairs, then generate one testable, GUID-preserving non-dummy ShaderLab candidate without publishing raw game assets. Test Unity compile and phone pixels separately. Coordinate expected SHA and scope before any shared changes.

Evidence: https://github.com/alwansan/raf/actions/runs/42223071341 ; https://github.com/alwansan/raf/actions/runs/42218286983 ; https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md
