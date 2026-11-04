# B16 incident — legacy B47 symlink fixture failed after concurrent water metadata hardening

- Session: `20261104T2151Z-B16-6e2a`, issue WATER-001; source under test `0098b585`.
- Evidence: [B47 CI 41920543082](https://github.com/alwansan/raf/actions/runs/41920543082), job `126891545947`, 7 B47 cases PASS and 1 ERROR.
- Exact failure: legacy `test_meta_symlink_never_counts_as_original` expected `inspect()` to return `water_compute_source_candidate_present=false`; the concurrent stricter `_regular_unlinked_asset` guard correctly raises `ValueError: Unsafe linked water source or metadata path` on the same unsafe input. This is a fixture/API expectation drift under live concurrent changes, **not evidence that B16 conditional preprocessing failed**.
- Recovery/evidence: [B16 CI 41920741687](https://github.com/alwansan/raf/actions/runs/41920741687) on later immutable `e0318a101ee477605f63ec3514c4d5a9eb987c3a` passed all 34 tests, including this original B47 case and the stricter water meta negative controls. The test fix itself belongs to the simultaneous metadata hardening worker; do not alter their ownership record.
- Rejected hypothesis: red B47 run demonstrates that disabled #if0 masking is invalid — **rejected**, its trace never entered the B16 masking path; source remains only structurally tested, not original FFT/device proof.
- Impact: no native compile/device execution, no lost asset, no force/rebase or restart/cancellation. Closed reason: correct authoritative negative-input behavior and follow-up tests green on newer HEAD. No action required for B16 test code.
