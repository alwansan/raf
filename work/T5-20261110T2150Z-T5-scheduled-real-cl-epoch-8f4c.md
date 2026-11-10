# T5 scope 20261110T2150Z-T5-scheduled-real-cl-epoch-8f4c
origin: scheduled
baseline_sha: d11d07d6119b12c77065a3ee20554536db37d629
issue: PERF-007
experiment_key: t5-real-cl-startup-stop-epoch-gate-42889557850
files: .github/workflows/raft-t5-cl-real-fps-cohort.yml; work/20261110T2150Z-T5-scheduled-real-cl-epoch-8f4c.md; clients/T5/sessions/20261110T2150Z-T5-scheduled-real-cl-epoch-8f4c.md
hypothesis: pinned second CL file has five genuine game_not_running samples before game start, so strict PID epoch auditor correctly rejects whole-session aggregation; workflow incorrectly asserts one safe epoch for both files.
observed: pinned CL first session 71 rows: unknown sample1 then verified PID from sample2. Second 119 rows: unknown sample1, game_not_running samples2-6, verified game_running sample7 onward. No PID publication. Expect first 1 safe epoch; second 7 epochs and unsafe; second 2 otherwise fresh FPS rows must be withheld.
shared_resource: none; source-only workflow no Unity. T4 retains physical mouse; T5 scope does not edit mouse.
next: replace only invalid workflow assertions, preserve conservative gate and provenance, inspect Actions result. Signed APK/OBB, right-side buttons, Resolution still open.
