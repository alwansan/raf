# T4 — full inherited event identity preflight, source-only

session_id: 20261109T1919Z-T4-chat-ledger-preflight-v4k8
origin: chat
issue_id: COORD-001
status: completed_source_only
base_sha: 6af1a2be89f70c66a922ef09443c4121fef4b18b
work_claim_commit: bc4cccf96768ac8aadd03f9d5161769a33cddc08
experiment_key: T4-COORD001-all-inherited-event-ids-nonmutating-enumeration-v1
resource_key: none
resumed_from_sessions:
- 20261109T1912Z-T4-chat-logger-session-guard-n5r7
- T2 20261109T1909Z-T2-chat-event-ledger-repair-n6q8
scope: only T4-owned new source auditor, tests, CI, report, separate T4 sessions and T4-to-team discussion. Never modify T2 refresh script or T3/T5 event data.

## Restored evidence and blocker

Reviewed live T2 CI42680680366 and CI42682378346: `refresh_b_team.py` fails at historical `B_TEAM/events/T3/20261106T2007Z-T3-chat-explicit-original-d52e.json`, which has no `id` or `event_id`. T2 had already fixed its own two T2 event files and requested T3 event-owned remediation; no ownership collision. Rather than weakening canonical identity requirements or editing foreign events, T4 enumerated the entire inherited event ledger and tested current schema equivalents in a separate tool.

## Code/results

- Source `scripts/t4_audit_team_event_identities.py` commit `65f1e298c7d3853c51eac42fb8c9b80d3fb47d06`. Exhaustively scans 15k bounded public metadata JSON events for missing/conflicting/duplicate identities, invalid JSON and symlinks, never repairs or infers IDs from filename. `audit_completed=true` never implies `canonical_summary_generation_proven=true`.
- Ten synthetic controls `tests/test_t4_audit_team_event_identities.py` commit `3738fd34e20e88dc4c8eb8797d370a231cafefb0`. Isolated workflow `.github/workflows/raft-t4-ledger-identity-audit.yml` commit `ad197f28c03fe9b5db66d088a74094e7c749aa26`.
- **Initial CI [42682466747](https://github.com/alwansan/raf/actions/runs/42682466747) SUCCESS**, 10/10 tests, 595 event files, **22 MISSING_RECORD_ID**, breakdown T3 14/T4 3/T5 5. Artifact 13702867598 provides full safe file paths.
- T4 independently reserved own event repairs in sibling session `20261109T1922Z-T4-chat-own-eventid-repair-z6q4`, added three owner-T4 event IDs only (commits 2b41ea0da, 891027dbbd, a41c46ef9e).
- Workflow trigger amended only for own T4 event files, commit `81c43f0b48365c18eb28a61e4f6bf26668c6e2ea`.
- **Second CI [42682900051](https://github.com/alwansan/raf/actions/runs/42682900051) SUCCESS**, job 129381898864, 10/10 tests, **596 event files, 20 MISSING_RECORD_ID** now T3 15/T5 5/T4 **ZERO**. A new unrelated T3 event `20261109T1913Z-T3-chat-smoke34-sameexport-v5m8.json` entered ledger after first scan. Artifact 13702214952.
- Public safe report `docs/T4_SUPPORT_T2_TEAM_LEDGER_AUDIT_2026-11-09.md`; coordination notice `prompt/coordination/discussions/COORD-001/20261109T1923Z-T4-chat-all-event-identities-v4k8.md` has all 20 files and links. No T3/T5 files modified.

## Boundaries and next handoff

T4 audit workflow green means only full census executed, not that T2 canonical `refresh_t_team.py` or linked source game passes. There are 20 remaining T3/T5 owner corrections, explicitly left to owners. T2 owns shared summary workflow. Do not erase events, produce fallback IDs from filenames in refresh script, or manually edit snapshots. Next T2/T3/T5 cycles should add own event_id values with CAS and rerun canonical summary once source ledger clean. This audit supports coordination, not RENDER-002/WATER-001/INPUT-005 phone acceptance, and **full Raft NOT_READY 0/3**.

No native game/mini build, no CI cancellation, no changes to .rgd, camera/touch/audio/Settings.
