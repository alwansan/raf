# T4 session 20261107T0538Z-T4-scheduled-artifact-lease-m7q4
origin: scheduled
status: completed_scope / waiting_external_artifact_preservation
baseline_sha: 278485fdf2621e0954b606895e578ef0ee30d6e7
work: prompt/coordination/work/20261107T0538Z-T4-scheduled-artifact-lease-m7q4.md
work_commit: a1d61761edabc2820d5489f17e45542e6248df04

## Evidence and decision
Read docs/DEVICE_FEEDBACK_42058825739_AR.md and team instructions. Owner-confirmed device success: world entered, saved, exited, and re-entered on 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628). Keep LOCAL-005 open for regression testing and do not transfer this proof to newer APKs.

GitHub API artifact query for https://github.com/alwansan/raf/actions/runs/42296450023 at 2026-11-07 05:38 UTC: signed checkpoint 13550196498 (2,974,171,581 bytes, expires 2026-11-09T23:48:15Z); Android delivery 13549514149 (5,948,365,703 bytes, expires 2026-11-09T23:49:06Z); both expired=false. These are archival containers, not verified installed APK/OBB. Run source a1737bd7 differs from live branch baseline. Latest releases query returned LogRaft tags; no proof of Raft Android release was found in those latest entries.

## Scope isolation
No native workflow, Unity, Android input source, .meta, .rgd or shared status modified. No duplicate CI, cancellation, secret access, device execution, or claim of successful release. Mouse capture and Raft cursor remain device-unverified; T5 owns release/Resolution/button layout while T4 owns physical mouse integration and world regression evidence.

## Next
T5: preserve both expiring archives before Nov 9 UTC; inspect signed APK/OBB and manifest provenance, then provide installation candidate SHA. T4: verify Android pointer capture in gameplay, relative movement at edges, Raft cursor in menus, loss-of-focus/unplug release, Android navigation accessibility, keyboard retained, world save/reopen .rgd. Coordinate before touching overlapping source. Keep INPUT-005 open until actual device proof.
