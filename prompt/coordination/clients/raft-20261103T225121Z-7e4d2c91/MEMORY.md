# A6 restored — dangling directory save-link safety

New A6 session `a6-20261103T225121Z-40bca78e`, identity `raft-20261103T225121Z-7e4d2c91`, resumed_from `raft-20261103T132000Z-a6e7f219` (prior state paused). Other A6 histories are preserved and were read. Owner rules: only `feature/android-native-port` writable, strict NOT_READY/0-of-3, ZIP2 original provider preferred and pinned at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; no LFS/Unity/APK/releases/automation edits.

Verified earlier independent A6 CI: save leaf 41623564391 SUCCESS, built-in include comments 41633638783 SUCCESS, Assets root 41644473219 SUCCESS. Another A8 ZIP2 local save provider plan is active and remains untouched. Latest live save-path workflow 41733872815 SUCCESS at 5f5be03230b3becc1f9fa88bc86fa9a395919483 before concurrent HEAD moved.

Current hypothesis: authored platform helper `LocalSavePaths.RejectLinkedSaveDirectories` gates reparse metadata read on `File.Exists || Directory.Exists`. Dangling world or intermediate directory symlinks may be missed, then redirected once the outside target is created. The separate leaf guard already performs unconditional metadata read. Next step: synthetic .NET regression, scoped source correction and same-source Actions confirmation. Does not prove original .rgd SaveAndLoad game integration, symlink-swap atomicity, or on-device world resume.
