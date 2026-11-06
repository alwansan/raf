# T4 chat — single-read immutable original owner JSONL evidence

- **session_id:** `20261106T2215Z-T4-chat-immutable-log-snapshot-n7b4`; **origin:** chat; **status:** active; **issue:** LOCAL-005.
- **base_sha:** `c2637f94aa71770caa34652e5a9e7442544e120a`; reservation commit `4d6fc5aad8cb8067f42d32cb41ae5bd4fb8959c3`.
- **resumed_from_sessions:** `20261106T2202Z-T4-chat-load-exit-proof-v6m2` (19/19 original clean Load<T> tests and CL-based evidence [CI42301269067](https://github.com/alwansan/raf/actions/runs/42301269067)); `20261106T2138Z-T4-scheduled-native-retry-q4n7` (separate T5 native build observation).
- **owned code/test:** `scripts/t4_owner5nov_jsonl_lifecycle.py` and `tests/test_t4_owner5nov_jsonl_lifecycle.py`; scope registered in `prompt/coordination/work/LOCAL-005/T4-20261106T2215Z-T4-chat-immutable-log-snapshot-n7b4-sealed-log-evidence.json` before edits.
- **hypothesis:** authentic original owner phone JSONLs are pinned by a Git blob read, but then separately reopened by `summarize` and the detailed chronological analyzer. A concurrent source rewrite can misattribute unverified bytes as pinned original.
- **approach:** synthetic RED interleave, then memory-only single capped byte snapshot for each input, private pinned byte and blob verification on the exact snapshot, common snapshot for both parsers. Source-only existing workflow checks all tests against real immutable CL@520c4cf without publishing the owner raw logs.
- **native build:** [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) pinned source `a1737bd7` still Unity import/compile (T5 ownership). No duplicate native job or changes to another agent.
- **bounds:** not original .rgd serialization, Android device acceptance, process relaunch, signed candidate or same-world proof. No game source, GUID, meta, FMOD, Settings, touch/layout edits; trial vote unchanged.

## RED / GREEN / Handoff
Pending source-only tested outcome.
