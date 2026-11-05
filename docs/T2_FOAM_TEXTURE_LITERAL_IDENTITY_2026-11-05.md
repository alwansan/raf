# T2 WATER-001 — Original Foam texture literal symbol identity, SHA-authenticated

## Scope and provenance
T2 resumed as `20261105T0023Z-T2-foam-texture-identity` from previous paused T2 source ABI session. This work adds a new *private numeric/name continuity diagnostic*, not ShaderLab or Unity runtime binding.

- Source: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original `Raft_Data/sharedassets0.assets`, 115978112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
- Authenticated original Foam Shader PathID 2420, raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`. Inherits B20 genuine four compiled stages, B25 pass name indices and T2's previous CB/resource cardinality gates; their work retains its authorship.
- [New source and workflow commit](https://github.com/alwansan/raf/commit/5dd02e7931aedfbb92c5cbcf3cc10ac1a6f9fd7c), [authenticated run 41941354379](https://github.com/alwansan/raf/actions/runs/41941354379) **SUCCESS** on that immutable SHA. CI: 20 existing Foam member ABI + 17 Foam resource ABI + **15 new** texture symbol adversarial tests passed, genuine ZIP2 original source restored, B20 four-stage packet and 6 image + 6 sampler numeric gate passed, private data erased before safe artifact upload. Safe artifact `13376592808` (GitHub-reported size 2081 bytes).
- Last real released Android game remains [APK86](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1); it predates this work, no new phone run.

## New reproducible observation
The new `scripts/t2_foam_texture_identity.py` authenticates the source owner, resolves the original per-pass `m_TextureParams[].m_NameIndex` through the genuine pass-local `m_NameIndices` registry, and compares original literal symbols in private memory with the corresponding compiled SPIR-V `separate_images[].name` lists after validating the already-pinned exact descriptor set/bindings.

- Original source texture rows: **6**, across 4 stages: pass0 fragment 5, pass1 fragment 1, both vertex stages 0.
- Translated SPIR-V separate images: **6**, separate samplers: **6**, with matching previously verified numeric stage cardinality.
- **Literal original texture-name ↔ reflected SPIR-V image-name matches: 0/6.**
- None of the private names, recovered shader code or bytecode are included in the script output, logs, docs or artifacts. CI prints only numeric aggregates and fixed booleans.
- Fifteen new source-free controls reject missing/unknown registry indices, duplicate/ambiguous names, invalid typed indices, translated binding drift and descriptor count drift. A legitimate zero-match result is accepted, not called an upload fix.

## Evidence boundary and next action
The new result rejects the naive hypothesis that the translated SPIR-V image variables retain the original *literal* serialized names. It **does not** establish that GPU/image binding is wrong: identity can be preserved by nonliteral compiler aliases, descriptor registers or Unity runtime material/property upload. The original `m_Index`, `m_SamplerIndex`, dimension/type and sampler-state semantics are not proven to map to the compiled reflection or actual Unity ShaderLab uniform declarations.

**WATER-001 remains OPEN, game NOT_READY 0/3.** Next: privately reconstruct exact original numeric texture-index/sampler association and active HLSL sampled-image/sampler use across the six rows with explicit source/translation provenance; only then assemble/install the authentic two-pass Foam ShaderLab and verify in Unity and Adreno. Leave audio, Settings and deferred touch alone. Preserve original .meta/GUID, no dummy or fabricated mappings.
