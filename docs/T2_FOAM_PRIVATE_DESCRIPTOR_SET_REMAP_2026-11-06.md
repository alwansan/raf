# T2 Foam — source-authentic PRIVATE fragment DescriptorSet-only SPIR-V remap (2026-11-06)

**Scope:** isolate compiler-generated Vulkan descriptor layout collisions without ever modifying Raft game assets. **WATER-001 OPEN / NOT_READY**.

## Genuine source and result

ZIP2 immutable source commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; SHA-pinned `Raft_Data/sharedassets0.assets` exactly 115,978,112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; original Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.

Previous [CI42149571827](https://github.com/alwansan/raf/actions/runs/42149571827) found **four real compiled SPIR-V descriptor-class collisions** between VS/FS in final 9731-byte private two-pass Foam ShaderLab: two per pass. Prior original shader sources/4 compiled stages, 2 pass states, original authored Texture/Vector and VS→FS numeric varyings source-authenticated.

New isolated `scripts/t2_foam_private_descriptor_set_remap.py` parses SPIR-V word lengths and `OpDecorate` decorations, cross-checks original reflection numeric (set,binding) and optional `id`, then **changes only the DescriptorSet literal operands** for fragment descriptors to a set unused by the Vertex stage. It compares all other original words bit-for-bit, including opcode operands, Binding decorations and SPIR-V variable IDs, verifies stage original descriptor classes, buffer sizes, array dimensions and numerical Binding after relocation, then reruns `spirv-val --target-env vulkan1.1` on both new private Fragment binaries.

[Original CI42151620701](https://github.com/alwansan/raf/actions/runs/42151620701), job `127675958430`, **SUCCESS**. All **67 source-free controls** passed (17 properties + 10 embedded stage + 14 varying + 14 descriptor conflicts + 12 relocation). SHA-original 4 stage programs validated and 2 remapped Fragment binaries separately validated.

| Genuine original compiled pass | Descriptor-type conflicts before | Fragment DescriptorSet literals relocated | Descriptor-type conflicts after | Shared numeric set/binding after |
|---|---:|---:|---:|---:|
| 0 | 2 | 11 | **0** | 0 |
| 1 | 2 | 3 | **0** | 0 |
| **Total** | **4** | **14** | **0** | **0** |

The test does **not** alter shader source, translated HLSL text or any actual game `.shader/.meta` files, nor upload private ShaderLab/SPIR-V/HLSL or original assets.

## Correct failure diagnosis before success

- [CI42150881209](https://github.com/alwansan/raf/actions/runs/42150881209) failed because the new verification demanded optional SPIRV-Cross resource `id`; no source shader failure proved.
- [CI42151101013](https://github.com/alwansan/raf/actions/runs/42151101013) generated a sanitized error code showing that same optional `id` absence.
- Replaced name/order/id guessing with a fail-closed **one-to-one numeric join of actual SPIR-V OpDecorate (set,binding) variables and reflected descriptor coordinates**, using optional supplied IDs only as additional checks. [CI42151534584](https://github.com/alwansan/raf/actions/runs/42151534584) then exposed one synthetic test's outdated call signature; corrected.
- Final successful code commits [8977b907](https://github.com/alwansan/raf/commit/8977b90757f6b966690e85a2a88cab23488517c2) and [46365076](https://github.com/alwansan/raf/commit/463650761b805f75bec149e0e39efadd4899017a). Source/negative fixtures fail closed rather than silently remap unknown resources.

## Critical integration boundary

These results prove **only a valid private Vulkan stage descriptor layout rewrite**. Whole-fragment relocation also moves Fragment CB0 away from the Vertex set, so a real game integration must authenticate **both** CB upload paths and the non-authored `Material.SetTexture`/sampler descriptors. A minimal conflict-only relocation might retain CB0 at its original coordinate, but original and reflected CB0 block byte extents differ between stages and CB member identity is not proven; it requires a separate experiment, not a guessed fix.

Unity 2021 shader importer behavior, actual material descriptor allocations, original CB0 data/member upload, original texture contents, Android/Adreno frames and water pixels remain **unverified**. The project is **NOT_READY**, WATER-001 remains **OPEN**. Preserve audio, Settings, scenes, save, .meta/GUID and other T agents' workflows.
