# T3 20261107T1329Z-T3-scheduled-format-sentinel-r5c8
origin=scheduled
track=RENDER-002
status=SOURCE_PATCHED_PENDING_EXACT_CI
resumed_from=20261107T1233Z-T3-scheduled-drift-ci-audit-m6q2.md
base_sha=717bacf220119cb1508b9fe08723e7bdc199902b
scope_sha=e2fbbf70b24572babc8662b937072bed62e060a3
source_sha=911fe3a9c48a3c62b548f4b9299a72f0362a5462
test_sha=00bc7520e7ce7bff9f1c2a3b9ab96f151fa40003
head_before_session=00bc7520e7ce7bff9f1c2a3b9ab96f151fa40003

## Evidence and actual change
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS, CURRENT_OWNER_REQUIREMENTS, STATUS, T_TEAM protocols, prior T3 session and source classifier; read current Actions and HEAD. No active/queued runs among latest branch results. Prior phone artifact 42058825739 confirms limited world/save/reentry, not white rendering fix. Prior real Texture2D export 41968665857 reported 30 RGB drift / 76 exact of 106 but aggregate-only reports cannot identify per-pair format/sRGB. Current classifier accepted a literal format string 'UNKNOWN' (including mixed case) as nonmissing metadata, bypassing --require-drift-metadata. Source patch canonicalizes that sentinel, and new regression tests three case variants and rejects missing drift metadata. Independent scope: prompt/coordination/work/RENDER-002/20261107T1329Z-T3-scheduled-format-sentinel-r5c8-format-sentinel.json. No game assets modified, no CI dispatched.

## Verification and limitations
Three synthetic sentinel variants passed in a locally reconstructed equivalent Python classifier; local network cannot resolve github.com, so exact published-source Python tests are **not yet executed**. Do not call this CI-verified. The real private pair manifest remains missing. This change is a safety guard only, not Android pixel restoration. No original assets, private data, .meta, GUID, .rgd, Settings, sound, mouse or native workflows touched. T4 mouse and T5 Resolution/UI remain separate.

## Next
Run exact published `PYTHONPATH=scripts python3 -m unittest discover -s tests -p test_t3_rgb_drift_strata.py` when CI/checkout available; retrieve private per-pair original format and sRGB metadata from authenticated ZIP2 export and classify the 30 drift pairs. Then trace affected Material/Shader/ParticleRenderer against CL images. RENDER-002 OPEN / NOT_READY. Trial build vote unchanged (no integrated device-facing fix).
