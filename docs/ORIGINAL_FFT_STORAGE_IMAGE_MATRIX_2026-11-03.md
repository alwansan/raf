# Original FFT storage-image format compatibility — 3 November 2026

Scope: authenticated original CSharp9, bounded CPU-only tests, SPIR-V/Vulkan format contract. No Unity, original game asset replacement, GPU dispatch, APK or release.

## Executed code and evidence

- New original cache source inventory [commit10d38455](https://github.com/alwansan/raf/commit/10d384554d00affdc170082625a5c692efdd3fd0), [CI41562582726](https://github.com/alwansan/raf/actions/runs/41562582726) SUCCESS. Privately scanned 2,394 CSharp9 original sources, uniquely found RenderTexturesCache SHA256 4157076c3e4bddc27ac5b24da768d29ff9e6c227c4da07a9e2f55ae9ff6b8245. Exactly one five-argument RenderTexture allocation, one enableRandomWrite assignment, one Create call, one filterMode assignment in this class. No separate RenderTexturesSet class definition; not evidence of a missing file.
- SHA-pinned cache format lineage [commit3452a898](https://github.com/alwansan/raf/commit/3452a898f5787e75a75c08b7acff52a851a9ce3e), [CI41562995693](https://github.com/alwansan/raf/actions/runs/41562995693) SUCCESS: constructor fourth argument is a direct lexical reference to RenderTextureFormat-typed declaration (zero lexical hops); fifth argument includes Linear/sRGB modes. A true-literal enableRandomWrite assignment exists, but the branch in which it executes is not proven. All original source probes and the 194,887 baseline butterfly numeric checks passed.
- Source-correlated compatibility matrix [commit9d98f43c](https://github.com/alwansan/raf/commit/9d98f43c75eeec1ad75fd0e34625a441a13446c0), [CI41563298155](https://github.com/alwansan/raf/actions/runs/41563298155) SUCCESS. Verifies SHA-pinned original GpuFFT and RenderTexturesCache, four channel/precision modes, and guarded Vulkan/SPIR-V format candidates. The matrix uses the output Rgba32f enum1 established by independent authenticated 20-program [CI41561153253](https://github.com/alwansan/raf/actions/runs/41561153253); it does not re-execute original shader translation or measure GPU output in this managed-source run.

## Source-requested format matrix (expected Vulkan view format only)

| Channel mode | Precision | Original Unity request | Expected SPIR-V typed ImageFormat | Typical Vulkan view |
| --- | --- | --- | --- | --- |
| One | Half | RGHalf | Rg16f / enum7 | VK_FORMAT_R16G16_SFLOAT |
| One | Float | RGFloat | Rg32f / enum6 | VK_FORMAT_R32G32_SFLOAT |
| Two | Half | ARGBHalf | Rgba16f / enum2 | VK_FORMAT_R16G16B16A16_SFLOAT |
| Two | Float | ARGBFloat | Rgba32f / enum1 | VK_FORMAT_R32G32B32A32_SFLOAT |

Original translated DXBC SPIR-V storage output at set0/binding2 declared ImageFormat Unknown (enum0) in all 20 modules. After HLSL/glslang roundtrip the declared output becomes Rgba32f (enum1) in all 20. Under an image view of the *expected requested format* above, Rgba32f can match only ARGBFloat, not RGHalf/RGFloat/ARGBHalf. This flags a concrete restoration-contract risk, NOT measured incorrect pixels: Unity's actual image view format, engine fallback/conversions and active original mode have not been captured.

Using Unknown for written storage images may require shaderStorageImageWriteWithoutFormat and per-format support, whereas typed Rg16f and Rg32f use StorageImageExtendedFormats. Validate corresponding Vulkan format features and actual Android GPU/Unity backend before choosing an implementation. The original shader write/read instruction/feature use needs further authentic inspection.

Official technical references: [SPIR-V Image Format enumerants](https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html), [Vulkan formats and formatless storage features](https://docs.vulkan.org/spec/latest/chapters/formats.html), [Unity RenderTextureFormat](https://docs.unity.cn/ScriptReference/RenderTextureFormat.html).

## Unresolved, fail-closed

- Reconstruct the full authentic FFT kernel-to-program identity, both passes, materials and original GUID linkage. Strict water gate remains false.
- Identify actual runtime image view formats, texture lifecycle/memory and compute GPU features, along with format-dependent rounding and output numerical agreement; format analysis alone does not validate the GPU.
- Finish existing RENDER-002, LOCAL-005, AUDIO-004, INPUT-006, DISPLAY-003 and PERF-007 source/integration reviews. Source-only CI is not a new APK test.

Build state NOT_READY. Under the owner's new rule there are 0/3 complete independent full candidate readiness audits, because no candidate with all pre-build blockers closed exists. No Unity/native APK/OBB/XAPK or release was launched; no scheduled tasks, original LFS assets or game .meta/GUID/.rgd were changed.


## Original cache lifetime API and bounded memory estimate

[Source/test commit0effd8f1](https://github.com/alwansan/raf/commit/0effd8f1698e1769c055148c8d6ef7b09e874f18) and [managed CI41563786696](https://github.com/alwansan/raf/actions/runs/41563786696) COMPLETED SUCCESS. The same pinned RenderTexturesCache source SHA 4157076c3e4bddc27ac5b24da768d29ff9e6c227c4da07a9e2f55ae9ff6b8245 has bounded lexical API counts: 1 new RenderTexture,1 Create,2 Release,2 Dispose,2 Destroy,1 Clear,0 Remove and2 GetCache references. This refutes an assertion that the original class contains no cleanup APIs, but neither proves their runtime reachability nor rules out a leaked reference/texture. Separate existing original Dx11FFT exception-lifetime managed harness is not a RenderTexturesCache actual device lifetime test.

Using source-requested dimension 2N×2N and conventional uncompressed format bytes per pixel, ONE requested N=512 target consumes RGHalf 4 MiB, RGFloat 8 MiB, ARGBHalf 8 MiB or ARGBFloat 16 MiB before padding, alignment, mipmaps and driver allocations. Verified stored quality maximums are32,64,256,512,512,256,256, not proven active device size. The number of simultaneous render targets, allocations caused by the engine and exact GPU heap impact remain UNKNOWN. Do not reduce resolution/quality or diagnose the historical phone OOM from these single-target estimates.

PERF-007 stays SOURCE_REVIEW_REQUIRED and water/format blockers remain OPEN; the actual CPU-only CI did not run Unity or phone GPU.


## Authentic FFT formatless-write experiment — 3 November 2026

[Original 20-program operation probe 41564682850](https://github.com/alwansan/raf/actions/runs/41564682850) COMPLETED SUCCESS on source 59a4a13b. All twenty SHA-authenticated DXBC programs translated to SPIR-V declare StorageImageWriteWithoutFormat capability 56, contain one OpImageWrite and three OpImageFetch per program, and use an Unknown-format storage image. The HLSL/glslang roundtrip instead declares Rgba32f and removes capability 56, with image-operation counts unchanged. No device feature support or numeric output proven.

[Temporary repair source f2507f00](https://github.com/alwansan/raf/commit/f2507f00bf8e7bcbf5aaf312a7b462b9f82aff31), [original program CI 41565279755](https://github.com/alwansan/raf/actions/runs/41565279755), job 125685201003, COMPLETED SUCCESS: a fail-closed, private-only experiment restores ImageFormat Unknown and OpCapability56 in each translated output, verifying 20/20 original typed-image declarations and 20/20 Vulkan1.1 spirv-val checks. Modified SPIR-V files exist only in private CI temporary directories and were never staged into game assets or published. This is structural restoration, NOT GPU numerical equivalence, original Unity runtime kernel identity, correct game water, or Adreno feature proof.

[Format classification fix 298faf7a](https://github.com/alwansan/raf/commit/298faf7aa6ad7879dbd9cb0a53e411cce0a9bcae) passed [managed source CI 41564904076](https://github.com/alwansan/raf/actions/runs/41564904076). SPIR-V StorageImageExtendedFormats capability is different from Vulkan shaderStorageImageExtendedFormats device feature: RGFloat has Vulkan core-mandatory storage format support, RGHalf may require individual format query when the extended-format guarantee is absent. See [Khronos features specification](https://docs.vulkan.org/spec/latest/chapters/features.html).

NEXT: test genuine numerical FFT GPU/shader outputs and resource-format dependence; correlate runtime kernel mapping and authentic multi-pass ShaderLab programs. Do not fake kernels, toggle strict water gate or claim actual GPU execution. WATER-001, RENDER-002, FFT-FORMAT-009 remain OPEN; readiness NOT_READY, complete immutable candidate audits 0/3, no APK/OBB/XAPK request. No changes to original assets, GUIDs, save content or existing scheduled tasks.
