# T3 chat: original Shader48 stage I/O roundtrip-drift classifier integration

- identity: T3; session_id: `20261105T1542Z-T3-chat-io-drift-integration-a6d9`; origin=chat; status=active; issue RENDER-002 OPEN; branch `feature/android-native-port`.
- work: `prompt/coordination/work/RENDER-002/T3-20261105T1542Z-T3-chat-io-drift-integration-a6d9.json`. resumed_from_sessions: `20261105T1526Z-T3-scheduled-iosem-6c42` (scheduled classifier), `20261105T1459Z-T3-chat-921-4pass-translation-c7d2` (authentic source translator).
- Proven input: [CI42052605123](https://github.com/alwansan/raf/actions/runs/42052605123) SUCCESS true 921-use original Shader48 4 Passes, 8/8 real SPIR-V/HLSL roundtrip, source↔roundtrip stage I/O location/type arrays **0/8** identical; source↔roundtrip resource numeric mapping 8/8 unchanged. No original ShaderLab/device proof.
- Scheduled T3 helper `scripts/t3_stage_io_drift.py` + tests exists; helper's local synthetic controls passed 5/5. Distinct job is to **integrate as opt-in in owned four-pass real CPU translator**, classify input-vs-output drift with private source data still only inside runner, implement more asymmetric/negative tests, run source SHA-authenticated job once for new question. No raw names, shaders, paths, source stage bytecode or per-program hashes logged/artifact.
- Experiment key: `T3-ZIP2-15964ea8-6scene-4owner-top921-Shader48-4passes-8realstages-vkd3d-SPV-HLSL-roundtrip-IO-input-output-location-type-drift-classify-v2`.
- No full native job active at inspection; T1 FFT #42057399746 independent in-progress; T5 previously native #42052375742 ended failure; do not touch T1/T2/T4/T5 workflows.
- Last active result: pending; next check numeric-only real source output. RENDER-002 OPEN; original audio/Settings preserved, touch deferred.
