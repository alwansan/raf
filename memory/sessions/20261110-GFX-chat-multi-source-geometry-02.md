# GFX-LAB 20261110-GFX-chat-multi-source-geometry-02

- origin: chat
- resumed_from: 20261110-GFX-chat-multi-bounds-source-01
- session_id: 20261110-GFX-chat-multi-source-geometry-02
- base_sha: 4839bdcef377d07c4aa47eea9357d05fd942e748
- experiment_key: gfx-multi-source-float32-spatial-span-select
- scope: source-only replacement of degenerate M02 with validated other original candidate; leave ZIP2 and T-team untouched.
- runs: GFX-MULTI-003 42718266273 FAILURE after M00/M01 success and M02 original fallback 1598v/2095t but degenerate actual vertex range.
- evidence_level: ORIGINAL_SOURCE chain previously PASS, spatial source M02 FAIL; UNITY_IMPORT_COMPILE incomplete; GPU/device not tested.
- control: source-verified typed original materials/shader/texture links, 7 material slots/21 original textures, strict finite/nonzero float32 OBJ spatial span and package mode not modified.
- work: extend source selector to try next verified original candidate, unit-test spatial validation and reject degenerate geometry pre-Unity.
- source_test_status: new CI to be verified, do not call this a fix until it passes.
- owner_screen: no six-model APK or Android device screenshots; prior Shears accepted only.
- next_step: verify GFX-MULTI-001 source selection, follow with pack test and APK only if audited.
