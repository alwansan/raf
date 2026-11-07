# T4 scheduled — authored unlock boundary for mouse capture log classification

- session_id: 20261107T1638Z-T4-scheduled-unlock-boundary-m8q4
- origin: scheduled
- resumed_from_session: 20261107T1541Z-T4-scheduled-mouse-release-boundary-n6r2.md
- base_sha: 42ec26d8c8621b4a869586d3eb48f8b8cfe3977f
- issue: INPUT-005 (OPEN); experiment_key: t4-mouse-classifier-authored-unlock-boundary-42ec26d8
- owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md confirms world entry, save, exit and re-entry on owner device with run 42058825739; no physical mouse device success is claimed.
- independent work scope: prompt/coordination/work/INPUT-005/20261107T1638Z-T4-scheduled-unlock-boundary-m8q4.json committed at f08dbf0dafb963c1efb1ebadcf8276216293d176.
- reproducible reasoning: the classifier previously bounded captured-relative events by physical_mouse_capture_released only. An authored_unlock transition could occur before a relative event, and without an explicit released event in a partial log that later relative event was falsely classified as captured movement.
- code commit: 1a450e859e8ec10c07493155264dd4f2cb0f1c3d. Count authored_unlock as a terminal event for the relative observation window, preserving the previous release bound.
- test commit: 0ad5bba0fdbac0694110b553f87a4adbede89393. Add two regression cases for relative-after-authored-unlock and relative-before-authored-unlock; suite now has 11 test cases.
- verification limits: reviewed source and test cases; not executed locally because the available container cannot resolve GitHub, and no Actions run on this new SHA was observed. The latest observed mouse CI success is run 42373576554 on earlier 27fc3baf, not this patch. No phone, APK, Unity or GPU execution.
- no edits to keyboard, touch, Raft cursor rendering, .rgd, save/load, audio or Settings. T5 retains three-buttons and Resolution scope.
- next: execute `python3 -m unittest tests/test_t4_classify_mouse_capture_log.py` on a checked-out repository, then feed actual new CL device logs containing authored_lock/unlock, request, relative and release events; only then decide whether native pointer-capture repair is needed. Preserve original world/save acceptance and test against a signed build.
