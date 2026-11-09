# T1 — source direct Dispatch error correlation hardening

session_id: 20261109T2030Z-T1-chat-index6-selector-correlation-c2d7
origin: chat
status: completed_source_ci_verified
resumed_from_sessions: 20261109T2002Z-T1-chat-cl-t105-proof-6e8a; 20261109T1915Z-T1-chat-mini-butterfly-a9f3; 20261109T2016Z-T1-scheduled-evidence-order-5e91
base_sha: 5016e372792c31a343fde6b25eeb904531181888
work_id: prompt/coordination/work/20261109T2030Z-T1-chat-index6-selector-correlation-c2d7.md
issue_id: WATER-001
experiment_key: t1-original-dx11fft-event6-correlated-index-selector-consistency-tristate-no-findkernel-v1
resource_key: none
source_sha: b78a2fa719e94974e20e31efa6d9b414223ec3b3
run_urls: https://github.com/alwansan/raf/actions/runs/42692853532

## Team overlap decision
Recent scheduled `20261109T2016Z-T1-scheduled-evidence-order-5e91` owns `scripts/t1_shared_fft_device_evidence.py` and its tests; did not edit those. The older active direct binding review `20261109T1912Z` lists independent coordination files only. T5 R5 Mini delivered CI42691609924 success and does not require another T1 build; T2/T3/T4 workflows and sources left untouched.

## Actual work
- Detected `reported_error_correlation=same_event_numeric_argument_match_only` could be emitted with source selector drift, FFT size/exponent drift, unavailable compute or missing resources. A matching Dispatch integer is not source mapping proof.
- Updated `scripts/t1_fft_original_direct_dispatch_gate.py` and 7 new source-only negative tests in `tests/test_t1_fft_original_direct_dispatch_gate.py`. Existing evidence input schema remains unchanged; classifies mismatch / source context / missing dispatch preconditions, preserves no-original-runtime-proof semantics.
- GitHub Actions [42692853532](https://github.com/alwansan/raf/actions/runs/42692853532) COMPLETED SUCCESS at `b78a2fa719e94974e20e31efa6d9b414223ec3b3`: **28/28 tests PASS**. Tests are synthetic input records, not private original Unity runtime or device GPU runs.

## Scope, limits and handoff
Source-authenticated original Dx11FFT direct numeric Dispatch formula with zero FindKernel callsites is the underlying prior evidence (CI42519853981). Corrected classification still cannot attribute the owner's index6 to Dx11FFT without matching same-installed-game-device-session runtime trace. `WATER-001 OPEN` / `NOT_READY 0/3`; no water shader restored, no Mini/full XAPK request or CI cancellation. Next T1 session may use original source-pinned direct Dispatch runtime producer when authorized game test becomes available; scheduled T1 evidence-order code unaffected.

Doc: docs/T1_ORIGINAL_FFT_EVENT_CORRELATION_2026-11-09.md
