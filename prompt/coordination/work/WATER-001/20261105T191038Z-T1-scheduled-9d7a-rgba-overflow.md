# T1 scope — 20261105T191038Z-T1-scheduled-9d7a
origin: scheduled
issue_id: WATER-001
base_sha: b050d0bd42a341bba824638aa3d2753667684a3f
resumed_from_sessions: 20261105T181052Z-T1-chat-885348; 20261105T180524Z-T1-scheduled-c8f2
intended_files: scripts/t1_fft_rgba_error_signature.py; tests/test_t1_fft_tolerance_overflow.py; this work record; unique session file
experiment_key: T1-rgba32f-finite-reference-rtol-overflow-v1
resource_key: none (source-only, synthetic floats)
taken_over_from: none; separate numeric guard from ongoing original FFT capture work
hypothesis: finite but huge relative tolerance overflows rtol*abs(reference) to infinity, incorrectly treating finite mismatches as equal; compare using bounded quotient instead.
status: completed\nsource_commit: d1108b717b3dbdb7431f03170a3cae8393b99565\ntest_commit: a15cc43c5e1c803c506d26cdc3c1ccbbd1ef362e\nlocal_validation: 3 synthetic unittest cases passed on manually reconstructed copy; exact repository suite not run (DNS).\nresult: overflowed effective tolerance now fails closed, no device or original FFT proof.\nnext: exact checkout CI regression and original pass-zero readback evidence.
No Unity or native workflow requested; no raw assets.
