# T2 — Foam pass1 explicit-null CFG provenance (chat)

- session_id: `20261109T1905Z-T2-chat-foam-null-branch-r7k3`
- origin: `chat`
- started_utc: `2026-11-09T19:05Z`
- base_sha: `be444d85cec8f0d3df9f526242442be5db14e01d`
- resumed_from_sessions: `20261109T1854Z-T2-chat-foam-report-alias-b8e7`, `20261109T1517Z-T2-scheduled-foam-provenance-p6k4`, `20261109T1216Z-T2-scheduled-cecil-ci-4e9a`
- work: `prompt/coordination/work/WATER-001/20261109T1905Z-T2-chat-foam-null-branch-r7k3.json` (published BEFORE edits in `b6d6accfd920698958c59943e123a80fddc96070`)
- issue: WATER-001 (OPEN); no claim of ready or Android pixels.

## Evidence recovered

- Source guard final CI `42678582388` **SUCCESS**, 63 T2 source-free checks plus original resource steps, no device pixels.
- Original managed SHA-pinned Foam Blit probe `42607763178` **SUCCESS**, original pass0 source `RenderTexture/typed_field/steps6`, pass1 source `Texture/typed_call_result/steps21` after one void call. Its pass1 original callee body has branch flow; CFG syntactic predecessors mixed, and forward return-value analysis was previously `value_mixed_or_joined`. That loses whether any reachable path explicitly loads `ldnull`, which matters for safe texture-source uncertainty.
- T1 FFT, T3 materials, T4 mouse and T5 release/UI scopes remain separate. No matching in-progress original T2 producer run was present at scope registration. No shared native request or Unity changed.

## Change and scope

Source commit `62a89888d2109d3a95d50d89c2b2ccd9acb20f44` modified **only** `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs`. Bounded original managed Mono.Cecil CFG abstract interpretation now unions (rather than destroys) source producer *families* at stack/local joins and return sites. The report emits a strictly finite tag `value_mixed_with_explicit_null_literal` versus `value_mixed_without_explicit_null_literal`, retaining existing single-category tags. Added synthetic selftests for field-vs-null, field-vs-constructor, and null through a shared return phi. On original managed source no private field/method/token/name/IL/bytecode is output.

**These tags distinguish an *explicit ldnull path*, not runtime nullability.** Fields, arguments, getters and opaque values may still be null, multiple field tokens may yield one abstract category, and cross-pass actual RenderTexture object identity is not established. The original method may throw on a path and still have other returns; no Unity/ShaderLab/Adreno pixel conclusion.

## Test launched

Path-filter launched existing safe-only authentic source workflow automatically:
- [CI42680030121](https://github.com/alwansan/raf/actions/runs/42680030121), source `62a89888`, initially **in_progress**. It runs Cecil synthetic selftest and authentic ZIP2 DLL/Shader owner SHA authentication then safe aggregate categories.
- [CI42680030029](https://github.com/alwansan/raf/actions/runs/42680030029) platform adapter triggered on same commit; unrelated, no cancellation or modification.

No duplicate manual workflow dispatch, APK, XAPK or owner phone test requested. CI must pass before this scope can be called validated.

## Handoff

Read final `42680030121` job logs and verify `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS` and `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW` safe category, original DLL SHA, and private scratch purge; if failed, diagnose exact source-only error before retry. If successful, integrate the **limited** explicit-null-path result into WATER-001 evidence and decide next based on *original* result. Next engineering gap remains passing source/destination **instance** equality (callee receiver/field identity, alias across calls) and actual CB0/ShaderLab/phone water visuals.

Existing original CI is a provenance experiment, not approval of water pixels or of a game package.
