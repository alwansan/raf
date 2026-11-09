# T2 — SHA-original Foam pass1 Texture callee CFG topology, 9 Nov 2026

**Issue:** WATER-001 remains OPEN · **Worker:** T2 · **Scope:** authentic original managed call target **reachable CFG and syntactic return predecessor categories**. This is neither shader reconstruction nor Android game acceptance.

## Source and prior proof

From prior original managed Cecil result at [CI42519122764](https://github.com/alwansan/raf/actions/runs/42519122764):
- The exact original Foam Material reaches both `Graphics.Blit` literal pass calls via original IL (not only names).
- Pass0 Blit source is statically declared `RenderTexture`, `typed_field` (six bounded reverse-IL steps).
- Pass1 Blit source has declared `Texture`, `typed_call_result` (21 steps including one earlier `void` call).
- The resolved pass1 source callee is an original managed method with branch/conditional/throw-class flow. Declared types are **not instance identity**, nor does a direct `callvirt` necessarily mean virtual dispatch; the analyzer checks original MethodDefinition flags and leaves true non-final virtual dispatch unresolved.

## This cycle's new authenticated evidence

T2 registered scope before changes: `work/experiments/20261109T0155Z-T2-chat-original-cfg-topology-a8f5.md`. Then added source-only `ReachableReturnTopology` in `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs`:
- independent reachable-instruction traversal over at most 128 CIL instructions;
- explicit direct/conditional/switch branches, throw, return and fallthrough;
- rejects invalid jump targets, fallthrough outside method, unsupported flows and exception-handler regions;
- checks all reachable `ret` predecessor categories and flags joins (including a test for multiple incoming edges) without following private field/object values;
- redacted fixed categories only. **No private method/field names, original instruction text, code offsets or game contents in logs or artifacts.** The previous strict safe JSON schema and all false instance/proof flags are unchanged.

First [CI42548298389](https://github.com/alwansan/raf/actions/runs/42548298389) failed **only** the new synthetic return-edge selftest after successful compilation; source assets were not reached on that run. T2 corrected the fixture to distinguish a single jump from a true multi-edge ret join (fix commit `615e8981c909b981a1afad7caf4087ec5ab9dc16`; initial source commit `43340cb5a26e1cb439eb867f2623bbaf32b751fa`).

**Authoritative run:** [CI42548419872](https://github.com/alwansan/raf/actions/runs/42548419872) at source `615e8981c909b981a1afad7caf4087ec5ab9dc16`, job `128938373231`, **COMPLETED SUCCESS**. Proof chain: 17/17 Python tests; Cecil synthetic fixtures PASS; ZIP2 source pinned `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original 3,211,776-byte managed DLL SHA authenticated and 115,978,112-byte shader-owner source staged and SHA verified; original scan PASS; private data removed before uploading bounded safe artifact.

Relevant sanitized actual-original observations:

```text
T2_FOAM_PASS0_BACKTRACE RenderTexture typed_field static_type_only_no_instance_proof steps=6 void_calls=0
T2_FOAM_PASS1_BACKTRACE Texture typed_call_result static_type_only_no_instance_proof steps=21 void_calls=1
T2_FOAM_PASS0_CALLEE_CFG_TOPOLOGY not_call_return_source
T2_FOAM_PASS1_CALLEE_BODY_FAMILY original_method_branch_flow
T2_FOAM_PASS1_CALLEE_CFG_TOPOLOGY cfg_mixed_syntactic_return_predecessors
```

**Interpretation:** At least two distinct *syntactic predecessor families* exist across reachable original Texture-return sites (not necessarily distinct runtime object instances). The original branchy method is not safely reducible to a unique direct return producer using this audit. The exact per-path origin/alias must be analyzed privately with stack, locals, receiver and path joins. This result is an **identified obstacle**, not a confirmed bug in the original game.

## Safe next engineering step

Using the existing T2 SHA-authenticated private runner, classify `ret` values with path-sensitive or merge-safe abstract IL evaluation stacks (including EH/virtual dispatch rejection) and explicit receiver/local/static-field identity semantics. For pass0 destination→pass1 source equivalence require a demonstrable, unique object-instance alias across their original actual allocations/writes; do not infer from two fields having the same type. Then validate CB0 source member types/offsets and sampler bindings, authentic ShaderLab pass selection and Unity/Adreno pixels before considering a water restoration claim.

No new Mini APK (T2 **NO_BUILD**) or full game XAPK was made; previous actual owner shared Mini r2 synthetic T2-01..04 Adreno730 PASS is separate evidence. This report does not alter `WATER-001`, trial votes, build readiness or existing graphics assets.
