# T2 session 20261111T1522Z-T2-scheduled-rt-capture-contract-k4p7
session_id: 20261111T1522Z-T2-scheduled-rt-capture-contract-k4p7
origin: scheduled
resumed_from: clients/T2/sessions/20261110T1923Z-T2-scheduled-evidence-cli-ci-q8v4.md
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42058825739; CL@520c4cf
baseline_sha: 13b3a859bcf1cf574971c70c352a39c7843184e6
scope_commit: a0dde066fdff6b670d35588af35b3b910dac2345
issue_id: WATER-001
result: Added an isolated fail-closed parser and regression tests for same-frame, same-capture opaque runtime RenderTexture tokens. It distinguishes token match from mismatch, and explicitly leaves original provenance and Android pixels unverified. No runtime hook is installed, so there is no real capture and no verified RenderTexture identity yet.
verification: source-only unit tests must run in CI or Python before claiming PASS. No Unity/native build or phone test.
next: instrument actual Foam pass0 destination and pass1 source in the same Unity frame, record a collision-resistant per-lifetime token with source build SHA, verify provenance and rerun gate. Then link CB0 and ShaderLab; coordinate T1/T3.
readiness: WATER-001 OPEN, NOT_READY 0/3.
