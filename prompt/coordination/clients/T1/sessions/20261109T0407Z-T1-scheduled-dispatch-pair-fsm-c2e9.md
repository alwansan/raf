# T1 — FFT Dispatch chronological pairing audit
session_id: 20261109T0407Z-T1-scheduled-dispatch-pair-fsm-c2e9
origin: scheduled
issue_id: WATER-001
base_sha: feae14e52bfc4e8e92f00b2716ba3556230e1f6a
scope_commit: 074562d0dfc411530e5462ef8b3e73ac2551ff29
code_commit: b999a77b1ce091e42f4104ff5af12cf65bb888a0
tests_commit: 335bcecb5919a5541ee2ad36a856ec6dfc006fa7
observed_head: 335bcecb5919a5541ee2ad36a856ec6dfc006fa7
status: SOURCE_PATCHED_TESTS_PENDING

## Evidence and scope
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner entered, saved, exited and re-entered world from run 42058825739 Artifact, while publish failed; 220911-559 contains 23,884 water-pass and 3,850 FFT kernel errors; 230108-327 contains 39,132 water-pass and 6,026 kernel errors. These are device-log reports, not actual Unity GPU execution proof. T4 mouse and T5 resolution/buttons are separate, untouched.

Resumed from 20261109T0306Z-T1-scheduled-runtime-hook-review-q6m2 and newer chat 20261109T0210Z-T1-chat-fft-dispatch-hooks-b6e4. Original source hooks have source-only CI42550454734 SUCCESS; Unity runtime/phone unverified.

## New result
Found deterministic chronology bug in scripts/t1_fft_dispatch_pair_audit.py: an AFTER row before its BEFORE was counted as matching merely because the AFTER event existed anywhere in the file. Added paired set populated only by AFTER observed after BEFORE, with duplicate-before preserving first pending record. Three regression cases added for orphan-then-before, orphan-then-before-then-duplicate-return, duplicate-before-then-return. No raw assets/logs published, no game code changed.

## Limits / next
Tests not executed in this run; run `python3 -m unittest discover -s tests -p 'test_t1_fft_dispatch_pair_audit.py' -v` on exact branch commit, inspect actual AndroidRuntimeLog JSONL schema and map real before/returned pairs from same game build. Source-only trace return is not GPU completion, FindKernel index identity still unproven; first numerical Vulkan/Unity divergence needs paired authentic captures. No native/Unity/mini build requested. WATER-001 OPEN; NOT_READY 0/3. Do not overwrite other sessions or shared state.
