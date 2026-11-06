# T2 — authentic Foam CB0 vector name is actual original Material.SetVector first argument

**Issue:** WATER-001 OPEN. **Session:** `20261106T110527Z-T2-chat-cb0-managed-namelinks-f2e1`, `origin=chat`, separate typed-operand work scope. **Status:** source-original first-argument proof (not original Unity CB0 upload).

## Previously established candidate

The original source-and-managed SHA-verified [CI42208958212](https://github.com/alwansan/raf/actions/runs/42208958212) compared true serialized original Foam Shader CB0 names (from B25 `m_NameIndices` and four original pass/stage CB0 entries) with original compiled `Assembly-CSharp.dll` `ldstr` strings. Source-authenticated original ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, Foam source `sharedassets0.assets` 115978112B SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original `Assembly-CSharp.dll` 3211776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.

That first result found five distinct original source CB0 vector member names, three of them present among actual compiled managed `ldstr` instructions (four occurrences total); one occurrence was near both `Material.SetFloat` and `Material.SetVector` within a method, but proximity alone was not argument proof.

## New conservative typed IL stack proof

New [commit 33ac53cf](https://github.com/alwansan/raf/commit/33ac53cf07d6ce839439e86bdf2c407f59aafbb2) extended the isolated Cecil checker with a bounded, straight-line instruction-stack ownership tracer:

- Start at the exact `ldstr` whose **private string SHA256** matches a source-original serialized CB0 member name, never a guessed translated HLSL name.
- Model pushes/pops of supported source-neutral IL instructions, local storage, receiver/field loads, other typed calls and optional `Shader.PropertyToID` conversion. Require the tagged name to survive on the **first formal argument** of an exactly classified public `UnityEngine.Material` / `Shader` / `MaterialPropertyBlock` typed setter. Any unrecognized opcode, branch/return/throw, unknown pointer or out-of-bound scan prevents proof.
- Verify matching caller's `MethodReference` declared parameter types and `HasThis`. The analyzer never executes the original managed assembly or treats method presence as runtime call reachability.
- Source-free synthetic Cecil selftests explicitly reject an unrelated nearby `ldstr` discarded before a setter and a branch between literal and call; positive direct string first-argument and typed `PropertyToID` first-argument paths are also checked. Bound: **24 following IL instructions**, no inference across unsupported branches.
- Private exact names, hashes, method/class identities, raw IL, ShaderLab, DXBC, SPIR-V and original DLL bytes are not logged or uploaded.

### Actual source-authentic evidence

[CI42209967318](https://github.com/alwansan/raf/actions/runs/42209967318), job `127865876765`, **SUCCESS**. Original source / DLL SHA authenticated, Python source-free 11/11 tests and Cecil selftests passed. It showed **one distinct original CB0 vector member name** (of five distinct names) used as an actual direct `System.String` first-formal argument of **one** typed Unity uniform setter; zero traced `Shader.PropertyToID` first-formal usages for that name.

The follow-up [CI42210166957](https://github.com/alwansan/raf/actions/runs/42210166957), job `127866539676`, **SUCCESS** on `c95cdaf51a9edf9a641c9463737427b619e2a67f`. It independently classified the exact **proven** typed call as **`UnityEngine.Material.SetVector(string, Vector4)`**, once. Although the neighboring method also has `Material.SetFloat`, **no source-matched literal first argument to `SetFloat` was proven**. No original literal or CB0 name was disclosed.

| Distinct typed first-formal result | Exact source-original count |
|---|---:|
| CB0 vector source names with compiled `ldstr` | 3/5 |
| Source names proven actual `Material.SetVector` `string` first argument | **1/5** |
| Exact original CB0 `string` first-argument setter call occurrences | **1** |
| First argument via `Shader.PropertyToID` proven | **0** |
| CB0 buffer source name directly in managed `ldstr` | 0/1 |
| Remaining CB0 source vector names with no proven first-argument setter | 4/5 |

Legacy aggregate report field `original_Ldstr_is_exact_setter_argument_proven=false` remains a broad/all-names flag; it must **not** override the new explicitly count-scoped `original_source_name_exact_typed_first_formal_unique_by_role.vector=1` and `original_source_name_exact_first_formal_typed_setter_API_categories.material_vector=1`. The other four original vector member names are not proven direct call first-formals.

## Why WATER-001 is not solved

This proves **one compiled managed call's first string property-name formal**. It does **not** prove that the second argument `Vector4` holds the original CB0 data, which instance of `Material` receives it, whether the Material's actual Shader is Foam, whether runtime reaches the call, how Unity populates the original 160-byte CB0, nor whether its pass0 Fragment and pass1 Vertex larger reflected arrays are correctly covered. The same material may belong to a different shader, or Unity may supply other CB0 members via engine/native globals.

The original [CB0 compiled index source CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) remains an independent critical constraint: 6 source-backed static compiled Fragment loads in pass0 and 2 Vertex loads in pass1 address beyond the opposite stage's smaller reflected array; do not infer a universal smaller buffer from common binding or this one setter proof.

**Next:** source-authentic IL stack value/receiver provenance of the one `Material.SetVector` call, and material-to-shader actual linkage where possible; compare with serialized original CB0 element IDs/size before any Unity importer, Vulkan or Adreno integration. No game `.shader`, `.meta`, GUID, assets, Settings, audio, touch, saves or native CI changed by T2 in this experiment.
