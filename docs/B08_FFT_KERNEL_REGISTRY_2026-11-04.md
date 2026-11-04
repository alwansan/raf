# B08 — authenticated FFT compiled-kernel name aliases (2026-11-04)

**Issue:** WATER-001, P0. **Session:** `20261104T2130Z-B08-b71c`. **Result:** authenticated negative identity proof. Not a restored authored compute source, Unity runtime mapping, GPU render or Android fix.

## New real-source result

[B08 run 41917369953](https://github.com/alwansan/raf/actions/runs/41917369953), [job 126880476260](https://github.com/alwansan/raf/actions/runs/41917369953/job/126880476260), source commit [c24dba47](https://github.com/alwansan/raf/commit/c24dba47cd49d9af4ae241de5032541b1a41e918): **COMPLETED SUCCESS**. Synthetic suite 11/11 plus actual SHA-verified original Unity serialized ComputeShader inspection and same-slot original DXBC identity match.

The original provider was read-only ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. The independently authenticated owner `Raft_Data/sharedassets0.assets` is **115,978,112 B**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Original ComputeShader pathID `2456`, object SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`. No LFS or private archive was needed. All original program bytes and names were kept inside ephemeral CI runner storage and excluded from artifacts.

The **one** original serialized variant has **20** compiled entries but only **one distinct kernel name**; its name-alias group covers compiled positions **0–19**. Every position was separately matched to the original source's bytecode SHA/order via the existing B48 authenticated correlation. Thus 20 serialized programs do **not** establish 20 individually named runtime Unity kernels, and using 0–19 as `FindKernel`/Dispatch runtime IDs is **not supported**. The original name is not published. Whether one lookup ID selects 20 variants through some other mechanism remains unknown.

## Controls and integration

New production-use source diagnostic `scripts/b08_probe_fft_kernel_registry.py` + 11 strict synthetic controls `tests/test_b08_fft_kernel_registry.py` + isolated `.github/workflows/raft-b08-fft-registry.yml`. Negative fixtures reject name absence, count drift, invalid keyword/variant map, compiled-order drift, fake per-slot runtime proof and falsely claimed Unity mapping. Even a synthetic registry with 20 different names must not claim actual Unity runtime identity. Source test is wired into the B08 workflow and ran on the real authenticated original; only safe counts/indices and SHA are printed.

**Rejected hypothesis:** every original compiled slot is automatically a separately named/numbered Unity runtime kernel. **Unproven:** exact original runtime `FindKernel` ID->selected compiled slot, authored Android `.compute` program, graphics output, 1024-thread capability, Unity import, Adreno/device, world/save. Do not rename the 20 candidates into fake kernels, change `authentic_water_kernel_identity_verified`, clamp kernel indices, or remove strict water gates.

## Follow-up

Find the original Unity engine/runtime selection key and actual `Dx11FFT` dispatch semantics that route one serialized kernel name across 20 compiled specialization entries. Join an *independent* original shader variant/runtime observation to B48's 10 selector candidate pairs; until such evidence exists, do not stage a synthetic `.compute` pretending original runtime ID parity. Coordinate with B01/B06/B47/B48. Preserve owner-confirmed audio/Settings, untouched deferred input, existing native build requests and other agents' work. WATER-001 **OPEN**; overall **NOT_READY, independent full reviews 0/3**.
