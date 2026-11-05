# T2 WATER-001 — source-authentic compiled Material.SetTexture first-argument proof for four Foam resources

**2026-11-05 — verified original CI [42021183522](https://github.com/alwansan/raf/actions/runs/42021183522) SUCCESS.** This closes the bounded question *which compiled managed string argument is passed to the typed Material.SetTexture call*, **not** the runtime rendering of Foam.

## Authenticity and retained earlier evidence

Original immutable ZIP2 `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original `Raft_Data/sharedassets0.assets` 115978112B SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`. Original `Raft_Data/Managed/Assembly-CSharp.dll` 3211776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Both source SHA/size checked on real file bytes in CI.

- [Original Foam native DXBC↔translated SPIR-V sampling-identity CI42013590671](https://github.com/alwansan/raf/actions/runs/42013590671) proved exact six original t/s→compiled descriptor identities and actual 21 SAMPLE calls.
- [Original authored property CI42017542487](https://github.com/alwansan/raf/actions/runs/42017542487) proved exactly one authored Texture property used in two fragment passes, with **four additional pass0 fragment Texture names not authored as Shader properties**, and no direct local Foam Material among 351 Materials in the same serialized owner.
- [Original Cecil IL source context CI42019735778](https://github.com/alwansan/raf/actions/runs/42019735778) proved all **four non-authored Foam Texture names occur as `ldstr`** in one original managed method containing typed Material.SetTexture and MaterialPropertyBlock.SetTexture calls, but mere proximity was not argument provenance.

## New real compiled IL operand/dataflow proof

`android-port/Experiments/T2/FoamRuntimeStringBridge/FoamSetterFlow.cs` (commit [479935ef](https://github.com/alwansan/raf/commit/479935efc870598ec6c36139738615b1cc178934)) implements a **conservative bounded IL evaluation-stack interpreter** for original source-name `ldstr` markers: from each matched actual original IL literal through supported stack, locals, typed calls and optional `Shader.PropertyToID` conversion, to **the first formal name parameter of a typed `UnityEngine.Material.SetTexture` or related known Unity setter**. Rejects branches, unknown instructions, unbounded loops, dynamic/unresolved aliases and unrelated strings that are merely near a setter. No original method/source identifiers appear in output.

Original [**CI42020924870**](https://github.com/alwansan/raf/actions/runs/42020924870) SUCCESS: first actual original SHA-pinned IL scan proves **4/4 distinct non-authored names occupy exactly the first `System.String` argument of `UnityEngine.Material.SetTexture`**. Four exact uses; **0** of those four go through `Shader.PropertyToID`, and **0** are first arguments to MaterialPropertyBlock setters in this bounded matched scan. The same source managed method contains other MPB setters but these literal strings are not proven MPB setter arguments. Separately one authored Texture property name occurs as an exact typed setter argument.

Strengthened branch-workflow acceptance gate commit [eceef5f7](https://github.com/alwansan/raf/commit/eceef5f7725d14e07c2e19394bc8341e30ed184f) requires **all four** exact names, **four** direct-string `Material.SetTexture` first arguments, **zero** `PropertyToID`/MPB first-name arguments, and no private name publication. Final immutable-source [**CI42021183522**](https://github.com/alwansan/raf/actions/runs/42021183522) **COMPLETED SUCCESS**. **13/13** synthetic Python private-name source controls and three independent public-source compiled Cecil IL fixtures (exact direct string positive, identical-window wrong string negative, optional PropertyToID→int setter positive) passed.

| Actual original source/IL fact | Result |
|---|---:|
| Four private non-authored Foam resource names in compiled original `ldstr` | **4/4** |
| Distinct names proven in exact first typed `SetTexture` formal arg | **4/4** |
| Exact string-name `UnityEngine.Material.SetTexture` compiled call edges | **4** |
| Exact first-arg `UnityEngine.MaterialPropertyBlock.SetTexture` for these four | **0** |
| Exact first-name `Shader.PropertyToID` intermediate for these four | **0** |
| Source-authentic managed assembly scanned | 3211776B SHA-pinned, **19118** methods and **491490** instructions |
| Runtime execution of original setter in actual Raft | **NOT tested** |
| Identity/contents of actual second `Texture` argument and `Material` receiver | **NOT yet proven** |
| Original shader properties, constant-buffer upload, UV/sampler-state and Unity ShaderLab/Android pixels | **NOT yet proven** |

Safe numeric-only artifact **13412190775** ZIP SHA256 `0a7603130abb87c8ab000777eb276cab00b5d2a3c59bdcc9cc4438716eac9498` at [CI42021183522](https://github.com/alwansan/raf/actions/runs/42021183522). Source names, their hash strings, original methods, classes, original IL, compiled game DLL and original Shader bytes never uploaded; source and hashed identifiers were deleted after CI. B05/W3/B20/B24/B25 and original T5 Mono.Cecil path retained attribution.

### Integration implication and necessary remaining work

It is now evidence-backed to describe those **four non-Properties resources as names explicitly passed into `Material.SetTexture` first parameters in the original compiled game**, rather than guessing global shader textures or fabricating six authored Material properties. However the test **does not establish whether that codepath executes**, if the corresponding `Material` instance uses Foam Shader, what actual `Texture` values are passed in the **second argument**, if Texture2D/RenderTexture data are current/valid, or whether shader sampler/UV/CB uploads are correct. Static IL dataflow of the second argument and Material receiver are the next boundary, followed by genuine private Foam two-pass ShaderLab Unity import, GPU/Adreno device pixels. Do not claim working phone water yet.

WATER-001 **OPEN**, game **NOT_READY 0/3**, last actual game phone APK86; no ShaderLab/game asset/.meta/GUID modifications, no unrelated CI cancelled, sound/Settings preserved, touch/layout deferred.

## New second-parameter IL operand opcode provenance — CI42022637009

Additional distinct question registered **before editing** in `prompt/coordination/work/WATER-001/T2-20261105T1152Z-managed-settexture-value-provenance.json`: does the actual **second** formal `Texture` argument of each of the four proven original `Material.SetTexture` calls arise from a field, argument, local, literal/null or a separate method return? The T2 conservative single-basic-block evaluator `FoamSetterFlow.cs` was extended **without changing existing first-name-argument proof**, to retain only safe opcode-family provenance (`argument_load/static_field_load/instance_field_load/null_literal/call_return/unknown`) and verify the original actual method's **second formal parameter type** exactly `UnityEngine.Texture`. No original source/class/method names or original value instances were read into a report.

[**Genuine original CI42022637009**](https://github.com/alwansan/raf/actions/runs/42022637009) **SUCCESS**: original SHA-pinned two source owners, 13/13 Python tests and source-free C# Cecil synthetic tests (null, static field, parameter and prior positive/negative first-argument proofs). The real four original callsites continue to prove **4/4** direct string first-arg names, with **4/4 second-arg declared as `UnityEngine.Texture`** and **4/4 second-arg IL opcode source classified as `call_return`**. This narrows the original Texture object-value source to a **result of another call expression** immediately on the managed IL stack. It **does not identify the called method by name or prove its return value was a valid object at runtime**, the `Material` instance uses Foam Shader, sampler/CB/UV, Unity import or Android pixels. The four real arguments do not directly originate from a `ldnull`, direct `ldfld`, `ldsfld` or `ldarg` opcode at this short bounded call boundary; those may feed the *producer method* internally and remain unproven.

New code [856fe207](https://github.com/alwansan/raf/commit/856fe2075ea2acca16c513939d85454fcf59ccbe) and [1d8747bd](https://github.com/alwansan/raf/commit/1d8747bd95d9b36461fd250f00515b581955591f), first original result safe numeric artifact **13411798413** ZIP sha256 `f21d225b688af31ccc6a7d453b0ce5ac132ea9e22ee0edb77ac121d12231c8ca`, no game binaries/names. Tightened original acceptance gate [7ba45557](https://github.com/alwansan/raf/commit/7ba455579400ed4901b4e5cf9f24f77865c87522) now requires **4/4** `call_return` origin and declared `UnityEngine.Texture`; later CI run final result tracked in work record, if available.

**Next:** resolve the *producer call* for each original returned Texture value to exact static declared return type and call-target provenance (original managed or Unity), without publishing method names or assuming RenderTexture instance/pixels. Then Material receiver shader binding and runtime reachability; only after that integrate actual original Foam ShaderLab/Unity/Adreno.
