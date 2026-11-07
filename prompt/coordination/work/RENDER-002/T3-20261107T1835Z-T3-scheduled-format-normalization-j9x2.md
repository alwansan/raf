# T3 scope — 20261107T1835Z-T3-scheduled-format-normalization-j9x2
origin: scheduled
track: RENDER-002
baseline: latest live branch (read per-file SHA before writes)
files: scripts/t3_rgb_drift_strata.py; tests/test_t3_rgb_drift_strata.py; own session file
hypothesis: format strings with leading/trailing whitespace can bypass UNKNOWN sentinel metadata guard, incorrectly counting unauthenticated format as known.
experiment_key: t3-format-sentinel-trim-j9x2
shared_resource: none; no CI/native build; no game assets
coordination: T1/T2 shader-water, T4 mouse, T5 resolution/delivery untouched. Source and tests edited with blob SHA, no force. Validate with test and report evidence limits.
