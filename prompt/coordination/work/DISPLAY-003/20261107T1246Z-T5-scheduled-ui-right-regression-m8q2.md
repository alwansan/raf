# 20261107T1246Z-T5-scheduled-ui-right-regression-m8q2
origin: scheduled
issue_id: DISPLAY-003
base_sha: 15ec1a28094ec3f3b97807fddabc230ccc0d4585
status: completed (source-contract added; CI pending)
intended_files: tests/test_t5_right_safe_area_buttons.py; prompt/coordination/clients/T5/sessions/20261107T1246Z-T5-scheduled-ui-right-regression-m8q2.md; this work file
experiment_key: t5-ui-right-buttons-static-contract-15ec1a2-20261107
resource_key: none (source-only; no Unity)
hypothesis: AndroidTouchUiPanel already anchors three diagnostic buttons to Screen.safeArea right; prevent regression by static contract tests, not a second overlay or speculative gameplay changes.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; original device e9c358eda01785b65e4eb14f18723da426635628.
coordination: T4 owns physical mouse; do not edit T4 files. Current right placement already implemented; test only. No native request while 5/5 trial consensus absent.

result: tests/test_t5_right_safe_area_buttons.py committed at 01a04441ff4134c79302dd67159587495692a2c3; direct source checks 5/5 conditions true; Python CI not yet verified. Session: prompt/coordination/clients/T5/sessions/20261107T1246Z-T5-scheduled-ui-right-regression-m8q2.md
