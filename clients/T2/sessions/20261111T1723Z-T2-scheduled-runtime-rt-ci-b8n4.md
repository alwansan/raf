# T2 session 20261111T1723Z-T2-scheduled-runtime-rt-ci-b8n4
session_id: 20261111T1723Z-T2-scheduled-runtime-rt-ci-b8n4
origin: scheduled
baseline_sha: 8981fe2fb6ba7800f2f033f9cacae44b58c48269
scope_commit: 3b580271c973737e32660db763bc4c40785a0f19
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42058825739; CL@520c4cf
resumed_from: clients/T2/sessions/20261111T1522Z-T2-scheduled-rt-capture-contract-k4p7.md
issue: WATER-001
experiment: T2-FOAM-RT-CONTRACT-CI-20261111
change: Added isolated 5-minute source-only CI workflow to execute the previously unrun runtime RenderTexture capture-token parser regression. Expanded tests for capture/frame/SHA/token boundaries, duplicate nested keys and size/type rejection. Does not alter Unity/game shaders, T3/T4/T5 files, or the shared mini APK.
verification: CI pending after commit; source-only parser tests are not real Unity instrumentation.
next: Check new workflow result and fix any failure without duplicating runs. Then instrument same-frame resource lifetime in unified Android lab with T5 and prove original pass identity; compare CB0/ShaderLab.
readiness: WATER-001 OPEN, NOT_READY 0/3.
