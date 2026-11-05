# T3 → T5/T2: B02 missing Particle third Texture2D is intentionally SKIPPED on nonexportable AssetRipper collection

Real source-authenticated [CI42132262184](https://github.com/alwansan/raf/actions/runs/42132262184) SUCCESS 100/100 source-free controls + actual pinned SHA-original ZIP2 export. Exactly one of the three SHA-original class28 Texture2D targets used by the unique source ParticleShader48 108-use Materials is **PRESENT IN AN AssetRipper `collection.Exportable=false`**. Current B02 exporter trace deliberately skips nonexportable source objects, explaining 2/3 vs the original three. The two exported source images and 9/10 Material TexEnv PPtrs exactly match. Five Material21 and all ten UV/slot labels persist; the untraced Material slot remains nonnull.

**Critical:** This is NOT a proven lost Android texture. It is a bounded B02 tracer selection boundary; do not inject placeholder or duplicate texture. Determine the exact `container.CreateExportPointer` for this private nonexportable source Texture2D and compare against actual exported Material's tenth PPtr to prove engine-builtin/nonexportable mapping parity. Then verify full native Unity/phone smoke/fire pixels and real emitter. No game asset or APK modified.

Source-only report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_PARTICLE108_B02_NONEXPORTABLE_CAUSE_2026-11-06.md
