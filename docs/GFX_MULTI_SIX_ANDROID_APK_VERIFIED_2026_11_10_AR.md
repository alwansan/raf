# GFX-LAB — ستة موديلات المصدر الأصلية: Android APK مثبت البناء

- role: GFX-LAB; session_id: 20261110-GFX-chat-six-android-retry-04; origin: chat
- branch: experiment/android-graphics-rootcause (only written branch)
- source: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385, original SHA-checked private runner
- branch SHA built: ee96e4d86dd6679be6814e4116368a664362b12a
- [real Unity Android build CI 42720920391](https://github.com/alwansan/raf/actions/runs/42720920391) **SUCCESS**
- [APK Artifact 13721725242](https://github.com/alwansan/raf/actions/runs/42720920391/artifacts/13721725242) (expires 2026-11-16 23:39:48 UTC)
- original-source selection CI42719663373 **PASS**, source pack CI42720399689 **PASS**, source shader topology CI42720400057 **PASS**
- model categories: M00 shears (375v), M01 person (5095v/100 source bones), M02 tool (1666v/8), M03 static multi-material (2163v/2 materials), M04 skinned unidentified (2445v/100), M05 generic skinned (4452v/2)
- 6 original Mesh / 7 material slots / 21 original images; 15 sparse source stream chunks /707788800 bytes downloaded only in runner.
- source Shader48: 1 shared original shader object, 2 SubShaders and 7 Passes; **not restored as native Android shader**, no shader parity, no original animations, no full game.
- APK: `com.alwansan.raft.graphicslab.multi`, Android GLES3 IL2CPP ARM64, 24098726 bytes, SHA256 `ef2b86b9384144fc3dd13c93d9b3a4e98cc07bfba3493b6a5c59b52d8db13f6c`. BuildPipeline PASS, apksigner verify PASS, aapt exact package PASS, independent artifact extraction/CRC/SHA256/ARM64 library check PASS.
- owner Android test: **NOT YET DONE FOR SIX-MODEL APK**. Previous Shears v0.2 visuals were accepted, but are a different APK and cannot verify these five.
- request: six screenshots + six COPY LOG JSON files at SOURCE_PBR_STANDARD_APPROX, test M03 both material regions, M01/M04 appearance, compare Albedo if needed.
- future: isolate original Shader48 Pass/Keywords/CB/sampler/Blend/Normal DXT5nm and rig before handoff, and keep RENDER-002/WATER-001 OPEN.
