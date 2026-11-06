# T2 — SHA-original Foam compiled CB0 load-index path evidence

**Issue:** WATER-001 (OPEN). **Session:** `20261106T103459Z-T2-chat-cb0-index-48bd` (`origin=chat`). **Verdict:** source-authentic compiled-path diagnosis; Unity CB0 upload and Android pixels **NOT VERIFIED**.

## Input authentication and execution

- Original ZIP2 pinned at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; `Raft_Data/sharedassets0.assets` has owner 115,978,112 bytes and SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Original Foam Shader PathID2420 SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`. B20 four linked source-authentic HLSL stages, two genuine original pass states, two authored Properties, and T2 private ShaderLab candidate are regenerated in CI scratch; no proprietary shader source published.
- Prior authenticated private member reflection: [42201778065](https://github.com/alwansan/raf/actions/runs/42201778065) verifies in both passes one shared numerical CB0 coordinate, same member offset/type token/stride but different array shape/byte extent. Source original serialized CB0 size from earlier work 160 bytes for each stage, but its exact member→translated upload semantics are **not established**.
- New verifier `scripts/t2_foam_private_cb0_index_access.py`, negative tests `tests/test_t2_foam_private_cb0_index_access.py`; same isolated SHA-pinned workflow `.github/workflows/raft-t2-foam-private-shaderlab-candidate.yml`. It recompiles four original-derived embedded ShaderLab HLSL stages privately; validates `spirv-val --target-env vulkan1.1`; matches each reflected UBO to binary `OpDecorate` set/binding/variable ID and cross-checks actual binary `OpEntryPoint` model (Vertex vs Fragment).
- It walks bounded SPIR-V `OpAccessChain`, `OpInBoundsAccessChain`, `OpCopyObject` pointer provenance into `OpLoad`, classifies 32-bit literal and unknown/dynamic indices conservatively, and computes only aggregate relations to both reflected stage array capacities. Malformed, unsupported, dynamic, or whole-buffer paths are never silently certified as statically safe. It **does not** prove all possible pointer aliases/function paths, branch reachability, or actually executed accesses.
- First [CI42204456139](https://github.com/alwansan/raf/actions/runs/42204456139) failed a source-free negative test whose synthetic binary omitted an `OpEntryPoint` model. Added the real binary/reflection stage guard and corrected source-free fixture; [CI42204897590](https://github.com/alwansan/raf/actions/runs/42204897590) ran between source and test commits and failed preflight as expected. Definitive [CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) on `5de93677334a5273ed185424be10d7f0dddc64ce`, job `127849093092`: **SUCCESS**, **100/100** source-free unittest methods across seven suites (17+10+14+14+19+12+14), original SHA/stages/ShaderLab/remap/compiled index checks success. Scratch erased before publishing bounded report.

## New original-derived compiled-path findings

| Source-backed per-pass aggregate | Pass 0 | Pass 1 |
|---|---:|---:|
| CB0 reflected larger array stage | Fragment | Vertex |
| Vertex `OpLoad` paths with constant array index | 3 | 2 |
| Fragment `OpLoad` paths with constant array index | 6 | 1 |
| Vertex constant-index loads outside Fragment's reflected capacity | 0 | **2** |
| Fragment constant-index loads outside Vertex's reflected capacity | **6** | 0 |
| Constant-index loads outside their *own* reflected capacity | 0 in both stages | 0 in both stages |
| Dynamic/unclassified array index `OpLoad` paths observed | 0 in both stages | 0 in both stages |
| Unresolved/whole-buffer pointer load paths observed | 0 in both stages | 0 in both stages |

**Interpretation.** The relative capacity direction reverses between passes, and the compiled original-derived programs actually contain distinct constant-index `OpLoad` paths into the portions of the **larger** CB0 array not represented by the other stage's shorter reflected array. A single smaller shared array cannot be assumed safe merely because the member start/type token/stride match. This adds real compiled-instruction evidence to the prior reflected shape-only discrepancy. It is not proof of an invalid runtime write, missing resource, or incorrectly uploaded uniforms: Unity may supply a larger buffer or different stage-specific layout, and the source-to-host upload path remains unknown. Conversely, array shape reflection alone was insufficient to detect these concrete instruction ranges.

**Privacy:** This report reveals only aggregate counts, relative stage, and source pin; no original symbols, exact register coordinates, numeric element indices/capacities, HLSL, DXBC, SPIR-V, textures or Unity binary assets are published. No fake success flags, padding, clamping, property aliases, original asset changes or content substitutions.

## Boundaries / next experiment

1. Establish whether the original 160-byte serialized stage-local CB0 and the Unity material/global upload producer provide the actual set of values required by the **larger** compiled stage, for each pass. The source serialized `m_Index` unit and original-to-translated field ID mapping remain unverified; do not assume `m_Index * 16` represents a byte offset.
2. Authenticate a real source/Unity write path and CB0 upload/lifetime/offset, not merely a global `SetConstantBuffer` search. If the compiled path cannot be tied to host data, preserve both different array capacities and keep the integration gate blocked.
3. Coordinate any full Unity shader import, GPU/Adreno pixel comparison, real water/FFT, or APK experiment with T1/T5. No game shaders, `.meta`, GUIDs, saves, input, Settings, audio or other workers' native workflows changed.

**WATER-001 OPEN / NOT_READY.** The owner-confirmed world/save/reentry Artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) is separate from water visual acceptance.
