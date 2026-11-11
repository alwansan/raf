# T2 WATER-001 — extra-resource lifetime regression
session_id: 20261111T2220Z-T2-scheduled-extra-resource-r8m3
origin: scheduled
baseline_sha: d53f044d8f80e139f9a3a27e10c14bd04e3c90cb
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 successful world/save/re-entry, water FFT errors remain
resumed_from: clients/T2/sessions/20261111T2019Z-T2-scheduled-lifetime-v9c4.md
scope: work/20261111T2220Z-T2-scheduled-extra-resource-r8m3.md
result: Added three targeted regression scenarios: unclosed extra allocation rejected, released extra allocation accepted, unclosed second write rejected. No runtime producer and no Unity evidence.
verification: source-only tests added, not executed in this tool environment; CI confirmation pending. Existing validator implementation already enforces these cases.
next: Run targeted Python tests; then integrate trusted Unity event capture in unified mini lab with T5 and match Foam CB0/ShaderLab to original.
readiness: WATER-001 OPEN; NOT_READY 0/3.
