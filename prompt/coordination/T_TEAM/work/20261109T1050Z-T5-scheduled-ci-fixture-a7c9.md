# T5 scope 20261109T1050Z-T5-scheduled-ci-fixture-a7c9
origin: scheduled
baseline_sha: 0c3553332e7ef8d14d12cad403a1655b3689d5cb
experiment_key: t5-png-ci-fixture-literal-20261109
scope_files: scripts/tests/test_t5_png_adam7_gate.py; clients/T5/sessions/20261109T1050Z-T5-scheduled-ci-fixture-a7c9.md
hypothesis: CI 42597471313 failed because Adam7 test fixture uses escaped backslash-x literals instead of actual PNG scanline bytes.
evidence: test_noninterlaced_one_pixel_valid constructs b"\\x00\\xff..." (20 ASCII bytes) rather than 5 decoded bytes. validate_png requires 5 bytes for RGBA 1x1; test fails.
shared_resource: none; source-only Python; no Unity/OBB/APK; T4 mouse scope untouched.
next: correct fixture, inspect CI result; no duplicate heavy workflow.
