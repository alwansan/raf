# T2 Foam — original translated two-pass Vulkan descriptor-layout collisions (6 Nov 2026)

**New source-authentic negative evidence**: [CI42149571827](https://github.com/alwansan/raf/actions/runs/42149571827) **SUCCESS**, job `127669230458`; code [375ade37](https://github.com/alwansan/raf/commit/375ade378ae990cdcbd06274fa25358d76e98c04).

## Exact source and test

- Immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; authenticated `Raft_Data/sharedassets0.assets` 115,978,112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- B20 original 4 translated stages+2 genuine states, original authored Foam 1 Texture+1 Vector, original exact DXBC stage model: reconstruct private **9731-byte complete ShaderLab**. Extract two true embedded HLSLPROGRAM sections; compile all 4 stage variants and validate SPIR-V Vulkan 1.1. `spirv-cross --reflect` stage descriptors are compared by private numeric (set,binding) keys, descriptor class, array dimensions and CB byte extent. Original labels and private numeric keys are never printed.
- All **55** tests pass (17 properties + 10 embedded compiler + 14 varying + 14 new descriptor adversarial tests). The source-derived classification is a **negative result** despite workflow SUCCESS, not a recovered water fix.

| Reconstructed original pass | Vertex descriptors | Fragment descriptors | same numeric set/binding | conflicting resource class | shared CB range difference |
|---|---:|---:|---:|---:|---:|
| 0 | 3 | 11 | 3 | **2: Uniform Buffer vs Sampler** | 1 |
| 1 | 3 | 3 | 3 | **1: Uniform Buffer vs Sampler; 1: Uniform Buffer vs Sampled Image** | 1 |

**4 Vulkan descriptor-type conflicts total** across the two passes; no descriptor array-shape conflicts. Per-stage SPIR-V validator and earlier VS↔FS varying match (3/3 and 2/2) cannot catch these. A single unchanged Vulkan per-pass descriptor-set layout cannot assign two descriptor types to the same (set,binding). The two CB byte extents also differ, but are a separate warning and **not themselves** proven descriptor-type-invalid.

## Proof limits and next steps

This establishes a real issue for the **current glslang-generated private SPIR-V stage pairs**. It does not prove that Unity2021 compiles/links them using identical conflicting assignments, which it may remap, nor that this is sufficient to explain black or missing water on a particular Android phone. A controlled binary-only private DescriptorSet-decoration remap with strict source-equivalence and four fresh spirv-val checks is a useful next experiment; actual Unity ShaderLab import, CB0 size/layout and Material texture upload have separate unsolved source/runtime contracts. No original game shader, GUID/.meta/scenes, compiled proprietary binaries or raw private HLSL was committed. Scratch erased after workflow.

**WATER-001 remains OPEN; game NOT_READY**. Source-only success does not mean GPU pixels, water fidelity or phone readiness.
