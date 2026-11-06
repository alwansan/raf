# 20261106T0606Z-T1-scheduled-gate-regression-v8p2
origin: scheduled
status: active
issue_id: WATER-001
baseline_sha: d9daaeea3ecf5496481372fd9c6059612f06394f
intended_files: scripts/test_t1_fft_unity_gpu_result_gate_contract.py; prompt/coordination/clients/T1/sessions/20261106T0606Z-T1-scheduled-gate-regression-v8p2.md; this work file
hypothesis: the currently committed Unity FFT result gate must reject contradictory NUnit suite/test status while retaining a genuine 2-case success, without private logs.
experiment_key: T1-NUNIT-GATE-CONTRACT-7a9e684397572419adcb38cb668a227a81cdda5b-20261106
resource_key: none (source-free CPU tests; no Unity GPU)
taken_over_from: T1 commit 348668d609ff82a6cdb2f6e41ddef1efcfce2de0 and prior T1 sessions; owner phone report 42058825739
scope: only new standalone tests; do not modify gate, game, T4 mouse, T5 resolution or CI workflows.
next: run unittest locally; capture result and independent checkpoint; no Unity/phone proof.
