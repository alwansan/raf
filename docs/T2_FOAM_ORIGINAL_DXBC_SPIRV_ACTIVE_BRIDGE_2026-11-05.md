# T2 WATER-001 — authenticated original Foam DXBC → SPIR-V active sampled-resource bridge

**Status: source/translation active-resource identity proven, Unity/Android material and visual integration NOT proven. 2026-11-05.**

## Original input and prior independent evidence

Immutable ZIP2 provider `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original `Raft_Data/sharedassets0.assets` exactly **115,978,112 bytes**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; Foam `Shader` PathID2420 raw object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`. B20/B24/B25 authentic source packet and pass-state/CB metadata were reused without overwriting their code. Four original DXBC stage SHA256 pins enforced in `scripts/b20_private_foam_packet.py`.

- [T2 original DXBC active SAMPLE CI41958159556](https://github.com/alwansan/raf/actions/runs/41958159556): native original source `m_TextureParams.m_Index/m_SamplerIndex` values `t0/s0..t4/s4` pass0 fragment and `t0/s0` pass1 fragment correspond to native executable `SAMPLE` operands. 21 native calls; 6 distinct stage-scoped used pairs. The two vertex stages have no textures/samplers.
- [T2 original-derived compiled SPIR-V sampler SSA CI41942245746](https://github.com/alwansan/raf/actions/runs/41942245746): 21 SPIR-V sampled operations and six used descriptor pairs, but that earlier count alone did NOT prove native register ownership. Source name equals translated variable name 0/6 from CI41941354379; avoid name aliases.
- Concurrent T2 [CI42009445569](https://github.com/alwansan/raf/actions/runs/42009445569) established that `m_SamplerIndex == -1` is a disabled/unknown sentinel rather than a proven t/s pair. This new experiment uses verified nonnegative original six pairs and does not overwrite that work.

## New exact compiler provenance (not inferred from order)

[T2 original CI42011706016](https://github.com/alwansan/raf/actions/runs/42011706016) **SUCCESS**, **16/16** independent synthetic negative controls, SHA-pinned original four-stage B20 packet. Standalone `scripts/t2_foam_explicit_descriptor_map.c` invokes the distro libvkd3d-shader compiler against the exact original native DXBC fragment programs under three interfaces: D/default, and two intentionally very different A/B explicit image/sampler bindings with source register indices. The `scripts/t2_foam_explicit_descriptor_identity.py` checker parses SPIR-V **binary typed variables** (image, sampler, uniform CB), IDs, and all descriptor-set/binding decorations. It proves source-indexed variable IDs are identical across A/B and the default and original B20 translated stage packet, and that **all SPIR-V words are identical after masking only numeric Binding/DescriptorSet decoration literals**. Any other changed program word, type, ID, variable or category fails closed. No original names/code/binary output.

| Native source register(s) | Same original program's default SPIR-V `set:binding` | Source proof |
|---|---|---|
| Pass0 fragment `t0..t4` | images `0:6..0:10` | A/B explicit remap ↔ stable variable IDs ↔ default and B20 original module |
| Pass0 fragment `s0..s4` | samplers `0:1..0:5` | same verified identity, no inferred numeric shift |
| Pass1 fragment `t0` | image `0:2` | same |
| Pass1 fragment `s0` | sampler `0:1` | same |
| Both fragment `cb0` | CB `0:0` | same fragment interface verification; does NOT prove Unity CB data member upload |

The two original vertex stages were SHA-authenticated and verified to have **zero texture/sampler rows**, so no nonempty t/s remap is asserted for vertex. The four-stage B20 packet itself remains source-authenticated.

## New exact active sample instruction join

[T2 source-authentic final CI42013590671](https://github.com/alwansan/raf/actions/runs/42013590671) **COMPLETED SUCCESS**: **16/16** typed explicit-interface tests plus **17/17** source-free active-join tests, immutable SHA-pinned original owner and B20 packet, native DXBC/serialized t/s declarations and executable native SAMPLE operands, private SPIR-V disassembly and SSA resource use tracer. `scripts/t2_foam_native_spv_active_join.py` takes the authenticated explicit source→descriptor mapping above, converts the **actually used** compiled SPIR-V image/sampler pairs *back to their original t/s register IDs* and compares the **exact per-stage set** to original DXBC executable `SAMPLE` pair operands. Fail closed for swapped sampler descriptors, duplicate mappings, equal totals with wrong pairs, unknown disabled/unbound/dynamic sampler, wrong stage or unknown source ID.

| Stage | Native original SAMPLE instructions | SPIR-V sample instructions | Exact active source pair set reconstructed from SPIR-V |
|---|---:|---:|---|
| Pass0 vertex | 0 | 0 | none |
| Pass0 fragment | **17** | **17** | `t0/s0, t1/s1, t2/s2, t3/s3, t4/s4` |
| Pass1 vertex | 0 | 0 | none |
| Pass1 fragment | **4** | **4** | `t0/s0` |

**21 original native and 21 translated sample operations / six exact actively used stage-scoped pair identities.** Total per-pair sample frequency beyond this per-stage exact pair set was not independently asserted; no source-to-output pixels, shader sampling numeric output, authored Material upload, sampler filter/wrap/UV, CB fields/offset semantics, rebuilt two-pass ShaderLab Unity import or Adreno actual device test yet. This proves resource-interface identity of the compiled translation, not complete water recreation.

### CI history, debugging, publication boundary

Original first compiled map [CI42011706016](https://github.com/alwansan/raf/actions/runs/42011706016) succeeded. Follow-up active-join [CI42012755702](https://github.com/alwansan/raf/actions/runs/42012755702) and [CI42013221572](https://github.com/alwansan/raf/actions/runs/42013221572) FAILED on an internal Python result-field key mismatch, **not** shader drift; sanitized source-only line 191 revealed the issue, corrected in [commit e5a88387](https://github.com/alwansan/raf/commit/e5a883872423ab980c32dc45062f222a33677fbf) with fail-closed 4-stage rollup and additional regression [57a70041](https://github.com/alwansan/raf/commit/57a700412733903c1a61e6134376a332f40ccae8). Both [CI42013532274](https://github.com/alwansan/raf/actions/runs/42013532274) and final [CI42013590671](https://github.com/alwansan/raf/actions/runs/42013590671) **SUCCESS**. All four original shader source stages, private programs and temporary C compiler outputs erased before finishing, no data or symbolic strings published.

Final numeric safe ZIP artifact **13407977911**, SHA256 **`93046863e5fa788b234b990a613554eb479851d4a9098131c7bd50efe7def0e1`**, contains only `t2-foam-explicit-safe.json` and `t2-foam-native-spv-active-safe.json` (verified manually after download). Link: [CI artifacts](https://github.com/alwansan/raf/actions/runs/42013590671).

Scripts: `scripts/t2_foam_explicit_descriptor_map.c`, `scripts/t2_foam_explicit_descriptor_identity.py`, `scripts/t2_foam_native_spv_active_join.py`. Tests: `tests/test_t2_foam_explicit_descriptor_identity.py`, `tests/test_t2_foam_native_spv_active_join.py`. Isolated workflow `.github/workflows/raft-t2-foam-explicit-descriptor-identity.yml`, timeout25m, no native Unity request, no game shader/.meta/GUID modifications, no other Actions cancelled. B18 explicit compile approach and B17/B20/B24/B25 original source work fully credited.

**Next actual engineering:** use this *proven* resource register mapping as input to the original Unity Material texture-property and sampler-state/UV upload integration; independently resolve CB member types/offsets and opaque CB0 aliases, reconstruct genuine Foam two-pass ShaderLab privately with B25 pass states and B20 source-authentic four stages, then Unity import/compile plus GPU/Adreno pixels. Spectrum 7-pass, Blur and FFT remain distinct open work. WATER-001 stays **OPEN**, project **NOT_READY 0/3**, last real phone test APK86; sound and Settings preserved, touch/layout deferred.
