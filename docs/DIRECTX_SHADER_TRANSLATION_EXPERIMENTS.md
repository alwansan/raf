# DirectX / Vulkan shader recovery experiments for the Raft Android native port

**Branch:** `feature/android-native-port` only. **Owner hold still active:** NO Unity Editor import, native Unity/Android build, APK/OBB/XAPK packaging or Release until the owner authorizes one. Do not modify the scheduled automation or either native request JSON. These experiments are CPU-only, no Unity and no LFS.

## What the original evidence establishes

The latest owner phone logs show the real `UltimateWater.Internal.Dx11FFT.ComputeFFT` attempting indices 2 and 6 against a ComputeShader with **zero** imported kernels. Separate original water shader programs expose one pass while gameplay requests indices up to 5. Shader source and correct original pass semantics are missing: neither changing the Adreno GPU model nor reinterpreting an API translation DLL fixes the missing Unity shader asset.

Existing [original source experiment 41521165451](https://github.com/alwansan/raf/actions/runs/41521165451): `Dx11FFT` has 2 `Dispatch` and 6 `SetTexture` calls with 11 `KernelIndex` references, but zero `FindKernel` calls. The original serialized **kernel ordering/index** is therefore critical, not just names or successful compilation.

## Tools, accurate roles, limitations

| Tool | What it actually translates | Relevance | Why not ship directly in the Android APK |
| --- | --- | --- | --- |
| [DXVK](https://github.com/doitsujin/dxvk) | Direct3D 8/9/10/11 runtime calls to Vulkan | Understand original Windows DirectX rendering semantics, DXBC/compute pipeline | Native Unity Android does not call the Windows D3D11/DXGI API; placing DXVK DLLs inside its APK does not restore Unity-serialized shader programs |
| [dxbc-spirv](https://github.com/doitsujin/dxbc-spirv) | Real DirectX compiled DXBC (shader model <=5.1) to IR/SPIR-V | **Directly inspect/translate a verified shader binary** and establish its stage, resources and SPIR-V compatibility | Its upstream README says standalone SPIR-V needs application-specific resource and I/O lowering; its default SPIR-V 1.6 may exceed the 1.1 Vulkan level seen on the Poco F5 Pro in the owner log |
| [VKD3D-Proton](https://github.com/HansKristian-Work/vkd3d-proton) | Direct3D 12 API to Vulkan, plus DXBC/DXIL translation in the shader system | A useful alternative/modern parser comparison for shader behaviour | The original Raft water code uses Dx11FFT rather than D3D12 and VKD3D runtime integration does not repair original Unity asset links |
| Ubuntu 24.04 [vkd3d-compiler](https://manpages.ubuntu.com/manpages/noble/man1/vkd3d-compiler.1.html) | Limited direct conversion for select shader bytecode types | Stable CPU-only comparison on standard GitHub runner | Version 1.2 did not create DXBC from our authored HLSL example, so it must not be described as a working complete HLSL/DXBC route |
| [FEX](https://github.com/FEX-Emu/FEX) + Wine / DXVK | x86/x86_64 userspace execution on ARM64 Linux, Windows APIs through Wine | Separate alternative to run the original Windows app, possibly as a diagnostic reference | Requires an appropriate ARM64 Linux/rootfs environment and Windows compatibility stack; not native Android Unity IL2CPP and neither extracts lost shader source nor fixes original GUIDs |
| [glslang](https://github.com/KhronosGroup/glslang) / SPIRV-Tools | HLSL source -> SPIR-V and SPIR-V validation/disassembly | Validate independent compiler and shader metadata contracts | Does not reconstruct missing HLSL from original commercial Unity compiled shaders |

## Verified experiment 1 — Public synthetic HLSL on CPU

[Actions 41525025301](https://github.com/alwansan/raf/actions/runs/41525025301) **SUCCESS**:

- Original test-owned `tools/shader_bridge_lab/compute.hlsl` compiled by glslangValidator to SPIR-V, passed `spirv-val` at `vulkan1.0`, and retained one compute stage with local workgroup `8×8×1`.
- `vkd3d-compiler 1.2` enumerated DXBC input/SPIR-V target capability, but could **not** produce DXBC from the HLSL fixture. No synthetic DXBC conversion was falsely counted as a success.
- `scripts/probe_directx_shader_bridge.py` and synthetic bytecode tests checked DXBC/DXIL chunk bounds, source privacy, SPIR-V entrypoint and workgroup structural metadata. This is NOT original Raft compilation, nor Android Vulkan execution.

## Verified experiment 2 — Authentic original bytecode without LFS

[Actions 41525570605](https://github.com/alwansan/raf/actions/runs/41525570605) **SUCCESS** on 80 original regular-Git Unity serialized source files:

- `Raft/Raft_Data/sharedassets29.assets` contains genuine `ComputeShader` object **pathID 577**, raw object SHA256 `3c4307f852785a8564f90d68256cebfed575876e70c5c5fda8fd7da77d74cfff`.
- Its raw serialized object contains exactly one structurally verified `DXBC` container with chunks `ISGN`, `OSGN`, `SHEX`, size **460 bytes**, SHA256 `93880946974676dee3a7fa4d56246e7f0808874e1ec0327592acfa382950d099`.
- Three original sources (`resources.assets`, `sharedassets0.assets`, `sharedassets36.assets`) remained Git LFS pointers and were **NOT** decoded. This scan sees only **1 of the 9** original ComputeShader objects found in earlier full-graphics inventory. It does NOT prove the 460-byte shader corresponds to the failing FFT, nor that its shader code is runnable.
- No code bytes, disassembly, compiled source, copyright assets or output artifacts were exported. No Unity or native build.

## Experiment 3 — Pinned open compiler on the authenticated 460-byte shader

The new [separate CI workflow](../.github/workflows/raft-real-dxbc-translation-probe.yml) compiles the exact open-source dxbc-spirv commit `f528e1e821527e361f34829f78d1fbd5340e6f6a` with Meson in the runner, authenticates the original Git shader by object + DXBC SHA256, compares it to Ubuntu's VKD3D compiler and checks each generated SPIR-V against Vulkan 1.1 and 1.3 using `spirv-val`. It publishes **only JSON boolean outcomes and structural counters**; actual original DXBC/disassembly/translated program files remain local temporary data and are deleted.

A DXBC translation reported as successful by a tool is NOT GPU execution, original water kernel recovery, or Unity shader import. If the generated SPIR-V requires Vulkan 1.3, it cannot be assumed to work on the observed Vulkan 1.1 handset. Real shader restoration additionally requires the original serialized kernel indices, shader passes, Unity .meta/GUID identity, material resource bindings and correct game semantics.

## Pending genuine recovery

1. Identify original FFT/water kernel owners among the still-unread LFS `*.assets`, using exact SHA256/source identity and the bounded `scripts/audit_original_compute_metadata.py` reader (no automatic heavy download under current session).
2. Determine whether the actual game exposes full DXBC programs or only platform-specific stripped blobs. Check shader stage, model, binding tables and kernel order; do not invent missing data.
3. Cross-check reliable, appropriately licensed same-version Ultimate Water System sources where obtainable; preserve Unity original GUIDs and expected calls. Never use blank kernels, one-pass fallbacks, wrong-version water assets, or silently disable wave/foam processing.
4. After owner explicitly authorizes a native build, validate GPU capabilities, memory use and correct visual output with device logs. Do not modify the existing owner automation.

