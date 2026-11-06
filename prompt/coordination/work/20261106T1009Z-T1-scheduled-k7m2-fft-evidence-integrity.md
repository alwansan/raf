# T1 independent scope — 20261106T1009Z-T1-scheduled-k7m2
session_id: 20261106T1009Z-T1-scheduled-k7m2
origin: scheduled
issue_id: WATER-001
status: completed_source_unverified
result_commits: 2e1182f150d84c3842db54ff72e1fdf4a48d0c65; eef3692d63c2247e0315a33e2b78b8a503acba5c; cac3d913cd3672ed148f7906fc53f156f073d3c2
checkpoint: prompt/coordination/clients/T1/sessions/20261106T1009Z-T1-scheduled-k7m2.md
validation: pending actual CI; no workflow dispatched
next_step: run unittest on actual branch, then compare Vulkan/Unity FFT numeric first divergence and original FindKernel/Dispatch mapping
updated_at: 2026-11-06T10:09:42Z
baseline: branch feature/android-native-port; verified current evidence gate blob da907f333c8a2c1aa337492ea592b1f24cc0b449 and tests blob 7b5e9378626c11a86e4d5268903dad8382679d54
intended_files: scripts/t1_fft_unity_evidence_gate.py; tests/test_t1_fft_unity_evidence_gate.py; prompt/coordination/clients/T1/sessions/20261106T1009Z-T1-scheduled-k7m2.md
experiment_key: fft-unity-sanitized-json-cli-race-safe-20261106-gate-da907f33
resource_key: none; no Unity/GPU/Actions requested
hypothesis: The CLI currently checks symlink/size via stat before read_text, so an attacker or concurrent process can replace a checked path with an unbounded or symlinked file before the read; read exact bounded bytes from a single opened descriptor and reject symlinks, oversized and malformed UTF-8.
resumed_from: T1 prior scheduled 2e472e13f6932e863f7d461b3538075fcd547cf1; owner device feedback 42058825739; earlier Unity success 42160755558. Scope is source-only evidence integrity, not FFT parity.
