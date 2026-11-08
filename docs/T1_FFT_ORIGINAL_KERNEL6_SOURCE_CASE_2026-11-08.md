# T1 WATER-001 — What original Raft FFT source can actually say about kernel-index 6

**Status: VERIFIED conditional source *numeric argument*; Unity kernel ID, authored source, Android runtime shader and actual water repair UNVERIFIED.**  
**Owner:** T1, chat session `20261108T2022Z-T1-chat-fft-source-gate-d8b4`, 8 Nov 2026.  
**Branch:** `feature/android-native-port`. **No native game or Mini APK rebuild in this investigation.**

## Authentic inputs and original-source gate

We used the existing tracked original PC `Raft/Raft_Data/Managed/Assembly-CSharp.dll` (3,211,776 bytes), pinned Git blob `fc9d4ba920a178fdb89c970d9d772a01051dadc6`, and reconstructed only temporary private CSharp9 using pinned `ilspycmd 11.2.0.10050`. The original `Dx11FFT` managed class must independently match canonical post-decompile SHA256 `8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0`; inherited `GpuFFT` must match SHA256 `2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704`. Private source/text, original shader data, compiler logs and raw device logs are not published or embedded.

Existing independently authored source contracts `scripts/probe_original_fft_inherited_seed.py` and `scripts/probe_original_fft_kernel_callsites.py` have been re-used with strict source SHAs rather than duplicating or guessing an original C# field name. First verifies that the selector exponent is *inherited* from `GpuFFT` through the original constructor and computed as an **integer truncation** of `Mathf.Log(size)/Mathf.Log(2f)`, not simply a value in `Dx11FFT`'s second integer constructor argument. Second verifies the **same receiver**, exactly **2 `Dispatch`** and **6 `SetTexture`** callsites, with first/second pass kernel expression offsets exactly **0 and +1**. In this authentic `Dx11FFT` managed class, **`FindKernel` is never called (count 0)**. This says nothing about other source classes or the native Unity runtime's kernel lookup behavior.

## Conditional answer for observed integer 6

The verified original source **arithmetic shape**, for a hypothetical integer exponent `n`, fourth constructor boolean bank selector, and pass offset, is:

`sourceNumericArg = ((n - 5) << 1) + (bankFlag ? 10 : 0) + (passOffset 0 or 1)`

Across the **20 source-candidate integer cases** (n=5..9, bankFlag false/true, passOffset0/1), the **only** case that yields the *numeric C# Dispatch argument* 6 is **n=8 (size (2^8=256)), bankFlag false/bank0, first pass (offset0)**. Its adjacent second pass uses numeric argument **7**. Under this same source formula, bank1 for a hypothetical 256-sized case would use **16/17**, not 6/7.

The mathematical inversion is derived from the exact original source expression and the existing 20-candidate enumeration. It is **not evidence** that:
- The owner's failing Android game actually configured FFT size=256, selected bank0, or evaluated the float `Mathf.Log` expression to exactly n=8.
- Any particular `ComputeShader` asset instance on the phone existed or had the same original serialized program order, asset GUID, keywords, kernel count, resource binding or imported pass table.
- Unity's runtime **kernel ID 6** corresponds to the sixth/seventh serialized DXBC compiled variant (original program slot 6), or to any specific *named* `#pragma kernel` in reconstructed shaders.
- `Dx11FFT` made the logged invalid-kernel call rather than another water renderer/compute user, or that the raw first-segment lexical `Dx11FFT` mentions are stack evidence.
- Any computation, GPU pixel or water material was repaired.

The existing owner CL collector first recorded a rejected index6 at **16:49:17.581 Baghdad** and 11,165 index6 root messages during that session, but the first raw CL segment's `Dx11FFT` lexical mentions **cannot** map that numeric error to a runtime method/instance. See [separately authenticated CL first-raw report](T1_WATER_FIRST_RAW_KERNEL_CONTEXT_2026-11-08.md). The source-compatible 256/bank0 hypothesis is **a specific testable possibility**, not a diagnosis of cause.

## Green source evidence and remaining blocker

- [CI #42519336164](https://github.com/alwansan/raf/actions/runs/42519336164) **SUCCESS**: fixed previous `SyntaxError` in `scripts/t1_fft_first_divergence.py` (literal backslash-n escape rather than source newline). This restores the synthetic paired-pass first-divergence comparator; it does not alter water algorithms.
- [CI #42519731107](https://github.com/alwansan/raf/actions/runs/42519731107) **SUCCESS** at `fed9e62b623323c82efd4c708514ebc417a9c04e`: 15 new source-free regression checks + 5 inherited-seed and 9 original-managed callsite regressions (**29 tests total**), exact original Git blob admitted, private ILSpy generated source hashes verified and authentic original numeric selector inversion completed. Zero GPU/Unity game executions.
- **Final fully authenticated gate:** [CI #42519853981](https://github.com/alwansan/raf/actions/runs/42519853981) **COMPLETED SUCCESS** at source SHA `f51c4e26d340a5db3f9b8781506e3e53dc180e2e`. **16 new negative/source selector tests**, **5 inherited-seed**, and **9 original-managed callsite tests = 30/30 source-only tests PASS**, plus original tracked DLL Git blob matched, full temporary ILSpy CSharp9 decompilation and exact private source SHA hashes, and runtime mapping flags asserted false. The workflow explicitly asserted that authentic `Dx11FFT` calls `FindKernel` **0 times**. New adversarial test verifies that merely inserting a *synthetic* `FindKernel` source mention still cannot prove Unity's runtime ID. No Unity runtime or Android GPU executed, no raw private code/artifact published.
- Integration stays blocked on **same-build actual Unity runtime** `ComputeShader` registration and importer/keyword behavior, not solely on knowing a source integer. Earlier private Unity 2021.3.45f2 container attempts hit **source-free activation/licensing blocker** before meaningful original import; repeating identical heavy original editor jobs without activation correction is unproductive. Other build workflows succeeding cannot be treated as proof this specific private editor environment works.

## Next discriminating runtime experiment, coordinated with T5

Instrument the original-derived **caller only after verifying its SHA and preserving the Unity `.meta` GUID** in the actual next authorized full-game build. At the first failed FFT call record **metadata only**: compiled game commit/installed APK SHA, original C# callsite hash, instance/asset identity (or private GUID hash), ComputeShader null/support status, actual FFT size and fourth boolean/bank state, computed `n` and two numeric Dispatch indices, whether `HasKernel(name)` and `FindKernel(name)` ran and their results where a name exists, `GetKernelThreadGroupSizes` outcome, `SetTexture`/buffer slot & render-target dimensions/bindings, `Dispatch(x,y,z)` and exception/invalid-log timestamp, scene-before/after world_loaded. Do not print shader code, texture pixels, private names, user identifiers or API secrets.

**Falsification:** If the failed instance was not size256/bank0/first-pass, the *original Dx11FFT source numeric-index6 explanation* cannot be assigned to that failure on the assumption that its source formula executes unmodified. If it was size256/bank0, that is **supporting evidence for the numerical argument only**, and still requires runtime registered named kernel/compiled program and resource binding evidence before a fix. Cross-check with T2's original Spectrum/Foam Material pass validation. T5 decides next XAPK strictly by team vote, not this source-only report.

**WATER-001 remains OPEN; full Raft NOT_READY 0/3. Shared Mini T1 vote NO_BUILD unless T1 compiled driver actually changes.**
