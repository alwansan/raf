# W1 original Depth Copy fragment-operation numerical comparison

This is bounded numerical execution of compute-lifted fragment operations, not an Android render test or full shader equivalence. The actual original ShaderLab reconstruction and Unity compilation evidence are separate reports.

## Method

Authenticate original owner files and shader2407 objectSHA cf978dad4f4c67e57fb58448cee7a8c033c30d1491ef54b0a6ad887317fba75a. Select actual per-pass serialized fragment programs; privately execute original DXBC→vkd3d SPIR-V→SPIRV-Cross GLSL and reconstructed HLSL→glslang SPIR-V→SPIRV-Cross GLSL after the same bounded compute lift. Original DXBC is not executed on native Direct3D. The two paths share tools and lift assumptions, so agreement cannot exclude their shared defects.

Only ordinary1–2vec2/vec4varyings and one scalarDepth or vec4color output, at most2combined2Dsamplers are supported. Raster-dependent builtins, derivatives, discard, buffers, structured resources or ambiguous interfaces fail closed. The lift injects pixel-centre UVs over31×19, fixedLOD0 nearest-clamp sampled RGBA32F linear images and writes the fragment result into a mappedRGBA32F storage output. It deliberately removes vertex execution/interpolation, actual depth attachment, blending, culling, stencil and render-target precision; resource slots are normalized in the harness, not original Unity property-binding acceptance. Not Unity-compiled bundle bytecode execution.

W1-owned executor is copied/adapted from A1's authored Vulkan harness; A1 files/workflows untouched. CPU physical-device type is required; no GPU fallback. A known8×1 sampled-texture sum canary independently compares mapped output with CPU input sums. Three deterministic asymmetricfields(seeds0,19,257),589pixels each, are compared for each9fragment occurrences, retaining original6+3subshader indices. Positive gate: full output coverage, no nonfinite components, maxAbs≤1e-4 andrelativeL2≤1e-5. All source/binary/pixel data stay private; reports contain only hashes/counts/metrics.20minjob/600s execution, cancel-in-progress:false; cached227511628-byte owner payloads reauthenticated.

## Results and controls

Initial runs41670870564/41671270613/41671567086:0numerical executions, Vulkan initialization failedVkResult=-9 because W1 assumed a fixed ICD filename. Repaired installedlavapipe discovery at9c84dd23; source/compiler lifting already succeeded. These are inconclusive harness failures, never shader discrepancy evidence.

[Run41672073080](https://github.com/alwansan/raf/actions/runs/41672073080) at9c84dd23 executed all9fragment occurrences,27positive comparisons: all maxAbs=0, relativeL2=0, no nonfinite or coverage mismatch. Known sum canary passed. All9arithmetic+0.25 and9wrongUVaxis controls differed. Resourceexchange differed for3singletexture occurrences but not6two-texture occurrences: this specific negative is nondiscriminating, consistent with symmetric merging but not an independent semantic proof. CI correctly remainedFAILED; no acceptance claimed. Keep that failed record.

Next source0eae48c39c620f05d678705cdcb5198b9955c6da changes only resource-negative design: alias both two-texture inputs toimage0; forsingletexture sample wrongimage1. [Successor run41672408152](https://github.com/alwansan/raf/actions/runs/41672408152) must actually detect all9resource negatives before bounded acceptance. It retains all27positive and18other negative comparisons, rather than waiving failed controls.

## Remaining

NaN/Inf, half/two-channel view formats, implicit derivatives/LOD, filter settings outside nearestclamp, vertex clip/depth conventions, all9fixed-functionpasses, Unity/propertybinding/keywords and POCO appearance remain unproven. No original authored source recovered and no original game.shader/.meta/GUID/material replaced. Do not flatten6+3, lowerquality or close WATER/RENDER/FFT. NOT_READY0/3. After successful bounded comparison, next independent question is real raster/depth/resource-binding behavior and GUID-preserving project integration before device build via separate lane.


## Final bounded result — verified live

[Exact source0eae48c3](https://github.com/alwansan/raf/commit/0eae48c39c620f05d678705cdcb5198b9955c6da), [run41672408152](https://github.com/alwansan/raf/actions/runs/41672408152), job126043952039 **COMPLETED SUCCESS**. All9original fragment occurrences executed across3asymmetric inputs: **27/27positive matches, maxAbs0/relativeL2=0**, no nonfinite or coverage mismatches. Each comparison wrote all589pixels. Known8×1CPU sum canary passed. **27/27negative controls detected**:9arithmetic mutations,9UV-axis swaps and9wrongresourcealias/wrongimage controls. The prior symmetric-exchange failed control remains preserved rather than counted as acceptance. Aggregate-only artifact13248597343, transport digest6fcaa31c7cc41afb30609eb8446c6eafa5eec6cbbcf2a40eaecc33d131f41ac6.

This narrows equivalence to the explicitly described compute-lifted fragment workloads. It does not prove rendering, actual Unity input/property/sampler bindings, vertex/depth conventions, NaN/Inf behavior, other formats/filtering or Android/POCO appearance. Reconstructed ShaderLab has also separately passed actual Unity import/AndroidVulkan bundle compilation; there is still no production game shader integration. Next measure real raster/depth output with exact original bindings and asymmetric vertex/UV geometry before GUID-preserving integration. No further equivalent compute repeats are warranted without a new failure or changed source.
