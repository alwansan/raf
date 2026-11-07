# 20261107T1246Z-T5-scheduled-ui-right-regression-m8q2
origin: scheduled
role: T5
base_sha: 15ec1a28094ec3f3b97807fddabc230ccc0d4585
resumed_from_sessions: 20261107T1148Z-T5-scheduled-pair-ci-green-c7e2 and earlier T5 DISPLAY-003 resolution probes.
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; successful world/save/re-entry is phone evidence for run 42058825739 only.
scope: DISPLAY-003; tests/test_t5_right_safe_area_buttons.py; no overlap with T4 physical mouse.
result: Existing AndroidTouchUiPanel.cs already uses AddRightButton for Show Xbox, Xbox layout, Test report with Screen.safeArea root, right anchor/pivot (1,1), negative inset and stretched caption. Added static unittest contract to catch regression of this exact arrangement, callbacks and safe area. Source assertions checked independently against current file: three unique calls, right anchor, safe root, callbacks all true. Python unittest has not run in CI yet.
commits: 93c3c11cf33ad6d8a2c13f1e2bb4086e5226cb32; regex correction 01a04441ff4134c79302dd67159587495692a2c3.
latest verified workflow: https://github.com/alwansan/raf/actions/runs/42373576606 SUCCESS for 27fc3baf (prior to new test). No Unity launch, no native request, no device measurement.
trial vote: trial-20261106-r1 not unanimous (T4 needs; T1/T2/T3/T5 no), no new native request.
limitations: static layout contract does not establish correct Android pixels or interaction; resolution implementation and internal APK/OBB hashes still need verification; LogRaft FPS samples in report are not GPU timings.
next: run python3 -m unittest tests/test_t5_right_safe_area_buttons.py (or discovery); inspect CI after test commit; then implement Resolution improvement with T5 DISPLAY-003 ownership and test against original Settings delegates; do not alter T4 mouse code.
