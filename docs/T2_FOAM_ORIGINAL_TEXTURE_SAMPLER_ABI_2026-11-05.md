# T2 WATER-001 — original Foam texture/sampler to translated resource ABI

## Actual source-authenticated finding

Follow-on from [T2 original CB member and name bridge](T2_FOAM_MEMBER_ABI_NAME_BRIDGE_2026-11-05.md). B20/B24/B25 own the genuine two-pass/four-stage Foam program staging; B17 authored the bounded numeric original descriptor canonicalizer. T2 reuses these original-specific verifiers, not their identities.

- Provider: immutable `zip2` source `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; reconstructed `Raft_Data/sharedassets0.assets`, 115978112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original Foam Shader PathID2420 raw object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Actual original source private CI [41939956032](https://github.com/alwansan/raf/actions/runs/41939956032), candidate [da367800](https://github.com/alwansan/raf/commit/da3678009444c212061ea8da72f940687beb25df) **SUCCESS**. Reused four B20 authentic stage translations and the T2 SHA/member inspection, then original stage numeric descriptor tables and `spirv-cross --reflect`. **20/20** member tests + **12/12** resource adversarial tests passed. Output safe artifact `13375033782`, ZIP transport SHA256 `28b2e527316f8e6170aac9b0be628acb76730e816f69a715cb3921d58d66607b` independently downloaded/checked. No raw source, symbols, DXBC, HLSL, SPIR-V or proprietary material uploaded.
- Output source/compiled stage pair cardinalities:

| Pass | Stage | Original `m_TextureParams` | Original `m_Samplers` / `m_UAVParams` | Compiled `separate_images` | Compiled `separate_samplers` |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | Vertex | 0 | 0 / 0 | 0 | 0 |
| 0 | Fragment | 5 | 0 / 0 | 5 | 5 |
| 1 | Vertex | 0 | 0 / 0 | 0 | 0 |
| 1 | Fragment | 1 | 0 / 0 | 1 | 1 |

Across the two fragment programs: exactly **six original texture rows** and **twelve compiled non-CB resources (six sampled images and six separate samplers)**. The translated numeric descriptor slots in SPIR-V set0 are: pass0 image b6–b10, samplers b1–b5; pass1 image b2, sampler b1. No translated non-CB resources in either vertex stage.

**What this does and does not mean:** The two fragment passes each expose one compiled sampled image/sampler pair per serialized original texture *by count*. Original `m_Samplers` table has zero rows; this does NOT mean the compiled program needs no sampler. Current SPIR-V translator emits separate image and sampler declarations; their numeric binding values are the *translation's* interface, not a proven original Unity Texture/Sampler or material property map. They are not necessarily original DXBC registers. The source's sampler modes, texel coordinates, authored textures, alias names, ShaderLab properties, Unity upload and Adreno pixels remain unproven. Counting a pair is not an identity match.

## Engineering integration and fail-closed plan

- `scripts/t2_foam_resource_abi.py` source authenticator uses B17 `stage_profile` for SHA-only bounded original table syntax and `spirv-cross` numeric descriptor reflection, excludes private names and programs; accepts only known categories and bounded nonduplicate register/set rows.
- `tests/test_t2_foam_resource_abi.py` tests spoofed names, malformed/duplicate binding/unknown source tables/missing stage and double-counting.
- Shared T2 source-only workflow `.github/workflows/raft-t2-foam-member-abi.yml` reuses a **single private original provider and stage packet** for both member and texture/sampler analyses and deletes original sources before uploading only aggregates.
- Exact original numeric cardinality fixture guard commit [023ae969](https://github.com/alwansan/raf/commit/023ae9690bccd2a5c22ee6160a7e397d05b971f7), controls [54a52f47](https://github.com/alwansan/raf/commit/54a52f47d16e6dd2f452496e7c95aa0f1834dace). Source-authentic CI runs [41940279771](https://github.com/alwansan/raf/actions/runs/41940279771) and [41940321740](https://github.com/alwansan/raf/actions/runs/41940321740) **both COMPLETED SUCCESS**: source-only pin guard/12 controls and final **20/20** CB + **17/17** resource regression tests, exact original owner/4-stage source, exact six sampled image + six sampler pairing verified. Final safe artifact `13375618709` ZIP digest `aafc51035d2976a1b9bf4fba3b1a4761af91ab62ffaef1b909d4c8b0046873b2`.. Guard pins six original texture rows, six translated images, six translated samplers and their observed translation numeric bindings; if original/sampler count or a binding changes, fails closed rather than quietly substituting a shader.
- Next: link the original per-texture `m_NameIndex` and sampler selection semantics to compiled reflection/HLSL images/samplers privately, preserving genuine material property and UV pointers. Construct exact per-pass ShaderLab only after this equivalence, then Unity/Adreno acceptance. No native build requested.

WATER-001 remains OPEN, project NOT_READY 0/3, latest installed game APK86 predates this probe. Audio/Settings and deferred touch untouched; no game ShaderLab/.meta/GUID, FMOD or local world changed.
