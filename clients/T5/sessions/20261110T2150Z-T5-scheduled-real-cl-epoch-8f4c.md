# T5 20261110T2150Z-T5-scheduled-real-cl-epoch-8f4c
origin: scheduled
baseline_sha: d11d07d6119b12c77065a3ee20554536db37d629
scope_commit: 39e3e875d0eeacd576ddbf2150f344fa280ab2ac
fix_commit: 9e7a510f0917fbadd02550b12dd44ddff3d070b6
issue: PERF-007
source_run: https://github.com/alwansan/raf/actions/runs/42889557850
pinned_CL_commit: 520c4cf409aa20a4db54ff80ed87d8807d9cba57
result: Inspected both original pinned CL JSONL files, not only synthetic tests. 220911 has unknown sample1 then verified Raft PID from sample2: one safe epoch. 230108 has unknown sample1, five genuine game_not_running probes samples2-6, then verified game process sample7 onward: seven process epochs. Strict auditor correctly withholds two otherwise fresh presentation samples for the second session. Previous workflow erroneously asserted both sessions safe and second session 2 reportable fresh samples. Updated only the pinned real CL workflow assertions, preserving strict process boundaries and SHA source checks. No changes to analyzer or readiness thresholds.
status: source_fix_published_waiting_ci; no successful new CI run verified. No signed APK/OBB or device FPS measurement.
next: check new workflow run for 9e7a510f, inspect failing step if any, never weaken PID provenance. Return to owner P1 right-side buttons/Resolution and signed APK/OBB after checking T5 concurrent work. T4 owns physical mouse.
