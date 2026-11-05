# T3 — actual exported Material→ShaderLab program-quality audit (2026-11-05)

**Owner T3; RENDER-002 OPEN, device visuals unverified.** This is not a full-game asset restoration or Android GPU acceptance.

## Why another test was necessary
Multiple authentic source-vs-same-export tests have proven preservation of original Texture2D pixels when decoding normal maps correctly (106/106), selected Material RGBA and TexEnv/UV values, and exact serialized Material→Shader target PPtrs (41/41). They do **not** show the program compiled behind a Shader `guid`. In pinned AssetRipperCLI `036098ab525a3f9f693dc101edeb21faad4d32d8`, `ExportSettings.ShaderExportMode` defaults to `Dummy`. The standard native build's disposable `android-port/Experiments/ExportLineage/Program.cs` overrides ScriptExportMode but **not ShaderExportMode**; selected vendor/postFX/water restorations happen only after default export. As a result, `scripts/w1_audit_export_material_shaders.py` may correctly report all source/output GUID targets resolved while every custom Shader program behind those links is still a placeholder.

On a SHA-authenticated same-AssetRipper-export test, 41 original Materials kept exact Shader target identity, nine of ten original custom Shader objects emitted `//DummyShaderTextExporter` and 31 source custom Passes became nine synthetic Passes. One original Shader with seven Passes is transported as an engine builtin and must not be included in custom ShaderLab source comparison. [Bounded original source/share summary](T3_ORIGINAL_41_MATERIAL_SHADER_DUMMY_PASS_GAP_2026-11-05.md), [CI42021188920](https://github.com/alwansan/raf/actions/runs/42021188920). Isolated experimental `ShaderExportMode.Decompile` [CI42022935055](https://github.com/alwansan/raf/actions/runs/42022935055) completed a real export but **all nine selected custom output files still carried Dummy fallback marker** and did not pass strict ShaderLab structure. Changing the production default to Decompile cannot currently be claimed a fix.

## Concrete new native integration
New read-only `scripts/t3_audit_exported_material_programs.py` consumes **actual exported Unity `Assets` after shader restorers**, not original asset names. It resolves every Unity Material YAML `m_Shader` pointer against a unique `.shader.meta` GUID and *the actual ShaderLab content of that file*, separately classifying:
- custom Shader reference with pinned `//DummyShaderTextExporter` marker;
- real shader source with/without structurally programmed Passes, unbalanced ShaderLab or `// No subprograms found` / unsupported exporter markers;
- Unity built-in Shader references, null references and unresolvable/unsupported references;
- numbers of distinct custom and dummy Shader target GUIDs, without publishing GUIDs themselves.

The audit rejects duplicate or reserved shader GUIDs, missing or ambiguous Shader metadata, symlinked source entries/ancestors, oversized input and malformed/duplicate Material Shader fields. It emits **only aggregate counts** and an explicit `selected_ShaderLab_documents_have_proven_original_programs=false`, so even a non-Dummy program cannot be mistaken for authentic compiled source. It does not edit anything, generate shaders, manufacture passes, alter `.meta` files or silently change readiness.

The authentic native workflow `.github/workflows/raft-unity-editor-android-import.yml` now invokes the audit **after** existing TMP/PostFX/volumetric/builtin/Depth/Blur restorations and the W1 pointer inventory, **before** the strict original-water gate. The resulting `t3-native-material-shader-quality.json` is included in existing aggregate artifact `w1-native-export-reference-audit-${github.sha}` even if a later step fails. Diagnostic step `continue-on-error: true` preserves current fail-closed water/original-source requirements and user-authorized experimental build exceptions unchanged.

**Native post-restoration execution has NOT occurred in this T3 session.** The integration source and source-free controls were verified; only a future authorized native run can establish how many Dummy ShaderLab programs remain **after** restoration in the actual full project.

## Real actual-source bounded trial (before vendor restorer)
[CI42026630845](https://github.com/alwansan/raf/actions/runs/42026630845) **SUCCESS**, pinned exact ZIP2 source commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` and twelve original source providers SHA-verified in temporary staging, same W1 Material21/Shader48 and B02 Texture2D28 private export, no Unity or Adreno, no LFS. Existing exact 41 Material→10 Shader source/export equivalence again PASS, and new full bounded output scan yielded:

| Measure in this **unrestored bounded** export | Authentic actual result |
|---|---:|
| Unity exported Material YAML documents | 731 |
| Material docs referencing Unity built-in Shader | 220 |
| Material docs referencing custom Shader GUID with valid .shader source/meta | 511 |
| Material docs referencing `//DummyShaderTextExporter` | **511** |
| Distinct referenced custom Shader targets | 54 |
| Distinct referenced Dummy Shader targets | **54** |
| Total .shader files with actual Dummy marker | **126/126** |
| Material docs with unresolved/unknown Shader references | 0 |
| Material docs with missing/zero Shader references | 0 |

The 511/511 and 126/126 source-export numbers are **pre-restoration**; do **not** claim these counts describe the latest assembled APK or that 511 objects on the phone are visibly white. The report proves the diagnostic hypothesis: original Material GUID fidelity and syntactically programmed shader code can both be true **while all custom programs remain placeholders**.

## CI and acceptance
- [CI42026250167](https://github.com/alwansan/raf/actions/runs/42026250167): two newly added synthetic test assumptions were invalid (report inside source root and confusing a field label with a private value), not a genuine Shader/material defect; fixed tests.
- [CI42026343292](https://github.com/alwansan/raf/actions/runs/42026343292) and [CI42026545273](https://github.com/alwansan/raf/actions/runs/42026545273): **SUCCESS**, source-free Material→Shader GUID/dummy validation, mutation guards and AST/YAML safety. Code and synthetic test suite audited, no PNG/Unity/GPU.
- [CI42026630845](https://github.com/alwansan/raf/actions/runs/42026630845): **SUCCESS**, actual 12-owner ZIP2 authenticated export, 731 YAML docs and 511 real dummy-bound docs.
- New native importer source integration [commit `e90d1c3521833feb51f7051dd0d05ab2d79e9234`](https://github.com/alwansan/raf/commit/e90d1c3521833feb51f7051dd0d05ab2d79e9234).

## Remaining engineering priorities
1. On the next **already authorized native build**, capture actual **post-restorer** Material-to-Shader quality counts and verify exact original Shader source metadata. Prioritize the renderer-linked Shader targets still using Dummy markers rather than changing the proved-good RGBA/UV/texture pixels.
2. Restore real authored/compiled programs or authenticated vendor equivalents under original Unity GUIDs and original SubShader/pass/variant semantics; a synthetic placeholder Pass is not an acceptable fix.
3. Validate Unity 2021 Android shader import/compiler and device screenshot colors, effects, water/FFT, and world gameplay. The current test does not prove this. Protect working sound/Settings, defer touch/layout and avoid interfering with T1/T2/T4/T5.

**Status: RENDER-002 OPEN**, native post-restoration counts UNKNOWN, no APK/OBB/XAPK created by T3, no game resources, GUIs, Unity metadata, Android runtime, shader source or original ZIP2 bytes changed.
