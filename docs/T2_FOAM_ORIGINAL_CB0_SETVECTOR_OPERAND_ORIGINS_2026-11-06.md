# T2 — SHA-original Foam CB0 `Material.SetVector` second value and receiver IL origin

**Session:** `20261106T1218Z-T2-chat-cb0-setvector-operands-4d79` (`origin=chat`). **Issue:** WATER-001 **OPEN**; Unity CB0/Adreno water **NOT_READY**.

## Exact original input and previous boundary

- Original ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original Foam owner `Raft_Data/sharedassets0.assets` (115,978,112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`); original Foam Shader PathID2420 raw object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Original `Raft/Raft_Data/Managed/Assembly-CSharp.dll` 3,211,776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Original owner and DLL verified byte-for-byte **inside runner**; no original managed assembly executed.
- Preceding [T2 source-authentic CI42210166957](https://github.com/alwansan/raf/actions/runs/42210166957) established that **one** of five source-authentic Foam CB0 vector parameter names, from four original pass-specific CB0 links, is the actual *first* `System.String` formal to exactly one original compiled `UnityEngine.Material.SetVector(string,Vector4)` call. Remaining four names still have no such proof; one nearby `Material.SetFloat` call does not receive that verified name as its original first formal.

## New original compiled IL operand trace

- Extended `Cb0ExactFirstFormal` in `android-port/Experiments/T2/FoamCb0ManagedLiterals/Program.cs`, retaining the source SHA/typed name-to-first-formal proof and strict **24 following IL instructions**. Captures the **second typed value operand and instance receiver** actually popped by that same matched `Material.SetVector` call, not a nearby typed call.
- Classifies supported IL origins (method argument, numeric literal, instance/static field load, other call return, `newobj`, null and unproven categories). Before-literal unknown stack values remain `pre_literal_unknown`; unsupported instructions/branches do not create positive provenance. The name's already-proven first-formal must still match or no origin is emitted.
- Added synthetic Cecil selftests for source-name direct first-formal and actual second method argument, instance field and call-return origins; local bridge preserves first-formal proof and models receiver argument after the literal; discard unrelated name, branch and unsupported instruction controls fail closed. No original private name/hash, IL opcode sequence, class/method identity or actual shader data published.
- Workflow `.github/workflows/raft-t2-foam-cb0-managed-literals.yml` now requires exactly one original verified `material_vector` first formal, and exact one-element origin bucket coverage for second operand and receiver, with no runtime/upload acceptance flags.
- **Definitive** [original source CI42217370118](https://github.com/alwansan/raf/actions/runs/42217370118), job `127890628850`, commit `205be806b79451097149c90a3a6301f05a6a009c`: **SUCCESS**. **11/11** sourcefree original name target tests and Cecil synthetic origin tests passed. Original source + managed pins, 19,512 original managed method bodies, 491,490 IL instructions, 7,246 string literals, 489 typed Unity numeric/uniform setter call records verified. Other CI on intermediate `e747744f` and `c29447d9` also passed, but final validation is the pinned CI above.

## Verified new finding

| Safe original-derived fact | Count / category |
|---|---|
| Exact source-authentic name→`Material.SetVector(string,Vector4)` first-formal calls | **1** |
| Actual **second formal operand** at that one matched call | **`new_object`: 1** |
| Actual `Material` **instance receiver** at that one matched call | **`pre_literal_unknown`: 1** |
| Actual original CB0 `Vector4` numeric component values proven | **no** |
| Exact constructor declaring type/signature/operand count proven here | **no** |
| `Material` receiver object identity or `Material.shader` is original Foam | **no** |
| Original full CB0 buffer upload, Unity 2021 stage mapping, Adreno pixels proven | **no** |

**Interpretation:** The second argument is an IL `newobj`-produced value at the same specific original compiled typed `Material.SetVector` call, not a direct method argument/field load/call-return in the bounded segment. That observation alone does **not** recover its numeric components, object lifetime or runtime value, and does **not** prove a full constant-buffer upload. The receiver's construction/loading precedes the first matched `ldstr`, so the forward-only stack trace classifies it as `pre_literal_unknown`. This must not be translated into a speculative Material→Foam Shader connection.

## Next independent targeted work

1. To recover the second value's true provenance, authenticate the **exact compiled `UnityEngine.Vector4` constructor** used by the `newobj` and track each of its formal inputs with bounded private IL stack slicing, retaining all original managed SHA constraints. Never disclose original scalar values or private symbols.
2. For the receiver, do a distinct **bounded pre-`ldstr` basic-block IL backward origin** analysis that respects branch/locals/field sources, then tie receiver Material to original Foam Shader identity using authentic material sources or stronger runtime/Unity evidence. Do not claim object identity by generic method class naming.
3. Even with one exact `Material.SetVector` first argument, the other 4 of 5 original CB0 vector names and **160-byte original CB0/upload** remain unaccounted. Existing [original two-pass SPIR-V compiled path CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) demonstrates pass0 Fragment six and pass1 Vertex two constant-index loads beyond the other stage's reflected capacity. Unity upload must cover actual larger per-pass stage access; do not pad, alias or replace private game shaders without original member/producer proof.

**WATER-001 OPEN.** No game ShaderLab, `.meta`, GUID, scene, save, FMOD, Settings, input, Unity import, native build, or APK changed by T2. This was a SHA-authentic managed-source diagnostic with one independently useful newly classified value path.
