# T4 scheduled — scroll callback evidence, 2026-11-08 17:46 UTC

- session_id: `20261108T1746Z-T4-scheduled-scroll-action-p8v3`; origin: `scheduled`; worker: `T4`; issue: `INPUT-005`.
- baseline HEAD: `b02ff5022f5e29968b69bbf94e49a0402c460f07`.
- previous T4: `20261108T1640Z-T4-scheduled-button-edges-m7q2` and source tests `70c90a75`.
- scope reservation: `e0e00d8641f4bcb576483aff471a220c76f6a6c7`, under `prompt/coordination/work/INPUT-005/`.
- source fix: `d62b09501e3ab1b2d36da7dc95f9e9a003555da5`: count vscroll/hscroll only when action is `ACTION_SCROLL`. Non-scroll callbacks carrying stale axis values are no longer counted as wheel evidence.
- regression: `16844d49bd952fdec54d124a7f24685f7ee8e27d`: synthetic ACTION_MOVE with nonzero axes, ACTION_SCROLL with nonzero axes, and zero-axis ACTION_SCROLL. Expected exactly one vertical and horizontal scroll event.
- validation: static inspection of changed source and test. Python test execution unavailable locally because runtime cannot resolve raw.githubusercontent.com; no CI execution claim. No duplicate Actions launched.
- Owner phone baseline: Artifact 42058825739 entered, saved and reopened .rgd world. 2026-11-08 phone feedback: camera relative motion works under capture; Mouse0/1/2 and wheel still do not work in game. Do not confuse lab callback proof with Unity bridge success.
- latest shared lab policy: `apk-for-testing/UNIFIED_LAB_POLICY_AR.md`: one shared APK and pack; T5 owns build; no new APK for classifier-only changes. T5 owns UI three buttons and Resolution.
- Preserve keyboard, camera capture, .rgd, sound and Settings; no runtime changes.
- next: execute `python3 -m unittest tests.test_t4_analyze_mouse_lab_routes` in accessible runner, inspect Android 15 captured and uncaptured JSONL, compare game bridge route, then implement only proven runtime repair. INPUT-005 remains OPEN.
