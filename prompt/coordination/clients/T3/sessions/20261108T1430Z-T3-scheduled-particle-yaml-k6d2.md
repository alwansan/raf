# T3 scheduled session — 2026-11-08 14:30 UTC

- session_id: 20261108T1430Z-T3-scheduled-particle-yaml-k6d2
- origin: scheduled
- resumed_from: 20261108T1326Z-T3-scheduled-audit-ci-n4q8
- initial HEAD: 7355730d3cd131aee17af7fe9f506d5230035b6c
- work reservation: 124ddbad4686c1c047ecd06fc3125bc31352bbb5
- tool commit: ee023697f7a47bfdedef712c835e309d5dd4f1ab
- tests commit: dedddfbea53b23002b3fad90b643454cb121fc08
- scope: RENDER-002 / source-only ParticleSystemRenderer material PPtr census
- files: scripts/t3_particle_renderer_yaml_audit.py; tests/test_t3_particle_renderer_yaml_audit.py
- experiment_key: particle-renderer-yaml-pptr-aggregate-v1-source-only

## Verified context
Read owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md first: world/save/reopen is confirmed only for artifact 42058825739, while white raft/hand and square smoke persist. CL image links and LF summaries are in the report (23,884 water-pass / 3,850 FFT-kernel errors for 220911; 39,132 / 6,026 for 230108). No raw image pixel examination or CL log parsing performed this cycle. Source-only T3 audit CI 42485092438 succeeded 40/40 on 2ba593a4. HEAD at scope start 7355730d. No duplicate native build requested.

## Engineering result
Added a new standalone, read-only, aggregate-only Unity YAML scanner for classID 199 ParticleSystemRenderer. It counts null, external GUID, local and ambiguous material PPtrs; empty, missing and malformed material arrays; skips symlink inputs; never emits GUIDs, names or paths. Two synthetic fixture tests (three pointer categories and empty/malformed arrays) passed in local isolated Python before publication. This is a first-stage particle chain triage, NOT proof of Material→Shader→Texture validity, Blend/Alpha or Android pixels. Do not attribute smoke squares to any pointer category without running on authenticated original and exported tree.

## Next
Run published tests in CI or local checkout; authenticate ZIP2 original export input and run census on a bounded genuine prefab tree. Then compare renderer material identities against actual Material→Shader→Texture with shader keywords, blend and alpha. Respect T1/T2 shader and T4/T5 input/display scopes. RENDER-002 OPEN, NOT_READY. No Unity, raw asset publication, .meta/GUID, audio, Settings, touch, save or XAPK edits.
