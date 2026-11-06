# T4 chat — reject ambiguous JSONL object members before classifying world-save evidence

- session_id: `20261106T1359Z-T4-chat-jsonl-duplicate-keys-r7m2`; origin: `chat`; status: `active`
- resumed_from_sessions: `20261106T1351Z-T4-chat-rgd-snapshot-whitespace-p6q2`, `20261106T1343Z-T4-scheduled-n8p4`
- base_sha: `af440fa5c42be5c62aeec502accb020272bbbd15`
- issue_id: LOCAL-005 (OPEN)
- work: `prompt/coordination/work/LOCAL-005/T4-20261106T1359Z-T4-chat-jsonl-duplicate-keys-r7m2-jsonl-ambiguous-object-keys.json`
- experiment_key: `T4-LOCAL005-JSONL-duplicate-object-members-and-nonfinite-JSON-ambiguous-evidence-sourcefree-original-logger-v1`
- resource_key: `T4-jsonl-evidence-source-only-no-device-no-Unity`

## Baseline and independent hypothesis
The previous chat 1351Z fixed a literal-backslash-s duplicate snapshot-field detector, [CI42228168580](https://github.com/alwansan/raf/actions/runs/42228168580) completed success 25/25 source-only controls; original device world-save test remains only owner [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), immutable source `e9c358eda01785b65e4eb14f18723da426635628`. A copied log JSON record with repeated keys is silently accepted by default Python `json.loads` and keeps the last field value; e.g., two `operation` fields may turn a non-save event into a positive `Save.argumentFileSnapshot`. Non-standard numeric constants NaN/Infinity are also accepted by Python default JSON parser and should fail closed as malformed evidence. No evidence that the game's own logger emits them; this is verifier hardening for untrusted exports.

## Planned scope before edit
- Add narrow strict object member and JSON number token parser hooks in `scripts/t4_verify_device_world_save_log.py`; return fixed sanitized error category, never duplicate keys or raw content. Keep original exact repeated *log lines* deduplication (startup/rotation), original session sequence/time checks, optional detail fields and cross-session hints (always non-device claims).
- Add synthetic tests for duplicated top-level `operation`/`detail` and nested member, non-finite JSON numbers, one standard valid record, and identical startup replay; run only existing T4 source-free GitHub workflow. No original .rgd, Android Unity, assets or private log files.
- Existing separate T4 1221Z 7-world CLR cross-process work owns C# runner. T1/T2/T3 restore water/render and T5 signs/attests packages, no competing files. Do not cancel or dispatch heavy Unity builds. Work reservation committed before these edits.

## Next
Implement, review exact GitHub Actions run logs and failing cases, record experiment/event/T5 handoff, keep LOCAL-005 and INPUT-005 OPEN pending new matching APK+OBB phone evidence.

## Code checkpoint, exact final CI pending
- Source on branch: [strict JSON object key parser commit 9b44be1](https://github.com/alwansan/raf/commit/9b44be1d6110c9bf3123c72bc195027db7c8632a), [four new source-free regressions 74607f8](https://github.com/alwansan/raf/commit/74607f816ab4bd6dd35686f928fe3d81bbb60494). Only `scripts/t4_verify_device_world_save_log.py` and `tests/test_t4_verify_device_world_save_log.py` changed; no Android native C#, original files, .rgd, settings, audio or player build.
- New `json.loads(..., object_pairs_hook=_strict_json_object, parse_constant=_strict_json_constant)` checks duplicates **including nested JSON**, and nonstandard `NaN/Infinity/-Infinity`. Raises only sanitized `duplicate_json_field` or `nonfinite_json_constant` errors, not raw key/value/paths. Retains valid unknown optional members, old event-replay deduplication and exact snapshot flag decoding.
- [First parser-only CI42230129397](https://github.com/alwansan/raf/actions/runs/42230129397) completed SUCCESS; final [CI42230233069](https://github.com/alwansan/raf/actions/runs/42230233069) was queued at checkpoint. Do not count parser-only result as acceptance for four new tests. No heavy Unity Actions dispatched/cancelled.
- Expected final: **27 parser negative/positive tests** (23 existing +4 new) and **2 overflow** tests, plus no game data gate. Original user-owned playable/save/reopen scenario only applies to earlier artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739); aggregate logger hints do not prove world durability/process restart. Work `prompt/coordination/work/LOCAL-005/T4-20261106T1359Z-T4-chat-jsonl-duplicate-keys-r7m2-jsonl-ambiguous-object-keys.json` awaiting exact CI; experiment `prompt/coordination/experiments/T4/20261106T1359Z-T4-chat-jsonl-duplicate-keys-r7m2.json`.
