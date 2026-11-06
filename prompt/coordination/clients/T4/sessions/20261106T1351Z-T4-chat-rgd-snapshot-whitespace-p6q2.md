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
