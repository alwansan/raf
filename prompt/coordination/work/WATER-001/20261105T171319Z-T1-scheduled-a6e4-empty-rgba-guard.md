# T1 isolated work — 20261105T171319Z-T1-scheduled-a6e4
origin: scheduled
base_sha: 3cbee8c415d9ad289acc90ff422e70b439d8e7a7
resumed_from_session: 20261105T170847Z-T1-chat-015973
issue: WATER-001 (OPEN); readiness: NOT_READY 0/3
scope: scripts/t1_fft_rgba_error_signature.py and new tests/test_t1_fft_empty_capture_guard.py; separate from active T1 Unity trace work.
hypothesis: signature(b'', b'') currently reports all_within_tolerance=true and pixels=0, allowing empty private captures to masquerade as numeric parity. Fail closed for zero pixels.
experiment_key: T1-RGBA32F-EMPTY-GUARD-20261105T171319Z
shared_resource: none; source-only Python, no Unity or Actions launch.
taken_over_from: T1 first divergence utility 398353a / relative path fix ce27214; current T1 chat 20261105T170847Z handles Unity trace separately.
plan: reproduce using exact signature function; add strict empty capture rejection and adversarial tests; verify locally; commit without force and recheck HEAD; record outcomes in separate session.
