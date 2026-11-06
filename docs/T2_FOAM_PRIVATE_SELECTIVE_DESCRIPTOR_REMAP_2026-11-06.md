# T2 Foam — SHA-original PRIVATE minimal descriptor conflict-only relocation (2026-11-06)

## Source-authentic compiled results

- Source-original pinned ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; `Raft_Data/sharedassets0.assets` 115,978,112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Earlier original [CI42149571827](https://github.com/alwansan/raf/actions/runs/42149571827) found **four Vulkan descriptor-type conflicts** in the fully assembled private 9731-byte ShaderLab's stage pairs (2 per pass), despite exact 3/3 and 2/2 VS→FS varying ABI matching.
- Original [CI42151620701](https://github.com/alwansan/raf/actions/runs/42151620701) removed all four conflicts using 14 Fragment-only SPIR-V `OpDecorate DescriptorSet` literal rewrites, preserving binary words otherwise and validating Vulkan1.1. But that initial approach moved every Fragment CB0 away from Vertex's numeric descriptor coordinate.
- New [commit 143ae134](https://github.com/alwansan/raf/commit/143ae1345a0bb222dba1cefe7bc82bf80da47bfa) adds an independent **collision-only** selection branch to the *same existing T2 private pipeline*. It derives exact numeric incompatible descriptor pairs from separately reflected authentic stage classes/arrays. It rewrites only those Fragment binary `OpDecorate DescriptorSet` numeric literal operands, changes nothing else including original Binding and SPIR-V variable IDs, then independently checks new reflection preserving original type, array shape and CB buffer extent.

[Real SHA-original CI42153150468](https://github.com/alwansan/raf/actions/runs/42153150468), job `127680946875`, **SUCCESS**. Source-free negative/positive controls: 17+10+14+14+16 = **71 passed**. All four actual original stage SPIR-V modules compiled and validated, and both separately modified private Fragment modules passed `spirv-val --target-env vulkan1.1`.

| Actual private compiled property | Whole-Fragment experimental remap | NEW collision-only remap |
|---|---:|---:|
| Resource-type conflicts before | 4 | 4 |
| Fragment DescriptorSet literal edits | 14 | **4 (2 per pass)** |
| Descriptor-type conflicts after | 0 | **0** |
| Compatible-class CB numeric bindings retained | 0 | **2 (1 each pass)** |
| CB reflected block-size mismatches still present | not shared after remap | **2 (1 each pass)** |
| Independent modified Fragment `spirv-val` | 2/2 | **2/2** |
| Other SPIR-V words, Binding numbers or variable IDs modified | none | **none** |

The selective approach is an improved *private source-backed interface experiment*, **not a Unity shader fix**. Preserving a CB0 descriptor *number and class* is not equivalent to establishing the same original constant-buffer members, byte offsets, upload path or data. The two CB extent mismatches remain high-priority source/runtime blockers. Original ShaderLab compiler acceptance in Unity2021, actual `Material.SetTexture` objects and Sampler/CB0 upload, device Adreno pixels and water fidelity have not been tested. No game .shader/.meta/GUID, scenes, saves or other agents modified; all original sources and private SPIR-V/HLSL erased before publishing only safe counters.

**WATER-001 remains OPEN, game NOT_READY.** Next: original CB0 field/member byte-layout verification and Android-side buffer upload, real Unity ShaderLab import, and phone water capture with T1 FFT/T5 integration.
