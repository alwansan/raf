# T1 scope 20261105T180524Z-T1-scheduled-c8f2
origin: scheduled
issue_id: WATER-001
base_sha: 431ac013ada30dd67717253d531c8030751fd6d7
resumed_from_session: 20261105T173738Z-T1-chat-3e271f; 20261105T171319Z-T1-scheduled-a6e4
status: active
intended_files: scripts/t1_fft_rgba_error_signature.py; tests/test_t1_fft_tolerance_validation.py; own session/work files
experiment_key: fft-rgba32f-nonfinite-or-negative-tolerance-guard-v1
resource_key: none; source-only, no CI/Unity resource
hypothesis: direct signature() accepts NaN/negative tolerances even though CLI checks, so nonmatching finite pixels may be classified as matching. Reject invalid tolerance at API boundary.
taken_over_from: T1 existing RGBA comparator (6247a6c) and T1 scheduled empty-capture guard (02ab907), preserving both.
verification: synthetic unittest with finite mismatched pixel and NaN, infinity, negative tolerances; no private capture.
