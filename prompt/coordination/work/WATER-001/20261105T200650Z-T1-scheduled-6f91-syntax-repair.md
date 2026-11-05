# T1 scoped work
session_id: 20261105T200650Z-T1-scheduled-6f91
origin: scheduled
issue_id: WATER-001
base_sha: 6ab8bbb29fac004e2c2ee25c9a60c1b47f37141b
status: active
intended_files: scripts/t1_fft_rgba_error_signature.py; tests/test_t1_fft_tolerance_overflow.py (inspect only); unique session/work files
experiment_key: rgba-signature-python-lexical-literal-backslash-n-source-6ab8bbb
resource_key: none
hypothesis: Previous tolerance overflow patch committed literal backslash-n tokens in Python code, causing SyntaxError and preventing all comparator imports.
taken_over_from: 20261105T191038Z-T1-scheduled-9d7a
plan: Inspect exact source and tests, repair only malformed escaped newline tokens, validate Python compile and tests if possible, record limitations. No Unity or assets.
