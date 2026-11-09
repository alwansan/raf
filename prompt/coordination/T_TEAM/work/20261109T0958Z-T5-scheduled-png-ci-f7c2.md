# T5 scope 20261109T0958Z-T5-scheduled-png-ci-f7c2
origin: scheduled
baseline_sha: b20a9252c8b79337e147367a4079826ac57a09e2
scope: .github/workflows/raft-t5-png-byte-regression.yml; scripts/tests/test_t5_png_adam7_gate.py only if CI proves fixture failure; clients/T5/sessions/20261109T0958Z-T5-scheduled-png-ci-f7c2.md
experiment_key: t5-png-byte-unit-ci-20261109
hypothesis: published PNG parser regression suites have not been executed; isolated standard-library CI can distinguish passing source from broken fixtures.
shared_resource: GitHub Actions lightweight runner only; no Unity/APK/OBB.
coordination: T4 owns mouse/pointer and its smoke. This run tests only T5 PNG evidence parser. No changes to T4 files.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md; clients/T5/sessions/20261109T0855Z-T5-scheduled-png-order-r6c2.md
status: IN_PROGRESS; no claim of device visual validation.
