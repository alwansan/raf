# T2 WATER-001 — source-authentic original Foam RenderTexture array setter-input provenance

**5 November 2026 — original SHA-authenticated CI [42028108346](https://github.com/alwansan/raf/actions/runs/42028108346) SUCCESS.** Owner selected **Stay in Chat**; all work performed directly on permitted `feature/android-native-port`. No private source/binary/disassembly/IL code or shader symbols were committed or uploaded.

## Authentic original inputs and inherited provenance

- Immutable source `alwansan/raf@zip2:15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original `Raft_Data/sharedassets0.assets` **115,978,112B** SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Original `Raft_Data/Managed/Assembly-CSharp.dll` **3,211,776B** SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Both source SHA/length verified by exact runtime bytes inside the independent CI runner, never by filenames or shell metadata alone.
- Existing T2 [original native DXBC→compiled SPIR-V pass sampler identity CI42013590671](https://github.com/alwansan/raf/actions/runs/42013590671): source SHA-pinned 4-stage Foam programs have six active t/s pairs and 21 native/translated sample calls.
- [Original Shader authored props CI42017542487](https://github.com/alwansan/raf/actions/runs/42017542487): exactly one authored Shader Texture property used once in each fragment pass, while four additional pass0 fragment texture source names are **not** authored Shader properties; original 351 same-owner Material objects have 0 direct local Foam Shader links (not global absence).
- [Original managed direct `Material.SetTexture` operand CI42021183522](https://github.com/alwansan/raf/actions/runs/42021183522): all four private extra source names occur as **actual direct System.String first formal name parameters** to UnityEngine.Material.SetTexture in original compiled game IL, not inferred from nearby strings; four actual typed calls, zero of those require PropertyToID.
- [Original caller second-operand CI42022922743](https://github.com/alwansan/raf/actions/runs/42022922743): all four second arguments of declared type `UnityEngine.Texture` are produced by other calls, not directly an inline Material property/field source.

## New verified single producer — not inferred from names

An extended conservative `Mono.Cecil 0.11.5` stack tag/provenance oracle `FoamSetterFlow.cs` retains the **actual** source `MethodReference` of the second Texture argument, rather than any nearby call. All four references are `callvirt` **instance** calls to a **single** original managed method, with exactly one `System.Int32` parameter and declared `UnityEngine.Texture` return. Four source references share one identical full private method signature; the original `Assembly-CSharp.dll` contains **one unambiguous exact matching MethodDefinition with real IL body** (all four references resolved). The private method name, token, signature hash, declaring-type name, source IL and original Shader identifiers were not published. [Original **CI42026683133**](https://github.com/alwansan/raf/actions/runs/42026683133) SUCCESS; public Cecil fixtures include exact definition/body match and rejection of same-assembly reference lacking a definition.

Bounded `FoamProducerBody.cs` then inspects **only this original SHA-authentic method body**. [CI42027242310](https://github.com/alwansan/raf/actions/runs/42027242310) SUCCESS established **10 IL instructions** (excluding NOP), **2 returns**, **one conditional branch**, **two instance field loads**, **three argument loads**, **one reference-array element access**, and **no nested calls or locals**. It is *not* the naive 5-op array-read method.

[Original **CI42027729117**](https://github.com/alwansan/raf/actions/runs/42027729117) SUCCESS found both original field loads are of a **`UnityEngine.RenderTexture[]` typed one-dimensional array field**, not generic `Texture2D[]` or static Material property. The simple early-branch case was not yet recognized, so source logic remained restricted.

**[Original CI42028108346](https://github.com/alwansan/raf/actions/runs/42028108346) SUCCESS** with synthetic positive and negative Cecil branch target fixtures: the verified original body exactly matches a **null-guarded instance array-index return** with alternate branch ordering. It reads the *same* `RenderTexture[]` instance field twice; a conditional branch checks the array for null; the null path explicitly returns null; the non-null path returns `this.RenderTextureArray[index]` using the original int argument and `ldelem.ref`. All ten instructions and jump destinations must match the strict original pattern, including both returns and identical field identity. No guessed source/HLSL translation or private IL sequences are committed.

| Proven original source-level compiled contract | Authentic result |
|---|---|
| Additional non-Shader-Properties Foam texture names | 4 |
| Direct string-name original `Material.SetTexture` calls | 4 |
| Second typed Texture producer calls | 4, all `callvirt` |
| Distinct original producer method definitions | **1** |
| Producer typed API shape (names withheld) | `UnityEngine.Texture Method(int index)` |
| Method exists with exact original body | **yes, SHA-pinned** |
| Backing field type | **`UnityEngine.RenderTexture[]`** |
| Return behavior | **null array→null; non-null→RenderTexture[index]** |
| Actual `index` values, render-target setup, RT content, caller reachability | **NOT PROVEN** |
| Unity Material receiver actually uses Foam, ShaderLab/Adreno water pixels | **NOT PROVEN** |

Only bounded numeric aggregate JSON uploaded. Latest CI42028108346 safe artifact **13414099116** ZIP SHA256 `95b99302e4af65efe173c4add074c8458f53a2359a0cb7cc2ee7ebe194a55b23`; source inputs, private source-name hashes, original game binaries and temporary C# compiler staging erased before publication. The scripts and tests are `scripts/t2_foam_managed_literal_targets.py`, `tests/test_t2_foam_managed_literal_targets.py`, `android-port/Experiments/T2/FoamRuntimeStringBridge/{FoamSetterFlow.cs,FoamProducerBody.cs,Program.cs}`; independent source workflow `.github/workflows/raft-t2-foam-managed-literals.yml`. CI setup includes original ZIP2 and DLL SHA/size gates plus source-free typed IL positive/negative controls. B05/B17/B20/B24/B25/W3 and T5 original compilation tooling attribution preserved.

## Next actionable original fidelity gate

The **proven source-to-Texture lookup** is now specific: four names from original Shader compiled t/s declarations are bound via a string `Material.SetTexture` call to the result of a single original `Texture(int)` method that null-checks an instance `RenderTexture[]` and returns the indexed member. **Unknown:** where that array field is assigned/filled, which original `RenderTexture` objects/format/dimensions/cross-frame writes exist, the actual four integer index operands, the Material receiver identity and its Foam Shader association, source-same runtime call reachability, UV/filter/wrap/CB0 data upload, genuine two-pass ShaderLab Unity import, Adreno/device pixels. A verified compiled method body is **not runtime execution**; do not patch hardcoded four textures or fabricate authored Shader Properties.

Next T2 could identify exact original assignment sites for that `RenderTexture[]` field and parse four int index argument origins in original IL with branch-aware guards; T1 tests FFT compute separately, T3 texture/material link separately, T4 offline world and T5 main build separately. Do not cancel/restart their jobs.

**Canonical issue `WATER-001` remains OPEN; Raft NOT_READY 0/3.** Last actual phone-tested game APK86, no native Unity Foam build or game asset/.meta/GUID changes. Sound and Settings preserved, touch/layout deferred.


## Addendum: exact original field writer and four direct int operands — 2026-11-05T13:28Z

This addendum strengthens the original source-managed contract without changing
any original gameplay ShaderLab, render state, scene, prefab or GUID. The existing
original SHA-verified managed `Assembly-CSharp.dll` remains 3,211,776 bytes,
SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.

- **Original field write-site proof:** [CI42034458197](https://github.com/alwansan/raf/actions/runs/42034458197), source commit [d47c739](https://github.com/alwansan/raf/commit/d47c73943b11e3b1d193dc56446fb63632abd47a), SUCCESS, 19,118 original managed methods scanned by Mono.Cecil. The *same exact* original private `UnityEngine.RenderTexture[]` getter backing field is the target of **one direct `stfld`** in one method. Its immediately preceding IL source is **`ldnull`**. There are **zero direct `newarr UnityEngine.RenderTexture`** assignments to that exact field, and zero other/unproven immediate `stfld` sources within this original assembly. Safe aggregate artifact ID `13417637189`, ZIP SHA256 `6f6737164c859f136d7790f995d001658110feba6e4d2d30c0b583277e934128`. This proves compiled clear-assignment existence, *not that it executed*, or how array members were created/filled. Other assemblies, reflection, indirect element writes and native Unity setup were not disproven.
- **Actual original caller int input source proof:** [CI42035529042](https://github.com/alwansan/raf/actions/runs/42035529042), source commit [afb3e94](https://github.com/alwansan/raf/commit/afb3e94af6c34a345d8fcfd81e6daaa2c01a89e4), SUCCESS. The four authentic Foam source non-authored texture names remain exact `Material.SetTexture` first `string` args; the four second texture values come from the one source-authentic guarded `Texture(int)` method. Bounded exact *actual call argument* IL stack trace proves **4/4 int inputs have direct `ldc.i4` origins**, not inferred from nearby integers, with synthetic argument-load and metadata-token negative controls. Safe artifact ID `13417228996`, ZIP SHA256 `2c9ff99f340c7364044bc5f8cfdcf2875fd1aa86c4b71da4a10c897efe0d0fe9`. No proprietary literal values, method/field/source identifiers, IL bytecode or private hashes were published.

**Still unproven:** literal **values and distinctness** (withheld), range relative to
the **runtime** `RenderTexture[]` length, array allocation and element content,
actual original `Material` receiver/Shader binding and runtime reachability,
sampler/UV/CB upload, true Foam two-pass ShaderLab Unity import, GPU/Adreno pixels
and phone acceptance. This source evidence is not a runtime shader fix.
Canonical WATER-001 remains **OPEN**, Raft **NOT_READY 0/3**.
Next T2 scope: verify original integer distinctness/range *privately* against
authenticated array-size/element-writer provenance; never invent aliases
or the original array contents.
