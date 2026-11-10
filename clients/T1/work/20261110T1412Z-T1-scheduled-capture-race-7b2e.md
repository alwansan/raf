# T1 scope 20261110T1412Z-T1-scheduled-capture-race-7b2e
origin: scheduled
baseline_sha: 019bc6e7d4c90efaad6d7b8cd7a349f6f3cbc68d
issue: WATER-001
experiment_key: T1-FFT-CAPTURE-TOCTOU-20261110
files: scripts/t1_fft_capture_integrity_gate.py; tests/test_t1_fft_capture_integrity_gate.py; clients/T1/sessions/20261110T1412Z-T1-scheduled-capture-race-7b2e.md
hypothesis: replacing a private capture between stat and open, or during read, can invalidate metadata-only SHA provenance; pin opened inode and verify fstat before/after.
shared_resources: none; CPU-only, no CI/build/Unity. No T4/T5 files.
owner_evidence: 42058825739 world save/reentry from artifact, publication failed; CL 220911-559 23884 water/3850 kernel, 230108-327 39132 water/6026 kernel; counts separate.
proof_boundary: integrity of local bytes does not prove original Unity FindKernel, Dispatch or GPU water.
