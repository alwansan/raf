# T1 scheduled checkpoint 20261106T041100Z-T1-scheduled-gate-f9c2
origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261106T031501Z-T1-scheduled-unity-failure-m8q4.md; 20261106T024340Z-T1-chat-84f0c6.md
base_sha: cd7fc78fab939ccd7c281e3c52d3e8416b1e5cf7
scope_commit: 975eb5f94a48c3995ec7528118fd123d320b5718
code_commits: 4517d10280b63309b57c8ba5c565d02e66b6b1f7; c3ffbfa5a59d87ef8d57f074c109cf87d433d596
origin_evidence: owner run 42058825739 world/save/reopen succeeded; package publication failed; CL 220911 water pass 23884 kernel 3850, 230108 pass 39132 kernel 6026. Slot 6 is NOT a proven Unity original FFT kernel name.
Unity runs 42152199100 and 42152295025 both completed failure: former resource validation, latter GameCI step 13. API job records identify only step, not earliest exception. Private GameCI log unavailable via accessible text endpoint; do not assert shader compile vs FindKernel vs Dispatch.
Engineering: fixed false-positive in scripts/t1_fft_unity_gpu_result_gate.py: root and test-case result Passed with an embedded NUnit failure/reason child could previously produce positive authenticity/dispatch flags. Now fail closed on contradictory nodes. Synthetic regression added in tests/test_t1_fft_unity_gpu_result_gate.py and existing fixture corrected to avoid spurious failure elements in passing records. Tests NOT EXECUTED in this run; no Unity/phone proof. No CI repeated or cancelled.
Next: run python3 -m unittest tests.test_t1_fft_unity_gpu_result_gate; obtain private 42152295025 GameCI log safely (redacted exception category only) and classify earliest failure before any new Unity run; then compare Vulkan/Unity first mismatching FFT pass and verify FindKernel/Dispatch identity. Protect original data and T4/T5 mouse/Resolution scopes.
status: completed (source guard only); WATER-001 OPEN, NOT_READY 0/3.
