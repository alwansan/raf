# T1 independent session — indirect FFT dispatch audit

session_id: 20261105T041234Z-T1-indirect-dispatch-regression
resumed_from_session: 20261105T031209Z-T1-member-call-audit
identity: T1
identity_conflict: possible parallel T1 activity; do not touch shared state/MEMORY
baseline_sha: a7cc6bbbfb7553d17c5f040d4a3a12ebdc47225c
issue: WATER-001 OPEN / NOT_READY 0/3

## Hypothesis and scope (pre-implementation)
The current audit counts DispatchIndirect in its boolean but its synthetic suite does not test indirect-only calls. Add isolated regression tests, not a claim of actual FFT runtime mapping. Files: new tests/test_t1_fft_dispatch_indirect_regression.py only; no original assets. taken_over_from: T1 20261105T031209Z member-call audit and earlier original bank0 CI41939314440; bank1 CI41938536760/41939082498 negatives preserved.

## Baseline
GitHub branch API verified a7cc6bbb; existing scripts/t1_fft_dispatch_evidence.py explicitly includes DispatchIndirect in the structural predicate. Git remote unavailable in local container (DNS), GitHub connector available. Current source-only evidence does not prove FindKernel/Dispatch kernel identities, Unity or Adreno. No Actions cancelled.

## Plan
Test indirect-only positive, indirect without FindKernel negative, comments/string false positives, and reject member-free local helper calls. Never emit private source. Run local synthetic tests where feasible, then commit isolated test on allowed branch.
