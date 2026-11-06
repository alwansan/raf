# T2 Foam — original completed ShaderLab Vulkan vertex/fragment numerical ABI (6 November 2026)

**Scope:** WATER-001 source-authentic CPU/CI-only evidence, NOT recovered water pixels.

## Genuine SHA pinned source and new positive evidence

- ZIP2 immutable source \`15964ea8f246b6e076ce26b60931ee2e1a9a2385\`; original owner \`Raft_Data/sharedassets0.assets\` **115,978,112 bytes**, SHA256 \`0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3\`; genuine original Foam Shader PathID 2420 raw SHA256 \`67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1\`.
- Prior T2 exact original source proof: two authored Shader properties (Texture+Vector), two original pass states and four translated programs, actual source-derived DXBC shader-model levels. Built **9,731-byte private two-pass ShaderLab**, with complete embedded HLSLPROGRAM bodies. [CI42144036981](https://github.com/alwansan/raf/actions/runs/42144036981) independently recompiled and SPIR-V validated four embedded stage variants.
- New isolated code [a0534d22](https://github.com/alwansan/raf/commit/a0534d22bc6bb32f12834acf736e565cd65d8a80) adds \`scripts/t2_foam_embedded_stage_io.py\`, targeted tests and an isolated T2 workflow extension. Instead of validating stage binaries **independently only**, it now obtains *private* \`spirv-cross --reflect\` JSON from the **actual compiled four original candidate stage binaries** and checks Vertex output signatures against Fragment input signatures per pass using unique (location,component) keys and exact scalar/vector type and array shape. Typed builtin inputs without locations are separately excluded, no guessed semantic mappings.
- Original [CI42146401691](https://github.com/alwansan/raf/actions/runs/42146401691) **SUCCESS**, job 127658818302: prior 17+10 and **14 new** synthetic anti-spoof controls (total **41**), original SHA owner and source code reconstruction succeeded; final assembled 9,731B ShaderLab stages compiled and \`spirv-val --target-env vulkan1.1\` passed 4/4. Numeric VS→FS varying ABI:
  
| Original pass | VS numeric outputs | FS numeric inputs | matched location/type/array | missing | incompatible |
|---|---:|---:|---:|---:|---:|
| 0 | 3 | 3 | **3/3** | 0 | 0 |
| 1 | 2 | 2 | **2/2** | 0 | 0 |

Thus a numeric SPIR-V cross-stage varying-location/type mismatch is **not** the current blocker for these authentic reconstructed stage pairs.

## Constraints and remaining blockers

The test establishes only interface identities in one Vulkan 1.1 SPIR-V code-generation path. It **does not establish** interpolation semantic identity, primitive topology or original D3D11 pixel parity, real Unity 2021 ShaderLab importer acceptance, original CB0 member alias/data upload, runtime \`Material.SetTexture\` Texture value/receiver validity, or Android/Adreno drawing. Source-authentic prior Mono.Cecil findings for the four non-authored texture setter name arguments are static only, not proof they executed or correctly populated material textures. No proprietary ShaderLab/HLSL/SPIR-V, compiled original binaries, real source names or private varying numbers were uploaded; original assets and private shader scratch deleted, no game .shader/.meta/GUID modified.

**WATER-001 remains OPEN and game water NOT_READY.** Next T2: connect authentic original CB0 and all four dynamic Texture values to generated HLSL resource slots and the real Unity material receiver, then run an isolated Unity2021 ShaderLab import and device water pixel test coordinated with T1 FFT/T5 integration. Preserve working sound/Settings and non-target platform code.
