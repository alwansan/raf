# T2 — SHA-original Foam two-pass CB0 reflected member shape

## Experiment and source chain
- Session: `20261106T102054Z-T2-chat-cb0-member-shape-3f9e`, origin `chat`.
- Source: original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, `Raft_Data/sharedassets0.assets` exact 115,978,112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Original Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`; B20 existing private four-stage packet with original render states and private two-pass ShaderLab candidate.
- Existing original remap reference: [42153150468](https://github.com/alwansan/raf/actions/runs/42153150468) removed 4 DescriptorSet type collisions with 4 selective literal edits, retained one compatible-class shared CB0 coordinate per pass, but two byte-extent discrepancies remained.
- New verified code: `scripts/t2_foam_private_cb0_member_shape.py` commit `6746b7eb72103f52ebb750b94dce3b2d27500546`; source-free adversarial tests `tests/test_t2_foam_private_cb0_member_shape.py` commit `715fcfb07207a51cb1dc4bc65fb977c7be1cd662`; integrated into existing SHA-private isolated workflow `.github/workflows/raft-t2-foam-private-shaderlab-candidate.yml` at `d8c5134e36f588a8273a5476e393d708c2ad639e`.
- Real original [GitHub Actions 42201778065](https://github.com/alwansan/raf/actions/runs/42201778065), job `127838546044`: **SUCCESS** on exact `d8c5134e36f588a8273a5476e393d708c2ad639e`. Preflight source-free Python suites **17+10+14+14+19+12 = 86 tests passed**. All original source pins, four original programs, two pass states, private compiled SPIR-V and existing descriptor remap passed; original scratch erased before safe-report publication.

## New source-authentic finding

SPIRV-Cross reflected each of the four recompiled source-authentic Foam stage programs from the fully assembled private two-pass candidate. For **each** of the two passes there is precisely one VS/FS shared numeric UBO coordinate, with one reflected member on each side. The member starts at the same byte offset within each reflected stage, uses the same reflected type token and has the same reflected array stride / matrix-stride / major-order values. **The reflected array shape differs in both passes**, and the corresponding reflected CB0 byte extents differ in both passes. Exact member geometry equality is therefore **0/1 for pass0 and 0/1 for pass1**.

| Safe aggregate | Pass0 | Pass1 |
|---|---:|---:|
| Shared numeric UBO coordinates | 1 | 1 |
| VS reflected members | 1 | 1 |
| FS reflected members | 1 | 1 |
| Same member start offset | 1 | 1 |
| Same reflected member type token | 1 | 1 |
| Exactly same member geometry | 0 | 0 |
| Same-offset array shape differences | 1 | 1 |
| Same-offset stride / major differences | 0 | 0 |
| Different reflected block byte extents | yes | yes |

This **narrows the CB0 extent disagreement to a reflected per-member array shape difference**, rather than a mismatched starting member byte position, type token, stride or major flag in the observed stage compilation. Type-token coincidence is *not* a proof of original authoring semantics, byte-by-byte compatibility, or correct runtime constant upload. Exact original array dimensions, names, raw HLSL/DXBC/SPIR-V, per-resource descriptor coordinates and texture names have not been published.

## Boundaries and engineering next step

- The tested private translated SPIR-V reflection is genuine for this pinned original stage/candidate, but **no Unity 2021 ShaderLab importer, actual Vulkan uniform upload, or Adreno visual water rendering was tested**. No game `.shader`, `.meta`, GUID, material, save, FMOD, Settings or input changed. **WATER-001 OPEN; NOT_READY**.
- A shared descriptor coordinate does not justify padding/truncating buffers or aliasing names. Before integration, establish the direction and bounds of array extent difference against source-authentic CB member/value producer and actual Unity material/global upload. Distinguish safe shared prefix from non-prefix indexing and active dynamic indexing; require evidence of upload range and lifetime. The existing synthetic gate deliberately continues to block unequal extents.
- Only after source-to-upload mapping and numeric/Unity proof may private two-pass ShaderLab be considered for game integration and coordinated device water capture with T1 FFT / T5 native build. Preserve original assets and privacy boundaries.
