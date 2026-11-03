# A6 LOCAL-005 — dangling directory symbolic-link metadata hardening

Date: 2026-11-03 UTC. Session: `a6-20261103T225121Z-40bca78e`; independent identity `raft-20261103T225121Z-7e4d2c91`, resumed from paused A6 `raft-20261103T132000Z-a6e7f219`.

## Bounded hypothesis and source change

The existing authored platform `LocalSavePaths.RejectLinkedSaveDirectories` gated each `File.GetAttributes` check on `Directory.Exists(path) || File.Exists(path)`. The result of these existence APIs for dangling symbolic links can be runtime/platform-dependent; the final `world.sav` leaf guard already reads link metadata unconditionally. This session removed the existence gate for each app-owned directory component and catches only `FileNotFoundException` / `DirectoryNotFoundException` when genuinely absent. A reparse-point entry throws `IOException`. This makes the test independent of the existence methods without changing world names, save path format, original game `.rgd`, GUIDs or assets.

[Production + tests commit](https://github.com/alwansan/raf/commit/2db90307d5c9df199c2986c92ed7fe8384a84e97) modified exactly two files: `android-port/Runtime/Platform/LocalSavePaths.cs` and `android-port/Tests/Smoke/Program.cs`.

## Evidence

[Same-source platform workflow 41734951563](https://github.com/alwansan/raf/actions/runs/41734951563), job `126261621800`, **COMPLETED SUCCESS** for `2db90307d5c9df199c2986c92ed7fe8384a84e97`. Retrieved runner job logs directly: `PASS dangling world directory link is refused before target appears`, `PASS dangling profile ancestor link is refused before target appears`, `TOTAL passed=17 failed=0`; original netstandard2.1 library build succeeded with `0 Error(s)`. Ordinary save/leaf/parent and profile identity tests remained enabled.

**Evidence limit:** No pre-patch RED test was run for this narrower change. Therefore the precise existence-check bypass is a prevention hypothesis rather than a confirmed exploit on the CI runner; do not misrepresent its former runtime behavior. This is a real code-hardening change with executable same-source tests. The helper's managed checks are not atomic against hostile concurrent path swaps. A synthetic `world.sav` in this platform helper is not original Raft `.rgd` integration. No Unity, native APK/OBB/XAPK, LFS, original shader/program, on-device save trial or schedule was modified or validated.

## Coordination and remaining issue

A8's active `zip2` original SaveAndLoad / Data.rgd provider integration and A10's original NRBF/RGD exploration use separate files; they were not touched. The latest ZIP2 provider pin remains `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. LOCAL-005 remains source/integration review pending, while WATER-001, RENDER-002 and FFT-FORMAT-009 keep full delivery **NOT_READY**; 0/3 immutable full readiness reviews. Follow up with original world create/load/save/resume source evidence, then candidate-specific phone tests only after legitimate build readiness.
