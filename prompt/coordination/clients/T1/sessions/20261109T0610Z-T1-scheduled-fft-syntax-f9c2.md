# T1 — FFT runtime gate syntax repair
session_id: 20261109T0610Z-T1-scheduled-fft-syntax-f9c2
origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261109T0407Z-T1-scheduled-dispatch-pair-fsm-c2e9; 20261109T0210Z-T1-chat-fft-dispatch-hooks-b6e4
base_sha: 75f4876cf7f486bac6d604a3d9018b478df5b699
scope_commit: e48103ff6463f61ce7759396b8fd023bae6c257c
code_commit: ae3477e0e57e340cb349813745a7c5dda1f1d2a6
tests_commit: 87e3eb9967bc1a59ed2f888ea1aa7657edd6030a
origin_scope: prompt/coordination/work/20261109T0610Z-T1-scheduled-fft-syntax-f9c2.md
status: SOURCE_PATCHED_TESTS_PENDING

## Device-first evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: run 42058825739 original source e9c358e; world entry/save/re-entry succeeded from artifact, package publish failed. Session 220911-559: 23884 water-pass errors and 3850 FFT kernel errors; session 230108-327: 39132 water-pass and 6026 FFT kernel errors. Later 8 Nov CL session reports 74359 water-pass and 11165 kernel6 errors, which do not establish original Unity kernel identity. Audio and Settings preserved. T4 mouse, T5 right-side controls and Resolution remain separate.

## Isolated source finding and repair
Read live scripts/t1_fft_runtime_evidence_gate.py: the radix-2 validation added earlier had FIVE literal backslash-n sequences inside the Python function body. These are not source line breaks, so the module could not be imported as valid Python. Replaced exactly those five escaped separators with physical newlines; no validation condition or GPU behavior changed. Connector read-back confirms no literal backslash-n indentation remains in the modified segment. Added tests/test_t1_fft_runtime_gate_syntax_f9c2.py: module import, FFT 256 acceptance, 0/1/3/255/257 rejection and boolean rejection.

## Validation limits
Connector source read-back verified repaired text. Local git/Python checkout of repository unavailable because container github.com DNS resolution fails; tests written but not executed. No CI or Unity/native/mini build manually launched; no game source, .meta, GUID or .rgd modified. Existing original Dispatch hook source-only CI42550454734 SUCCESS predates this repair. Actual Unity FindKernel/Dispatch and numerical Vulkan vs Unity first divergence remain UNPROVEN.

## Next
Run python3 -m unittest discover -s tests -p 'test_t1_fft_runtime_gate_syntax_f9c2.py' -v on exact SHA; confirm source CI then collect same-build device FFT trace with shader/size/bank/groups and kernel names; map first mismatch to authentic original Vulkan input and Unity output. WATER-001 OPEN / NOT_READY 0/3. No XAPK vote change.
