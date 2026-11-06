# T2 — Original Foam exported Shader GUID / Material pointer bridge, guarded original two-pass candidate

**2026-11-06 · T2 · session `20261106T2020Z-T2-chat-foam-export-guid-material-3c5e` · WATER-001 OPEN · game NOT_READY.**

## Direct game-export finding — a concrete fix target, not a hypothetical shader absence

The owner-direct experimental native [GitHub Actions 42281310905](https://github.com/alwansan/raf/actions/runs/42281310905), immutable source `d692400115c36c4839fa4f4954e5f6ed1c60d413`, reached the actual AssetRipper Unity export before failing later at Unity C# Editor compilation. Its genuine `RAFT_EXPORTED_RENDER_CONTRACT` logged **`UltimateWater/Foam/Global`: one programmed Pass**. Its genuine `RAFT_ORIGINAL_WATER_RENDER_GATE` logged **one active SubShader with one completed Pass**, **original_meta_present=true**, and **required_passes_from_device_log=2** (owner phone log requested pass index 1). Consequently the current exported Foam implementation cannot satisfy the logged per-Shader pass requirement. This observation is **before** any newly prepared private Foam source candidate installation.

Other water issues are independently still unsatisfied: Spectrum requires 6 active passes but the old export had 1; Depth Copy has alternate SubShaders 6/3 and fails the per-active-SubShader four-pass requirement; FFT/compute kernel source authenticity and execution remain blocked. The native job **FAILED** at Editor `CS0234` unresolved `RaftAndroid.Platform.AndroidPhysicalMouseCapture`, not at our new Foam probe. New T4 source-only ABI checks do not retroactively cure the old Unity compile. No APK/OBB/XAPK delivered by that job.

## New read-only exported shader → material GUID audit

Integrated [commit `0d0a9790`](https://github.com/alwansan/raf/commit/0d0a9790b78953c6f7c7b6be1324a15dfd862bf2) adds `scripts/t2_foam_export_binding_probe.py`, `tests/test_t2_foam_export_binding_probe.py` and an independent 7-minute source-only CI workflow.

The probe scans a real Unity **exported Assets** directory when available, without writing to it. It requires exactly one parsed original Foam ShaderLab name (not a file path guess), a physical well-formed nonreserved `.meta` GUID, and no duplicate GUID in **any** exported Assets metadata. It rejects symlinked paths, malformed/multiple/oversized metadata, duplicate Foam Shader identities and malformed Material `m_Shader` PPtrs. For each YAML `!u!21` Material document, exactly one `m_Shader` field is required. The exact local Foam Shader reference is `{fileID:4800000,guid:<actual-exported-Foam-GUID>,type:3}`; matching the same text/number outside a Material or using a wrong `fileID/type` is never counted as a valid link. Exports only **source-free count and boolean fields**, not paths, private shader source, original GUID values, raw YAML or Unity object IDs.

**Important limitations:** Unique well-formed exported GUID **does not prove** it matches the original PC Unity PPtr or a runtime active `Material`. Zero serialized Foam references is **not** proof of a broken shader: independent SHA-original compiled CIL [42280502421](https://github.com/alwansan/raf/actions/runs/42280502421) shows Foam `Shader.Find` → original instance Shader field → `new Material(Shader)`, a plausible dynamically instantiated path. No absolute Android or game rendering claim is made.

[**CI42288126476**](https://github.com/alwansan/raf/actions/runs/42288126476), job `128134165427`, exact source `0d0a9790`, **SUCCESS**: **16/16 new synthetic exported GUID/Material PPtr tests** and **17/17 existing Foam private installer tests** passed, including duplicate meta collision, corrupt PPtr, wrong fileID/type, wrong YAML object class, missing/duplicate target, reserved GUID and symlinks. These are safety controls, not authentic exported game material associations.

## Original-source candidate + synthetic exported Material continuity

The prior SHA-original [Foam private two-pass ShaderLab candidate](T2_FOAM_PRIVATE_SHADERLAB_EMBEDDED_HLSL_VULKAN_2026-11-06.md) is reconstructed **privately** from ZIP2 pinned commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Actual `sharedassets0.assets` source owner **115,978,112 bytes** SHA authenticated before UnityPy object parsing. It has **9,731 private ShaderLab bytes**, 2 authored properties (Texture+Vector), 2 authored Passes, 4 exact original stage-derived programs. It remains source-level HLSL/Vulkan validation, not original authored Unity ShaderLab import parity.

Existing **T2-owned** isolated original workflow now tests a **synthetic** exported Unity project with one exact Foam ShaderLab target and exactly one synthetic YAML Material pointing by `m_Shader.fileID=4800000`, real-in-fixture GUID and `type=3`. Using the actual SHA-original reconstructed 9,731-byte private candidate, it proves:

- before: **[1] Pass**, `Material` count **1**, exact Foam exported GUID references **1**;
- after: **[2] Passes**, exact Foam exported GUID references still **1**, Material bytes **unchanged**, Shader `.meta` bytes **unchanged**, original backup retained;
- source original owner SHA verified; source-specific private symbols, HLSL, shader and binary scratch purged before artifact publication;
- `actual_original_AssetRipper_export_tested=false`, `real_original_Unity_GUID_proven=false`, `unity_shader_import_compile_verified=false`, `android_Foam_pixels_verified=false`.

[**CI42288126264**](https://github.com/alwansan/raf/actions/runs/42288126264) **SUCCESS** at code `0d0a9790`, job `128134164949`. Log marker `T2_FOAM_SOURCE_AUTH_MATERIAL_PPTR_BRIDGE` contains only counts/booleans. Safe aggregate [artifact 13538108468](https://github.com/alwansan/raf/actions/runs/42288126264/artifacts/13538108468), ZIP **4,823 bytes**, artifact ZIP SHA256 `35d8735f54cb474ab111a4ce0908cd2e698d6b4b918eba727e91bc0ecf76b458` — **not** a private original-source hash.

### Concurrency / complementary work

The concurrent **T2 scheduled** session `20261106T2021Z-T2-scheduled-foam-guid-collision-f8a3` independently fixed a different installer hazard: duplicate `.meta` GUID across two exported assets now blocks installation *before any backup or shader mutation* ([commit 014d48fa](https://github.com/alwansan/raf/commit/014d48fafbfd93b0bf0f2bff46c3c82ad2940ef3), [CI42287347419 SUCCESS](https://github.com/alwansan/raf/actions/runs/42287347419)). This chat did **not** edit the scheduled session's installer file; our read-only preflight validates the complete metadata inventory and Materials, and complements that guard.

T4 owns Android physical mouse Editor compile repair, and T5 owns shared full native workflow and package delivery. T2 did **not** edit `.github/workflows/raft-unity-editor-android-import.yml`, trigger new Unity, overwrite metadata, modify gameplay shader/scene assets, or alter `.github/raft-native-build-request.json`.

## Immediate actionable handoff

See [T2→T5 native Foam handoff](../prompt/coordination/discussions/WATER-001/20261106T2020Z-T2-chat-foam-export-guid-material-3c5e-to-T5.md) for staging inputs and exact narrowly constrained source-only pre/post checks. Only a future **owner-authorized** native candidate should apply the private source-verified Foam ShaderLab over its **actual** AssetRipper-exported `.shader` file while keeping original `.meta` bytes unchanged. After that require actual Unity 2021 import diagnostics, shader runtime CB0/Material binding, FFT/Spectrum and finally Adreno screenshots. Do not bypass other water contracts or replay stale exception lists in the trial request.

**T2 trial `trial-20261106-r1`: «لا يحتاج».** No substantial native water-renderer code landed in the runnable Android project. WATER-001 stays OPEN, full game NOT_READY (3/3 independent full reviews not met).
