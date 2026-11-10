# T1 scheduled checkpoint — 20261110T0906Z-T1-scheduled-fft-marker-integrity-b83f
origin: scheduled
resumed_from_sessions: 20261110T0814Z-T1-scheduled-fft-multipair-a6c9; 20261110T0712Z-T1-scheduled-fft-terminal-contract-f2a9
issue: WATER-001 (OPEN, NOT_READY)

## Priority evidence
Owner device run 42058825739 / source e9c358eda01785b65e4eb14f18723da426635628: world enter, save, exit, reopen succeeded from Artifact; package publication failed. Device sessions 220911-559: 23884 water-pass and 3850 FFT-kernel errors; 230108-327: 39132 water-pass and 6026 FFT-kernel errors. Separate session counters; neither proves unique failure count or root cause. Device screenshots and logs: alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57 (read-only). Latest 8 Nov mini-lab requirement supersedes old touch deferral for physical mouse; T4 owns pointer capture/clicks, T5 owns three buttons/Resolution/delivery.

## Scope and implementation
Work file: clients/T1/work/20261110T0906Z-T1-scheduled-fft-marker-integrity-b83f.md (created commit 50fce4a5bf2739d6eaf0fb1dd9672af15482c2a6).
Changed scripts/t1_fft_dispatch_pair_audit.py (f7da4de0a024cc8ea5fc3ec411f481c7e65642a6): reject native trace records that claim verified runtime mapping, FindKernel callsite, GPU result or water rendering despite unverified original hook. Terminal events cannot upgrade a source-only managed Dispatch return to GPU proof.
Changed tests/test_t1_fft_native_trace_contract.py (70e8cbd1c4de761ce2702404a5a5375f675b7db1): three regressions for forged terminal markers. No Unity build, GPU execution, phone run, or CI result claimed; tests not executed in this run.

## Evidence boundary / next action
Current original hook explicitly records original_findkernel_callsite_present=false, original_runtime_mapping=unverified and gpu_result=unverified. This prevents authentic kernel/resource mapping and first-pass Vulkan vs Unity numeric comparison. Next: run regression tests on commit containing 70e8cbd, inspect original FFT .compute GUID and exact FindKernel/Dispatch callsites, capture authenticated paired GPU readback from one build/session, compare first mismatch, then propose genuine source correction. Do not infer restored water from synthetic FFT test. Avoid overlapping T4/T5 files and redundant CI.
