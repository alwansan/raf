# T1 — Unity2021 OpenGLCore synthesized FFT float-bitcarrier sampled-image read

- session_id: 20261106T172258Z-T1-chat-bitcarrier-textureload-c4e9
- origin: chat
- status: completed (scoped Unity synthetic OpenGLCore primitive diagnostic, WATER-001 still OPEN)
- issue_id: WATER-001 (OPEN, NOT_READY 0/3)
- base_sha: 7c04928db1f45f4e66a656286bacc9e055bfea10
- resumed_from_sessions: 20261106T171240Z-T1-chat-unity-keyword-runtime-9f3a; 20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4; 20261106T163310Z-T1-chat-real-fft-pair-d91e
- work: prompt/coordination/work/WATER-001/20261106T172258Z-T1-chat-bitcarrier-textureload-c4e9.json
- experiment: prompt/coordination/experiments/T1/20261106T172258Z-T1-chat-bitcarrier-textureload-c4e9.json
- event: prompt/coordination/B_TEAM/events/T1/20261106T172258Z-T1-chat-bitcarrier-textureload-c4e9.json
- source pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 (not accessed, never exported)
- workflow: .github/workflows/raft-t1-fft-unity-bitcarrier-texture-load.yml
- current run: https://github.com/alwansan/raf/actions/runs/42261467757
- job: 128042200390
- source workflow commit: 2373a9310c659520e46479a0373d2b44f0d26134
- original compiled FFT or Android runtime modified: **no**

## Verified context and distinct scope

Original-vs-HLSL **same Mesa Vulkan fixture** [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) genuinely matched 384 invocation-keyed reads (site counts 64,256,64) with identical actual inputs and dispatch, but only on the one 1024x32 seed19 fixture. Authentically derived Unity2021 OpenGLCore FFT replay [42198180194](https://github.com/alwansan/raf/actions/runs/42198180194) previously produced 252/256 address mismatches on first butterfly site X and 64/64 on second site, with 63/64 pass0 mismatches, despite exact uploaded input identity. Scheduled T1 `20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4` independently owns original-source Unity trace experiment design; no active engine CI from it on this review. Last T1 chat [42259968584](https://github.com/alwansan/raf/actions/runs/42259968584) successfully executed a **different** synthetic ComputeShader local keyword GPU variant, 192 uint32 readbacks; no source asset or variant proof for actual FFT.

## Hypothesis and isolated synthetic execution

The narrow question is whether the *primitive* HLSL sequence bitcast(uint4 -> float4), select components/swizzle, bitcast(float2 -> int2), followed by Texture2D<float4>.Load(int3), is numerically faithful in Unity2021 OpenGLCore. It tests subnormal-sized float32 bit patterns of GPU-generated dynamic integer coordinates, not original secret shader bytes. Five paths are recorded per invocation: source direct, butterfly site1 direct, butterfly site1 float2 carrier, butterfly site2 direct, butterfly site2 float4 swizzle carrier. Each of 64 invocations addresses a deterministic 64x32 RGBAFloat texture with exact coordinate-coded R channel. The Unity test asserts 320 exact uint32 float-bit outputs in total (64 per path), uses actual GPU ComputeBuffer/Texture2D.Load, and records five bounded counts (0–64) only. Explicit OpenGLCore device assertion prevents backend substitution.

Published files (all new, no source overlap):
- `android-port/Experiments/T1/T1FftBitcarrierTextureLoad.compute`: original-free synthetic HLSL with direct vs float-bitcarrier/swizzle load.
- `android-port/Experiments/T1/T1FftBitcarrierTextureLoadTests.cs`: full Unity2021 EditMode NUnit source with 64x32 RGBAFloat texture input, 64 invocations, 320 uint outputs and five class-level mismatch counts.
- `tests/test_t1_fft_bitcarrier_texture_fixture.py`: source-only authored fixture checks.
- `.github/workflows/raft-t1-fft-unity-bitcarrier-texture-load.yml`: SHA-pinned GameCI CLI0.1.72 Unity2021.3.45f2, shared `raft-native-engine-${{ github.ref }}` mutex, 25-minute limit, no original data or artifacts, private logs and project removed. Exact 1-case NUnit gate; only class mismatch counts are published.

## Observed stage and next

[42261467757](https://github.com/alwansan/raf/actions/runs/42261467757) sourcefree unit preflight SUCCESS, SHA-pinned CLI download SUCCESS, genuine Unity EditMode GPU step in_progress as of first checkpoint. No parity claim before terminal job. Read only bounded `RAFT_T1_BITCARRIER_TEXTURE_COUNTS` and `RAFT_T1_BITCARRIER_NUNIT`, plus explicit final Action stage. If nonzero bitcarrier mismatches but direct controls pass, this synthetic backend primitive is suspect. If all zero, reject this **simple primitive-only** explanation; it would not disprove more complex original SSA/Phi/precision path causes. If Unity test fails before count, classify compiler/runtime boundary and fix exact synthetic issue if justified. No Android water or original Unity FFT claim from sourcefree tests. Do not repeat unchanged CI.

## Actual Unity runtime result (2026-11-06 17:27 UTC)

Run [42261467757](https://github.com/alwansan/raf/actions/runs/42261467757) on `2373a9310c659520e46479a0373d2b44f0d26134`, job `128042200390`: **COMPLETED SUCCESS**, genuine Unity2021.3.45f2 licensed EditMode stage and cleanup **SUCCESS**. Exact source-only Python tests: 3 fixture tests + 4 fixture-staging tests, all PASS. Exact NUnit case `T1FftBitcarrierTextureLoadTests.SourceAndButterflyBitcarriedFetchesMatchExactIntegerAddresses` PASS 1/1 (strict expected case gate).

Verified live GPU categories: `RAFT_T1_BITCARRIER_TEXTURE_COUNTS`: `capture_reached=true`; `source_direct=0`, `butterfly1_direct=0`, `butterfly1_float_carrier=0`, `butterfly2_direct=0`, `butterfly2_swizzled_carrier=0` mismatches over 64 reads each. `RAFT_T1_BITCARRIER_NUNIT`: `GPU_word_tests=320`, `all_expected_tests_passed=true`, original shader compared=false, Android Adreno proven=false. Unity actual GPU dispatch and 320 exact readback bits were validated; private logs/project/test XML cleaned by successful always step.

**Discriminator:** The trivial dynamic `uint4 -> float4 -> int2` and float4 swizzle into two `Texture2D.Load` sites is faithful in this synthetic OpenGLCore fixture. Therefore the real original-derived OpenGLCore butterfly error (252/256 site1 X, 64/64 site2) cannot be attributed to the *basic carrier->texture fetch primitive alone* under this tested configuration. It may depend on more complicated arithmetic, nested Phi/loop predecessor selection, register layout, host variant binding or compiler lowering of the original HLSL. This positive test does not prove the original shader, unity authored mapping, source-vs-Unity parity, full water or Adreno.

**Next independent discriminator:** add the observed `OpPhi float32` merge/nested CFG branch and original HLSL vector-carrier arithmetic to a *source-free* OpenGLCore test, while another session pursues actual source-authenticated Unity keyed trace and per-site comparison. Do not modify Raft shader speculatively. Session completed, resource released. WATER-001 OPEN / NOT_READY.
