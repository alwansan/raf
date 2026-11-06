# T1 scope 20261106T041100Z-T1-scheduled-gate-f9c2
origin: scheduled
issue_id: WATER-001
base_sha: cd7fc78fab939ccd7c281e3c52d3e8416b1e5cf7
status: active
intended_files: scripts/t1_fft_unity_gpu_result_gate.py, tests/test_t1_fft_unity_gpu_result_gate.py, this work file, clients/T1/sessions/20261106T041100Z-T1-scheduled-gate-f9c2.md
experiment_key: unity-gate-failure-classification-42152295025-source-4ed17012
resource_key: none (source-only diagnostic)
hypothesis: existing NUnit gate may obscure whether GameCI failed before producing XML, so add a fail-closed classification that does not disclose private logs.
resumed_from_sessions: 20261106T031501Z-T1-scheduled-unity-failure-m8q4.md, 20261106T024340Z-T1-chat-84f0c6.md
Phone baseline: 42058825739 world/save/reopen confirmed; water errors 23884/3850 and 39132/6026. Kernel slot 6 not proven identity.
CI: 42152295025 failed step 13; 42152199100 failed step 12; no duplicate CI.
