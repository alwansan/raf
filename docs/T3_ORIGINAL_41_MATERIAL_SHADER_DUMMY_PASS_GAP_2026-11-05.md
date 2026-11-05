# T3 — authenticated original Material→Shader targets and default-Dummy ShaderLab gap (2026-11-05)

## Engineering question and important distinction
The user reports missing/white colors and effects on Android. Historical B05/B44/T3 SHA-pinned authentic export experiments had already excluded selected Material `m_TexEnvs`, UV and RGBA serialization drift. [CI 42014733420](https://github.com/alwansan/raf/actions/runs/42014733420) additionally proved 106 original linked Texture2D decoded RGBA identities after correctly accounting for 30 original `NormalmapDXT5nm` maps and AssetRipper's deliberate `UnpackNormal` packing: 106/106 exact, six sampler fields for 106/106, no Android GPU proof. The next distinct question was whether the 41 selected original Materials had retained their actual **Shader targets and original Shader Pass programs**, not only keyword state.

**Crucial provenance limit:** All ShaderLab outputs compared here came from the **bounded diagnostic AssetRipper exporter running its unchanged DEFAULT `ShaderExportMode.Dummy`**, not from a proven current Android project import. The exported one-pass fallback is an expected consequence of that setting; do NOT state that Raft Android itself is proven to contain these nine generated dummy files. It is not correct to patch original source `.shader` programs on this evidence alone. A separate experimental `Decompile` mode must be checked.

## Immutable source and actual same-instance pointer proof
Original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, manifest and per-owner size+SHA256 verified before parsing:
- `Raft_Data/sharedassets6.assets` 6,607,272B, SHA256 `0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632` — 41 selected original Materials.
- `Raft_Data/sharedassets0.assets` 115,978,112B, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
- `Raft_Data/sharedassets1.assets` 34,888,388B, SHA256 `c6bdf49f7d38ab060872fcb298770bc7113959f85ea2fd1a42dc663323d7660a`.
- `Raft_Data/resources.assets` 111,533,516B, SHA256 `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c`.

[Source-only pointer table CI42017451573](https://github.com/alwansan/raf/actions/runs/42017451573) **SUCCESS**: 41/41 source original non-null Material `m_Shader`; 11 local, 30 external; 10 distinct original targets, owner-link occurrences `sharedassets0.assets` 17, `sharedassets6.assets` 11, `resources.assets` 11, `sharedassets1.assets` 2.

[Genuine source→same-instance export CI42018170879](https://github.com/alwansan/raf/actions/runs/42018170879) **SUCCESS**: 12 separately SHA-authenticated ZIP2 serialized owners (nine B21 plus `sharedassets0`, `sharedassets1`, `resources`, no streamed pixels required for Shader references), pinned public `nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8`, instrumented W1 Material21/Shader48 and B02 Texture2D28 private same-export traces. Source original 41 Material `m_Shader` owner+PathID target classes and actual exported `Material.m_Shader` YAML `fileID/guid/type` **41/41 matched**, all 10 source typed Shader48 present in trace. Nine custom ShaderLab files have unique matching `.shader.meta` GUIDs, one source Shader transported as Unity builtin reference. All nine generated custom ShaderLab files have **one syntactically programmed Pass** each. This is only source/export graph plus ShaderLab structure: not a compiled shader or runtime verdict.

## Original Pass topology and EXACT GUID-paired output delta
[Source-only SHA-pinned original ten Shader pass topology CI42018873366](https://github.com/alwansan/raf/actions/runs/42018873366) **SUCCESS**: ten original source Shader48 objects contain 38 serialized `m_ParsedForm.m_SubShaders[].m_Passes` records in 11 SubShader records; original pass histogram `2:1, 3:3, 4:5, 7:1`, no source Shader has zero Passes.

[Exact W1 original-target→real exported ShaderLab GUID join CI42020419098](https://github.com/alwansan/raf/actions/runs/42020419098) **bounded genuine difference**, intentionally returns exit code 2 because actual source/export Pass topology differs. It excludes the one engine-transport original Shader with 7 Passes rather than comparing that Shader to a non-existent custom `.shader` file.

| SHA-authenticated original source owner of **custom** Shader | Source Shader objects | Original parsed Pass records | Actual exported ShaderLab Pass records | Bounded default-Dummy difference |
|---|---:|---:|---:|---:|
| resources.assets | 1 | 4 | 1 | 3 |
| sharedassets0.assets | 4 | 14 | 4 | 10 |
| sharedassets1.assets | 1 | 2 | 1 | 1 |
| sharedassets6.assets | 3 | 11 | 3 | 8 |
| **9 custom source→ShaderLab GUID pairs** | **9** | **31** | **9** | **22** |

**All 9 custom shaders** have fewer generated Passes than their *individually authenticated* original source Shader48 objects. `9/9` generated ShaderLab programs are syntactically well-formed CGPROGRAM Passes, but syntax does not prove original program instruction, shader variant, render state, sampler, compiled vertex/fragment pair, HLSL/GLSL semantics, Unity shader compiler or Android pixels.

[CI42021188920](https://github.com/alwansan/raf/actions/runs/42021188920) **source/export successful, deliberate fail-closed Pass-difference outcome**: 9/9 matched output `.shader` files contain the literal marker `//DummyShaderTextExporter`, from the pinned AssetRipper source `Source/AssetRipper.Export.UnityProjects/Shaders/DummyShaderTextExporter.cs`. Pinned `Source/AssetRipper.Export.UnityProjects/Configuration/ExportSettings.cs` sets `ShaderExportMode` default `Dummy`; our published `android-port/Experiments/ExportLineage/Program.cs` overrides only script export, **not shader export**. Therefore the cause of nine truncated synthetic fallback files in the bounded experiment is now **known to be the exporter default**; it does **not** imply corrupted source shaders or prove that the current Android installation imported exactly these files.

## Verified code and test artifacts
- `scripts/t3_original_material_shader_target.py` and its isolated source-only workflow/tests.
- `scripts/t3_material_shader_same_export.py` and 11 synthetic original vs exact Shader-target YAML and ShaderImporter guards.
- `scripts/t3_original_shader_pass_topology.py` and its four-owner SHA-pinned original source-only CI.
- `scripts/t3_same_export_shader_pass_topology.py`, source-free adversarial tests, bounded authentic same-export workflow. The first two runs were **verifier-only defects**: an omitted safe failure stage, then invalid Python `utf8-sig` codec name for BOM-aware `.shader/.meta` reading. Corrected to `utf-8-sig` with real-like 9 ShaderLab file regression; CI42020419098 and CI42021188920 both reach genuine Pass comparison. No original game asset/Unity `.meta` was changed.
- The independent subsequent `.github/workflows/raft-t3-real-shader-decompile-export.yml` opts into `ShaderExportMode.Decompile` in *runner-local disposable Program.cs only*, leaving shared repository/exporter defaults intact. It intentionally uses separate concurrency and does not cancel others. The Decompile mode is explicitly unstable in pinned AssetRipper source and results must be independently classified.

## Follow-up — actual `ShaderExportMode.Decompile` and production pipeline (2026-11-05 12:26 UTC)
[Independent original 12-owner Decompile run CI42022935055](https://github.com/alwansan/raf/actions/runs/42022935055) completed a real, SHA-pinned export using a **disposable only** setting `ShaderExportMode.Decompile` applied to the runner-local Program.cs; the checked-in/native exporter settings were untouched. An exact source Shader48 GUID-paired quality classifier found **all nine original custom ShaderLab outputs still contain `//DummyShaderTextExporter`**, and all nine were structurally unbalanced according to the bounded ShaderLab parser (zero parseable Passes). The subsequent strict per-original-Pass comparator correctly remained `INCONCLUSIVE`, not a successful decompilation. This means a naive switch to `Decompile` is NOT a verified native shader restoration fix.

The production [native importer workflow](../.github/workflows/raft-unity-editor-android-import.yml) compiles the same pinned exporter with its **default Dummy ShaderExportMode** before performing authenticated vendor/TMP/PostFX/volumetric/Depth/Blur postprocessing. A new independent [T3 post-restorer Material→Shader program audit](T3_NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_2026-11-05.md) was wired into that native workflow without changing game assets, and its true bounded (pre-restorer) source/export trial [CI42026630845](https://github.com/alwansan/raf/actions/runs/42026630845) found **511/511 custom Material links target 54 dummy shader GUIDs**, with **126/126** actual ShaderLab source files bearing the pinned Dummy marker; 220 additional Material docs use builtin Unity shader references. The **post-restoration full native result remains unmeasured**. These counts MUST NOT be promoted into a claim about the last installed APK86 or Adreno pixels. RENDER-002 remains OPEN.

## Integration and acceptance boundary
This work is a **genuine structural finding about a default-Dummy diagnostic export** and a reproducible exact pointer/Pass audit, **not yet an Android graphics fix**. T5 should inspect whether the current imported game shader set uses a Dummy exporter or real restored authored source before changing materials; T1/T2 should continue original water/FFT ShaderLab program stage restoration, not add dummy Passes to meet counts. To restore the nine custom original Shader programs, a future experiment must establish actual compiled stage/subprogram/variant fidelity and Unity 2021 compilation, then game scene/GPU pixels. A syntax-valid one-Pass template, an artificially increased passCount, or a hidden unsupported program is not an acceptable substitute.

Issue `RENDER-002` remains **OPEN**, no game APK produced, last phone evidence APK86, no original game Shader binaries, PPtrs, `.meta`, sound/Settings, deferred touch, local world/save or other T agents' Actions changed by T3.
