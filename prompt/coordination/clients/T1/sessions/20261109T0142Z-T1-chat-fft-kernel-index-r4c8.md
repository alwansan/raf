# T1 — WATER-001 runtime kernel identity consistency
session_id: 20261109T0142Z-T1-chat-fft-kernel-index-r4c8
origin: chat
resumed_from_sessions: 20261109T0114Z-T1-scheduled-runtime-identity-h7q4; 20261108T2022Z-T1-chat-fft-source-gate-d8b4
base_sha: 687d181d63c48cc2811e38948942a93d06a0a385
issue_id: WATER-001
work: prompt/coordination/work/WATER-001/20261109T0142Z-T1-chat-fft-kernel-index-r4c8.json
intended_files: scripts/t1_fft_runtime_evidence_gate.py; tests/test_t1_fft_runtime_bijection_r4c8.py; .github/workflows/raft-t1-fft-runtime-evidence-regression.yml; this session
experiment_key: t1-water-fft-runtime-named-index-bijection-gate-v1-6fe95344
resource_key: null
conflict_check: T3/T5 lightweight source Actions running; T4 recent changes in other scope. No T1 or Unity heavy overlapping Action.
hypothesis: one named kernel of one shader_guid cannot have two observed FindKernel indices, and one index cannot describe two names.
change: validate bidirectional consistency across dispatches and reject C1/control chars in resource labels and identities.
test_plan: run seven older unexecuted identity controls and eight new contradictory/valid cases in no-APK workflow.
status at initial commit: SOURCE_PATCHED_PENDING_CI; original Unity runtime bindings and Android device evidence still missing.
next: inspect immutable Actions result and store run; get authentic same-build Unity FindKernel/Dispatch/binding trace, then first-pass comparison.
limits: No original/private game binaries, no CL writes, no APK, no water fix proof; WATER-001 OPEN / NOT_READY 0/3.

## Proven CI checkpoint — 2026-11-09T01:46:29Z
- commit: https://github.com/alwansan/raf/commit/a6b88ddcd5677a8b1a13303f398402366b9f6908
- run: https://github.com/alwansan/raf/actions/runs/42547313000
- job: check-runtime-evidence (128934982791), completed SUCCESS on exact commit SHA.
- original seven T1 identity regressions: **7/7 PASS** (the earlier scheduled unexecuted controls are now actually exercised).
- eight new cross-dispatch runtime name↔index and hidden control character checks: **8/8 PASS**.
- TOTAL: **15/15** source-only tests, no game assets, no Unity Editor, no GPU, no Android APK/XAPK, no CL writes.
- No evidence of actual original runtime FindKernel result, and old source numeric 6 remains hypothetical, NOT equivalent to device kernel index6.
- work closure: completed_source_ci_verified; issue WATER-001 still OPEN; project readiness NOT_READY 0/3.
- follow-up for next T1 chat/scheduled session: obtain original same-build private trace with genuine shader GUID, name, FindKernel result, Dispatch index, groups, texture bindings, bank/pass/FFT size; only then correlate bad kernel and first divergent output. Do not request another shared mini APK for this script-only fix.
