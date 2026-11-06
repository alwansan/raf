# T2 — Source-authentic Foam CB0 Material field assignment exact IL stack value

**Session:** `20261106T1314Z-T2-chat-material-stfld-stack-4c62`, `origin=chat`, issue `WATER-001 OPEN / NOT_READY`.

## Source, baseline, and question

- Source: ZIP2 immutable `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original `Raft_Data/sharedassets0.assets` Foam owner 115,978,112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; original 3,211,776B managed `Assembly-CSharp.dll` SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Exact source/DLL SHA verified *inside private CI*; no original game assembly executed.
- Prior [source-backed original setter CI42220621927](https://github.com/alwansan/raf/actions/runs/42220621927) proved one original Foam CB0 source-name first string formal to actual Unity `Material.SetVector(string,Vector4)`, with typed Material instance-field receiver and 3 distinct `System.Single` field inputs to the ctor's `Vector4`. Its receiver field has exactly one compiled original `stfld` in one method. Later [CI42222884964](https://github.com/alwansan/raf/actions/runs/42222884964) found the instruction directly before the `stfld` was **not classifiable as a directly typed local, parameter or immediate `Material` constructor**, so the fact that the writer method contained `Material::.ctor` remained only a candidate.
- This experiment tests **actual IL stack ownership of that exact `stfld` value**, including a same-basic-block constructor, `dup`, locals and typed `Shader` argument propagation. It is not a test of whether original Material.shader is exactly Foam, because the source Shader asset identity is a separate question.

## Bounded fail-closed implementation

T2 added isolated `android-port/Experiments/T2/FoamCb0ManagedLiterals/MaterialStoreValueTrace.cs`, connected it **only** to the pre-existing authenticated source-name→setter receiver's exact private `FieldReference` in the T2 Cecil scanner, and added bounded-safe JSON assertions in the isolated `.github/workflows/raft-t2-foam-cb0-managed-literals.yml`.

- Select the basic block containing the `stfld` by control-transfer, branch/switch target and exception-handler entry boundaries. Reject any alternate entry directly at the target store; cap to **128 instructions** and **96 stack items**; any unmodeled opcode blocks attribution instead of inventing state.
- Track only necessary IL stack sources through public typed `ldarg`, `ldfld`, `ldsfld`, calls, `newobj`, `dup`, `stloc`, `ldloc`. Require a **typed** `UnityEngine.Material::.ctor(UnityEngine.Shader)` to produce the **actual popped value operand** for the exact source-owned `stfld`, not merely appear nearby. Classify how its first `Shader` formal was produced but do not release original field/member names or other private identifiers.
- Synthetic Cecil controls verify direct `new Material(Shader)` assignment, same-block local and duplicate forwarding, a nearby constructor that is popped and is **not** the stored value, branch into store, wrong field type, null assignment, unsupported instructions and exact typed Shader method parameter.
- The original owner and managed DLL are only staged and SHA-authenticated in Actions and deleted. Only aggregate value/Shader origin categories and booleans leave the CI.

## Authentic outcome

Initial [CI42224601338](https://github.com/alwansan/raf/actions/runs/42224601338), [CI42224703030](https://github.com/alwansan/raf/actions/runs/42224703030), and [CI42224754004](https://github.com/alwansan/raf/actions/runs/42224754004) **failed compilation of the T2-only checker before reaching any original-game claim**, with public C# diagnostic codes `CS0136` and `CS1929`. Repaired a synthetic local variable name conflict and a dictionary-interface use in `MaterialStoreValueTrace.cs` at commit `d623cef56876b2ffd9fc76949e20598d02090391`, preserving the tests and original SHA gates.

**Definitive genuine original [CI42224883549](https://github.com/alwansan/raf/actions/runs/42224883549)**, job `127915749429`, commit `d623cef56876b2ffd9fc76949e20598d02090391`: **SUCCESS**. All 11 source-free Python name-registry tests, new public Cecil stack ownership controls, original ZIP2 Shader source/name registry, and original managed 3,211,776B SHA gates passed; 19,512 method definitions and 491,490 original managed IL instructions examined.

| Newly proven original IL observation | Result |
|---|---|
| Original source CB0 member-name to exact typed `Material.SetVector(string,Vector4)` | **1 call** |
| Typed receiver `Material` field matching original `stfld` writer | **1 field / 1 store** |
| **Exact value popped by that store** | **`new Material(Shader)` constructor product** |
| **Typed Shader constructor formal's immediate source** | **one `UnityEngine.Shader` instance-field load** |
| Basic-block IL instructions examined for store value | **7** |
| The exact private Shader field proven to be *the original Foam asset* | **NO** |
| Runtime execution / original complete CB0 upload / Android pixels | **NOT PROVEN** |

**Interpretation:** The same original Material field that receives a source-original CB0 property name has a source-verified compiled assignment from a `Material` object created with a Shader formal. The latter is loaded from an original managed instance field of declared type `UnityEngine.Shader`. This is an actual IL stack source-to-store link, not simply a same-method `newobj` co-occurrence. It does **not** prove the Shader object is the original Foam shader; material field object identity, runtime reachability, 160B CB0 bytes to both compiled stages and Adreno rendering remain unverified.

**Next necessary experiment:** retain the exact private `Shader` field identity as an in-run memory-only handle and inspect whether it is assigned by managed code or populated from an original Unity serialized scene/prefab/material reference. If managed `stfld` writer exists, trace its actual source. If not, do not assume it is null—Unity serialized Inspector fields can be populated externally. Only prove original Foam Shader GUID/PathID from an authenticated serialized material/object reference, never from symbol resemblance.

No game `.shader`, .meta/GUID, Assets, world/save, Settings, audio, input, native Unity build, APK/OBB or other agent files modified by this source-only T2 experiment. `WATER-001` remains OPEN.
