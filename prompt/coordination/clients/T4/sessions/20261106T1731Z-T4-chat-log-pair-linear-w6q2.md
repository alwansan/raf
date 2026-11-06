# T4 chat — bounded near-linear phone-log save/reopen evidence pairing

- session_id: `20261106T1731Z-T4-chat-log-pair-linear-w6q2`; origin: `chat`; status: `active`
- base_sha after HEAD retry: `697787bd3f9e582deda2f5dbe09ffe2b0456bd31`
- work reservation commit: `e7c173fadef28f310be18c8077af0251a6a138cf`, path `prompt/coordination/work/LOCAL-005/T4-20261106T1731Z-T4-chat-log-pair-linear-w6q2-linear-log-pairs.json`
- resumed_from_sessions: `20261106T1719Z-T4-chat-first-unity-error-recovery-b5q7` (297/297 source logs), `20261106T1637Z-T4-scheduled-v8m2` (mouse provenance); independent base report `docs/T4_DEVICE_LOG_EVIDENCE_CHECKER_2026-11-05.md`.
- owner [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) separately OWNER_CONFIRMED world enter/save/exit/reopen on old source `e9c358eda01785b65e4eb14f18723da426635628`; current source and real phone logger not yet attested.

## Scope and actual defect

In the source-free T4 device-log analyser `scripts/t4_verify_device_world_save_log.py`, `valid_pairs = [(i,j) for i in range(n) for j in range(i+1,n) ...]` constructs every pairing, even though `save_nonzero_in_earlier_session` and `load_nonzero_in_later_session` are both just booleans. Under a long-but-allowed input of hundreds/thousands of separate logger sessions this can cause O(n²) comparisons and O(n²) memory from tuples. On a privacy-safe 200-session input, exact original UTC comparisons can be bounded independently of runner speed.

Plan: add controlled comparison-count negative control using synthetic UTC wrapper for 200 sessions (100 save, 100 later load), preserving baseline positive hint and strictly false process/world/game acceptance; old quadratic code must fail the budget. Then replace pair construction with chronological one-pass scan tracking the earliest ending eligible save session, accepting a later eligible load only when `save.last < load.first` and both previous/current session completeness/UTC monotonic hold with no observed queue overflow. Add an early-exit loop and preserve `local005_device_confirmed=false`, `cross_session_same_world_proven=false`, original RGD format and all existing negative controls. No original game sources, `.rgd`, assets, native builds, T1/T2/T3/T5 work, mouse/touch/settings/audio changed.

Expected test workflow `.github/workflows/raft-t4-world-save-log-evidence.yml` (source-only Python unittest). Report separate red and green exact SHA; no device/IL2CPP claim. Work active until CI evidence recorded, independent event, T5 handoff and status completed.
