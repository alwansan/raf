# T4 — original JSONL envelope provenance
session_id: 20261109T2136Z-T4-scheduled-envelope-h8q2
origin: scheduled
issue_id: INPUT-005
baseline_sha: 96872c48cd318f4f1f49d13c24e87162435ab02c
scope_commit: d1b81b4af1cce82fb679cc261af1e3b4d4ec3abd
source_commit: 0c966c6feddb04c5ba270bc59b6f8ea3c5f38581
test_commit: fae88f7fc5213ee8d211bc2fb81283a3eeb48b57
status: waiting_ci
experiment_key: T4-INPUT005-jsonl-envelope-required-fields-v1
resource_key: none
resumed_from: 20261109T2042Z-T4-chat-release-final-window-q6n4; 20261109T2036Z-T4-scheduled-ci-provenance-m4q7

## Finding and change
The epoch correlator previously treated any dictionary with session/sequence as attributable to the original PersistentDiagnosticLog, even if utc/thread were absent or area was not input. This can mislabel synthetic or partial records as original runtime evidence. The new guard requires the original session, sequence, nonempty utc, integer thread and input area for attributed JSONL; legacy un-attributed text remains legacy and never gains original provenance. Six negative/positive tests added separately. Await actual CI confirmation; source-only, not phone/game PASS.

## Owner device baseline
Original owner Artifact 42058825739 on source e9c358eda01785b65e4eb14f18723da426635628 entered world, saved, exited and reentered. Preserve original .rgd. CL/test latest known shared-20261109-233132-554663211 had T4-01..09 NEEDS_INPUT; no captured physical game LEFT/RIGHT/MIDDLE/scroll phone proof. Previous T4 source-only CI42696168324 PASS 71/71. Latest branch baseline 96872c48cd318f4f1f49d13c24e87162435ab02c; no in_progress Actions on last read. No native game build, T5 shared Mini, Resolution, keyboard, audio, Settings or touch changes.

## Continuation
Confirm workflow run on fae88f7f and investigate any failures, then correlate genuine captured=true source callbacks with original Unity getters on same signed game build and gameplay effects. If CI fails, correct only T4 files. INPUT-005 OPEN, game NOT_READY 0/3.
