# B44 — 20261104T2059Z-B44-f0ac

Goal: RENDER-002, find and repair a proven original Material color/tint/texture SavedProperties loss in Unity export/restore without changing shader authenticity. Do not overlap B47/B49 ShaderLab pass integrity, B48 FFT kernel identity or B50 local Steam dependency.

Initial base HEAD: 4072288020d7a42daf6d235af6549f8b43d89132; live branch feature/android-native-port. Source ZIP2 pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385; archive payload validation unresolved; do not use unverified archive bytes. Owner phone game APK86 from run https://github.com/alwansan/raf/actions/runs/41812889049; CL review: https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/coordination/B_TEAM/REVIEW_2026-11-04.md (water invalid passes/kernel; white visuals; no mesh-loss inference). Current progress NOT_READY 0/3. Audio and Settings owner-confirmed and must not change; touch deferred.

Read: B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, SUMMARY.md, REVIEW_2026-11-04.md, TEMPLATES.md, RESTORE_AR.md; AGENTS.md, CURRENT_OWNER_REQUIREMENTS, prompt/README.md, CONTINUE_RAFT_AR.md, STATUS.md; ZIP2_SOURCE_PROVIDER; W1/W4 water/build evidence. B47/B49 working water pass validation, B48 FFT identity, B50 Steam.

Hypothesis under test: an exported Material losing concrete SavedProperties color/texture information can whiten meshes independent of shader pass count; distinguish loss in original-to-export serialization from truly missing original custom shader. Do not claim root cause until evidenced. Scoped intended files: targeted script/tests and coordination records. Will check existing W2/W3 audits before duplicate work. No original raw assets/bytecode published.

Checkpoint at start: plan recorded; no code changed, no new Actions runs or device verification. Next inspect existing material-property instrumentation, then implement verified preservation or a fail-closed test to detect concrete loss.
