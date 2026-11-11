# T2 WATER-001 — runtime lifetime audit
session_id: 20261111T2019Z-T2-scheduled-lifetime-v9c4
origin: scheduled
baseline_sha: 019ead087d5b31a34bec2ae3ecc2cf836281d1d4
scope_commit: 00da40f927a18554bc9430f8f0dd67443bf9b151
resumed_from: clients/T2/sessions/20261111T1723Z-T2-scheduled-runtime-rt-ci-b8n4.md
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md (phone world/save/re-entry succeeded on artifact; water/FFT errors remain)
experiment: T2-FOAM-RT-LIFETIME-V1
result: Added source-only strict ordered lifetime audit with regression tests for allocation/write/read/release, token reuse, aliases, JSON boundaries and nonfinite/duplicate keys. Separate from prior token-pair gate; does not touch Unity or shaders.
limits: Tests not yet confirmed by CI; capture producer not implemented or authenticated. Cannot prove original RenderTexture identity or pixels. Coordinate trusted producer with T5 shared mini lab; CB0 and ShaderLab remain open with T1/T3.
next: Verify tests with Python CI or locally, inspect live producer, then wire actual Unity events without generating synthetic proof; do not duplicate Unity build.
readiness: WATER-001 OPEN, NOT_READY 0/3.
