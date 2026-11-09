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
status: SOURCE_PATCHED_PENDING_CI; original Unity runtime bindings and Android device evidence still missing.
next: inspect immutable Actions result and store run; get authentic same-build Unity FindKernel/Dispatch/binding trace, then first-pass comparison.
limits: No original/private game binaries, no CL writes, no APK, no water fix proof; WATER-001 OPEN / NOT_READY 0/3.
