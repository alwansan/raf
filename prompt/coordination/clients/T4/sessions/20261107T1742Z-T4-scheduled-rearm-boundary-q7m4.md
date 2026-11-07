# T4 INPUT-005 — cancelled-lock request boundary

- session_id: 20261107T1742Z-T4-scheduled-rearm-boundary-q7m4
- origin: scheduled
- base_sha: ef45764c6531688833bb20bc32db951926486427
- resumed_from_sessions: 20261107T1638Z-T4-scheduled-unlock-boundary-m8q4; 20261107T1440Z-T4-scheduled-mouse-trace-classifier-p8q3
- owner device result: run 42058825739 / source e9c358eda01785b65e4eb14f18723da426635628; world enter, save, exit, reopen confirmed. Delivery failure does not negate this limited phone result.
- owner feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57; images/logs read through report. No new device run in this cycle.
- scope: isolated Python log classifier and its tests, not physical mouse runtime/keyboard/.rgd/Settings. T5 retains three buttons/Resolution.
- hypothesis: after Escape, authored_lock -> authored_unlock -> late capture_requested -> relative must NOT be interpreted as a successful rearm. A new authored_lock after unlock may be valid.
- implementation: 685eac00 (first guard), 5ccae513 (correctly allow fresh locks), 82ac197b (two regression tests). No Unity build requested; no Actions cancelled.
- result: conservative request window now ends at authored_unlock/next Escape; tests cover stale request and valid fresh lock. This is a source change, not device validation. Full 13-test suite has not been executed in this environment; CI pending independent workflow trigger/check.
- work: prompt/coordination/work/INPUT-005/20261107T1742Z-T4-scheduled-rearm-boundary-q7m4.json
- next: run python -m unittest tests.test_t4_classify_mouse_capture_log on exact commit 82ac197b or later; compare real device logs using classifier. Verify camera free rotation, Raft cursor in menus, keyboard, Escape/focus-loss/reconnect. INPUT-005 OPEN, NOT_READY 0/3.
