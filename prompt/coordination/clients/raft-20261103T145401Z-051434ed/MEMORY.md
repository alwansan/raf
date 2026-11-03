# A6 resume — LOCAL-005 independent backup-leaf guard

Identity raft-20261103T145401Z-051434ed; session a6-20261103T145401Z-ba243dcc; resumed_from raft-20261103T132000Z-a6e7f219 (paused); label A6 retained. Old identities untouched.

Reviewed unified prompt, coordination protocol, all A6 identity chain states and memories, A6 experiments/work/incidents, LOCAL-005 messages and live source. Previous A6 root Assets guards passed runs 41644415213 and 41644473219 at source da4b98a6. Authentic .rgd game runtime still unproven.

Current isolated hypothesis: existing dangling symlink at backup destination is invisible to Path.exists() but shutil.copy2 follows it, writing original source outside backup. POSIX temporary-file reproducer confirmed external file creation. Will add synthetic negative tests and fail-closed checks in both original source adapters, preserving original assets, .meta, GUID and .rgd. No atomic race immunity claim; no Unity/native/Release/LFS/automation/CL writes.

Checkpoint: before source changes; local synthetic reproduction succeeded. Check HEAD/Actions before each write and verify same-source CPU CI after source/test patch.

## Verified RED/GREEN checkpoint — 2026-11-03T15:02:06.638Z

- Independent backup-leaf redirect bug reproduced: POSIX tempfile showed dangling symlink `exists=false`, `is_symlink=true`, and `shutil.copy2` produced an external file. No original game data involved.
- Test-only [3c3c5cbc](https://github.com/alwansan/raf/commit/3c3c5cbc286d2ed9b8ca6ae3ad7f5e9773b20606): [RED save 41658800717](https://github.com/alwansan/raf/actions/runs/41658800717) 1/6 failing and [RED offline 41658800643](https://github.com/alwansan/raf/actions/runs/41658800643) 1/10 failing, both `ValueError not raised`.
- Production [d922f999](https://github.com/alwansan/raf/commit/d922f999c11bbd2e9b02fef5bc4ea945d0eb8f1e) and [b6a96201](https://github.com/alwansan/raf/commit/b6a962018e06513d5cf408e646751f161f0e00ca) reject linked existing/dangling backup source/meta leaves before `shutil.copy2`.
- [GREEN save 41659075182](https://github.com/alwansan/raf/actions/runs/41659075182) SUCCESS 6/6 save + 4/4 selector + pinned original path checks. [GREEN offline 41659111730](https://github.com/alwansan/raf/actions/runs/41659111730) SUCCESS 10/10 offline + 6/6 save and other offline suites; original private managed compile `exit=0 errorCodes={}`.
- [Report](../../../../docs/A6_LOCAL005_BACKUP_LEAF_SYMLINK_2026-11-03.md); new discussion and GitHub ref-error incident recorded. Transient batched update_ref GraphQL UNKNOWN did not install changes; recovered with file-blob-SHA conditional updates, no force or overwrite.
- A6 scoped work complete and session paused. No Unity/native game build, device, LFS, CL, release, tasks or protected branch edited. LOCAL-005 authentic .rgd/world/device remains OPEN; WATER-001/RENDER-002/FFT-FORMAT-009 OPEN; NOT_READY and full reviews 0/3.
