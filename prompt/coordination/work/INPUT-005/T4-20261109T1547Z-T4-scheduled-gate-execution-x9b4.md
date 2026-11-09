# T4 INPUT-005 — gate executable regression
session_id: 20261109T1547Z-T4-scheduled-gate-execution-x9b4
origin: scheduled
baseline_sha: 5e2d9a8af78c1bcfb1d3f1dc5b39c14b2ee78d5c
scope: new scripts/tests/test_t4_capture_acceptance_gate_runtime.py only; no game/Unity/T5 files.
hypothesis: a deterministic unittest can exercise existing fail-closed Android-only gate and prevent accidental DEVICE_PASS on callback evidence.
experiment_key: T4-gate-runtime-x9b4
shared_resource: none; CPU Python unittest only; no CI duplicate or Unity build.
owner evidence: Artifact 42058825739 world/save/reopen succeeded; 8 Nov physical camera capture works but buttons/wheel remain unproven in Raft.
next: run python -m unittest discover -s scripts/tests -p test_t4_capture_acceptance_gate_runtime.py -v, then compare captured callbacks against actual signed Raft Unity legacy consumption.
