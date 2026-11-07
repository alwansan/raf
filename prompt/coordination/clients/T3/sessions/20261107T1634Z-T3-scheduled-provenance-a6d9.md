# T3 scheduled session 20261107T1634Z-T3-scheduled-provenance-a6d9

origin: scheduled
track: RENDER-002 / ASSET-RESTORE-001
status: IN_PROGRESS; NOT_READY
work: prompt/coordination/work/RENDER-002/T3-20261107T1634Z-T3-scheduled-provenance-a6d9-metadata-source-contract.md
work_commit: 0dcd1a557d50bcee7deddec95646ea4058aa5532

## Owner-first evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. Artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628: owner confirmed world enter/save/exit/re-enter; package publication failed, and white hand/raft, square smoke, lighting issues persist. CL fixed snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 linked in report. Its water pass/FFT log counts belong to T1/T2; physical mouse T4 and Resolution/buttons T5. No new device evidence inferred.

## Recovery and checks
Read AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/PROMPT_AR.md, OPERATING_MODEL_AR.md, CHAT_AND_SCHEDULE_AR.md, clients/T3/state.json and MEMORY.md. Previous T3 bounded original/export CI41939404454 (227/227 TexEnv UV) and CI41940350604 (150/150 RGBA) did not reveal loss for selected 41 materials. Later RGB comparison CI41968665857: 106 texture pairs, 30 RGB drift; per-pair format and sRGB unavailable in public aggregate. Previous T3 classifier commits and last session 20261107T1528Z-T3-scheduled-cross-strata-n3f6.md referenced by current chat.

Fetched current script/tests via GitHub connector: scripts/t3_rgb_drift_strata.py blob eeb7c21703d01164a8c71c84412e18d49f13e7ca, tests/test_t3_rgb_drift_strata.py blob 9645b1144c9871ed01f8ad064b0c22a7ef4bac6a. The mounted local snapshot is older: five tests PASS; cannot claim expanded published tests passed. Container git ls-remote failed due DNS (github.com unresolved); connector reads and scope write succeeded. No new Actions or device test run; no raw assets shared.

## Finding
Current classifier requires private per-pair metadata, and aggregate reports cannot satisfy --require-drift-metadata. Material pointer/UV/RGBA parity in selected source is not proof of correct shader pass/variant or Android pixels. Root cause of white objects and square smoke remains unproven. No gameplay changes or fake fixes made.

## Next
Fetch current Actions status and T3/T1/T2 live scopes, then implement per-pair private export instrumentation on SHA-verified ZIP2 if no equivalent active experiment; run exact current tests before dispatch; map source Shader PPtr and ParticleRenderer alpha/blend to device symptoms. RENDER-002 OPEN/NOT_READY. Preserve .meta/GUID/.rgd, Settings and audio.
