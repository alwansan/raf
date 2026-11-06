# T1 — signed-zero / texture x0 signature for computed FFT coordinates

- **session_id:** `20261106T1933Z-T1-chat-zero-coordinate-signature-73e1`
- **origin:** `chat`
- **base_sha:** `de574cc91877d55157fff850debb48549cba5b91`
- **resumed_from_sessions:** `20261106T1916Z-T1-chat-address-provenance-e6b2`, `20261106T1907Z-T1-scheduled-report-shape-n8v2`, `20261106T1850Z-T1-chat-gpu-input-join-b71c`
- **issue:** `WATER-001` OPEN; project **NOT_READY 0/3**.
- **scoped work:** `prompt/coordination/work/WATER-001/20261106T1933Z-T1-chat-zero-coordinate-signature-73e1.json`, status `completed`.
- **experiment:** `prompt/coordination/experiments/T1/20261106T1933Z-T1-chat-zero-coordinate-signature-73e1.json`.
- **canonical event:** `prompt/coordination/B_TEAM/events/T1/20261106T1933Z-T1-chat-zero-coordinate-signature-73e1.json`.
- **trial:** `trial-20261106-r1` T1 `لا يحتاج` unchanged; no substantial integrated original water shader change or owner phone build.
- **original ZIP2 source pin:** `15964ea8f246b6e076ce26b60931ee2e1a9a2385` **NOT acquired in this cycle**. No original authored Unity kernel mapping asserted.

## Recovered work and scope

