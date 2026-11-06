# T4 chat — repair genuine save/load snapshot parsing after scheduled T4 guard

- session_id: `20261106T1351Z-T4-chat-rgd-snapshot-whitespace-p6q2`
- origin: `chat`
- base_sha: `9c6e70887fab25089beacc2ef790f29c2e11c252`
- resumed_from_sessions: `20261106T1343Z-T4-scheduled-n8p4`, `20261106T1334Z-T4-chat-windowfocus-m8v3`
- work: `prompt/coordination/work/LOCAL-005/T4-20261106T1351Z-T4-chat-rgd-snapshot-whitespace-p6q2-snapshot-token-whitespace-followup.json`
- status: `active`; issue LOCAL-005 OPEN, INPUT-005 unrelated OPEN

## Evidence and follow-on approach (before source change)

Read most recent scheduled T4 1343Z which implemented duplicate snapshot keys guard, status completed_source_change_unverified_ci. Exact later [CI42227641309](https://github.com/alwansan/raf/actions/runs/42227641309), source `289f59176586ebdc3eb7be758dc2be9be5416597`, failed THREE preexisting tests: expected nonzero snapshot became contradictory; two legitimate cross-session nonzero file hints became false. Added duplicate test passed misleadingly because its regex rejects legitimate semicolon-separated `length_class` token too. Diagnosis: Python source used raw `r"(?:^|;\\s*)"` (escaped `\\s` regex literal backslash-s), not actual whitespace `\s` matcher. This follow-on must correct regex without relaxing duplicate token rejection, and execute existing exact CI. Earlier CI42227626291 same earlier source failed. No user .rgd changed, no new phone logs.

## Nonoverlap and safety

Other T4 original seven-world fresh CLR Save/Load work (1221Z) remains separate; prior scheduled source was completed and left 3 regression failures. This is a bounded follow-on to that exact test failure, not overriding its session. T5 signed APK+OBB and T1/T2/T3 shader/FFT/visual code untouched. Only source-free log parser + its tests + own checkpoint/experiment/event. Do not claim on-device world save or missing Android renderer restoration.

## Next

Correct token separators, test valid semicolon+whitespace and contradictory duplicates with negative tests, run the existing original-data-free T4 JSONL CI and record actual final SHA/result; include the limits of aggregate log hints.

## Completed whitespace-token parsing repair — actual CI evidence

- Started on HEAD 9c6e70887fab25089beacc2ef790f29c2e11c252 and inherited completed T4 scheduled session 20261106T1343Z-T4-scheduled-n8p4. Its guard introduced two count regex literals `r"(?:^|;\\\\s*)"`, which matched a literal escaped s rather than whitespace. Even legitimate `exists_at_filename_argument=True; length_class=nonzero` became `contradictory`. Scheduled source CI [42227641309](https://github.com/alwansan/raf/actions/runs/42227641309) failed 3 prior cases, recorded before correction. New duplicate-token case had falsely passed because any semicolon-separated length_class was rejected.
- Fix at [commit 8a99840](https://github.com/alwansan/raf/commit/8a99840fa20bf830fb496ad9681913168a439d8e): change each count regex to `r"(?:^|;\\s*)"`, retaining exactly-once flags, original snapshot classifier and optional diagnostics. Additional two positive+negative whitespace/duplicate controls committed at [66b45b86](https://github.com/alwansan/raf/commit/66b45b86d7723ef80221da5087967bbb4b8c9936); only `scripts/t4_verify_device_world_save_log.py` and `tests/test_t4_verify_device_world_save_log.py` touched.
- Final exact [CI42228168580](https://github.com/alwansan/raf/actions/runs/42228168580) **COMPLETED SUCCESS** on 66b45b86d7723ef80221da5087967bbb4b8c9936, job 127926873063. Log: **23/23** parser tests, including all three earlier failed original tests and two new whitespace cases, plus **2/2** overflow controls = **25/25**. Earlier [42228118335](https://github.com/alwansan/raf/actions/runs/42228118335) on fix-only code also succeeded, but final includes tests. No Actions cancelled or manually dispatched; existing source-only workflow auto-triggered.
- Scope: no original game bytes, .rgd, native Unity/IL2CPP, Android device, player APK/OBB, Unity editor, T1/T2/T3 water or T5 delivery files changed. Does **not** prove physical device .rgd durability nor process restart, previous owner phone world/save/reopen remains linked to earlier artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739). LOCAL-005 still OPEN; NOT_READY 0/3.
- Work `prompt/coordination/work/LOCAL-005/T4-20261106T1351Z-T4-chat-rgd-snapshot-whitespace-p6q2-snapshot-token-whitespace-followup.json` completed bounded source tests; experiment `prompt/coordination/experiments/T4/20261106T1351Z-T4-chat-rgd-snapshot-whitespace-p6q2.json`. Handoff to T5 and independent event indexed after this checkpoint. Next: Use new matched signed Raft APK/OBB SHA/versionCode on owner POCO F5 Pro, collect private post-source JSONL + real world save/force-stop/reopen and actual hardware mouse focus/menu; source-only hints do NOT prove same-world durability. T4 1221Z original CLR fresh-process RGD scope remains independent.
