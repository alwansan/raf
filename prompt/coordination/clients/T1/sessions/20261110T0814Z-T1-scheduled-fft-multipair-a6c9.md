# T1 scheduled checkpoint — 20261110T0814Z-T1-scheduled-fft-multipair-a6c9
origin: scheduled
issue_id: WATER-001
updated_at: 2026-11-10T08:14:28Z
resumed_from_sessions: 20261110T0712Z-T1-scheduled-fft-terminal-contract-f2a9; 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
baseline_source: feature/android-native-port; read owner feedback, AGENTS.md, owner requirements, STATUS and T_TEAM coordination/operating prompts.
scope_commit: c8586bf413e712171eab022d978b84b76fcd7e57
source_commit: bae1d56a07cf163eef8ae4694a037b835c81bf15
files: prompt/coordination/work/WATER-001/20261110T0814Z-T1-scheduled-fft-multipair-a6c9.md; tests/test_t1_fft_multipair_provenance.py; this checkpoint.
result: Added four independent Python regression scenarios for two native FFT Dispatch pairs, cross-build contamination, duplicate-before invalidation, and cross-session contamination. They assert source-only evidence cannot imply GPU or Unity kernel identity. No Actions dispatched and no CI execution claimed; tests are UNVERIFIED until run on commit containing bae1d56a.
owner device evidence: 42058825739 world entry/save/reentry from artifact; 220911-559 water-pass 23884 and FFT kernel 3850; 230108-327 water-pass 39132 and FFT kernel 6026. Sessions not additive. Actual original FFT resource GUID, FindKernel mapping, Unity GPU execution and numeric first mismatch remain unknown.
next_step: Run python -m unittest tests.test_t1_fft_multipair_provenance (or unittest discover) on SHA containing bae1d56a; if PASS, use actual same-build before/returned/threw phone JSONL to match Unity kernel/dispatch, then original Vulkan-vs-Unity per-pass readback. Coordinate with T5 shared mini APK and T4 physical mouse; do not duplicate CI or modify their files.
status: WATER-001 OPEN / NOT_READY 0/3. No source/game assets modified, no phone/Unity test claimed.
