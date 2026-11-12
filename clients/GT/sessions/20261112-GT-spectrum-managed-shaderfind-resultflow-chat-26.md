# GT Chat-26 — Original Spectrum managed typed Shader.Find and branch-aware local result flow

**Date:** 2026-11-12. Writable only `feature/android-native-port`; original read-only `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`. No Git LFS, no original .meta/GUID/Material edits.

## Confirmed verified steps

- Earlier Chat25 original ZIP2 82/82 serialized owners/1556 Materials: **zero direct `Material.m_Shader` PPtr to Spectrum `sharedassets0.assets / PathID2432`**, [43300053045 SUCCESS](https://github.com/alwansan/raf/actions/runs/43300053045). Therefore source-original dynamic Shader.Find path is important; do not invent a static Material GUID.
- [43300958608 SUCCESS](https://github.com/alwansan/raf/actions/runs/43300958608): real original **Assembly-CSharp.dll 3,211,776B**, source Shader owner 115,978,112B independently checked against immutable ZIP2 manifest SHA. Mono.Cecil typed IL scanned **19,118 compiled method bodies**, **491,490 instructions**, **7,246 ldstr**, **81 typed UnityEngine.Shader.Find calls**. There is **one exact original Spectrum name literal** and **one direct literal→typed Shader.Find**; **0 Material(Shader) constructors in the same source method**. This is genuine code reference, not gameplay execution.
- [43301684794 SUCCESS](https://github.com/alwansan/raf/actions/runs/43301684794): source-original result immediately stored in a **typed Shader local variable**, not a directly resolved instance/static Shader field nor direct Material constructor. Typed field read source path remains 0.
- [43302209121 SUCCESS](https://github.com/alwansan/raf/actions/runs/43302209121): conservative **linear** IL probe resolved source Shader local, but stopped at first control-flow boundary; **0 linear loads**, **1 branch boundary**; therefore unproven downstream.
- [43302598498 FAILURE](https://github.com/alwansan/raf/actions/runs/43302598498): first CIL CFG code had a C# branch-target variable name conflict; fixed [100a4ae5](https://github.com/alwansan/raf/commit/100a4ae5c13cf94d5f501bb3e67a8a9c08e2f222).
- [43302914466 SUCCESS](https://github.com/alwansan/raf/actions/runs/43302914466): corrected real SHA-original Mono.Cecil CFG. **35 reachable IL instructions**, **3 branch nodes**, **1 reachable typed Shader local load on some path before overwrite**, **0 overwrites**, **1 unclassified consumer**. Zero direct local→Material constructor, local→Shader field store, local→typed one-Shader-argument call, or typed Shader return **in the bounded analysis**. This **does not prove** the local is unused; consumption may involve operands/multi-arg calls/control-dependent aliases outside the conservative classifier. Only source reachability is proven, no runtime execution, original Material binding, CB0/Sampler/RT or Adreno GPU pixels.

## Next concrete action

1. Improve source-authentic CIL stack semantics for the one reachable original Shader local load: class of actual consuming instruction/method parameter and passing across branches. Do NOT publish source symbol names or IL in artifacts. Require exact SHA original owner/managed DLL and negative controls. Do not equate reachable with actual runtime.
2. Verify original source Shader.Find→Shader local→actual water Material/renderer or Graphics/Blit pathway. If runtime-generated, source owner Material PPtrs will remain zero legitimately.
3. Only after original source bindings + Sampler/CB0/RT semantics, prepare exact-name source ShaderLab integrated into disposable Unity project, then Android phone test. 7pass private Unity success and synthetic material toggle alone are insufficient.
4. Foam Global two original passes, kernel6 identity, 770 Dummy Materials, phone water invalid pass baseline unresolved. Full native [43299084397](https://github.com/alwansan/raf/actions/runs/43299084397) older snapshot `2666622cbc93a4fde0dae22371cd3b157dc15ab7` was reconstructing at last check; do NOT cancel/restart or attribute new GT proofs to that snapshot.

## Recovery

Read `RESTORE_AR.md`, `RESTORATION_PLAN_AR.md`, `RESTORATION_PLAN.json`, `state.json`, `SUMMARY_AR.md`, `MEMORY.md`, then Chat25/26 and GitHub Actions job conclusions. Keep source, private Unity, Android packaged and phone pixel proof separate. No LFS and no original GUID mutations.
