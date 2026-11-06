# T2 — Original Foam CB0 Material receiver field assignment and shader producer clues

**Session:** `20261106T1306Z-T2-chat-material-field-assignment-8e6a`, origin `chat`; **issue:** WATER-001 **OPEN / NOT_READY**.

## Original source and verified experiments

- Original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original Foam asset owner `Raft_Data/sharedassets0.assets` (115,978,112B, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`); original `Raft/Raft_Data/Managed/Assembly-CSharp.dll` 3,211,776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Private CI validates both pins; original DLL is statically scanned only, not executed.
- [Original compiled-index CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) found pass0 Fragment / pass1 Vertex longer CB0 reflected array with respectively 6 / 2 compiled constant-index loads outside the shorter stage capacity. These are original compiled paths, not Android runtime reads.
- Previous [CI42220621927](https://github.com/alwansan/raf/actions/runs/42220621927) authenticated one original Foam CB0 member-name first argument to `UnityEngine.Material.SetVector(string,Vector4)`, with one typed receiver field load immediately before the source original name, and four-float Vector4 input from three original distinct scalar fields plus one numeric IL literal. Three `stfld` write instructions to those exact scalar fields reside in one method. This does not establish the receiving Material's Shader.

## Distinct current question and method

Scope was reserved under `prompt/coordination/work/WATER-001/T2-20261106T1306Z-T2-chat-material-field-assignment-8e6a.json` before modifying any file. Added one **strictly source-only** Cecil check in the T2-owned `android-port/Experiments/T2/FoamCb0ManagedLiterals/Program.cs`, and bounded negative controls in the same tool's selftest, reusing isolated `.github/workflows/raft-t2-foam-cb0-managed-literals.yml`. It identifies the same exactly proven source-name to `Material.SetVector` receiver's private `FieldReference.FullName`, kept only inside process memory.

In the original SHA-pinned managed DLL it enumerates `stfld` operations targeting that **same exact field**, counts distinct original source methods containing a write, classifies the immediately preceding IL producer with public Unity types, and separately checks presence in those *writer method bodies* of public `Shader.Find`, `Material::.ctor`, or `Renderer.get_material` calls. The last method-level data are **co-occurrence only, not value-flow proof**. A direct typed immediate producer requires the previous instruction to produce a `UnityEngine.Material` value and no branch/switch or exception entry targeting the `stfld`. Unknown/ambiguous predecessors remain unknown; no private original source symbols/values/method identities are logged.

**Definitive [original SHA-authentic CI42222313603](https://github.com/alwansan/raf/actions/runs/42222313603)** (job `127907105758`, source commit `cf5a01b3149128c8ca6ee995537896baf2df524b`) **SUCCESS**. Original direct preceding code [CI42222254314](https://github.com/alwansan/raf/actions/runs/42222254314) also **SUCCESS**. The original managed scanner parsed 19,512 original methods and 491,490 IL instructions; 11 source-free Python tests and public Cecil negative controls passed. The CI validates exact original input hashes and deletes private material and name scratch after use.

## New grounded result

| Original compiled observation | Exact aggregate |
|---|---:|
| Distinct original `UnityEngine.Material` receiver fields associated with the source-named `SetVector` | **1** |
| `stfld` writes to that same Material field | **1** |
| Distinct original methods containing its write | **1** |
| Immediate typed producer of that `stfld` | **unproven (1)** |
| Same writer method contains a `Material::.ctor` call | **yes (1 method)** |
| Same writer method contains a `Shader.Find` call | **no (0 methods)** |
| Same writer method contains a `Renderer.get_material` / `get_sharedMaterial` call | **no (0 methods)** |
| Original `Material.shader` verified to be Foam / CB0 upload verified | **NO** |

**Interpretation:** The receiving Material field, previously known only from a source-authenticated `ldfld` prefix, has exactly one compiled writer site in one original managed method. That writer method contains some `Material` construction, but the instruction directly preceding the store cannot yet be classified as a typed value producer. **Therefore the Material constructor is a source-backed investigation lead, not proven the source of the field assignment.** The lack of an explicit `Shader.Find` in this managed writer method does not imply the field's Shader is absent or cannot be obtained from other calls or assets.

The result is independent from but consistent with the earlier one-typed-Vector4/three-float-field dataflow discovery. Neither proves runtime reachability, object identity, the original 160-byte CB0 upload to both stages, Unity 2021 importer support, real Vulkan pipeline or Adreno water pixels. The original world/save and audio/Settings stability remains outside this diagnostic.

## Next experiment (precise)

Trace the **actual second value of the exact Material `stfld`** through a bounded basic-block and local variable provenance model, including the same-method `Material` constructor candidate and its Shader first argument. Only elevate constructor→field identity if **exact IL stack ownership** is proven; do not use call proximity as evidence. After that, verify the Shader argument is original Foam by immutable original Material/Shader asset reference; a named C# call alone is insufficient.

No original game ShaderLab, Unity .meta/GUID, scene/prefab, audio, save, Settings, touch, native workflow or APK modified. `WATER-001` remains OPEN.
