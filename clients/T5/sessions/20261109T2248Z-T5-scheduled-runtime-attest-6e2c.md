# 20261109T2248Z-T5-scheduled-runtime-attest-6e2c
origin: scheduled
resumed_from_sessions: 2026-11-09 T5 native failure checkpoint (commit 19bf77c); earlier OBB parity sessions
base_sha: 69ded8f0bea9c0cee84bb6a7f851b05b9f64fd33
scope_commit: e0bc850d4f2b6a51b0b7c02bc411b1992bafabb9
fix_commit: f03af6c3c4f2e0aad2cee5862787932d6e1c52da
issue: NATIVE-RUNTIME-STAGING-ATTEST
origin_run: https://github.com/alwansan/raf/actions/runs/42696228231
job_id: 129428944191
observed: reconstruct step 65 failed before Unity Editor. GitHub public job metadata confirms failure but not the detailed exception; job logs endpoint unavailable to this connector.
change: validator now reports safe staged C# missing/unexpected filenames and changed-byte filename. Equality, allowed file list, symlink and size checks remain unchanged. No source bytes printed.
verification: source-only code review and exact-pattern replacement; Python unit tests and CI not yet executed. No Unity build launched.
status: SOURCE_FIXED, DEVICE_NOT_TESTED, CI_PENDING
other_open: APK/OBB SHA pairing, Resolution modes, right-side three buttons device confirmation, performance comparison. T4 mouse pointer capture remains separate.
next: inspect CI source guard result for commit f03af6c; if native reconstruct reruns under coordinated approval, read exact filename diagnostics and repair staging cause without relaxing checks. Run targeted unit tests and avoid duplicate Unity.
