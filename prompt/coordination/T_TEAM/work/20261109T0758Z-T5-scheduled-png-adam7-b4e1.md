# T5 scope — 20261109T0758Z-T5-scheduled-png-adam7-b4e1
origin: scheduled
base_sha: d114472f402ffe6d0cdab57c8a3eb588109b12e3
issue_id: T5-PNG-ADAM7-VALIDATION
status: active
intended_files: scripts/t5_verify_png_bytes.py; scripts/tests/test_t5_verify_png_bytes.py (only if present and compatible); clients/T5/sessions/20261109T0758Z-T5-scheduled-png-adam7-b4e1.md
experiment_key: png-adam7-false-positive-gate-source-fd8a1b8-no-device
resource_key: none (CPU-only source validation)
hypothesis: current validator accepts Adam7 interlaced PNG without scanline validation; fail closed instead of claiming full structural validation.
coordination: T4 owns physical mouse; T1/T2 water; T3 colors. No Unity build or shared mini APK.
updated_at: 2026-11-09T07:58:00Z
