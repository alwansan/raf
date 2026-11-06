# T2 — SHA-original Foam CB0 scalar field identities, IL writer sites and Material receiver prefix

- session_id: 20261106T1250Z-T2-chat-CB0-fieldwriters-materialprefix-7b2e
- origin: chat
- issue: WATER-001 OPEN / Android water NOT_READY
- experiment key: ZIP2-original-Foam-CB0-confirmed-SetVector-4float-3ldfld-private-field-identity-types-writers-receiver-IL-prefix-v1

## Input authenticity and baseline

- ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original `Raft_Data/sharedassets0.assets` 115,978,112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; original Foam Shader raw PathID2420 SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Original `Assembly-CSharp.dll` 3,211,776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Original binary **only statically read** in private GitHub runner; never executed, copied to artifacts or printed.
- Earlier source original [CI42210166957](https://github.com/alwansan/raf/actions/runs/42210166957) verified one of five original CB0 vector property names is the *first* string argument to an actual typed original `UnityEngine.Material.SetVector(string,Vector4)` IL instruction.
- Earlier [CI42218712162](https://github.com/alwansan/raf/actions/runs/42218712162) verified unique typed `Vector4::.ctor` with four float arguments, three instance-field loads plus one numeric literal. No actual runtime upload was inferred.

## Method and source fail-closed controls

T2 added only a source-only Cecil diagnostic at `android-port/Experiments/T2/FoamCb0ManagedLiterals/Program.cs`, with own scoped work registered before modification and isolated `.github/workflows/raft-t2-foam-cb0-managed-literals.yml`. No original ShaderLab/Unity .meta or other agents' files were touched.

- The same source-name→actual setter first-formal→unique `Vector4` ctor stack trace now maintains private `FieldReference` identity through `ldfld`, `dup`, locals and ctor argument pops. This avoids attributing unrelated adjacent field loads as constructor inputs. Private member identifiers are never serialized; only counts and declared public primitive type statistics are emitted.
- A second static pass over the **same SHA-authenticated original DLL** counts `stfld` opcodes targeting those exact original constructor input field identities, including distinct fields and distinct original method bodies. These are *write instruction sites*, not runtime-executed writes or actual values.
- If the receiver's stack value is consumed from *before* the source property-name literal (one pre-literal pop), a guarded prefix audit checks the immediately preceding IL instruction. It recognizes the public type `UnityEngine.Material` on a `ldfld` or related typed source only if the literal is not directly targeted by any branch/switch or exception-handler entry. Other cases fail closed as unknown; a typed Material field load is **not** evidence the Material's `shader` points to original Foam.
- Synthetic Cecil controls include 3 distinct typed `System.Single` fields from one declaring type feeding one `Vector4`, an adjacent typed `Material` field, a wrong/non-Material prefix, and a branch directly into the literal. Original 11 Python name registry tests and prior ambiguity/branch safeguards retained.

## Authentic result

Original source [GitHub Actions run 42220621927](https://github.com/alwansan/raf/actions/runs/42220621927), job `127901459744`, source commit `710ffd83b38554f45e602dba85d01027d7f8b4aa`: **SUCCESS**. 11/11 synthetic Python original-name tests, bounded Cecil fixture controls and original owner/DLL SHA pins passed; 19,512 original methods and 491,490 IL instructions inspected. No native Unity build or Android device rendering.

| Source authenticated compiled fact | Result |
|---|---:|
| Original CB0 member-name → exact typed `Material.SetVector(string,Vector4)` | 1 |
| Unique typed 4 × `System.Single` constructor | 1 |
| Actual `Vector4` argument's `ldfld` source references | **3** |
| Declared `System.Single` on all three source fields | **3/3** |
| Distinct original managed field identities | **3** |
| Distinct declaring classes for those fields | **1** |
| Original `stfld` IL write sites to the exact three fields | **3** |
| Exact fields with at least one original managed `stfld` site | **3/3** |
| Original compiled methods containing those write sites | **1** |
| Receiver prefix immediately before source property name | **1 × typed `Material` instance-field load** |
| Runtime values, Material.shader Foam identity, original CB0 upload and phone water | **not verified** |

**Interpretation.** The direct float field operands used to create the one observed original managed `Vector4` are now tied to three specific original fields of one declaring class, each with one detected static managed `stfld` writer site, all appearing in one method. The receiver was loaded from a typed `Material` field immediately before the source-authenticated name `ldstr` on the guarded straight-line path. Original method/field names, field values, Material object identity, constructor numeric literal, binary code, and shader property strings remain private. The fact that all three field writes occur in one method is **not** proof the method executes, nor of their numeric values or per-frame update.

## Remaining prerequisites

1. Resolve the **original Material field assignment and actual Material.shader link** to original Foam using source-authentic material/managed evidence, avoiding name heuristics.
2. Trace the producer of the three original `float` fields and the precise original Foam member/index relationship. One proven `Material.SetVector` name is not proof of all five original CB0 vector members.
3. Original [two-pass stage index CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) confirmed longer CB0 array stage is Fragment in pass0 and Vertex in pass1. Real Unity CB0 host allocation/write range and Vulkan/Adreno pixels still require proof. No arbitrary padding/clamping, invented aliases, placeholder shaders, or READY flags.

WATER-001 OPEN. No game shader, Unity .meta/GUID, saves/world, Settings, FMOD, touch, Unity native build or APK altered by T2.
