# T3 session 20261104T2354Z-T3-render-harness

Started 2026-11-04T23:54:00Z. Base b56ebc3847f251cee2539e9797471417d32698d2. T3 assumes RENDER-002 material-export lineage and allied B12 synthetic diagnosis. Actions consulted: 41933025319 (failed: missing ComputeShader/Resources/Encoding stubs), 41933025251/41933025184 (success at older SHA). Current game Android APK86 only. Work item: T3-20261104T2354Z-T3-render-harness-b12-csharp-fixture. See ../MEMORY.md. Status: active; next engineering step: exact-production harness fixture repair, then same-instance asset comparison.

## T3 checkpoint 2026-11-05 00:23 UTC
- B12 synthetic exact production harness [CI 41937719270](https://github.com/alwansan/raf/actions/runs/41937719270) success.
- Genuine original Material TexEnv/UV [CI 41939404454](https://github.com/alwansan/raf/actions/runs/41939404454) success: 41 Materials/227 slots, 89 internal texture targets exact, 113 original null, 25 external not proven, 227 UV matches.
- Genuine original Material m_Colors [CI 41940350604](https://github.com/alwansan/raf/actions/runs/41940350604) success: 41 Materials/150 RGBA slots, 40 originally tinted, zero drift; earlier synthetic-only CI 41940116028 fixture bug corrected.
- Read [docs/T3_AUTHENTIC_MATERIAL_EXPORT_PARITY_2026-11-05.md](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_AUTHENTIC_MATERIAL_EXPORT_PARITY_2026-11-05.md), T3 state/memory, issues and resources for exact SHA/tools. No original asset modification, no Android Unity build/phone colors proven. RENDER-002 OPEN. Session paused at this checkpoint, not background running; resume current HEAD and investigate Shader/variants/sRGB and 25 external-owner links, coordinate with other T agents. Touch deferred, Settings/audio unchanged.
