# A1 authentic FFT software Vulkan numeric experiment

Registered 2026-11-03T14:50:31.560Z, identity raft-20261103T145000Z-a1c92f74, session A1-20261103T145000Z-49bf82e0, resumed from paused A1 raft-20261103T120720Z-a1e4f6c9 on live HEAD af85dde964781ce6d392e3977520e63005d1d538.

Reviewed live permanent owner prompts, AGENTS, latest STATUS/handoff, docs/APK_BUILD_READINESS, coordination protocol and prior A1 and W1/FFT CPU2D results. Peer W1 owns original graphics pass reconstruction and Depth Copy; separate a81c6e42 owns FFT precision policy, 4e91b2cd original CPU FFT oracle. This A1 scope is *isolated Vulkan-on-CPU executable original compute* not W1 ShaderLab, CPU-only FFT arithmetic oracle, or native APK. Other workflow owners and scheduled tasks untouched.

Hypothesis: A1 SPIR-V opcode/SSA structural differences (0/20 profiles matching) and typed-image declaration differences (0/20) might be checked numerically by running authenticated original vkd3d-generated Vulkan SPIR-V and HLSL-roundtrip/SPIR-V on identical deterministic sampled images with compatible storage image formats, **without ever publishing original shader bytes or outputs**.

Plan: original-verified 3-LFS owner private isolated workflow, lavapipe/llvmpipe software Vulkan on x86 only. Synthetic shader executable check first; then 20 auth originals or bounded subset. Explicitly test descriptor/image formats, shaderStorageImageWriteWithoutFormat, dispatch capacity and at-least-one-written pixel. Record discrepancies/error codes; negative controls and synthetic reference output, compare only defined writes; never infer GPU Adreno or source shader equivalence from one input. If CPU driver/format/feature unsupported fail closed and report, no readiness false positives.

No Unity Editor, APK/OBB/XAPK, user-device release, new native request, original asset/GUID/.meta/.rgd modification, LEFT Mouse0/500ms/UGUI/controller changes, CL write, or schedule edits. WATER-001/RENDER-002/FFT-FORMAT-009 OPEN, project NOT_READY, 0/3.
