# T2 scoped work — summary schema failure diagnosis

session_id: 20261105T1520Z-T2-scheduled-e7c1
origin: scheduled
issue_id: WATER-001 (evidence-index blocker)
baseline_sha: adf2c665244b0dc9365ca803fc454f3be2a04788
resumed_from_sessions: 20261105T1418Z-T2-scheduled-a91c, 20261105T1509Z-T2-chat-original-byref-sink-a83c
status: completed_diagnostic
intended_files: this work record and own T2 session only; no T5 records or shared source edits
experiment_key: T2|summary-42053770984|schema-identity|event-T5-20261105T1455Z|no-rerun
resource_key: none

Hypothesis: T2 evidence summary workflow fails before git push because inherited ledger contains an event without the identity key expected by refresh_b_team.py, not due to concurrent branch push or shader regression.

Evidence: [CI 42053770984](https://github.com/alwansan/raf/actions/runs/42053770984) job 127336509352, step 'Rebuild T summary from current inherited ledger; fast-forward only': Python traceback refresh_t_team.py -> refresh_b_team.py read_records -> ValueError Missing record identity: prompt/coordination/B_TEAM/events/T5/20261105T1455Z-native-cancel-failed-step.json. Live T5 record has event_id but no id; source ownership T5. Failure precedes git commit/push. No retry of identical run. This diagnosis does not imply source, Unity, GPU or device failure.

Next: Coordinate owner T5 to add canonical id consistent with event_id without overwriting their event; re-run only when source changes. Meanwhile T2 next source-authentic question is actual typed byref target body from successful [42053062181](https://github.com/alwansan/raf/actions/runs/42053062181), or independent Spectrum/Foam resource-to-material mapping. WATER-001 OPEN; NOT_READY.
