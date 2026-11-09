# T4 chat | independent mouse-counter invariant gate
session_id: 20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6
origin: chat
issue_id: INPUT-005
status: active
base_sha: 4a26329f0cc8edd0961b832feeab761869cf6540
scope_reservation_commit: 2d7c268248b505e4dd9ad1daa9491787df07665c
resumed_from_sessions:
- 20261109T1939Z-T4-scheduled-reader-poison-q8m5
- 20261109T1912Z-T4-chat-logger-session-guard-n5r7
experiment_key: T4-INPUT005-Unity2021-mouse-action-reader-counter-structural-invariants-v1
resource_key: none
intended_files: scripts/t4_correlate_mouse_runtime_epochs.py; scripts/tests/test_t4_correlate_mouse_runtime_epochs.py; own work/session/experiment/event only.
run_urls:
- https://github.com/alwansan/raf/actions/runs/42685509815
updated_at: 2026-11-09T19:46:00Z

## Recovered baseline
Latest T4 scheduled source-only test commit a3660d2e passed 25 tests (CI42685509815 SUCCESS). Prior chat source logger provenance CI42681491521 passed 24 tests. Old original Raft world/save evidence artifact 42058825739 is **not** proof for current mouse fallback. Current T4 INPUT-005 physical LEFT/RIGHT/MIDDLE and both scroll axes need a newer signed same-source full game and actual user testing; NO DEVICE PASS and no XAPK vote override. Live HEAD checked 4a26329f with zero queued/in_progress runs before reservation. T3/T5 working elsewhere; no same-file active work identified.

## Planned independent engineering
Source C# PhysicalMouseActionEvidence.Record increments Count once per accepted action, press/release each at most once, vertical and horizontal scroll may be counted on the SAME action. PhysicalMouseLegacyReaderEvidence.Record increments one total call and (at most) one native/fallback positive, and positiveEdges and positiveScroll are disjoint subsets of positives. The Python analyzer guards native+fallback<=getterCalls but not these additional producer-level constraints. Try adversarial tests; if failing, add exact fail-closed constraints. Preserve all previous proof levels; never mutate Unity/Android game, mini APK, owner CL or other worker's files.

## Next
Run isolated existing T4 mouse-epoch source-only workflow via watched path commits (not Unity build), capture job counts and status, append source commit and test evidence, publish own T4 experiment/event, mark own work completed or waiting_ci.
