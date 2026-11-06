# T1 — SHA-original translated HLSL butterfly1 X Phi incoming values and branch predecessors

- session_id: 20261106T131603Z-T1-chat-hlsl-phi-inputs-a71e
- origin: chat
- issue_id: WATER-001 (OPEN)
- status: waiting_ci
- base_sha: 727a15ef97b3b498c4353fcbcdd49f650fbc0eb2
- resumed_from_sessions: 20261106T130729Z-T1-chat-pair-gate-6c2e; 20261106T125645Z-T1-chat-hlsl-x-stop-a93d; 20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3
- scope_commit: 1ce09e9c248739c788ea2fc40eff358d1da7f112
- source_commit: 5ebf7411b03302a12ea9bed9bb87c45c06f933c6
- test_commit: 6f5f8ad8a22094eb33ede0d4ad795c3433c1ac58
- workflow_commit: b801e7cb8f9c9c3f4777aae9995d5505ee6c44f1
- run_urls: https://github.com/alwansan/raf/actions/runs/42224533880
- work: prompt/coordination/work/WATER-001/T1-20261106T131603Z-T1-chat-hlsl-phi-inputs-a71e.json
- experiment_key: water001-sourcepin15964ea8-translated-butterfly1-x-float32-phi-incoming-value-predecessor-classification-v1
- resource_key: t1-fft-vulkan-roundtrip-isolation-ubuntu24-nonunity

## Restored and scoped evidence

Original ZIP2 source pin `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Source-authenticated CI [42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) traced original butterfly1 X signed32 Input vector through two shuffles and an integer-bit-pattern-to-float bitcast. CI [42221700354](https://github.com/alwansan/raf/actions/runs/42221700354) completed success and established that the corresponding HLSL-roundtrip lane at legal coordinate-depth 12 stops at **float32 OpPhi**, not the generic unknown or OpIAdd whole-slice opcode. Independent strict evidence gate [42223419922](https://github.com/alwansan/raf/actions/runs/42223419922) passed 40 source-free tests; this does NOT imply actual GPU parity.

Registered this independent source-private scope after checking no active/queued T1 private source workflow. Added `scripts/t1_fft_hlsl_phi_input_origins.py` and `tests/test_t1_fft_hlsl_phi_input_origins.py`, then source-authenticated existing no-Unity Vulkan workflow call, without touching engine shaders, full Android builds, audio/Settings, or T2–T5 files. The analyzer parses exactly the selected X coordinate lane; rejects malformed Phi input shapes and non-predecessor labels, reports only fixed opcode/type families, bitcast categories and stop reasons, and explicitly marks runtime branch selection and numerical parity as unproven.

## Current CI / acceptance

Run [42224533880](https://github.com/alwansan/raf/actions/runs/42224533880) triggered from workflow commit `b801e7cb`; source-free gate must first pass 13 new tests, then private exact-ZIP2 generated glslang HLSL slot0 candidate must pass. Read ONLY safe `RAFT_T1_FFT_HLSL_BUTTERFLY_X_PHI_INPUTS` JSON marker; never publish raw original bytecode or IDs.

Expected comparison: immediate incoming OpBitcast / OpFAdd / OpLoad / OpPhi, each with predecessor edge family. Actual result may be different and must override expectation. Even a concrete Phi input census is not same-input Vulkan-vs-Unity numerical parity, not authoritative FindKernel binding, not Android water restoration. Keep WATER-001 OPEN.

Next: review CI steps/logs, fix minimal synthetic defect if present, then publish sanitized source-backed Phi inputs in own experiment/event/work and close this independent diagnostic scope. Do not rerun equivalent original heavy test without a changed source question.
