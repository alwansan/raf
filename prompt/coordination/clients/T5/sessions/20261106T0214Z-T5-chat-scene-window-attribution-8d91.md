# T5 chat — 20261106T0214Z-T5-chat-scene-window-attribution-8d91
- session_id: `20261106T0214Z-T5-chat-scene-window-attribution-8d91`; origin=chat; status=active
- base_sha: `19cf49c47b72ba828bc582fcad1212544a87b69f`; write branch feature/android-native-port only.
- resumed_from: T5 latest `20261106T0145Z-T5-chat-unity-surface-bridge-f4c2.md`; T5 scheduled `20261106T0047Z-T5-scheduled-c4e8.md` works Resolution/Settings and remains separate.
- source read: current original `AndroidTestDiagnostics.cs` blob 40cfdbb023f08d1a16378a2841fd9b72619b5616, `tests/test_android_diagnostics_policy.py` blob d0e0304dd4dca8829b24f1386ad6e5c5feae8803.
- Work lease: `prompt/coordination/work/PERF-007/20261106T0214Z-T5-chat-scene-window-attribution-8d91.json` (file/resource/experiment registered before any code changes).
- REAL source: CL original pinned Git commit `520c4cf409aa20a4db54ff80ed87d8807d9cba57`. Sample in session 220911: 19:10:34.360 last MainMenu perf, 19:10:39.991 active changed to MainScene, 19:10:41.532 96-frame perf labeled MainScene, thus scene attribution cross-window. Session 230108 20:04:02.855 MainMenu perf, 20:04:05.078 transition, 20:04:08.285 12-frame sample labeled MainScene. Avoid claiming exact frames belong exclusively to old or new scene.
- Planned: keep all frame samples and loading stalls, record start/end scene+activeSceneChanges for each window; separate source-policy verification, no new native game build.
- Scope only AndroidTestDiagnostics performance fields + new T5 policy tests/report; no T5 scheduled Resolution, T1 FFT, T2 Foam, T3 render, T4 input, Unity workflows or game assets.
- On completion: create experiment and B_TEAM event; update STATUS, session, and team summary. Ready remains NOT_READY 0/3; source-only checks don't prove phone behavior.
