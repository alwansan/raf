# B20 WATER-001 — authenticated Foam original CB register lineage and size boundary

## Integration result

B20 resumed as `20261104T2257Z-B20-fmp3`, building on the original B24 four-stage program recovery and B25 two-pass constant-buffer name/slot proof. [B20 original private packet](B20_FOAM_PRIVATE_PACKET_2026-11-04.md) ran at [41930578292](https://github.com/alwansan/raf/actions/runs/41930578292) SUCCESS with 10 synthetic controls. Then [source code](../scripts/b20_foam_cb_descriptor_lineage.py), [11 negative controls](../tests/test_b20_foam_cb_descriptor_lineage.py) and the same private original-data workflow inspected `spirv-cross --reflect` UBO declarations and translated HLSL explicit `cbuffer ... : register(bN)` declarations, with private names and programs discarded before artifact publication.

- **Source-authentic CI**: [41931585626](https://github.com/alwansan/raf/actions/runs/41931585626), commit `00ca84050300ab01a1dd3396ea863c12f5e14520`, **SUCCESS**: 10 packet +11 descriptor synthetic controls, original ZIP2/SHA pinned Foam object, four genuine stage translations and original render states, eight original CB name-index links.
- **Source pins**: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, `sharedassets0.assets` 115,978,112 bytes / SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; Shader PathID 2420 / SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- **Genuine finding**: all four generated HLSL CB b-register sets AND all four SPIR-V reflected UBO descriptor-set-0 binding sets coincide **numerically** with original B25 source CB register positions (vertex slots 0,1,2 and fragment slot 0 in both passes). This narrows the future alias/binding proof but is **not** CB0 identity or Unity material constant upload proof.
- **Important rejected assumption**: same slot numbers do **not** imply equal reflected byte size or complete original CB layout. Original serialized `m_Size` and generated SPIR-V `block_size` differ in seven of eight pass/stage/binding comparisons, as proved directly from the safe original report.

## Numeric comparison: original typed partial CB vs translated SPIR-V UBO

| Pass | Stage | Slot | Original partial CB `m_Size` (bytes) | Reflected `block_size` (bytes) |
| ---: | --- | ---: | ---: | ---: |
| 0 | vertex | 0 | 160 | 96 |
| 0 | vertex | 1 | 176 | 64 |
| 0 | vertex | 2 | 368 | 336 |
| 0 | fragment | 0 | 160 | 128 |
| 1 | vertex | 0 | 160 | 160 |
| 1 | vertex | 1 | 176 | 64 |
| 1 | vertex | 2 | 368 | 336 |
| 1 | fragment | 0 | 160 | 112 |

**1/8** sizes numerically match; **7/8** differ. These are **different representation domains** (serialized *partial CB declared size* versus SPIR-V reflected block extent). Optimizer field removal, padding/layout rules and actual used-member extents remain possible; this comparison is **NOT evidence of damaged original bytes, lost colors, or faulty rendered pixels**. A future assembler must prove original member offsets, types and upload semantics, including the opaque CB0 source name, rather than padding or truncating data to force equal totals.

## Safe evidence, independent verification and prior failure

- Immutable GitHub [source-authentic safe artifact 13370884370](https://github.com/alwansan/raf/actions/runs/41931585626) is a 1,464-byte ZIP containing only `b20-safe.json` and `b20-foam-cb-safe.json`, original stage/count/descriptor numeric and SHA records. ZIP SHA256 **`01287889fa7040caba4926026e439a9e6cf31bb563a50d02da8276b0414af0a3`**, CB safe JSON SHA256 **`2ffb3f1b5f03e742e3c6b42502172f378a0c62e566452ea95768e7a721370135`**. The exact eight source/reflection numeric pairs above were rechecked independently from the downloaded artifact. No shader source or private CB names were in that ZIP.
- [Reusable numeric size checker](../scripts/b20_foam_cb_size_parity.py), [nine negative/positive tests](../tests/test_b20_foam_cb_size_parity.py), [source-only CI 41932300308](https://github.com/alwansan/raf/actions/runs/41932300308) **SUCCESS 9/9** on `a5a235076fa026cc3ec09a87581c25bf23c3c79f`; the CI uses the safe numeric fixture (not a new original-data download) and confirms 8 links, 1 same /7 different, false aliases/device flags. The exact authentic report is independently checked above; CI fixture is **not an additional genuine-source run**.
- The initial [41931521584](https://github.com/alwansan/raf/actions/runs/41931521584) **FAILED solely on an invalid synthetic fixture** passing an empty string instead of a nonempty HLSL program without CBs; the real original shader was never reached by that run. Corrected test [00ca8405](https://github.com/alwansan/raf/commit/00ca84050300ab01a1dd3396ea863c12f5e14520); final genuine run 41931585626 SUCCESS. Keep both results, do not hide the failed negative-control setup.

## Remaining and next step

Need source-member **offset/type/usage** parity across original serialized per-pass CB schemas and translated SPIR-V structured UBO member layout before assigning original CB0 to a generated HLSL identifier. Verify actual material/property and texture/sampler bindings, then construct a real original two-pass private ShaderLab and validate Unity compile/Adreno pixels. In parallel B18's separate original FFT register-mapping progress should be reused for FFT, not inferred from this Foam probe. Original program source bytes, .meta/GUIDs, runtime game project, audio, Settings, touch/layout, native request and shared workflows were not changed. WATER-001 / RENDER-002 / LOCAL-005 remain OPEN; game NOT_READY and 0/3 independent full readiness reviews. Last Android game phone evidence is APK86, predating all these source fixes.
