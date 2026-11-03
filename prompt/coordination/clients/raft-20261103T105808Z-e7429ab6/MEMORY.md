# A9 new-session memory — raft-20261103T105808Z-e7429ab6

- Resumed from completed A9 `raft-20261103T100326Z-9df2b7ac` and verified prior profile symlink guard source `345b151d1fce59a996883b8c673930b56876fc68` and CI 41617170076 (7 new, 12 smoke successful). Earlier work remains completed, not overwritten.
- UTC registration: 2026-11-03T10:58:08.597Z. Current owner files and coordination protocol refreshed; only writable branch `feature/android-native-port`; CL read-only. No native Unity/APK/OBB/XAPK/build request/release, no tasks.
- Conflict scan: A6 owns world.sav leaf symlink/LocalSavePaths and Smoke Program; A10 original save selector completed; A8 DIAG-010; A1 water; A2 DISPLAY; A3 HAPTICS. These files are excluded.
- Independent scope: synthetic negative acceptance in `OfflineSession(string)` currently only checks non-empty; `LocalPlayerIdentity.FromProfile` requires exactly32 lowercase hex, and `LocalSavePaths` later rejects unsafe segments. This permits reporting Connected/Host for unusable profile ID. Validate identity at constructor boundary, without changing source identity mapping or .rgd schema.
- Planned files: `android-port/Runtime/Platform/OfflineSession.cs`, standalone `android-port/Tests/OfflineSessionIdentity/*`, isolated CPU-only A9 workflow. No shared workflow, Smoke or tracked game asset touched.
- Need actual red/green CI, stable-source SHA, exact evidence and limits. Final state completed only if validated; keep overall LOCAL-005 OPEN.
