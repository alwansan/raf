# T2 WATER-001 — 20261110T032515Z-T2-scheduled-cil-join-k8m4
origin: scheduled
UTC: 2026-11-10T03:25Z
branch: feature/android-native-port
resumed_from_sessions: 20261109T2323Z-T2-scheduled-writer-rhs-scope-m7q2; prior 2026-11-10 T2 CIL guard sessions
baseline_scope_commit: 5740bed9eb2a88824ebd7501faffa5b14f3af9bb
work: prompt/coordination/work/WATER-001/20261110T032515Z-T2-scheduled-cil-join-k8m4.json

## Owner/device evidence first
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. Owner succeeded world enter/save/exit/reenter from Actions artifact 42058825739, while packaging publish failed. CL pinned 520c4cf4: 220911-559 has 23,884 water invalid passes and 3,850 FFT kernel errors; 230108-327 has 39,132 pass errors and 6,026 kernel errors. This does not demonstrate current water recovery. Newer 8 Nov unified lab/owner tests also require careful source version attribution. Mouse click/scroll delegated to T4, Resolution to T5; do not duplicate.

## Engineering completed
Created isolated source-only synthetic return-value provenance gate:
- scripts/t2_cil_return_join_gate.py commit 599d5eed632c3e86efdb53cde44fa64d5470112d
- tests/test_t2_cil_return_join_gate.py commit b822dab83604550d09d9a4cd31aa27afbf11fc06
- 13 local Python unittest cases PASS (2026-11-10T03:25Z), including divergent fields, receiver mismatch, incomplete CFG, unknown calls, null, allocation, invalid stack, and cast placement.
Hypothesis: field name equality alone is insufficient to prove cross-pass instance identity; a return join must reject conflicting or incomplete paths. Synthetic gate requires externally certified complete_cfg, deliberately rejects allocations as instance identity. It is NOT Mono.Cecil, does NOT establish complete original CFG, receiver identity, actual aliasing, CB0, sampler or ShaderLab, and cannot be used to mark WATER-001 ready.

## Constraints and handoff
No Unity/Android build or CL writes, no T3/T4/T5 files changed. Local git DNS unavailable; GitHub connector wrote isolated files. No new CI dispatched. Source-level tests local only, not Actions. Original ZIP2 analysis CI42519122764 remains separate prior evidence. Next: integrate only after original CIL parser can supply complete CFG and resolved receiver token, then run original-data CI and link return to pass1 Blit source; do not equate SSA symbols with runtime object identity. WATER-001 OPEN, NOT_READY 0/3.
