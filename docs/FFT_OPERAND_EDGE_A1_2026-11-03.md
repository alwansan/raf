# A1 — authentic FFT direct producer-edge comparison

Client: raft-20261103T120720Z-a1e4f6c9. Branch: feature/android-native-port. Exact code source: 2be0c6938257591818414e407909814dbcd5b599.

## Objective and implementation

Earlier A1 FFT opcode census found 0/20 arithmetic-profile matches, while public GLSL.std.450 extension counts matched20/20. New scripts/probe_fft_spirv_operand_edges.py measures direct producer-to-consumer SSA dataflow only for public opcodes OpBitcast(124), OpIAdd(128), OpIMul(132), OpPhi(245). This is a bounded subset, not a whole shader dataflow analyzer. Unknown producers are counted unclassified. Phi predecessor labels are not treated as value operands. Original shader names, binaries and SSA IDs are not published.

## Reproducible tests and authenticated originals

- Source [07dc7781dcaf517311ecfe08923cbb9da661e253](https://github.com/alwansan/raf/commit/07dc7781dcaf517311ecfe08923cbb9da661e253) adds nine synthetic tests and no-LFS workflow. [CPU CI41633667561](https://github.com/alwansan/raf/actions/runs/41633667561), job125909295208, SUCCESS 9/9. Negative control keeps the same opcode histogram but rewires producer edges, which the new checker detects. Separate tests ensure matched edges never claim numeric equality, handle Phi forward references without counting predecessor labels, reject duplicate/out-of-bound tracked IDs.
- [Integrated code 2be0c6938257591818414e407909814dbcd5b599](https://github.com/alwansan/raf/commit/2be0c6938257591818414e407909814dbcd5b599) wires the checker into the SHA-verified private three-LFS-owner original FFT pipeline. [CI41634076530](https://github.com/alwansan/raf/actions/runs/41634076530), job125910690956, COMPLETED SUCCESS on this exact source, repeats nine passing tests and authenticates/validates 20/20 original Vulkan1.1 SPIR-V modules. Bindings and workgroups preserved20/20. No original binary was published or inserted as Unity replacement.

## Aggregate structural evidence over 20 pairs

| Tracked relationship | Original | HLSL roundtrip | Pairs differing |
|---|---:|---:|---:|
| OpBitcast124 → OpBitcast124 | 0 | 390 | 20/20 |
| OpIAdd128 → OpIAdd128 | 140 | 40 | 20/20 |
| OpIMul132 → OpIAdd128 | 205 | 140 | 20/20 |

The 20/20 comparisons ran, but **0/20** direct tracked producer-edge profiles and 0/20 tracked opcode counts match. Total direct tracked edge uses were **525 original → 750 roundtrip**. Inputs not produced by these four tracked instructions are counted separately (**1665 original → 1701 roundtrip**) and remain **unclassified**. There were three changed public edge families across all20 pairs; all other tracked edge family counts stayed equal. Existing GLSL.std.450 operation ID histograms remain20/20 matched, but typed-image and arithmetic opcode profiles 0/20.

These counts establish structural SPIR-V compiler lowering differences, **not** different numerical FFT output, operand/constants equivalence, execution precision, complete dependency graphs, original Unity kernel identity, or Adreno/Vulkan compatibility. Original water resource contract remains FALSE.

## Coordination and limits

The work modified only diagnostic scripts, synthetic tests, CPU-only workflows and coordination documentation. No proprietary source or raw shader binaries were published; original assets/.meta/GUID, .rgd data, LEFT Mouse0/500ms, UGUI/Xbox/physical devices, CL logs, native build requests, Unity/APK/OBB/XAPK, Releases or scheduled tasks were touched. Latest CL raft-log/lf still had only four historical 2026-11-02 sessions; old game tag android-early-test-41448086401-1 remains source9462f8e (11 delivery assets), unrelated to this repair.

WATER-001, RENDER-002 and FFT-FORMAT-009 remain OPEN. NOT_READY; no immutable candidate; full readiness reviews0/3. Next useful proof: authentic executed shader numeric/format behavior with correct resources, not inferred opcode equivalence.
