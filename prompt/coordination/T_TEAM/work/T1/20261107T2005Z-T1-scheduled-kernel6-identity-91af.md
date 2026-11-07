# T1 WATER-001 — kernel-index identity gate
session_id: 20261107T2005Z-T1-scheduled-kernel6-identity-91af
origin: scheduled
issue_id: WATER-001
status: active
base_sha: 6b442d3c4c5f6aea18c4290cfec08b47b55cf14e
intended_files: scripts/t1_kernel_index_identity_gate.py; clients/T1/sessions/20261107T2005Z-T1-scheduled-kernel6-identity-91af.md; this work record
experiment_key: kernel-index6-not-identity|owner42058825739|CL520c4cf|source-e9c358e|source-only-negative-gate-v1
resource_key: none (CPU-only; no Unity build)
taken_over_from: B08/B18/B30/B48 FFT investigations; T1 previous 20261107T1919Z auth bridge
hypothesis: Unity's kernel index 6 is only meaningful when joined to a specific ComputeShader asset and its compiled kernel table; reject any report that identifies FFT solely from integer 6.
coordination: independent new files; no T2/T4/T5 files; no shared CI dispatch.
updated_at: 2026-11-07T20:05:24Z
