# T2 scope — 20261111T2220Z-T2-scheduled-extra-resource-r8m3
origin: scheduled
baseline_sha: d53f044d8f80e139f9a3a27e10c14bd04e3c90cb
issue: WATER-001
experiment: T2-FOAM-RT-LIFETIME-EXTRA-RESOURCE-REGRESSION
files: scripts/test_t2_foam_rt_lifetime_gate.py; clients/T2/sessions/20261111T2220Z-T2-scheduled-extra-resource-r8m3.md; work/20261111T2220Z-T2-scheduled-extra-resource-r8m3.md
hypothesis: An otherwise completed Foam pair must not mask an unclosed additional allocation/write. Current validator already rejects this, but regression coverage is absent.
shared_resource: none; no Unity/CI build triggered.
taken_over_from: clients/T2/sessions/20261111T2019Z-T2-scheduled-lifetime-v9c4.md
owner_device: docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/reentry succeeded, water remains open.
coordination: T1 FFT, T3 visuals, T4 mouse, T5 resolution and shared mini lab; no overlap in source files.
