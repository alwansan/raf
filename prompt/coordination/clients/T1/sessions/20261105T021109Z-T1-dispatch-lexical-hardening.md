# T1 independent session — 20261105T021109Z

identity: T1
resumed_from_session: 20261105T002850Z-T1-bank1-isolated
identity_conflict: possible concurrent T1; state.json and MEMORY.md deliberately untouched
baseline_sha: 619ca19c0600d8ac6e3f275f990dded6f83e0f21
issue: WATER-001 OPEN; NOT_READY 0/3
hypothesis: lexical scanner in scripts/t1_fft_dispatch_evidence.py can incorrectly count FFT calls embedded in C# interpolated strings; prevent false positives while retaining real calls.
files: scripts/t1_fft_dispatch_evidence.py, tests/test_t1_fft_dispatch_evidence.py
source: synthetic controls only; original FFT private SHA not supplied; no device/Unity proof.
taken_over_from: T1 original sampled-image CI41939314440 and negative bank1 CI41942366020; prior FFT audit commits 93867b5, a23633f.
plan: reproduce false positives, implement bounded masking of interpolated/verbatim/char literals, test and record results. No changes to T2-T5, no build cancellation.
