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

## Result
- Commits a86164a8e8e7df46ef8a01d9e560c96368301bef and 486b3b96b6a1ccbcc66cc431c2b95b8ff9ade88f: lexical masking extended to C# interpolated regular/verbatim and char literals; added regression that requires genuine Dispatch while rejecting fake FindKernel and SetTexture in interpolated strings.
- Local minimal Python regex reproduction: fake calls masked, genuine Dispatch preserved (5 synthetic samples). Full repository unittest execution **not performed**: container cannot resolve github.com; connector write succeeded. CI not started.
- No authenticated original caller, Unity 2021 execution, Adreno or device evidence. WATER-001 remains OPEN, NOT_READY 0/3.
- Next: run `python -m unittest tests.test_t1_fft_dispatch_evidence` in CI/worktree and then examine original SHA-pinned caller program-to-kernel dataflow, not just syntax. Avoid treating lexical scan as runtime proof.
