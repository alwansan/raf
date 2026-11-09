# T1 FFT provenance-presence checkpoint
session_id: 20261109T1806Z-T1-scheduled-provenance-presence-q5n8
origin: scheduled
resumed_from_sessions: 20261109T1705Z-T1-scheduled-session-boundary-p8n4; 20261109T0155Z-T1-chat-direct-dispatch-f7a2
base_sha: 87ad14f48e6b11ec18232caa577c58e62125dca3
issue_id: WATER-001
work: prompt/coordination/work/20261109T1806Z-T1-scheduled-provenance-presence-q5n8.md
source_commit: f85d715fd638876a23488c7bae1d5a0523f9f155
test_commit: deba2d29eaa56c546508aa3b56a8a58ce24e385a
owner_device_reference: docs/DEVICE_FEEDBACK_42058825739_AR.md (run 42058825739; artifact world entry/save/reopen succeeded; package publishing failed)
5-Nov CL 220911: 23884 invalid water passes, 3850 kernel warnings; CL 230108: 39132 passes, 6026 kernel warnings. Do not sum sessions.
8-Nov separate session: 74359 water invalid passes, 11165 FFT kernel warnings; not Unity kernel binding proof.
engineering: Previously provenance equality checked only when present; one JSONL could mix legacy rows without session/build with attributed rows and count valid pairs. Audit now detects cross_session_provenance_presence for session_id/build_sha and invalidates all positive pairs on mixed presence. All-legacy inputs remain parseable and never prove GPU execution.
verification: three regression tests added; not executed in this cycle; no new Unity/Vulkan/device evidence. No CI or APK requested. No edits to T4 mouse or T5 Resolution.
next: run python -m unittest tests.test_t1_fft_dispatch_pair_audit; inspect real original Unity FFT FindKernel/Dispatch traces and compare first numeric Vulkan/Unity divergent pass. WATER-001 OPEN, NOT_READY 0/3.
