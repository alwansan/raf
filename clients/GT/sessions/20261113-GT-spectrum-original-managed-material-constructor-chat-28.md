# GT Chat-28 — SHA-original Spectrum Shader.Find → own constructor → Material(Shader) dataflow

**Date:** 2026-11-13 (Asia/Baghdad). Writable branch only `feature/android-native-port`. Source original `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385` remains read-only with SHA verification. No Git LFS, original .meta/GUID mutation or shader/program identifiers in public evidence.

## Verified original managed lineage (not pixels)

- [43302914466 SUCCESS](https://github.com/alwansan/raf/actions/runs/43302914466): source-authentic `Assembly-CSharp.dll` 3,211,776B (19,118 methods, 81 typed `UnityEngine.Shader.Find` calls), exactly one source Spectrum exact-name direct call, `Shader` saved in typed local then used along a possible CFG path; 35 IL / 3 branches / 1 local load before any overwrite. This is source-reachability, not runtime execution.
- [43337606930 SUCCESS](https://github.com/alwansan/raf/actions/runs/43337606930): enhanced source-local next-instruction safe classification reveals exactly **one `newobj` constructor candidate**. Direct `Material(Shader)` was still zero at that immediate local load.
- [43337840022 SUCCESS](https://github.com/alwansan/raf/actions/runs/43337840022): the exact `newobj` is an **original own-Assembly managed type constructor** with **three arguments**, final exact `UnityEngine.Shader`; neither `UnityEngine.Material` nor another Unity Engine class.
- [43338106531 SUCCESS](https://github.com/alwansan/raf/actions/runs/43338106531): resolved SHA-original own-constructor body **44 IL instructions**, with **one typed `new UnityEngine.Material(UnityEngine.Shader)`** call. The method had no direct `Shader` field stores or `Graphics`/`RenderTexture` calls. At this stage, same-Shader argument forwarding was NOT yet proven.
- [43338326341 FAILED](https://github.com/alwansan/raf/actions/runs/43338326341): new stricter source argument checker initially failed with C# CS0136 local variable name shadow, not a Unity build or source identity failure. Fixed with `34234ee24a32743acf25d989148cfccb8311b998`.
- [43338485431 SUCCESS](https://github.com/alwansan/raf/actions/runs/43338485431): same authentic constructor has **one** `Material(Shader)` call whose **immediately preceding stack load is the original third argument (`ldarg.3`, typed Shader)**. This proves original `Shader.Find` result reaches the **typed shader argument of `new Material(Shader)`** along a possible in-method CFG path. Direct store of newly created Material to same-own-type field = 0 and to a local = 0; actual next consumer is **unclassified**. GPU run/Shader.Load/Material→Renderer/Graphics/RT/CB0/Sampler remains unproven. This is neither original Spectrum phone GPU acceptance nor original program binding acceptance.

**Source-derived path (static, path-possible, not runtime):**

`source-exact Spectrum name → UnityEngine.Shader.Find → typed Shader local → 3-argument original managed own constructor (third argument exact Shader) → new UnityEngine.Material(original Shader argument)`.

This confirms why the original 82-owner/1,556-Material serialized PPtr census yielded zero direct Spectrum refs: a **dynamic source Material creation path exists**. It does not prove that no other path exists, or that this path executes on phone.

## Added source field-retention proof after original Material construction

- [CI43339062121 SUCCESS](https://github.com/alwansan/raf/actions/runs/43339062121): exact original `new Material(original Shader)` result is immediately **duplicated via CIL `dup`**, not immediately stored in a field or local. This explains why direct-next-`stfld` counted zero.
- [CI43339407339 SUCCESS](https://github.com/alwansan/raf/actions/runs/43339407339): source managed IL after that `dup` contains an in-line property setter on the new Material/Unity Object, **then a `stfld UnityEngine.Material` inside the original managed class**. This is an exact, source-authentic, typed, in-constructor chain; it proves the Material object is retained, not that renderer uses it.
- Pending real field-reader test [43339688082](https://github.com/alwansan/raf/actions/runs/43339688082) follows that exact original Material field to compiled field loads, source Material API usage and per-method Renderer/Graphics candidates. **Do not report field readers as confirmed until test finishes; a method containing Graphics is not necessarily proof that the field supplied the drawing call.**

## Device and delivery — independent from source path

- [CL owner night session](https://github.com/alwansan/CL/commit/a320d5e23962568b62bffec95399cf3e0cb1f579) `LogRaft-20261112-235351-196`: 4 white/blue/cyan phone images and 36,828 invalid water shader passes (Spectrum 15,054 + Foam Global 21,774), 6,106 kernel index6, 2,844 cursor RGBA32, 2 OBB GUID failures; `World has been loaded` observed but actual device graphics is rejected. New dual-session [CI43336564346 SUCCESS](https://github.com/alwansan/raf/actions/runs/43336564346) proves safe known-bad log classification, not a water fix.
- [Full native 43299084397](https://github.com/alwansan/raf/actions/runs/43299084397): `reconstruct=success`, signed package checkpoint artifact `13997201215` and full delivery artifact `13996908213`; `publish-early-test=failed` from Release POST HTTP403 because built-in token lacks required workflow-write scope when branch differs from default under `.github/workflows`. The workflow already requested contents:write; commit `24a0291266ab572233301630c40e239d5154d9d0` clarified fail-closed error and narrow `RAFT_RELEASE_TOKEN` remedy, without changing release target. User/admin must provision an appropriate repo-limited token or approved GitHub App to publish.

## Next exact engineering operations

1. Trace the **result** of `new UnityEngine.Material(original Shader)` beyond the constructor `newobj`. Classify its direct next IL consumer; if added to container/collection or handed to setter, trace its original game methods/owner fields to actual Renderer, Graphics, Blit, RenderTexture.
2. After exact original dynamic Material→GPU binding, integrate exact-name, source-authenticated 7Pass Spectrum shader + global keyword into native Android AssetRipper import as a fully validated alternative; do **not** fabricate GUIDs. Pair with original Foam 2Pass and determine actual source kernel6 identity. 770 remaining custom Material documents still Dummy after vendor restorer.
3. Run source/Unity Android Vulkan strict shader/payload gates, build new signed XAPK only after actual source changes, then require matched Adreno phone screenshots plus clean or explanatory LogRaft for P06/P07 before declaring water restored.
4. Maintain fixed original source SHA, ZIP2-only/no LFS, read-only main/zip2 and no original asset modification. Update `clients/GT/RESTORE_AR.md`, `state.json`, `SUMMARY_AR.md`, `RESTORATION_PLAN_AR.md`, `RESTORATION_PLAN.json`, `MEMORY.md` and this session after verified batches.

**Do not claim:** original Spectrum pixels are fixed, runtime Unity `Shader.Find` actually executes, original shader custom buffer parity, original water RTT/FFT repair, OBB GUID repaired, or Release published. Source and Unity/import/package/device proofs remain distinct.
