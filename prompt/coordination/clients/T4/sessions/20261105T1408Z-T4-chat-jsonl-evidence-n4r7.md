# T4 chat — LOCAL-005 JSONL device trace gate

- session_id: 20261105T1408Z-T4-chat-jsonl-evidence-n4r7
- origin: chat
- status: completed
- resumed_from_sessions: 20261105T1246Z-T4-chat-load-file-gate-m8q2; 20261105T1338Z-T4-scheduled-v6n9
- baseline_sha: 87c0e1b9b889a67b245891819d44d4d9c0b18898
- started_at: 2026-11-05T14:08:57.818Z
- work_id: prompt/coordination/work/LOCAL-005/T4-20261105T1408Z-T4-chat-jsonl-evidence-n4r7-jsonl-evidence.json
- experiment_key: local005-jsonl-trace-contract-persistentDiagnosticLog-v1-20261105
- resource_key: none
- intended_files: scripts/t4_verify_device_world_save_log.py, tests/test_t4_verify_device_world_save_log.py, .github/workflows/raft-t4-world-save-log-evidence.yml, docs/T4_DEVICE_LOG_EVIDENCE_CHECKER_2026-11-05.md, prompt/coordination/work/LOCAL-005/T4-20261105T1408Z-T4-chat-jsonl-evidence-n4r7-jsonl-evidence.json, prompt/coordination/clients/T4/sessions/20261105T1408Z-T4-chat-jsonl-evidence-n4r7.md

## Evidence and overlap check
T4 other chat active work 20261105T1405Z-chat-original-rgd-runtime-k6n8 owns original 2941B Data.rgd BinaryFormatter/151 managed sibling CLR experiment. This session DOES NOT write its experiment paths or execute its original RGD test. Scheduled T4 1338Z documented phone evidence contract; this session implements a concrete source-free operational JSONL parser to enforce those boundaries. GitHub run sample latest T3 42036281059 succeeded, no queued/in_progress in sampled latest 34; CL main 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29 and last game APK86 remain old. No native run requested.

## Hypothesis
JSONL sequence-based, session-separated *evidence integrity* can be tested now from public PersistentDiagnosticLog source without reading original save data or releasing device logs. It should fail closed for missing candidate binding, incomplete sessions, no user confirmation, missing relaunch and unproven durability. Only aggregate diagnostics are allowed in CI artifact/log.

## Next
Develop and execute targeted tests; capture run and exact assertions; update this file and work, T5 handoff. LOCAL-005 OPEN, NOT_READY 0/3.

## Final verified result — 2026-11-05T14:17:52.386Z

- Source-free parser `scripts/t4_verify_device_world_save_log.py` was integrated [305e8952](https://github.com/alwansan/raf/commit/305e8952e4fc91afd0b3f2aef8a83df649d65db4). Synthetic workflow and tests on exactly the four scoped files; no original Raft assets or game source.
- Genuine logger contract read: `android-port/Runtime/Platform/PersistentDiagnosticLog.cs` emits JSONL utc/session/sequence/area/operation/detail; startup and segment copies can replay exact rows. Tool deduplicates identical rows, rejects conflicting replay and missing/rotated sequence, classifies Save/Load argument file size only and redacts details/session names/paths. Never reports device-confirmed.
- [CI42042997915](https://github.com/alwansan/raf/actions/runs/42042997915) SUCCESS 11/11 initial synthetic Python tests.
- Targeted inspection found independent Save and Load flags could combine an out-of-order three-session trace. Fix [b383b6e](https://github.com/alwansan/raf/commit/b383b6e86720369069e7cb61026105b78d6d668d) now requires strict earlier-session final UTC < later-session initial UTC. Two negative cases were added [fa3d5555](https://github.com/alwansan/raf/commit/fa3d5555d964d217351d43c4e1673642eb6bdb39) for Load-before-Save and overlapping sessions.
- [Final CI42043385806](https://github.com/alwansan/raf/actions/runs/42043385806) SUCCESS **13/13** synthetic controls, including repeat dedup, conflicts, sequence gaps, corrupt/invalid JSON, no user private path echo, missing .rgd evidence, ordering ambiguity. No device JSONL files or genuine .rgd were processed.
- Full report `docs/T4_DEVICE_LOG_EVIDENCE_CHECKER_2026-11-05.md`, work `prompt/coordination/work/LOCAL-005/T4-20261105T1408Z-T4-chat-jsonl-evidence-n4r7-jsonl-evidence.json` completed. Other concurrent T4 chat 1405Z original RGD seed CLR experiment owns distinct files and was not touched. Scheduled T4 phone evidence contract 1338Z remains authoritative.
- No native build/Unity/IL2CPP, no signed APK, no user-device playability/save/reopen proof, no changes to B50 Steam guards, audio, Settings, input, .meta, or original RGD. LOCAL-005 OPEN and NOT_READY 0/3.
- next_step: T5 signed candidate must report immutable source SHA and real phone sequence; run source-free verifier over startup and segment JSONL locally, then correlate with actual same-world offline play, save, full process exit and reopen. Do not take cross-session hints alone as acceptance or repeat current synthetic CI without changed input/hypothesis.
