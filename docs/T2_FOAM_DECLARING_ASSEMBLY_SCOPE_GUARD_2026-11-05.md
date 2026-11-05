# T2 — Foam RenderTexture returned-method assembly scope guard

**Status:** synthetic guard tested; source-original method assembly identity and real Unity/Android pixels **not verified**. WATER-001 OPEN, Raft NOT_READY 0/3.

## Evidence and why this matters

T2's genuine original [CI42065864809](https://github.com/alwansan/raf/actions/runs/42065864809) proved that the Foam `RenderTexture[]` element value is a compiled call with declared `UnityEngine.RenderTexture` return. [CI42072739153](https://github.com/alwansan/raf/actions/runs/42072739153) found one name-and-signature-compatible method definition inside the SHA-pinned original `Assembly-CSharp.dll`, and [CI42073459459](https://github.com/alwansan/raf/actions/runs/42073459459) showed one unresolved return source. [CI42077586809](https://github.com/alwansan/raf/actions/runs/42077586809), from T2's *independent scheduled scope*, further showed a sequential return load from an RT-typed local, one compiled writer of that local, but the writer's source remained unresolved by its immediate-predecessor checker. These are all **compiled-source** facts; none proves non-null objects or Android water pixels.

The original T2 method-definition matching was by `MethodReference.FullName`, declaring type's `FullName`, return type's `FullName` and formal parameter type names. These strings alone do not encode declaring *assembly scope*. Consequently, a method in another assembly with exactly the same type, name and signature can be a false match. The same issue applies to a forged `UnityEngine.RenderTexture` type name in a different assembly.

## Independent source-free test

New isolated project: `android-port/Experiments/T2/FoamAssemblyScopeGuard/` with .NET 9, Mono.Cecil **0.11.5** and no game data. Independent [CI42078113502](https://github.com/alwansan/raf/actions/runs/42078113502) **COMPLETED SUCCESS**.

Its constructed synthetic assemblies establish all of the following:

- A method with identical Cecil `FullName` in **another** assembly passes a loose lexical match; the new scoped predicate rejects it.
- A correct declaration in the same assembly, or referenced by its actual `ModuleDefinition`, passes the scoped test. An actual correct declaration in the other assembly also passes when the reference targets that other assembly.
- A mismatched `UnityEngine.RenderTexture` return **assembly**, a foreign module, an unresolved `ModuleReference`, or a wrong formal signature is rejected.
- No original Raft DLL, original IL, original indices, shaders, executable game or device resources were loaded, generated or published.

The [standalone workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t2-foam-assembly-scope-guard.yml) checks those exact positive and negative results. It is independent of scheduled T2's active original-return local-writer analysis.

## Next source-authentic integration gate

After the scheduled T2 return-local writer edits settle, integrate this strict *declaring assembly* plus *returned type assembly* predicate in the genuine source-original method resolution path, using the same exact ZIP2 `Assembly-CSharp.dll` SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Inspect the actual `MethodReference.DeclaringType.Scope` and returned `TypeReference.Scope` against the original matching definition's module and return type scope. Handle unsupported/ambiguous scope types as unresolved, not matched.

Run a new SHA-pinned original managed CI only after that real integration; verify that the unique existing method match remains sound or explicitly report unresolved. Do not publish source-original method names, original IL or numeric literal values/digests. Do not turn a same-assembly match into a claim that the method executed, created a non-null GPU texture, bound the original ShaderLab sampler or drew pixels on Adreno.

**Owner:** T2. **Source-only synthetic work session:** `20261105T1736Z-T2-chat-rt-return-reason-8e2d`. **Original result pending.**
