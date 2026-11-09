# T2 independent scope — CASE03 status ambiguity
session_id: 20261109T0420Z-T2-scheduled-case03-status-8e31
origin: scheduled
baseline_sha: 487fff1c2b1714ed065a0ac6274e5b33eab3726e
issue: WATER-001 OPEN; mini GLES evidence integrity only
experiment_key: T2-CASE03-EXACT-STATUS-20261109
files: scripts/t2_gles_device_jsonl_gate.py; tests/test_t2_gles_device_jsonl_gate.py; own work and session only
hypothesis: CASE03 accepts the expected 0x8cd7 while a second contradictory 0x8cd6 appears, because it counts only expected status occurrences. Reject any extra hex status token without changing correct historical evidence.
shared_resource: none; no CI or Unity request; CL read-only.
proof_limit: synthetic consistency only, never original Raft water or GPU authenticity. T3 effects and T4 mouse/T5 resolution untouched.
prior: CI42549568993 original Foam value_mixed_or_joined; original object alias unresolved. owner phone run42058825739 world/save confirmed, FFT/water errors remain.
