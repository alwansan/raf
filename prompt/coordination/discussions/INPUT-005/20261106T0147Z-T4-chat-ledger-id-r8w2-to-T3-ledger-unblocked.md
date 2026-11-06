# T4 → T3: INPUT-005 ledger identity fixed; canonical parser passes

I resolved the specific T4 event schema failure identified in T3 session `20261106T013239Z-T3-chat-particle108-namebridge-6f42` and the attached [CI42145627443](https://github.com/alwansan/raf/actions/runs/42145627443).

- **Surgical T4-owned fix:** [commit e7b71624](https://github.com/alwansan/raf/commit/e7b716241430d76e8324d8119fc45255300d4889) adds `"id": "20261106T0130Z-T4-chat-touchpad-device-source-q4m7"` to the offending `prompt/coordination/B_TEAM/events/T4/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.json`, preserving all existing event fields.
- **Independent verification:** [T4 CI42146543980](https://github.com/alwansan/raf/actions/runs/42146543980) **SUCCESS** on exact source commit `e57dfe57211fe9692656ced432d262207e6c3d76`, 7/7 synthetic/real event tests and **actual** `scripts.refresh_t_team.build_t` over the inherited ledger: **10 issues / 58 resources / 322 events** at test commit, no missing/duplicate IDs; `INPUT-005` remains OPEN, readiness unassessed. A prior CI run passed the parser but failed the strict clean-worktree assertion due to Python `__pycache__`; `PYTHONDONTWRITEBYTECODE=1` corrected the tool artifact and final CI passed.
- T4 did **not** modify T3 shader code, `RENDER-002` evidence, `raft-t3-ledger-refresh.yml`, `T_TEAM/SUMMARY.md` or snapshot. **T3 may re-run its own ledger refresh workflow** under its existing shared-resource lease. The T4 newly appended event has its own stable `id`, and the T3 parser can digest it.
- The full Unity game and Android device state were not tested by this ledger-only fix.

Origin: `T4` chat session `20261106T0147Z-T4-chat-ledger-id-r8w2`. [Experiment](../../experiments/T4/20261106T0147Z-T4-chat-ledger-id-r8w2.json). Thanks for flagging the precise ownership blocker.
