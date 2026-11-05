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


## Addendum: private signed IL-int decoding and actual artifact gate — 2026-11-05T14:20Z

T2's subsequent original SHA-pinned experiment [CI42043293335](https://github.com/alwansan/raf/actions/runs/42043293335) **COMPLETED SUCCESS** on source commit [43a6338](https://github.com/alwansan/raf/commit/43a633869a4185bd0176e139b9abf3b28045bd8e). It extends the exact original four-name `Material.SetTexture(string,Texture)` argument flow: all four previously proven direct integer IL sources were **decoded in private scratch** from typed `ldc.i4.m1`, short signed `ldc.i4.s`, compact and wide `ldc.i4` forms. Public synthetic tests reject method-argument and metadata-token false literal evidence and include duplicate/negative controls. The original report passes the exact **four decoded integer** gate and preserves a safe *distinct-count integer in 1..4* and *all-nonnegative boolean*, without exporting any four original numeric values or reversible numeric hashes.

Safe artifact ID `13423996658`, GitHub-reported SHA256 `724e25d6f7de6d78abb054a75f37bdd73303096a19205e485efbc1f548edc00b`. Its **actual** distinct-count and sign output values have **not been inspected by this chat** due artifact ZIP reader limitations; do **not** infer four distinct/positive inputs from the mere successful CI gate. The original `RenderTexture[]` allocation, actual runtime length and element validity, `Material` receiver shader relationship, true Foam two-pass ShaderLab integration and Adreno pixels remain unverified. A source-only CI pass is **not** a playable water result. Work/experiment/event and artifact identifiers are in `prompt/coordination/clients/T2/sessions/20261105T1408Z-T2-chat-foam-four-i4-uniqueness-4e7a.md`. **WATER-001 OPEN / NOT_READY 0/3**.


## Addendum: exact backing-field serialization modifiers and four private i4 values — 2026-11-05T14:38Z

**Original [CI42046650774](https://github.com/alwansan/raf/actions/runs/42046650774) SUCCESS** at commit [9b01015a](https://github.com/alwansan/raf/commit/9b01015a9e3aa47718d9b102d31bd8d39d52b638), original managed `Assembly-CSharp.dll` 3,211,776 bytes, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`, ZIP2 SHA pin unchanged. Mono.Cecil v0.11.5 original getter private `RenderTexture[]` FieldReference resolved to **exactly one** original managed FieldDefinition (not a guessed similarly typed field). Source-free adversarial public/private/`SerializeField`/`NonSerialized`/static/readonly/missing-definition controls and private source cleanup passed.

The exact original backing-field metadata: `DeclaredPublic=false`, `HasExplicitUnitySerializeField=false`, `HasNonSerializedMetadata=false`, `IsStatic=false`, `IsInitOnly=false`, `EligibleByFieldModifiersOnly=false`, `OwnerDirectBaseTypeCategory=not_proven_unity_owner_by_direct_base`. This is **not** an assertion that no Unity scene/prefab, reflection, native or other managed code can initialize the field. It only excludes ordinary visibility/attribute eligibility based on this field's own compiled modifiers; no source-based actual serialized instance value or runtime length is verified.

The same SHA-original **actual original four `Texture(int)` call arguments** were decoded privately under the preceding strict IL stack-dataflow proof: `decoded_count=4`, `distinct_count=4`, `all_nonnegative=true`. These source-authentic aggregate values were verified in the safe `T2_FOAM_FIELD_METADATA_SAFE` GitHub job log; no original private literal value or reversible small-domain digest was published. **Nonnegative and distinct do not prove in bounds** without actual runtime `RenderTexture[]` length/contents. Safe-only artifact `13424871676` ZIP SHA256 `4fada83b5337702252c61fdb121350418d99db4fb97dc6f0218cbf50e1269c7f` (1923B).

Remaining source questions: owner type ancestry, managed `ldfld/ldflda` uses (especially other than exact getter), possible indirect and external array creation/writes, genuine Unity scene/prefab instance data, Material receiver actual Foam association and GPU/Adreno water pixels. **WATER-001 OPEN; Raft NOT_READY 0/3.**


## Addendum: exact original array field access topology — 2026-11-05T14:45Z

[CI42047763379](https://github.com/alwansan/raf/actions/runs/42047763379) **COMPLETED SUCCESS**, source commit [0881f972](https://github.com/alwansan/raf/commit/0881f9722f553e01e3694d7d49b964d53d2dff1e), on the same exact original 3,211,776-byte Assembly-CSharp.dll SHA pin. New `FoamFieldReadTopology.cs` counts IL instructions referring to **exactly** the previously proven private Foam `RenderTexture[]` field, not a similarly typed field. Synthetic positive getter/additional reader/address and wrong-field negative controls passed. Only safe cardinality leaves the runner.

Authentic IL result: **10 `ldfld` field reads across four distinct reader methods**; exactly **two** belong to the strictly proven original null-guarded `Texture(int)` getter and **eight** are in other methods. **One `ldflda` address load** appears in a non-getter method (one distinct address-taking method). The source reader does not infer that this address use modifies the field or establishes any array contents. Safe artifact `13426150452` (2016 bytes), ZIP SHA256 `6340258c4c983df3bbf8c4ca68845ed7960c4f84e69f95d562ab4e03e7245cca`; source symbols, IL and private int literals withheld.

Combined with earlier source results: original backing array field is private without explicit SerializeField, the single observed compiled direct `stfld` is a `null` clear, and four actual compiled `Texture(int)` int arguments are **distinct and nonnegative**. Thus additional direct reads and one address load now identify non-getter candidates for deeper original dataflow analysis. **No original runtime initialization/array length/element contents, Unity Material receiver shader attachment, ShaderLab import, water pixels or device play is proven.** Next: inspect private original `ldflda` sink and eight other reads with verified IL stack flow, without exporting game source. **WATER-001 OPEN; NOT_READY 0/3.**


## Addendum: exact source-original Foam field byref call consumer — 2026-11-05T15:17Z

Source-only Mono.Cecil verifier commit [34f84056](https://github.com/alwansan/raf/commit/34f840561993b44c59cd7c61b22f1f013e64cd89) and exact original SHA-pinned [CI42053062181](https://github.com/alwansan/raf/actions/runs/42053062181) **COMPLETED SUCCESS**. The *only* original `ldflda` address site on the previously proven exact private `RenderTexture[]` backing field is **actually consumed by a typed `ref RenderTexture[]` method argument**. Genuine source-safe categories: one exact address site, one distinct owner method, one `typed_byref_array_call_potential_mutation`, zero runtime execution/contents proof. Public synthetic source-free controls separately validate direct `stind.ref`, typed byref calls, `ldind.ref` then element store, array length read, and typed wrong-field rejection. All original shader/class/method/field identifiers, private numerical literals and original IL remain undisclosed. Safe-only artifact `13428570089` SHA256 `153c1a689176b885f3bd62feeeb44bbf986dd7b1ad82108df2f6a627b8cf908b`.

This establishes a concrete **possible indirect field-assignment path** not discoverable by scanning only `stfld`. It does **not** establish that the recipient modifies the reference, how any array/RenderTexture members are created or populated, call reachability, runtime size, Unity material binding, ShaderLab import or Adreno water pixels.

**Next separate experiment:** resolve the exact privately retained byref recipient MethodReference against the genuine original managed MethodDefinition or its external declaration, then inspect the callee for a proven direct `ref RenderTexture[]` write/array initialization (or fail closed if unresolved). Do not invent original method names, private indices or source C# beyond compiled proof. **WATER-001 remains OPEN; Raft NOT_READY 0/3.**
