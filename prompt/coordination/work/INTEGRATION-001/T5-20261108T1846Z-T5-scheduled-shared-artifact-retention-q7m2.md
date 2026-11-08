# T5 independent scope — 20261108T1846Z-T5-scheduled-shared-artifact-retention-q7m2
origin=scheduled; worker=T5; branch=feature/android-native-port; observed_head=876a1ef258abf3e8727514f31ac45348ea2eba80

## Scope and hypothesis
Read-only verification of shared mini-lab artifact retention and build duplication policy; no edits to Unity, T1–T4 code, .meta, saves, or CL. Experiment key: shared-mini-artifact-retention@42509945996/13628828717. Shared resource: none (read-only Actions API). Files owned: this independent work record and independent T5 session only.

## Live evidence (2026-11-08 18:46 UTC)
- Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md reviewed first: game world/save/reopen proven only on original run 42058825739, source e9c358e; not mini-lab proof.
- Shared mini-lab CI42509945996 succeeded; REST artifacts API returned artifact 13628828717 expired=false, size=77951 bytes, expires_at=2026-11-22T18:26:36Z, ZIP digest sha256:f98d32f6a78e49ba319e250234cca5ed3eb48853a760c4ec6c78950227648fa6.
- Verified current SHARED_BUILD_READINESS r2 T5=NO_BUILD; T1/T2 NEED_BUILD entries still refer to r1, which has already delivered. No new r2 qualifying integrated driver evidence observed in the readiness file. Both queued and in_progress branch Actions queries returned zero. Do not duplicate r1.
- Existing TEST_CENTER correctly identifies Artifact ZIP, not a direct APK. Prior verified inner APK SHA256 cee2df1b3bb2a1a3c8e9ab757f520040d36c5bf16d711587f7e2bc537f917472; not independently re-downloaded in this audit.

## Verdict and next action
No new build. Device validation of shared APK SAF/OBB, physical mouse and graphics is pending. Compare signed game APK/OBB only after actual phone files are available; no invented versionCode or file hash. Preserve full game NOT_READY 0/3. No CI launched, no shared files changed.
