# T4 to T5 — machine-checkable Android JSONL evidence gate

- session_id: 20261105T1408Z-T4-chat-jsonl-evidence-n4r7
- issue_id: LOCAL-005
- origin: chat
- CI: https://github.com/alwansan/raf/actions/runs/42043385806 (13/13 PASS synthetic, no device)
- code: scripts/t4_verify_device_world_save_log.py
- work: prompt/coordination/work/LOCAL-005/T4-20261105T1408Z-T4-chat-jsonl-evidence-n4r7-jsonl-evidence.json

Phone logs from new signed source candidate should be preserved in owner-controlled storage; run `python3 scripts/t4_verify_device_world_save_log.py --input <local-jsonl-directory>` on the merged startup/raft JSONL directory. Output is aggregate marker counts/session ordinals/sequence flags and class counts only, never raw paths/session IDs/game data.

Ordering safety: requires matching nonzero Save snapshot in an earlier session and nonzero Load snapshot in a strictly later session (earlier final UTC before later initial UTC). Replayed startup segment lines deduplicate; conflicting sequence and malformed rows fail closed. Rotated/missing segment sequences mark incomplete. All of these are diagnostics, not true process restart or same-world proof.

Native candidate source SHA/packaging must be independently verified; old APK86 cannot supply new instrumentation. Owner still must actually interact with new offline raft, save, kill fully and reopen the same world with restored state. No parser result can mark LOCAL-005 device confirmed automatically.

Independent other T4 1405Z original seed CLR deserialization work remains active and was not touched. Preserve existing B50 Steam, sound, Settings and deferred touch; T5 coordinate any native run, no run dispatched here.
