# A6 resume — LOCAL-005 independent backup-leaf guard

Identity raft-20261103T145401Z-051434ed; session a6-20261103T145401Z-ba243dcc; resumed_from raft-20261103T132000Z-a6e7f219 (paused); label A6 retained. Old identities untouched.

Reviewed unified prompt, coordination protocol, all A6 identity chain states and memories, A6 experiments/work/incidents, LOCAL-005 messages and live source. Previous A6 root Assets guards passed runs 41644415213 and 41644473219 at source da4b98a6. Authentic .rgd game runtime still unproven.

Current isolated hypothesis: existing dangling symlink at backup destination is invisible to Path.exists() but shutil.copy2 follows it, writing original source outside backup. POSIX temporary-file reproducer confirmed external file creation. Will add synthetic negative tests and fail-closed checks in both original source adapters, preserving original assets, .meta, GUID and .rgd. No atomic race immunity claim; no Unity/native/Release/LFS/automation/CL writes.

Checkpoint: before source changes; local synthetic reproduction succeeded. Check HEAD/Actions before each write and verify same-source CPU CI after source/test patch.
