# T1 session 20261108T0411Z-T1-scheduled-fft-nul-guard-8d2f
origin: scheduled
base_sha: 1438f83c9a1eb30521cc8d9079072426ece0b050
latest_checked_head: d72ced0f3a5148b9495af84fbb50d9ffa9b2dade
resumed_from: clients/T1/sessions/20261108T0315Z-T1-scheduled-original-trace-gap-6e91.md
work: work/experiments/20261108T0411Z-T1-scheduled-fft-nul-guard-8d2f.md
issue: WATER-001 (OPEN)

## Owner evidence
docs/DEVICE_FEEDBACK_42058825739_AR.md: owner played, saved and re-entered world using run 42058825739 artifact; publishing failed. CL fixed snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57; session 220911-559: 23884 water pass / 3850 kernel errors, session 230108-327: 39132 / 6026. No identity inference from index 6.

## Change
Identified scripts/t1_fft_first_divergence.py checked the literal four-character string backslash-x00 instead of actual NUL in private capture path. Changed to actual NUL code point guard in 9a85ea928e7765e6d9e362bec98f3ff441c008c4. Added two tests in scripts/test_t1_fft_capture_path_nul.py (final d72ced0f3a5148b9495af84fbb50d9ffa9b2dade) for early NUL rejection and accepting a valid POSIX filename with a literal backslash-x00 sequence. Scope file 38f759eb7228a4c8c9d04e2301168f0262e6dc08.

## Evidence and limits
GitHub connector confirmed commits and re-read source; local git ls-remote fails DNS (Could not resolve host github.com). Tests not executed; do not claim test PASS. No Unity, GPU, native build or original assets touched. The fix is capture input validation only; it does not restore water or map FindKernel index 6.

## Next
Execute python3 -m unittest scripts.test_t1_fft_capture_path_nul scripts.test_t1_fft_capture_budget scripts.test_t1_fft_dispatch_coverage on exact SHA in suitable CI; then obtain original FFT program/resource and Unity FindKernel/Dispatch captures for numeric first-pass comparison. Preserve T4 physical mouse and T5 buttons/Resolution scopes. Trial vote unchanged; NOT_READY 0/3.
