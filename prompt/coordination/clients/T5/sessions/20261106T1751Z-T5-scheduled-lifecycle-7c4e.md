# T5 scheduled lifecycle regression

- session_id: 20261106T1751Z-T5-scheduled-lifecycle-7c4e
- origin: scheduled
- resumed_from_sessions: 20261106T1745Z-T5-chat-trial-vote-adoption-46c2; previous scheduled PID-epoch commits 858e7f1 and 2890644
- base reference: feature/android-native-port; scope commit 1f4ed4184465aa0ef97c1643f36859472af14e69
- issue: PERF-007; independent PID lifecycle test; no Unity shared resource.
- hypothesis: stopped LogRaft game interval followed by same numeric PID was incorrectly counted as one process epoch, making presentation FPS medians unsafe.
- implementation: a5f2172f7433e8e0a6c4a6a178029a56a82d8cc9 modifies scripts/t5_cl_pid_epoch_audit.py to close the verified epoch on nonrunning rows; da7fdeadd7f95a6273dca22d71aee4bce6736416 adds two regression tests.
- expected test: python3 -m unittest tests.test_t5_cl_pid_epoch_audit (or unittest discover -s tests -p test_t5_cl_pid_epoch_audit.py).
- validation: code and tests committed, **CI and runtime tests NOT YET CONFIRMED**; do not report PASS. No new performance measurement or device proof.
- delivery: existing APK/OBB original artifact and original phone world/save success are unchanged; no new build. Trial vote 20261106-r1 is not 5/5; do not request native build.
- next: verify test runner result; ensure cohort analyzer rejects stop/restart same PID; link to LogRaft real sample epochs only after source version and device session provenance are checked. Preserve T4 mouse and T5 chat Resolution scopes.
