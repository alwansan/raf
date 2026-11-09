# T1 original Dx11FFT index6 event-correlation hardening
session_id: 20261109T2030Z-T1-chat-index6-selector-correlation-c2d7
origin: chat
status: completed
base_sha: 5016e372792c31a343fde6b25eeb904531181888
issue_id: WATER-001
experiment_key: t1-original-dx11fft-event6-correlated-index-selector-consistency-tristate-no-findkernel-v1
resource_key: none (CPU-only source test)
intended_files: scripts/t1_fft_original_direct_dispatch_gate.py; tests/test_t1_fft_original_direct_dispatch_gate.py; docs/T1_ORIGINAL_FFT_EVENT_CORRELATION_2026-11-09.md; prompt/coordination/clients/T1/sessions/20261109T2030Z-T1-chat-index6-selector-correlation-c2d7.md; prompt/coordination/experiments/T1/20261109T2030Z-T1-chat-index6-selector-correlation-c2d7.json; prompt/coordination/B_TEAM/events/T1/20261109T2030Z-T1-chat-index6-selector-correlation-c2d7.json; this work log
source_commit: b78a2fa719e94974e20e31efa6d9b414223ec3b3
run_urls: https://github.com/alwansan/raf/actions/runs/42692853532
run_result: SUCCESS 28/28 Python unit tests, including 7 new negative source-selector/correlation controls
result: matching index6 no longer yields a clean numeric label when source formula/exponent/size/bank or compute preconditions drift; original runtime mapping false
limits: no Unity, no original GPU, no original owner device trace; WATER-001 OPEN NOT_READY 0/3
next_step: source-pinned real game direct numeric Dispatch/runtime call correlation on same APK+session; do not rebuild Mini for source-only work.
