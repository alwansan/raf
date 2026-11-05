# T4 chat — original SaveWorld RGD producer IL provenance

- session_id: 20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2
- origin: chat
- status: active
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
