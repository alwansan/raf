# 20261107T1349Z-T5-scheduled-right-geometry-k9p4
origin: scheduled
role: T5
baseline_sha: 19df5e53984925bf3fd991aa5539ad7d99e12e5a
resumed_from: 20261107T1246Z-T5-scheduled-ui-right-regression-m8q2; 20261107T1148Z-T5-scheduled-pair-ci-green-c7e2
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (phone world/save/reentry only on e9c358ed).
scope: DISPLAY-003; tests/test_t5_right_safe_area_buttons.py; no changes to T4 mouse.
plan_commit: a00692156c7579606df99bcfd58eec606c8ef67e
code_commit: 5ffb89fe68719fd80bb535370eb732b759fb5ecd
result: Added static geometry regression: right-side diagnostic buttons must be unique, ordered, inside HUD clearance and separated by at least 42 UI units. Existing code: Show Xbox (8,78,150), Xbox layout (8,126,150), Test report (8,174,150); height 42. Independent JavaScript equivalent against live source PASS; Python unittest not executed because runtime cannot resolve github.com to obtain complete checkout. No Unity, Android device, APK or GPU evidence.
coordination: T4 owns physical mouse; no T4 files changed. Trial vote trial-20261106-r1 not unanimous, so no native build requested. No other Actions canceled.
limitations: Static assertions do not prove Android layout pixels; real device must test safe-area cutouts, landscape transitions and Settings. Resolution implementation, internal APK/OBB SHA pair and LogRaft controlled performance comparisons remain open.
next: Run python3 -m unittest tests.test_t5_right_safe_area_buttons in full checkout/CI; inspect actual Resolution path and persisted render-scale behavior without changing original Settings delegate; verify signed APK+OBB internal SHA against manifest; collect same-scene LogRaft p50/p95 with unavailable GPU reported as such.
