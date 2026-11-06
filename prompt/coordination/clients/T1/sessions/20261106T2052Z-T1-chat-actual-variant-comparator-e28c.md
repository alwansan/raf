# T1 — real-GPU integer_source counterfactual comparison gate

- **session_id:** `20261106T2052Z-T1-chat-actual-variant-comparator-e28c`; **origin:** `chat`.
- **resumed_from:** `20261106T2038Z-T1-chat-integer-source-a47c`, `20261106T2031Z-T1-chat-real-unity-pair-6d9a`, `20261106T2017Z-T1-chat-private-producer-gate-8f31`.
- **baseline HEAD:** `4ae3a130dd671909649dedbdee1f6f21c62e0210`; issue **WATER-001 OPEN**, **NOT_READY 0/3**. T1 vote **لا يحتاج** unchanged.
- **scope:** `prompt/coordination/work/WATER-001/20261106T2052Z-T1-chat-actual-variant-comparator-e28c.json` completed; source-only, distinct from active `20261106T2038Z-T1-chat-integer-source-a47c` Unity GPU test, no duplicated heavy runner or native XAPK request.
- **experiment:** `prompt/coordination/experiments/T1/20261106T2052Z-T1-chat-actual-variant-comparator-e28c.json`.
- **event:** `prompt/coordination/B_TEAM/events/T1/20261106T2052Z-T1-chat-actual-variant-comparator-e28c.json`.

## Confirmed true GPU result across two exact pinned runs

Original baseline [42289238865](https://github.com/alwansan/raf/actions/runs/42289238865) job `128138000484` compared SHA ZIP2 direct SPIR-V Vulkan original vs original-derived Unity2021.3.45f2 OpenGLCore HLSL: source and butterfly CopyInput GPU identical (0/32768 mismatches), 64/256/64 keyed reads, coordinate differences `[63,252,64]` and X-zero collapse `[63,252,63]`; pass0 63/64 and pass1 31/32 pixel differences.

Independent already running T1 counterfactual [42290211798](https://github.com/alwansan/raf/actions/runs/42290211798) job `128141366121` finished **COMPLETED FAILURE at expected final numeric parity guard**, but actual Unity GPU import, dispatch, direct original Vulkan, SHA identity, NUnit completion and privacy cleanup **succeeded**. Only ephemeral slot0 original-SPIRV->HLSL **source ImageFetch integer-source** lineage was rewritten; original reference untouched. Its source and butterfly CopyInput still 0/32768 mismatch. Keyed site mismatches became **`[0,252,64]`** (x zero collapse `[0,252,63]`, site2 Y zero 64). Thus site0 improved by **-63/64 mismatches** and fully matches original in coordinates, while butterfly sites1 and2 unchanged and pass0/pass1 pixel mismatches **63/64** and **31/32** unchanged. This is actual meaningful partial repair, **NOT** full FFT parity, no original authored in-game FindKernel or Android Adreno proof, and **NOT** causal evidence of FTZ.

## Independent durable tool

- [Safe actual GPU run-delta parser](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/t1_fft_real_gpu_variant_delta_gate.py) [3cd1c9e](https://github.com/alwansan/raf/commit/3cd1c9e175038c99c1914493138970f34bbd88db): reads two different bounded actual CI log files locally and admits only fixed public markers, exact original/Unity trace source stage and SHA-producer flags, C# `complete`, 0/32768 GPU CopyInput, 3 keyed-site counts, actual numerical drift. Emits only safe coordinate-mismatch aggregates, never original shaders/pixels/hash values/identifiers. **Logs are unsigned; this tool alone cannot independently attest compiled shader binary or source zip identity.**
- [13 adversarial source-only tests](https://github.com/alwansan/raf/blob/feature/android-native-port/tests/test_t1_fft_real_gpu_variant_delta_gate.py) [dabf164](https://github.com/alwansan/raf/commit/dabf16484518cd1fa402a65d4357f6ca51cea94d), plus existing FFT diagnostics.
- [T1 paired diagnostic source-only workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t1-fft-paired-diagnostic-checks.yml) [b8d823a](https://github.com/alwansan/raf/commit/b8d823a86ac9d5c300f7f02dfaa5e75de915cb01) **[42292770357 SUCCESS](https://github.com/alwansan/raf/actions/runs/42292770357)** job `128150192350`, 13/13 new tests passed; additional existing suites passed. No new Unity/native dispatch.

## Specific next action

Use actual original SPIR-V source-authenticated butterfly site1 X reaching-store and HLSL Phi CFG lineage to propose separate *source-preserving* two-butterfly-site integer-coordinate transformation. Preserve old bitcasts/CFG/branches and original roles, build source-only adversarial semantic gates, then test isolated real Unity/Vulkan pinned inputs. Only after entire FFT pass numeric match and original game authored kernel/dispatch mapping is verified consider production shader fix and owner Android test. **Do not relabel partial site0 coordinate repair as water restored.**
