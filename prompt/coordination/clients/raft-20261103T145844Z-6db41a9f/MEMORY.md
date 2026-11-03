# A9 restored checkpoint — A9-20261103T145844Z-91c65a3f

- New identity raft-20261103T145844Z-6db41a9f, resumed_from completed A9 `raft-20261103T121910Z-a9c47e01`; old A9 chain and state left untouched. UTC 2026-11-03T15:00:06.569Z.
- Baseline HEAD `0cee9fe8e0c11e615a7a410cc373013d494ca912`. Reviewed coordination and four A9 histories: LOCAL-005 profile symlink guard 345b151d/CI41617170076; local OfflineSession identity 5e4cedcb/CI41624155797; RENDER-002 ShaderLab identity d159f348/CI41629545455; AUDIO-004 atomic staging 44af18c7/CI41635870775 and repeat 41643072610 SUCCESS. Reviewed work, discussion, experiments, incident and handoffs.
- Live HEAD/Actions checked: A1 WATER/FFT and A3 DELIVERY active, not our source paths. Actual original game unchanged since APK80; candidate NOT_READY, full reviews 0/3; no device evidence for newer fixes.
- Independent original zip branch and immutable APK80 source 9462f8e have seven identical root Git blob OIDs to current branch, including Data.rgd, four VO/strings banks, MasterBank.bank pointer, and config. A9 stage only pins MasterBank bytes and 29 Haptics manifest, otherwise relies on branch-local Git OIDs.
- Scope: scripts/stage_original_streaming_assets.py, tests/test_stage_original_streaming_assets.py, tests/test_a9_streaming_stage_atomic.py, A9 independent records. No original bytes, LFS, Unity/APK/OBB/XAPK, CL, native request, tasks or protected branches.
- Next: source+HEAD co-edit fail-first test, root source immutable Git blob pin, CI and evidence ledger. Source test fixtures synthetic only.
