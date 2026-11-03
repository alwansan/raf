# W1 actual Depth Copy raster and depth comparison

[Exact source41ba9a1d](https://github.com/alwansan/raf/commit/41ba9a1d9d904f017dae82088f1e32375a402ade), [run41675980141](https://github.com/alwansan/raf/actions/runs/41675980141), job126056576894 **COMPLETED SUCCESS**. Earlier [3275ed01/run41675126618](https://github.com/alwansan/raf/actions/runs/41675126618) also passed the actual graphics workload; final source adds mandatory Khronos Vulkan API and synchronization validation rather than accepting arithmetic-only or invalid-API output.

## Proven result

All9original pass occurrences were drawn independently, retaining original subshader6+3indices. **27/27paired color+depth images match**, maxRGBA absolute difference0, maxD32 absolute difference0, no nonfinite components or coverage mismatch. All589pixels in each31×19 framebuffer are compared, including404clear pixels and185actually changed pixels. This is actual vertex+fragment graphics-pipeline execution on Mesa CPU Vulkan, not the prior compute lift. **36/36negative controls detected**:9wrongUVaxes,9mirrored input clip geometry,9depth comparisonNever and9wrongresourcealias/wrongimage bindings. No negative-control gate was waived.

An independently authored constant-color(0.2,0.4,0.6,0.8)/fragment-depth0.25canary wrote188pixels and matched known CPU expectations, with geometry/depth negative controls detected. **Khronos API and synchronization validation enabled**,0errors and0warnings in the reported positive cases and canary. Every negative executor also requires0validation errors before its result is accepted.3/3independent SPIR-V binding fixtures pass locally and on this exact CI source, including wrong resource register, missing descriptor decoration and malformed instruction rejection. Aggregate-only artifact13251030678 (1406bytes), transportSHA2563fa7a10cafb48a284348ee1db0925150dad9ef67b23fc3a8d0278dd8af3fc098.

## Inputs and method

Before parsing, verify original resources.assets111533516bytes/SHA87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c and sharedassets0.assets115978112bytes/SHA0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3 using the existing exact two-owner LFS cache. Original Shader pathID2407 objectSHAcf978dad4f4c67e57fb58448cee7a8c033c30d1491ef54b0a6ad887317fba75a. No original resource is altered or exported as an artifact.

The reference path executes original DXBC translated byvkd3d into SPIR-V. The candidate executes recovered HLSL after **actual serialized texture/sampler-property rebinding and original POSITION/UV semantic restoration**, recompiled byglslang. No fragment-to-compute rewrite occurs. Each original/rebuilt VS/FS pair keeps its own compatible varying locations, so the previously observed varying renumbering is not mistaken for a semantic failure.

Resource decorations are normalized into the test descriptor layout by originalt/sregister identity for the reference and exact serialized property names for the candidate, never declaration order. The bridge rewrites SPIR-V Binding/DescriptorSet decorations by the identified variable IDs and validates resulting SPIR-V. This exercises the authored property-rebinding mapping, **not Unity's automatic runtime material/global binding machinery**. Sampler/image slots are test layout slots; original names remain private.

Draw one asymmetric triangle with nonuniform clipW, nontrivial UVs,31×19viewport and3deterministic asymmetric finite imagefields(seeds0,19,257); depthclear0.21/0.61/0.91. Inputs are linearRGBA32F2D nearest-clamp sampled images, outputRGBA32Fcolor and optimalD32_SFLOATdepth with explicit depth-image-to-buffer readback and host-visible coherent mapped color. Supported original state is explicitly verified before pipeline creation: original color mask, ZWrite, ZTest(inherit0→defaultLEqual) and ZClip; original CullOff, neutral blending/bias/stencil and alpha-to-coverageOff are required rather than guessed. Serialized dynamicFog remains in recovered ShaderLab but is not evaluated by this Vulkan harness. Unexpected resource/interface/state classes fail closed.

Both paths share translators, serialization assumptions and CPU driver; agreement does not exclude common defects. Native original Direct3D execution is not available in this experiment. Compiler validation contents and original shader/property/vertex/pixel payloads remain private; debug callbacks retain counts, not raw messages. Independent W1 workflow/group cancel-in-progress:false,25minute total/600second execution cap; no Unity import, Player/APK/OBB/XAPK or release in this experiment.

## Classification and limits

| Category | Evidence |
|---|---|
| Authenticated original | Exact owner/object bytes, serialized pass/state/resource metadata and original DXBC linkage |
| Reconstructed implementation with bounded equivalence | RecoveredHLSL/ShaderLab: actual Unity2021.3.45f2 AndroidVulkan bundle compilation41663393724; compute-lift27cases41672408152; actual raster color/depth27cases and36negative controls41675980141 |
| Still unproven | Complete real Unity material/global/sampler binding and subshader selection, actual staged-projectGUID integration, other filtering/view/half formats, NaN/Inf, full-game interaction, Adreno Vulkan/OpenGLES and POCO appearance |

No production shader/.meta/GUID/material is changed. NOT_READY0/3; WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN. W2's Linear-color metadata and W3's full1556-material reference inventory are separate lines of evidence; this shader result does not repair every pale surface or particle/fire material.

## Precise next step

Install the authenticated regenerated Depth Copy wrapper into its **actual exported identity/path**, preserving existing .meta/GUID bytes and all references, with a private outside-project backup and rollback on any failure. Inspect the real stage's export/provenance first; do not infer a GUID from the small historical107subset or fabricate a fresh GUID. The real native staging boundary is RUNNER_TEMP/project/ExportedProject in raft-unity-editor-android-import.yml, before copy tounity-candidate. Existing strict builtin identity failure must not be weakened to test this one shader. Use a W1-isolated source/staging validation, no shared request or fullAPK. Then run a bounded Unity integration/render check with original caller pass indices and resource bindings; remaining hardware acceptance belongs to the later separate device build lane. No repeat of equivalent arithmetic/raster workloads is needed absent a new source change or failure.

## Tool versions from exact CI

UnityPy1.25.4; glslang-tools	15.1.0-2~ubuntu0.24.04.2; libvulkan-dev:amd64	1.3.275.0-1build1; mesa-vulkan-drivers:amd64	25.2.8-0ubuntu0.24.04.4; spirv-cross	2021.01.15+1.3.239.0-1build1; spirv-tools	2025.1~rc1-1~ubuntu0.24.04.2; vkd3d-compiler	1.2-15build1; vulkan-validationlayers:amd64	1.3.275.0-1.
