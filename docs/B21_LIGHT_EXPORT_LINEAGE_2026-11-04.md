# B21 — original native Light class108 same-instance export lineage

B21 session `20261104T2257Z-B21-8e72`, P0 RENDER-002. Write branch `feature/android-native-port` only.

## Evidence obtained

B21's previous pinned original scene evidence [41921259677](https://github.com/alwansan/raf/actions/runs/41921259677) and [41922372594](https://github.com/alwansan/raf/actions/runs/41922372594) showed six SHA256-authenticated original scenes: no baked lightmap assignments in them, and one enabled native Light in each of original level0/level1. Other scenes, exported files, lighting pixels and device render remained unknown.

The reviewed W1 exporter trace contains only original Material21/Shader48. The separate B02 optional staged trace adds Texture2D28; neither captures native Light108. Simply matching source pathID, name or matching Light count cannot prove AssetRipper exported the same Light object.

B21 implemented `scripts/b21_stage_light_lineage.py` which composes exactly the SHA-pinned W1 helper (Git blob `8e64093f5d1cd283f34163e2527c414b3f86b7a7`) and B02 staged helper (SHA256 `c99c6e163ee20d9ff72e2180ed72ce94b5c608e20dc1095c3c81d3e678532c1e`) into a **new private temporary** exporter helper with optional `RAFT_PRIVATE_EXPORT_LIGHT_LINEAGE`. It captures ClassID108 source collection+pathID and exported MetaPtr (when Exportable) with the **same** `export_instance` generated for W1/B02, tracking non-exportable skipped counts. No shared helper, base AssetRipper source in git, or game files changed. Generated B21-only SHA256 `25b1846284242293d314626fdcd40497bad3be03f275c8a94068f384f76467ee`.

[Pin/compile CI41929975841](https://github.com/alwansan/raf/actions/runs/41929975841) **COMPLETED SUCCESS** on source `37f7354af3bf068caf067b59591c8bf0d12bc38d`: 11/11 negative and preservation controls; exact public AssetRipperCLI `036098ab525a3f9f693dc101edeb21faad4d32d8` .NET9 compiled with all W1/B02/B21 capture routes and tool smoke passed. The compile did not load any Raft original inputs.

B21 also added **read-only** `scripts/b21_compare_export_lights.py`, enforcing original six-scene SHA256 authenticity, two actual typed native original Light values, same-instance W1/B21 private trace identities, one-to-one exported pointer, matching actual exported Unity YAML/scene GUIDs and local GameObject presence. It compares Enabled, Type, RGBA, Intensity and Range using explicit finite numeric tolerance, reporting aggregate drifts with no private identifiers. It refuses guessed/zero GUID, missing original Light, collapsed pointers and mismatched trace instances.

[Guard CI41930580691](https://github.com/alwansan/raf/actions/runs/41930580691) **COMPLETED SUCCESS**, 17/17 adversarial synthetic controls; separate job checked all six original ZIP2 SHA256/size pins and exactly two real source Lights using UnityPy1.23.0. **No real same-instance export was tested by this guard workflow**.

## Live bounded original-data experiment

[Run 41930891466](https://github.com/alwansan/raf/actions/runs/41930891466) **COMPLETED SUCCESS** as isolated bounded attempt, NOT a Unity/native build or APK. Exact ZIP2 pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385; only six original scenes + globalgamemanagers + globalgamemanagers.assets + sharedassets6.assets (9 small verified source providers), no LFS, 25-minute job cap and 2-core exporter. It stages three PRIVATE traces and runs the comparer against the actual same export if the incomplete source subset supports export. No game shader/source bytes or private identifiers are placed in GitHub artifacts; reports contain safe aggregate only. **Observed:** all 9/9 pinned original providers authenticated, original source graph contained **42 Materials, 18 Shaders, and 2 Lights**. The pinned AssetRipper .NET9 exporter completed the actual bounded project export and emitted W1, B02, B21 traces privately. A real same-instance W1↔B21 `export_instance` matched, the two original Light identities were each mapped by exporter-generated `MetaPtr` to actual exported Unity YAML; **2/2 Lights matched** for Enabled, Type, RGBA color, Intensity and Range; aggregate `value_mismatches={}`, `assets_changed=0`. No raw private trace or original resources/artifacts were published. This is real source-to-export value parity for those **two** scene Lights only, not a full-game result or native runtime light response.

## Status and boundaries

RENDER-002 and WATER-001 and LOCAL-005 OPEN. This is a concrete source-integrated diagnostic and exporter capability, NOT a Light color repair, shader/FFT fix, validated Unity render, real phone color proof, playable world or new signed XAPK. Still **NOT_READY, 0/3** immutable full reviews. Audio and Settings remain owner-confirmed; touch/layout deferred.

Next: prove the original native Light→GameObject owner relationship remains the SAME owner after export with a private class1 GameObject identity trace (both sides only locally present so far); then use source/export verified lighting exclusions to isolate genuine shader/material/ambient pixels. No FMOD/Settings/touch or game build modifications. Never patch original Light/color/GUID based only on matching names or count.

## Verified B21 real export acceptance checkpoint

[Actual run 41930891466](https://github.com/alwansan/raf/actions/runs/41930891466) completed SUCCESS, not pending. The source-authenticated 2/2 comparison is a **scoped original-to-actual-export field fidelity proof**, not an assertion of Unity/Adreno runtime quality. Do not repeat this identical bounded export without a changed source question. Record the GameObject owner identity separately from the already-proven Light values.
