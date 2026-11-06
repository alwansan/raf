# T1 — real input-byte evidence join for original FFT versus Unity

- session_id: `20261106T1850Z-T1-chat-gpu-input-join-b71c`
- origin: **chat**
- base_sha: `97f156f9f09e8cd6f5412e281bb751d2bb1a8cd6`
- resumed_from_sessions: `20261106T1837Z-T1-chat-ftz-trace-89ac`; `20261106T181000Z-T1-chat-carrier-report-gate-4c7d`; `20261106T1808Z-T1-scheduled-unity-carrier-gate-m4k8`.
- issue_id: WATER-001 **OPEN**; full readiness **NOT_READY 0/3**.
- scope_status: **completed**, source-only CI verified; no original Raft private assets downloaded or Unity run in this cycle.
- work: `prompt/coordination/work/WATER-001/20261106T1850Z-T1-chat-gpu-input-join-b71c.json`
- experiment: `prompt/coordination/experiments/T1/20261106T1850Z-T1-chat-gpu-input-join-b71c.json`
- result event: `prompt/coordination/B_TEAM/events/T1/20261106T1850Z-T1-chat-gpu-input-join-b71c.json`.

## Recovery, context, peer coordination
Read T_TEAM RESTORE_AR, CHAT_AND_SCHEDULE_AR, PROMPT_AR, policy and trial vote, owner device report 42058825739, ZIP2 source rules and T1 chat/scheduled session handoffs. Live initial HEAD `97f156f9f09e8cd6f5412e281bb751d2bb1a8cd6`, no queued/running workflow at start. Subsequent T2/T3/T5/LOCAL-005 workflows used disjoint files; did not cancel or modify them. Reserved independent source-only work via [c5faa9b](https://github.com/alwansan/raf/commit/c5faa9b65a6b8d102e746c10880bcb3af9d5e356). T1 prior [42272859383](https://github.com/alwansan/raf/actions/runs/42272859383) confirmed 16/16 source-only FTZ taxonomy controls. Actual original-derived Unity OpenGLCore butterfly mismatch remains from historical original-data experiments, unproven cause; don't infer FTZ alone or Android water fix.

## Engineering change
Created `scripts/t1_fft_private_unity_input_join.py`: [0278df](https://github.com/alwansan/raf/commit/0278df06850b0566dd29f29fd7ff08c81f8fcb05), [6fc67cf](https://github.com/alwansan/raf/commit/6fc67cf22cbfa49615297a93f4db6d445e9e3ab3). This composes prior keyed trace SHA/role/content checks with direct **physical** exact-size `1024x32 RGBA32F` Vulkan and Unity source/butterfly images, per-backend actual content-derived `input_hash`, pinned canonical `1024x32 seed19 1x1x1` dispatch SHA, physical files distinct (no link, alias, symlink), distinguishable source and butterfly roles, and a strict `OpenGLCore\n0\n0\n` report from the prior `T1PrivateFftInputIdentityTests.cs` GPU CopyInput check. Reports safe counts only and declares unsigned GPU report/metadata limitations. This prevents equal fake SHA declarations from passing against different actual bytes, but is **not** cryptographic proof of the Unity compiler/runtime or original-authored kernel ID.

Added `tests/test_t1_fft_private_unity_input_join.py` in [33c41f2](https://github.com/alwansan/raf/commit/33c41f27dc61f1f347324a850226c44cf27851e1) with **17 adversarial synthetic tests**: valid join; mismatched source/butterfly even when declared SHA agrees; indistinguishable roles; bad digest/dispatch; truncated/oversized input; incorrect backend or nonzero GPU mismatch; absent/extra/BOM/oversized text; accepted CRLF; hardlinks, symlinks, altered trace, wrong candidate role, duplicate metadata keys, public CLI data redaction.

Added exact test command and path watch to existing own small CI workflow `.github/workflows/raft-t1-fft-invocation-pair-gate.yml` in [1819105](https://github.com/alwansan/raf/commit/181910545d4ced5a8454b95e4d380756ba2ac36f). Preserved 4-minute budget, ubuntu-24.04, prior controls and cancel-in-progress:false.

## Actual CI result
**[Actions 42274801434](https://github.com/alwansan/raf/actions/runs/42274801434) @ `181910545d4ced5a8454b95e4d380756ba2ac36f`, job `128088260468`: COMPLETED SUCCESS.** Checked decoded job logs: new **17/17 Python tests PASS**, prior paired-invocation suite and privacy gate all successful. No original Raft binaries, real Vulkan/Unity GPU test, APK/OBB/XAPK or on-device water pixels included in this run. No source-shader fix is claimed.

## Handoff
T1 trial vote `trial-20261106-r1`: **لا يحتاج** unchanged (only new diagnostic, no major game FFT integration). Last owner-tested Raft `e9c358eda01785b65e4eb14f18723da426635628` from [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739); owner entered, saved and reopened world, water/color deficits remain. No native request, shader or other worker file changed.

Next: coordinate authorized private Unity 2021 OpenGLCore real source-authenticated FFT keyed trace run with T5; gather *actual* original/Unity traces, both source/butterfly image sets and genuine CopyInput GPU marker in same runner; run:
```
python3 -m scripts.t1_fft_private_unity_input_join \
 --manifest PRIVATE_PAIR_MANIFEST.json --original ORIGINAL_TRACE.bin \
 --unity UNITY_TRACE.bin --vulkan-input-dir PRIVATE_PROJECT/T1VulkanCapture \
 --unity-input-dir PRIVATE_PROJECT/T1UnityCapture
```
Only then interpret per-site zero-collapse versus same-address subnormal FTZ, separately verify kernel name/FindKernel/group/bindings/variant. No speculative original shader edits or APK build on source-only success. Re-read live HEAD/Actions and other T1 sessions next cycle. Work scope released.
