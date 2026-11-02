# Authentic UltimateWater ComputeShader LFS owner audit — 2026-11-03

**Branch:** `feature/android-native-port`. **Unity / APK / Release hold remains active.** The existing scheduled task and both native build request JSON files are unchanged.

## Confirmed source provenance before this audit

The Git LFS pointers already tracked in the permitted branch declare:

| Original serialized owner | Bytes | SHA256 |
| --- | ---: | --- |
| `Raft/Raft_Data/resources.assets` | 111533516 | `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c` |
| `Raft/Raft_Data/sharedassets0.assets` | 115978112 | `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` |
| `Raft/Raft_Data/sharedassets36.assets` | 110149324 | `b32fcd9d327c8926b2309ffc1b5645a0c23d64ed95be37ed94e96f34736530c8` |

Total 337660952 bytes (three narrowly targeted owners; **not** all 6.85GB of original resources). The previously verified regular-Git `sharedassets29.assets` compute program is separate and cannot yet be assigned to FFT.

## New engineering gate

- `scripts/verify_targeted_lfs_compute_sources.py` confirms pointer hashes/sizes **before** hydration and exact original payload SHA256 **after** hydration; rejects missing data, symlinks, unexpected pointer changes and any truncated/modified payload.
- `scripts/probe_authenticated_water_compute_inventory.py` combines the existing original compute raw-container scan with serialized type-tree metadata. It cross-checks the original object SHA256 and `(owner, pathID)` identity across two distinct readers, requires **exactly nine** unique ComputeShader objects, and fails closed on missing LFS owners or a mismatched identity.
- `.github/workflows/raft-original-water-lfs-compute-audit.yml` is source-data-only; it checks out **without LFS smudge**, verifies original pointers, fetches exactly the three whitelisted LFS objects, validates hashes, reads metadata and reports only structural identifiers, flags, hashes and counts. No Unity, APK, shader/source code upload, game execution, secret or release.
- Six new synthetic Python unit cases passed locally (three provenance; three reconciliation), without original game data. GitHub CI outcome must be checked after its first run. The actual nine-object result, FFT owner, kernel order, original program semantics, Unity shader import, and phone execution are **not yet verified** by this source change.

## How to interpret the next run

Even a green CI means only that original data is authenticated and structural inventory/correlation succeeded. It does **not** clear `authentic_water_kernel_identity_verified`, replace any missing FFT kernel, restore missing multi-pass shaders or justify a Unity build under the owner's hold. Any failure should be traced to its first exact test, Git LFS hydration or UnityPy typed-tree error before changes to original resources. Source objects, `.meta`, GUIDs, `.rgd`, build request JSONs and scheduled automation must stay unchanged.


## Verified real-data result — 2026-11-03

- Source commit: [cd4ab1e854a0daa2e5845a28e45125834b11cd0b](https://github.com/alwansan/raf/commit/cd4ab1e854a0daa2e5845a28e45125834b11cd0b).
- [Source-only GitHub Actions 41533270315](https://github.com/alwansan/raf/actions/runs/41533270315): **COMPLETED SUCCESS**, job 125578639659. No Unity Editor/APK/OBB/XAPK/Release invoked.
- Verified 3/3 actual Git LFS payload bytes by SHA256 (337660952 bytes total), alongside original ordinary-Git owners.
- Cross-checked **all 9/9** authentic original ComputeShader object identities and discovered **42 valid embedded DXBC containers** with ISGN/OSGN/SHEX chunks: 21 in `resources.assets` across original pathIDs 905–911; 20 in `sharedassets0.assets` pathID 2456; 1 in `sharedassets29.assets` pathID 577. `sharedassets36.assets` was authenticated but contained no ComputeShader object in this inventory.
- Typed-tree metadata kernel array totals: `resources.assets` pathID 905: **12**; 906:1; 907:2; 908:1; 909:2; 910:2; 911:1; `sharedassets0.assets` pathID 2456: **20**; `sharedassets29.assets` pathID 577:1. These total 42, matching the structurally recognized DXBC count; this numerical alignment is evidence only, not proved index-to-program correspondence.
- Source code's fixed runtime indices 2 and 6 cannot be served by a resource declaring fewer than 7 kernels. **PathID 905 and 2456 are candidates** to examine first; neither is yet proved to be the exact original FFT reference. Preserve all serialized ordering and bindings. Never repair by setting kernel index to zero.
- Next engineering gate: inspect private serialized kernel order/name hashes, Unity source references and shader-model/resource binding metadata for these two candidates; independently test private DXBC translation without publishing program bytes, shader code or inferred water correctness.
- CI success here is provenance/structural evidence only. Authentic FFT ownership, original shader fidelity, Unity GPU import, Adreno runtime and device visuals remain unresolved.


## Candidate identity correction and original shader-model evidence

- New candidate inspector added at commit [7e707883a1858cf64450093015e2184e644f730f](https://github.com/alwansan/raf/commit/7e707883a1858cf64450093015e2184e644f730f). First [CI 41534127309](https://github.com/alwansan/raf/actions/runs/41534127309) failed only on incorrect assumption that the serialized `kernels` list was top-level; original typed-tree paths show `variants[]/kernels`. Fixed with SHA-checked exact source in [4c6ac63cf466a9441080090c99ebb45bdb0d4e46](https://github.com/alwansan/raf/commit/4c6ac63cf466a9441080090c99ebb45bdb0d4e46).
- [Corrected CPU-only CI 41534426923](https://github.com/alwansan/raf/actions/runs/41534426923) **COMPLETED SUCCESS**. Both original candidate ComputeShader objects are checked against their object SHA256 before extracting private structural name digests and stage/model tokens. No bytecode, shader names, source or HLSL are published.
- `sharedassets0.assets/pathID2456`: authentic `m_Name` **contains FFT** (name digest `60c1b5ee2352bd6e303aa5fc68c88f61031cf21234f524d54ec02334a8e142d1`); 20 DXBC entries, all **Compute Shader Model 5.0** (stage code 5), but **all 20 serialized kernel name digests are identical**.
- `resources.assets/pathID905`: authentic `m_Name` does not contain FFT, water or spectrum; 12 DXBC entries, all Compute Shader Model 5.0. Kernel name digests form **four distinct groups, each repeated three times**.
- **Important correction:** 42 is a count of serialized `kernels` entries and DXBC containers, **not proof of 42 distinct Unity runtime kernel indices**. The repetition demonstrates variant/duplicate identity ambiguity. Having `kernels` length at least 7 does not prove that runtime index 6 exists. Do not select, renumber or synthesize any Unity kernel or set `authentic_water_kernel_identity_verified` from these counts. The FFT-named resource is a strong *name-level* clue, not yet an exact match to the failing `Dx11FFT` `ComputeFFT` object and binding contract.
- Next: check serialized variant and dispatch/SetTexture routing and actual compiled resource register contracts before any private SPIR-V/HLSL reconstruction. Original water pass/compute gate remains intentionally blocking, and all hardware acceptance remains untested.
