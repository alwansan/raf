# 20261106T0606Z-T1-scheduled-gate-regression-v8p2
origin: scheduled
issue_id: WATER-001
base_sha: d9daaeea3ecf5496481372fd9c6059612f06394f
scope_commit: c47ff892d3c54a1879598fbef4a1611744ae35f9
source_commit: 6b6b01619a832cf0009cebc348aa09a854756aee
resumed_from_sessions: 20261106 T1 FFT Unity gate fixes (348668d, e88c739, 96d3f0c) and T1 prior Vulkan/Unity runs 42141540903, 42160755558
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, owner original device run 42058825739, CL fixed 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
result: Added seven bounded source-free unittest contract tests for authentic two-test NUnit proof gate; positive success, nonzero process exit, nested suite failure, nested reason, nested failure, duplicate case, no runtime/device/numeric parity claims, malformed/oversized XML. Local seven tests passed against a manually reconstructed equivalent of the fetched gate implementation; committed exact repository test not yet executed in CI.
files: scripts/test_t1_fft_unity_gpu_result_gate_contract.py (new only); no game assets or runtime code changed.
limits: This checks the *proof gate*, not original kernel FindKernel/Dispatch nor original Vulkan-vs-Unity pixel parity. Local test harness copied gate logic, not the exact repository module. CI confirmation remains required. Android owner world/save/reopen applies only to 42058825739 artifact; WATER-001 OPEN, NOT_READY 0/3.
next_step: Run python3 -m unittest discover -s scripts -p 'test_t1_fft_unity_gpu_result_gate_contract.py' -v against exact repository tree; inspect latest 42160755558 Unity proof artifact and first original Vulkan-vs-Unity FFT differing read/texel; do not dispatch duplicate Unity jobs. Confirm T4 physical mouse and T5 Resolution scope without editing their files.
