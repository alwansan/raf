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
