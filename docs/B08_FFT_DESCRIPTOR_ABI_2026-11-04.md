# B08 — authenticated original FFT DXBC→SPIR-V descriptor ABI (2026-11-04)

- Identity: **B08**, resumed session `20261104T2246Z-B08-7d2a`; issue WATER-001, P0.
- Real private-source CI: [run 41928583281](https://github.com/alwansan/raf/actions/runs/41928583281), job [126919393498](https://github.com/alwansan/raf/actions/runs/41928583281/job/126919393498), source [2c9ffdd5](https://github.com/alwansan/raf/commit/2c9ffdd5bf27b8b67465431d23dc75e01a586f60): **COMPLETED SUCCESS**. **14/14 source-free synthetic mutation tests PASS**, original 20/20 compiled FFT programs authenticated, converted privately using vkd3d-compiler and checked against B18 executable source declarations (2 read Texture2D t0,t1 and 1 output Texture2D u0).
- Original source: immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. `Raft_Data/sharedassets0.assets`: **115,978,112 bytes**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Original FFT ComputeShader pathID `2456`, object SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`. No LFS, unvalidated private release, loose shader program or proprietary asset was published.

## Exact observed translated interface

Every one of the 20 original compiled DXBC positions (not Unity runtime kernel IDs) translated into SPIR-V with the **same numeric image descriptor ABI**:

| Image role class | Vulkan DescriptorSet | Binding | Element scalar kind/bits | Format enum | Access enum |
|---|---:|---:|---|---:|---|
| Sampled Texture2D candidate A | 0 | 0 | float, 32 | 0 | unspecified |
| Sampled Texture2D candidate B | 0 | 1 | float, 32 | 0 | unspecified |
| Single storage Texture2D | 0 | 2 | float, 32 | 0 | unspecified |

The normalized *numeric* interface SHA256 is `5bea50a922c423edde59ea0346541a4ba2a4db437e3a764bdf26b756f5c47aca`. This SHA hashes the safe numeric interface, **not original asset content, image pixels, or semantic shader equivalence**. The source DXBC per-program workgroup and two-read/one-write counts were separately checked by B18's strict original/converted contract before collecting the ABI. The source 20 SHA/order correlations remain required before translation; no guessed program order or Unity kernel ID.

**Proven:** exact translated descriptor set/binding/type-class numbers and cross-slot uniformity for the chosen pinned vkd3d translation on these immutable source programs. This is a useful fail-closed precondition for reconstructing a real Android-compatible compute pipeline, not its end-to-end implementation.

**Not proven:** which of the two *sampled* target descriptors maps to original DXBC `t0` (source image) and which maps to `t1` (butterfly). Despite the unique `u0` output class, executable source→target instruction-by-instruction semantic equivalence is not proven. The metadata cannot provide original Unity `FindKernel` numeric IDs (B08 previous one-name/20 compiled slots, B30 opaque routing hypothesis rejected), authored `.compute`, real Unity import, Adreno capabilities or water pixel fidelity. No change to strict water gate or kernel-authenticity flag. WATER-001 remains **OPEN**, game **NOT_READY 0/3**.

## Integrated guard and failure controls

Implemented reusable source verifier `scripts/b08_fft_spirv_descriptor_abi.py`, 14 synthetic controls `tests/test_b08_fft_spirv_descriptor_abi.py`, isolated `.github/workflows/raft-b08-fft-descriptor-abi.yml` (20-minute maximum, separate concurrency with `cancel-in-progress: false`, precise ZIP2 SHA, no LFS or uploads). Tests detect missing or duplicate descriptors, source register role changes, shifted sampled and storage sets/bindings, single-slot precision drift, wrong workgroup, second entrypoint, incomplete 20-slot set and **forged Unity/t0-t1 mapping attestation**. Swapping the two declaration orders while keeping the same bindings must not invent source `t0` vs `t1` identity.

No original shader, .meta/GUID, asset content, game/runtime C#, .rgd, audio, Settings, deferred touch, native request, protected branch, Unity build, APK/OBB/XAPK, CL or schedule was changed.

## Next integration boundary

An independent source+target **resource use/operand lineage** proof or controlled genuine Vulkan numeric comparison must distinguish `t0` from `t1` before adopting descriptor candidate ordering. Then map actual Unity runtime kernel lookup/variant selection, stage the authentic translated program behind existing water authenticity gates and check Unity/Adreno. Avoid repeating B18's source role census or B30's already-falsified `variantMap` discriminators.

## Follow-up: executable SPIR-V image-use verification, not declaration only

**Final expanded CI:** [41929513820](https://github.com/alwansan/raf/actions/runs/41929513820), job [126922530492](https://github.com/alwansan/raf/actions/runs/41929513820/job/126922530492), source [ac98030e](https://github.com/alwansan/raf/commit/ac98030e51148a6a1b7e2203d9d8bdc2f327704f) **COMPLETED SUCCESS**. It supersedes the first run for the stronger validation but does not invalidate the first numeric ABI result.

The guard now applies the already-tested source-agnostic SPIR-V SSA image operand lineage to each authenticated original translated program, in addition to the 20-slot numeric ABI above. For **all 20 original programs**:
- Both declared sampled image descriptors (set0/binding0 **and** set0/binding1) have executable fetch/read/sample/gather uses.
- The single declared storage descriptor (set0/binding2) has executable image write uses.
- Supported SPIR-V image operations in the bounded scanner were uniquely traced to declared descriptor sets/bindings; none were unresolved or multiply bound.

Six additional synthetic mutation controls (20/20 total) reject dead sampled input, never-written storage output, unresolved image operands, incorrectly sampled storage output and declaration-only false positives. The final authentic stage used SHA-pinned original ZIP2 `sharedassets0.assets` and exact FFT object bytes, without private program upload, Unity/native game build or release. The preceding source-only run [41929448442](https://github.com/alwansan/raf/actions/runs/41929448442) also passed its original-data stage with 14 older controls, before the six new mutation tests were added.

**Boundary:** this detects executable *SPIR-V image read/write use*, not source DXBC `t0` versus `t1` binding semantic equality, complete instruction coverage of unknown future SPIR-V opcodes, pixel/FFT numeric correctness, original Unity kernel index or Android GPU support. Do not repurpose these results to claim authored water shaders or real game readiness. WATER-001 **OPEN**, NOT_READY 0/3.
