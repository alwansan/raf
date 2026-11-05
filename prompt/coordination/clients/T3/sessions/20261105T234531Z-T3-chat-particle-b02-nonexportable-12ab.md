# T3 chat — one B02 missing Particle Texture2D traced to AssetRipper nonexportable collection

- session_id: `20261105T234531Z-T3-chat-particle-b02-nonexportable-12ab`; origin chat; T3; RENDER-002 OPEN/NOT_READY; status: completed actual diagnostic.
- base SHA `b6a66b64875ec053c05f5204e0cded84d886731a`, scope registered before edits in `prompt/coordination/work/RENDER-002/20261105T234531Z-T3-chat-particle-b02-nonexportable-12ab.json`, commit `781b5662f9a933022f94637997accf9c0f2a3028`.
- resumed from prior authentic first same-instance export [42130529677](https://github.com/alwansan/raf/actions/runs/42130529677) and `20261105T232821Z-T3-chat-particle108-sameexport-68c4` (5/5 source Materials, 2/3 source Textures traced, 9/10 exact pointers).
- experiment key `T3-SHA15964-particle108-1missing-B02-Texture2D-class28-nonexportable-vs-uncollected-actual-one-export-v1`; resource key `T3-own-dedicated-12owner-one-stream-B02-collection-classification-50min` RELEASED.

## Real CI

[CI42132262184](https://github.com/alwansan/raf/actions/runs/42132262184) source commit `aeca9d9c39132a448cf15ca3b357369deb6a7a4f` **SUCCESS** 100/100 source-free tests + pinned original six scenes/four Shader/Material owners/two globals + one original source stream full SHA + genuine one pinned AssetRipperCLI export. Both private W1 and B02 traces share the same exporter instance; actual exported Material YAML compared.

- Five original source Material21 still all five present. Three original source Texture2D28: 2 included in B02 `Exportable=true` list, exactly ONE in B02's **private** `Exportable=false` collection source identity list. It is **NOT absent from all collections**. B02 intentionally excluded it. Ten original nonnull Material TexEnv slots remain present in exported YAML, nine exact expected source Texture GUID matches and ten UV matches; one nonnull slot still unclassified against the intended nonexportable source engine pointer.
- New synthetic source instrumentation compile helper `scripts/t3_stage_particle_nonexportable_trace.py` (commit `f3a35298be9fe7b8eed84d4e24972bb38355a39d`), four test controls `f7003190c232be409002fdf191da98dfe64e70e2`, comparator classification `af10c22aa57783f5ea70d933005270ef073e730f`, three comparator tests `188839a8bbf35cb96e71971935284206666ae06d`, fixture correction `008db28949c46e66dc820b402822613866b58d35`, final actual workflow `aeca9d9c39132a448cf15ca3b357369deb6a7a4f`.
- Earlier [42132171708](https://github.com/alwansan/raf/actions/runs/42132171708) failed **one synthetic fixture** before source export due test assuming one synthetic Texture target was used once, whereas two Material slots shared it. That assertion corrected to 8/10. No original asset mismatch was involved in the synthetic failure.

**Boundary:** This does not establish source texture is present/absent from user's signed APK/OBB, nor whether exported nonexportable asset uses engine-builtin GUID in tenth Material pointer. No device GPU test, no shader/asset/.meta edits, audio/Settings/input/water/world unaffected. Other teams' jobs not cancelled.

Detailed report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_PARTICLE108_B02_NONEXPORTABLE_CAUSE_2026-11-06.md
Next: Privately derive same-instance container.CreateExportPointer for the exact source class28 Texture2D skipped by B02 because collection.Exportable=false, and compare it to the still-nonnull exported Material .mat TexEnv pointer. This may legitimately reference an engine/builtin Texture rather than missing Android asset; no game shader or texture must be changed until pointer parity and device pixels are verified.