Read T_TEAM RESTORE_AR/CHAT_AND_SCHEDULE_AR/PROMPT_AR, trial votes, latest T1 scheduled `20261106T1907Z` (independent report-shape parser) and chat `20261106T1916Z`, pinned original FFT source provenance, current branch and running/queued Actions. Initial branch HEAD `3647270113bcc0672f7e298491f261c31e7682f9`, recheck before scope `de574cc91877d55157fff850debb48549cba5b91`. No running or queued CI before scope. Registered independent sourcefree T1 WATER-001 work lease first: [663bccce](https://github.com/alwansan/raf/commit/663bcccefa99af34dc8483ae95d1b9d2d05c0def).

Previous actual Unity2021 OpenGLCore synthetic [42278153683](https://github.com/alwansan/raf/actions/runs/42278153683) had computed shift/add/mask address float bitcast/plain multiply/precise multiply/Texture2D.Load paths each **63/64** mismatches while the same numeric address imported via `StructuredBuffer` had **0/64** mismatches in five corresponding paths. Six integer/normal-float/direct-image/static-global controls passed. This proved source-sensitive mismatch but did not reveal what bit pattern or sample coordinate the mismatches represented. Previously independently original-authenticated `FFT` first butterfly X source traced to signed32 Input vector through a bitcast and shuffle in original SPIR-V in [42220554705](https://github.com/alwansan/raf/actions/runs/42220554705); translated HLSL produced a float32 Phi stop [42221700354](https://github.com/alwansan/raf/actions/runs/42221700354). Original SHA-SPIR-V vs HLSL-roundtrip candidate keyed **on same Mesa Vulkan** matched in [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826); Unity original-derived [42198180194](https://github.com/alwansan/raf/actions/runs/42198180194) had butterfly coordinate drift. None alone proves original in-game kernel binding.

## This cycle's engineering change

Scoped to T1-owned synthetic test/gate and its own sourcefree workflow, leaving original Raft game, T2–T5 assets, settings, audio, touch, native build request and trial votes untouched:

- `android-port/Experiments/T1/T1FftAddressProvenanceTests.cs` [c41e29ba](https://github.com/alwansan/raf/commit/c41e29badea34ed722684b46b30dae7fb7d9b358): after same GPU `Dispatch(1,1,1)` and `ComputeBuffer.GetData`, retain 16 original mismatch counters; additionally count **only mismatch channels** whose computed float carrier bit pattern becomes signed +/-0 (scalar lanes 2..7) or whose `Texture2D.Load` output equals the unique synthetic `x=0` texel (image lanes 10..13). Preserve exact 6 positive controls, no per-pixel private output.
- `scripts/t1_fft_address_provenance_gate.py` [0246db33](https://github.com/alwansan/raf/commit/0246db33d5ae7fcfdf4e594ba4ee85aef29cb02e): now **requires a second independently bounded sixteen-line** report via `--signatures`; each 0..64, signature<=mismatch per category, zero signatures on controls, public report decomposes signature and other mismatches; still exact one NUnit pass and Unity return0. Both text inputs are bounded and symlink rejected, original private data not published. An observed zero signature is **not** formal proof that FTZ alone caused it.
- `tests/test_t1_fft_address_provenance_gate.py` [6d8a380b](https://github.com/alwansan/raf/commit/6d8a380b6f7e5fd3ced7e82200506c09381534f7): extends original 11 tests to **16** including all-signature, mixed signature/other, signature>mismatch, control violation, malformed second report, privacy and source fixture updated contracts.
- `.github/workflows/raft-t1-fft-unity-address-provenance.yml` [93f27342](https://github.com/alwansan/raf/commit/93f27342d4b2c46d811c6c16a2672d9a247f346a): exact expected `--signatures t1-address-provenance-unity/t1-address-provenance-zero-signatures.txt`, same `UNITY_LICENSE` environment and `raft-native-engine` mutex, 25m, `cancel-in-progress:false`, pinned GameCI v0.1.72 and Unity2021.3.45f2, no ZIP2/LFS. Intermediate pushes automatically queued/superseded older pending workflow revisions; those were **not manually cancelled**, and the final exact revision succeeded. Only final SHA is authoritative.

## Verified actual Unity GPU result

[Actions **42279949574**](https://github.com/alwansan/raf/actions/runs/42279949574), source SHA `93f27342d4b2c46d811c6c16a2672d9a247f346a`, job `128106388433`, **COMPLETED SUCCESS**. Read decoded job logs:
- Source-only adversarial Python tests **16/16 PASS** and Unity fixture tests **4/4 PASS**.
- Real Unity2021.3.45f2 OpenGLCore licensed NUnit test PASS, exactly one case, 64 invocations × 16 uints = 1024 GPU words, same synthetic address source/dispatch as prior 42278153683. All six positive controls PASS; all Unity scratch, XML and private GameCI logs cleaned in successful cleanup step.
- `computed_address_category_mismatches=[63,63,63,63,63]`, `computed_zero_signatures=[63,63,63,63,63]`, `computed_other_mismatches=[0,0,0,0,0]`, corresponding five buffer-loaded address paths and all controls **0**. The five computed paths are bitcast, ordinary float multiply, `precise` float multiply, `Texture2D.Load` from bitcast and `Texture2D.Load` from precise. The scalar mismatches were each signed-zero carrier bit patterns, and image mismatches each matched synthetic `x=0` texel exactly.
- Public category mismatch counts (in order) `[0,0,63,0,63,0,63,0,0,0,63,0,63,0,0,0]` and signature counts **identical**.
- Classification: `computed_only_context_difference`; **no other mismatch class** observed on this exact synthetic test.

**Interpretation:** Same integer address values survive when staged through a buffer but not when calculated and carried as subnormal float32 bits in this Unity OpenGLCore fixture. A value of signed-zero observed downstream does **not** alone identify if hardware FTZ, Unity HLSL translation, GLSL compiler optimization or some other lowering step is responsible. The `x=0` pixel is a *designed unique synthetic proxy* for a collapsed coordinate; raw GPU coordinate registers were not captured, and original Raft FFT/Adreno/water pixels remain unverified. Do not overclaim that water has been restored.

## Handoff to T1 scheduled / next chat

1. Recheck live HEAD, T1 and other T workers' scopes, queued/running CI before touching shared resource.
2. Highest-value next step: on **authenticated original ZIP2 FFT slot0**, map signed32 Input via bitcast/shuffle and translated HLSL `OpPhi` reaching butterfly1 X to actual runtime source and private **Unity2021 original-derived** indexed read/texture binding. Use `scripts.t1_fft_private_unity_input_join` and SHA-bound original-vs-candidate per-invocation keyed capture on identical actual source/butterfly images + dispatch. This is the threshold before any game shader fix or device build.
3. If the real FFT coordinate indeed follows a computed-float/bitcarrier path, implement smallest semantics-preserving integer-bitcast HLSL translation change (not fake kernel IDs, not replacing game systems), verify both original and Unity GPU numeric parity, then consider owner phone acceptance under T1 vote policy.
4. If actual private Unity capture infeasible, bounded source-authentic static evidence about butterfly1 X origin and sampler/texture IDs is more useful than repeating synthetic canaries.
5. No ongoing CI/resource reservation after this scoped success; T1 trial `لا يحتاج`; WATER-001 OPEN / NOT_READY.

This checkpoint records the independent experiment and does not overwrite any other T1 session, T2–T5 artifact or the canonical shared issue.