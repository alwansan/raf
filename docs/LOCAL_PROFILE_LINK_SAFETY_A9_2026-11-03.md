# A9 — LOCAL-005 profile identity symlink redirect guard (3 Nov 2026)

## Scope and provenance
Independent client `raft-20261103T100326Z-9df2b7ac` / session A9. Only `feature/android-native-port` modified. Original `.rgd` serialization, game code, `.meta`/GUIDs, water kernels, touch Mouse0/500ms and virtual Xbox are unchanged.

Baseline `LocalProfileStore.cs` blob `24d5f0ed157898ddefec61e6238052190e63ba93` loaded `profile.id` through `File.ReadAllText` and created the `RaftAndroid/profiles/local` path. Under ordinary Unix filesystem semantics, a pre-existing symlink to an external file containing a valid32-character hex ID resolves through the link. A small local Python fixture confirmed that file read-through behavior without using game data; it does not execute C#.

## Actual source change
[Commit 345b151d1fce59a996883b8c673930b56876fc68](https://github.com/alwansan/raf/commit/345b151d1fce59a996883b8c673930b56876fc68) checks `FileAttributes.ReparsePoint` at every app-owned path component (`RaftAndroid`, `profiles`, `local`, `profile.id`) before/after directory initialization, and again before reading the ID. Redirects fail with `UnauthorizedAccessException`. Newly absent paths continue to be created. Original `FileMode.CreateNew` exclusive claim and existing 32-character lowercase-hex validation remain unchanged.

A dedicated actual managed C# fixture `android-port/Tests/ProfileLinkSafety` covers a valid normal identity, linked `profile.id`, linked `local` directory, and linked `RaftAndroid` directory, plus external file immutability. Added one step to the existing cheap offline-platform workflow; no Unity, LFS, native artifact or release triggered.

## Verified result
- [Source-pinned GitHub Actions run 41617170076](https://github.com/alwansan/raf/actions/runs/41617170076), job 125853405998: **completed SUCCESS** for source `345b151d1fce59a996883b8c673930b56876fc68`.
- Actual managed regression emitted `PROFILE_LINK_SAFETY_PASS checks=7`.
- Existing offline platform Smoke suite emitted `TOTAL passed=12 failed=0`. Other steps in the same job succeeded, including netstandard2.1 library compilation.
- A separate local Python POSIX symlink fixture reproduced read-through of an external valid identity; it was not a C# pre-fix runtime execution.

## Limits and next work
This is a **local profile storage safety subissue only**. It does not prove game world creation, host/scene readiness, save or load of `.rgd`, FMOD, actual Android filesystem semantics, or on-phone gameplay. Reparse checks are not an atomic defence against an adversarial simultaneous path replacement; application-private directory ownership still matters. The original persistentDataPath root itself may be intentionally redirected by the platform and is not rejected. Further original-source world/save integration and actual device acceptance remain necessary. **LOCAL-005 overall remains open. Build readiness remains NOT_READY, 0/3 complete immutable-candidate reviews.**

Coordination: A6 owns `LocalSavePaths.cs` and Smoke tests, A8 owns world-readiness probe, A10 owns original world/save source contract; none of those owned paths was overwritten by A9.
