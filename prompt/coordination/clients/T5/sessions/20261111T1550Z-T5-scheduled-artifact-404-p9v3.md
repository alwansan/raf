# T5 scheduled checkpoint — 20261111T1550Z-T5-scheduled-artifact-404-p9v3
origin: scheduled
base_sha: d9896fbbbcdcb8b0372005a15ff06dc97b7cce07
resumed_from_sessions: 20261111T1448Z-T5-scheduled-artifact-retention-m4q8; 20261111T1348Z-T5-scheduled-ledger-identity-q7m2
work: prompt/coordination/work/T5/20261111T1550Z-T5-scheduled-artifact-404-p9v3.md (commit f79e18f463d5fe8f13fc79ef6ad1a9914dadce95)

## New verified result
GitHub connected artifact download endpoint on 2026-11-11 returned HTTP 404 Not Found for IDs **13441227298** and **13441766832** individually. Prior 400 from generic fetch was endpoint allowlist only; this is new API evidence that these checkpoints are not presently retrievable through the current connection. Cannot determine whether expired, deleted, inaccessible by permission, or misidentified. The owner report says successful world/save/re-entry on artifact run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628; that fact remains untouched. The run-scoped four tiny diagnostics are not signed delivery bytes. No APK/OBB versionCode, SHA, or actual on-device build mapping can be claimed.

## Coordination and limits
Branch observed HEAD d9896fbbbcdcb8b0372005a15ff06dc97b7cce07. Recent workflow list showed T2 ledger run 43028966025 failure, T5 right-panel source test 42998052750 success; no Unity or phone test triggered. T4 owns physical mouse; no overlap or changes to Unity, UI, Settings, CL, shaders, save files, or artifacts. Prior LogRaft owner estimate avg 22.29 FPS over 57 samples, HUD 18.27 FPS/p95 82.82ms, not new GPU measurements.

## Next
Locate an immutable authorized signed-output mirror/release or coordinate a single rebuild of pinned source with existing signing/packaging workflow; inspect package manifest and OBB bytes, compare versionCode, OBB basename/size/SHA256, and only then associate LogRaft. Independently pursue original Resolution Settings event binding with isolated source evidence. NOT_READY 0/3.
