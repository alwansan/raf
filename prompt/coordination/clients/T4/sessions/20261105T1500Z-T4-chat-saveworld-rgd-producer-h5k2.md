# T4 chat — original SaveWorld RGD producer IL provenance

- session_id: 20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2
- origin: chat
- status: completed
- base_sha: 696ca2f9c933001dd9cb1aac457bccce6db928c4
- resumed_from_sessions: 20261105T1433Z-T4-chat-original-seed-save-roundtrip-j2v8, 20261105T1440Z-T4-scheduled-q8p3, 20261105T1405Z-T4-chat-original-rgd-runtime-k6n8
- experiment_key: local005-original-zip2-sha0a6f-compiled-CIL-SaveWorld-to-SaveRGD-argument-construction-count-v1
- resource_key: read-only original ZIP2 Assembly-CSharp SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e
- work: prompt/coordination/work/LOCAL-005/T4-20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2-rgd-producer-il.json
- files: android-port/Experiments/T4/OriginalRgdProducerIl/OriginalRgdProducerIl.csproj, android-port/Experiments/T4/OriginalRgdProducerIl/Program.cs, scripts/t4_validate_original_rgd_producer.py, tests/test_t4_validate_original_rgd_producer.py, .github/workflows/raft-t4-original-rgd-producer-il.yml, docs/T4_ORIGINAL_SAVEWORLD_RGD_PRODUCER_2026-11-05.md, prompt/coordination/work/LOCAL-005/T4-20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2-rgd-producer-il.json, prompt/coordination/clients/T4/sessions/20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2.md

## Coordination
T4 scheduled 1440Z JSONL UTC inversion task is blocked on concurrent HEAD updates; its intended scripts and tests are not edited by this session. T4 chat 1433Z original shipped Data.rgd CLR root vs private Save(string,RGD) mismatch is completed CI42047540260 and not duplicated. B14 already proved lexical SaveWorld->Save call existence; this new experiment checks **compiled CIL exact callee and RGD argument construction** and authentic source identity independently. No Unity heavy resource or native build, and no other client jobs cancelled. Only feature/android-native-port is writable.

## Next
Implement private CIL probe and strict source-free negative controls, run isolated Actions. Distinguish direct caller construction from global state/indirect origins and preserve unknown where evidence missing. LOCAL-005 OPEN, NOT_READY 0/3.

## Final checkpoint — 2026-11-05T15:22:30.223Z

- Work record completed: prompt/coordination/work/LOCAL-005/T4-20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2-rgd-producer-il.json. Source-provenance original DLL immutable exactly 3,211,776 bytes SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e from ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385. No original assets or decompiled IL published.
- Isolated new C# .NET8 Mono.Cecil v0.11.5 inspector, source-free Python verifier, synthetic tests and GitHub workflow: android-port/Experiments/T4/OriginalRgdProducerIl, scripts/t4_validate_original_rgd_producer.py, tests/test_t4_validate_original_rgd_producer.py, .github/workflows/raft-t4-original-rgd-producer-il.yml. No original game runtime code/serialized data modified.
- [CI42052712119](https://github.com/alwansan/raf/actions/runs/42052712119) SUCCESS 16/16, authenticated original SaveWorld and SaveUser each call exactly one original private Save(string,RGD), neither directly newobj RGD, nor declares RGD typed local or stores RGD field.
- [CI42053331738](https://github.com/alwansan/raf/actions/runs/42053331738) SUCCESS 19/19, both immediate preceding operand-source categories UNKNOWN_PRECALL_SOURCE. No dynamic argument-instance proof; original side effects not invoked.
- [FINAL CI42053882300](https://github.com/alwansan/raf/actions/runs/42053882300) SUCCESS 22/22 source-free tests, original exact DLL SHA/size verified, changed original DLL SHA rejected, full private .NET8 inspector executed; other SaveAndLoad methods have **zero direct newobj RGD**; SaveWorld and SaveUser have **zero direct generic Load<RGD> calls**. SaveWorld direct private Save RGD call count=1; SaveUser=1; original runtime never executed.
- Interim CI42053150724, CI42053281192, CI42053743825 and CI42053815348 failed due additive report/validator mismatch during staged changes, superseded by matched final CI; no actual game runtime failed.
- Main report docs/T4_ORIGINAL_SAVEWORLD_RGD_PRODUCER_2026-11-05.md; source commits 54e1431dec2b2afab5c63522f206be2394bbcf1a, 32448282aa9aceb5166c04c18e4692438dcced95, 2bc356110a4279fcbeb7e7ac53f94a1fb8f173c4, final controls 03978c08dff9cc58a84acea60948bd7d6461d6bf.
- The exact original SaveWorld→Save edge exists; RGD initialization/actual producer remains UNKNOWN. This does NOT establish the object came from a field/constructor/Load, nor game saving, Android/Unity IL2CPP, host completion, same-world relaunch or playability. The previous shipped 2,941B Data.rgd root mismatch still holds CI42047540260. No RGD fabricated or game serializer changed.
- T4 scheduled 1440Z JSONL UTC inversion work remains independently open; its source files and work/session were NOT modified in this chat. No native builds dispatched or cancelled, no changes to sound/Settings/touch, no force push; T5 owns candidate coordination. LOCAL-005 OPEN, NOT_READY 0/3.
- Next: track RGD population further **outside** direct SaveAndLoad constructor/generic Load IL patterns or use current T5 coordinated native candidate with actual user-generated RGD, play/save/full process quit/same-world reload and ordered device logs. Preserve no-fake flags and original binary source guard.
