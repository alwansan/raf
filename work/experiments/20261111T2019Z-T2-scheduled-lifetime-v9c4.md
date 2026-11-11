# T2 WATER-001 — runtime RT lifetime evidence contract
session_id: 20261111T2019Z-T2-scheduled-lifetime-v9c4
origin: scheduled
baseline_sha: 019ead087d5b31a34bec2ae3ecc2cf836281d1d4
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL@520c4cf; Actions 42058825739
resumed_from: clients/T2/sessions/20261111T1723Z-T2-scheduled-runtime-rt-ci-b8n4.md
experiment_key: T2-FOAM-RT-LIFETIME-V1
hypothesis: Matching opaque tokens alone does not establish a resource remains live between pass0 write and pass1 read. Require allocation, ordered write/read, release boundaries in a single instrumented capture.
files: scripts/t2_foam_rt_lifetime_gate.py; scripts/test_t2_foam_rt_lifetime_gate.py; clients/T2/sessions/20261111T2019Z-T2-scheduled-lifetime-v9c4.md
shared_resource: none; source-only Python, no Unity build. T3 shaders, T4 mouse, T5 mini APK untouched.
status: planned; this source-only tool cannot attest that Unity emitted the events.
