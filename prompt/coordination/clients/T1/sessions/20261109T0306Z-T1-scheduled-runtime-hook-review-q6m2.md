# T1 scheduled session 20261109T0306Z-T1-scheduled-runtime-hook-review-q6m2
origin: scheduled
base_sha: 830bd8b4101736a47038c4a63efbcce3cb3ba796
scope_commit: c779b2f81867ac21cff977cf79e37f10f4ee3384
code_commit: afc2a4301075eabd95dc6e887ef085b72a8eba08
tests_commit: 8c66b877cbe72326342d7366b873c5f16fe3187a
status: SOURCE_ADDED_TESTS_PENDING

Read owner feedback docs/DEVICE_FEEDBACK_42058825739_AR.md before prioritizing: owner successfully loaded/saved/reentered world using Artifact 42058825739; packaging publish failed; 220911-559 summary had 23,884 water-pass and 3,850 FFT kernel errors; 230108-327 had 39,132 pass and 6,026 kernel errors. Do not regress this to APK86.

Read AGENTS, CURRENT_OWNER_REQUIREMENTS, STATUS, CHAT_AND_SCHEDULE, PROMPT, OPERATING_MODEL and latest T1 memory. Current HEAD at start 830bd8b4101736a47038c4a63efbcce3cb3ba796. Latest inspected T1 original hook CI42550454734 SUCCESS on 41559e96324b96293457ff578d5e069fe5a8bf53, and runner guard CI42550454759 SUCCESS; no equivalent CI repeated. T4 latest commit owns separate analyzer. T4 physical mouse and T5 resolution/buttons stay separate.

Concrete new source: scripts/t1_fft_dispatch_pair_audit.py and tests/test_t1_fft_dispatch_pair_audit.py (7 synthetic regression cases). Audit validates bounded sequence 1..16, duplicate fields/events, missing AfterDispatch and orphan AfterDispatch, and explicitly returns GPU and runtime-kernel proof false. It consumes only sanitized single-session JSONL event/message records; actual AndroidRuntimeLog export schema is NOT yet verified, so adapter and real-world input must be confirmed before deployment. No game assets or raw logs published. This is a diagnostic aid, not original Unity FindKernel mapping or water repair.

CI for new tests: NOT_RUN. No Unity/APK/phone GPU test. Need run python3 -m unittest discover -s tests -p 'test_t1_fft_dispatch_pair_audit.py' -v; then inspect actual sanitized AndroidRuntimeLog record schema and connect to same-build source SHA, shader GUID, runtime size/bank, resource binding and Dispatch, first numeric mismatch Vulkan/Unity. Preserve original .meta and save files. WATER-001 OPEN / NOT_READY 0/3. No build request; T5 owns shared mini/full XAPK coordination.
