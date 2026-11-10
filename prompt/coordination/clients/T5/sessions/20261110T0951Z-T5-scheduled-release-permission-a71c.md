# T5 scheduled checkpoint — 20261110T0951Z-T5-scheduled-release-permission-a71c
origin: scheduled
started_utc: 2026-11-10T09:51:05Z
resumed_from_sessions: 2026-11-10 prior scheduled delivery investigation (last reported ea2b0d6), prompt/coordination/clients/T5/state.json (older chat reference), and 2026-11-09 R5 shared Mini evidence.
branch: feature/android-native-port
scope_commit: b933421a4b49492dfaf2a7bc87f6177e03e6a743
work: prompt/coordination/work/20261110T0951Z-T5-scheduled-release-permission-a71c.md

## Concrete result / competing hypotheses
- Read docs/DEVICE_FEEDBACK_42058825739_AR.md: source e9c358eda01785b65e4eb14f18723da426635628, owner world/save/re-entry PASS only on that artifact. LogRaft 220911-559: 23,884 water-pass errors, 3,850 FFT kernel errors, 1 OBB GUID warning, 1,333 cursor RGBA32 warnings; 57 FPS samples mean 22.29 and min 3.02; screenshot HUD 18.27 FPS p95 82.82ms. No new phone test.
- Previous T5 log extraction identified gh release create HTTP403 Resource not accessible by integration after artifact download success. Inspecting the CURRENT workflow shows publish-early-test already requests job permissions contents:write/actions:read AND selects GH_TOKEN: secrets.RAFT_RELEASE_TOKEN || github.token. Thus simply adding permissions or the fallback is a duplicate fix and cannot prove the historical failure resolved. Token presence, repository Actions policy and effective permission for a new run remain unverified. Do not print secret.
- Workflow already validates delivery.json package, run number and part/full SHA256 before publishing; validates published asset names/sizes after release. This does NOT establish APK manifest versionCode, OBB internal name/GUID or actual device mounting. The historical 403 does not invalidate reconstruction.
- Owner update Nov8 supersedes Mini strategy: one shared Mini, R5 build CI42691609924 succeeded with ZIP artifact13707257362; do not build duplicate Mini. T4 owns captured physical mouse button/wheel bridge. Full XAPK still 5/5 vote, NOT_READY 0/3.

## Limits
No branch code modification, no CI dispatch, no fresh device measurements, no signed APK/OBB binary SHA comparison. Only isolated scope/session documentation committed. Historical release failure cannot be fixed merely by a second contents:write stanza; requires effective token or repository policy verification. Avoid creating release with inadequate permissions and avoid any misleading success fallback.

## Next concrete engineering step
Inspect effective repository Actions workflow permissions (including org policy) and whether RAFT_RELEASE_TOKEN has repo Contents write; use non-secret boolean capability test only when authorized. Independently acquire exact signed artifact and delivery.json, compare APK versionCode/signature, OBB filename/versionCode/size/hash against delivery manifest, and associate LogRaft with verified binary. Keep mouse changes with T4, Resolution/three right buttons source/device verification in T5 scope.
status: blocked_on_effective_permissions_and_signed_binary_evidence
