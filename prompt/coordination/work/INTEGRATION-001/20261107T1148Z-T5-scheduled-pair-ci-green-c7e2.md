# T5 scope 20261107T1148Z-T5-scheduled-pair-ci-green-c7e2
origin=scheduled
baseline_sha=19b1e04d5098e1154fdd4179fada24b197b0d5a3
area=INTEGRATION-001; read-only verification of new paired APK/OBB manifest duplicate-key regression CI; no shared Unity resource.
Files owned: prompt/coordination/work/INTEGRATION-001/20261107T1148Z-T5-scheduled-pair-ci-green-c7e2.md and prompt/coordination/clients/T5/sessions/20261107T1148Z-T5-scheduled-pair-ci-green-c7e2.md only.
Hypothesis: run 42365737052 validates latest three duplicate-key regression cases at commit 477c62f, unlike earlier pending run.
Result: GitHub Actions API reports completed/success on 2026-11-07 10:52:27 UTC. This establishes workflow green, not device APK/OBB identity. No new native build; trial r1 votes T1/T2/T3/T5 no, T4 yes.
Next: inspect job step/test totals and validate actual signed APK/OBB internal SHA/versionCode against delivery manifest once retrievable; then address right-side buttons and existing Resolution without conflicting with T4 mouse work.
