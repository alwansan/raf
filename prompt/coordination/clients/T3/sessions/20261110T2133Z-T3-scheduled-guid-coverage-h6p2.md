# T3 session 20261110T2133Z-T3-scheduled-guid-coverage-h6p2
origin=scheduled
issue=RENDER-002
status=SOURCE_FIX_COMMITTED_TESTS_UNVERIFIED
resumed_from_sessions=20261110T2030Z-T3-scheduled-guid-multiline-k4v9;20261110T1931Z-T3-scheduled-guid-regex-proof-q5m8
work=prompt/coordination/work/RENDER-002/T3-20261110T2133Z-T3-scheduled-guid-coverage-h6p2.md

## Owner evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628, phone world/save/exit/reentry confirmed; white hand/raft, square smoke and lighting remain open. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57, water errors 23884/39132 and FFT errors 3850/6026 in two sessions. This cycle did not independently fetch original CL image binaries or logs. T4 owns physical mouse; T5 owns resolution/layout. Latest AGENTS and owner instructions also specify shared mini lab policy dated 8 Nov.

## Source-only change
Observed scripts/t3_unity_guid_link_audit.py silently skipped Unity YAML and .meta files >32 MiB without exposing incomplete coverage. Registered scope commit e1f33cdc8c11ebeda9c81d33538b1c9642565642, changed audit counters and coverage boolean at e7f55228e09ac5433a018969d721a6568e11ad59, added two source-free size-coverage tests at a34035df515b24a242fedb765045a53c0680b0f2, work checkpoint 6f89deccd5e5682f21e9da4328c2cf488a49ab18. Existing Unity resources, .meta, shaders, .rgd, sound, Settings, mouse and resolution untouched. No CI or APK dispatched. This is a diagnostic reliability improvement, NOT a game graphics fix.

## Verification and next
Test files are committed but not executed; do not claim PASS. Run python3 -m unittest discover -s tests -p 'test_t3_guid_audit_oversize_coverage.py' and the existing GUID suite on live HEAD. Then run authentic bounded ZIP2/export audit, recording skipped-file counts and joining smoke ParticleRenderer->Material->Shader->Texture with blend/alpha/ZWrite and phone image. Check Actions/other T scopes before any expensive run; do not repeat prior 41-material UV/RGBA/keyword parity. RENDER-002 OPEN; NOT_READY 0/3.
