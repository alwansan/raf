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


## Verified CPU-only real FFT DXBC translation and original caller evidence — 3 November

- The original CSharp9/ILSpy source is SHA-pinned and inspected in temporary CI only. [Managed source test 41536176647](https://github.com/alwansan/raf/actions/runs/41536176647) **SUCCESS**: original `WavesRendererFFT` has exactly one literal with SHA256 equal to the authentic `sharedassets0.assets/pathID2456` ComputeShader `m_Name`; original `Dx11FFT` has 2 Dispatch and 6 SetTexture callsites. [Refined managed check 41536703308](https://github.com/alwansan/raf/actions/runs/41536703308) **SUCCESS**; direct API call category around the matching literal remains unclassified, so do not infer a direct Unity PPtr or runtime correct loading.
- [Original PPtr audit 41536233370](https://github.com/alwansan/raf/actions/runs/41536233370) **SUCCESS**: checked 3482 script/material/game object sources in `resources.assets` and 14790 in `sharedassets0.assets`. Only one raw same-file pointer pattern to `pathID2456` occurred in `MonoBehaviour/pathID23172`, at raw offset **260/272** bytes. UnityPy's base typed-tree stops after 56/272 bytes; therefore this pattern is **not yet typed-reference evidence**. [Partial head 41536605032](https://github.com/alwansan/raf/actions/runs/41536605032) **SUCCESS**: original MonoBehaviour's m_Script is an **external** PPtr with `fileID=1, pathID=2305`. Need resolve that source MonoScript and original custom field before proof of linkage.
- New private FFT DXBC translator: `scripts/probe_authentic_fft_dxbc_translation.py` and synthetic SPIR-V descriptor tests, included in isolated `raft-original-water-lfs-compute-audit.yml`.
- [Authentic 20-program CPU CI 41536892720](https://github.com/alwansan/raf/actions/runs/41536892720) **SUCCESS** at source [fd22d711](https://github.com/alwansan/raf/commit/fd22d7117ae3b7fbafb3d0b9830b0143c70d2f7e). All **20/20** original sha-verified FFT-name DXBC compute programs translated by Ubuntu VKD3D compiler to SPIR-V **1.0**, all **20/20** passed `spirv-val --target-env vulkan1.1`. Every converted module exposed descriptor set **0**, bindings **0,1,2**, and one compute workgroup with X dimension among **64,128,256,512,1024** and Y/Z=1; different variants had instruction counts ~409–512. Distinct DXBC bytecode and workgroup shapes are real, even though the serialized kernel name digest repeats. Output binaries deleted in CI temp; no HLSL, proprietary shader sources or bytecode published.
- **Critical distinction:** Scan position 6 is **not** Unity runtime kernelIndex 6. One repeated kernel name across 20 DXBC programs may represent permutations/variants, not 20 user-addressable kernels. Original shader binding to `Dx11FFT`, GPU limits, exact resources and mathematical equivalence remain unverified. Vulkan1.1 `spirv-val` means structurally valid module, not that the Adreno phone can dispatch groups of 1024, or that restored water renders.
- All experiments are independent source/Python/CPU-only workflows. Owner Unity/native APK/OBB/XAPK/Release hold remains in force. The scheduled task, native request JSON files, original assets, .meta/GUIDs and .rgd remain unmodified.


## Authenticated external MonoScript link and private CSharp identity — verified

- [CPU-only LFS CI 41537296765](https://github.com/alwansan/raf/actions/runs/41537296765) **COMPLETED SUCCESS**, using `scripts/probe_original_fft_serialized_refs.py` with the real UnityPy `read_typetree(check_read=False)` MonoBehaviour base head, after rejecting incomplete full typed trees. Original `sharedassets0.assets/MonoBehaviour pathID23172`, 272 bytes, has the same-file raw 12-byte `fileID=0,pathID=2456` pattern at byte offset 260. The *base* `m_Script` field is a verified external PPtr `fileID=1,pathID=2305`, which resolves to `globalgamemanagers.assets/MonoScript pathID2305` and is successfully parsed. Its original managed namespace/class identity SHA256 is `cb4d4c048bb81a9c6260539769f50e73b91b44ae5d6ccc048038d342154ed687`. The class/namespace name is water-related; no private type name emitted.
- [Managed original ILSpy CSharp9 CI 41537890210](https://github.com/alwansan/raf/actions/runs/41537890210) **COMPLETED SUCCESS**, source [7ad871b716cb8a06d65ab72ae0d85b1c19c39216](https://github.com/alwansan/raf/commit/7ad871b716cb8a06d65ab72ae0d85b1c19c39216). `scripts/probe_fft_monoscript_field.py` matched **exactly one** private recovered CSharp source class by that SHA256: source SHA256 `2e56c01c13c84b2bb908a628be6ab5378be7b702185fac9fe906545b602d3893`. The class source has two `ComputeShader` occurrences, but **zero direct field declarations matching the currently bounded regex**. This does not prove absence of a serialized ComputeShader field (could be inherited or differently declared), nor make the raw PPtr at offset 260 typed. Continue inspecting the authenticated class/serialization field layout, not a guessed shader name.
- All tests for this evidence run without Unity Editor, native game build, APK/OBB/XAPK, release, raw shader export or device GPU testing. `authentic_water_kernel_identity_verified` remains **false**.


## Next source-only recovery milestone — authentic original FFT array and HLSL roundtrip

**Original 20-program CPU program semantics contract — [CI 41538782459](https://github.com/alwansan/raf/actions/runs/41538782459): SUCCESS, commit `948ff7f6f318df6ff31e213228303860c09d9035`.** Every authenticated original `sharedassets0.assets/pathID2456` DXBC compute program (20/20) succeeded through:
`DXBC -> VKD3D SPIR-V -> SPIRV-Cross HLSL50 -> glslang SPIR-V -> spirv-val(vulkan1.1)`.
All 20 preserved compute workgroup shapes and numeric descriptor set/binding pairs across the roundtrip; *neither semantic equivalence nor Unity/Adreno execution proved*. Generated HLSL/program bytes were confined to temporary CI storage and deleted.

**Real original resource-kind reflection — [CI 41539468899](https://github.com/alwansan/raf/actions/runs/41539468899): SUCCESS, commit `b3f4f850c441e024b57363bd2b4516a0a24c4ae8`.** All 20 programs had exactly one storage image at descriptor `set0/binding2` and two separate input images at `set0/binding0` and `set0/binding1`. No resource names or shader code published. This provides a concrete `SetTexture` binding contract to investigate, not a runtime resource-name map or guaranteed output.

**Verified original C# array declaration and one-element serialized shape.**
- [CSharp9 source CI 41539741723](https://github.com/alwansan/raf/actions/runs/41539741723): SUCCESS, commit `743619d3d2b62127044bf2e31862afa047f2bf1a`. The authenticated water MonoScript's exact source SHA `2e56c01c13c84b2bb908a628be6ab5378be7b702185fac9fe906545b602d3893` contains **one direct `ComputeShader[]` field declaration** (scalar count zero), with type-context classification and hashed field identifier only.
- [Authenticated LFS CI 41539779362](https://github.com/alwansan/raf/actions/runs/41539779362): SUCCESS, commit `eaa6b6767acdcc14bfea3ad2d4855e04043d7473`. Original `sharedassets0.assets/MonoBehaviour pathID23172` raw SHA256 `de71d828e84ce3960008a31cf82f0e0253bad89600f81a1ec9670d619eab7245` is 272 bytes. Its last 16 bytes structurally comprise `int32=1` at offset256 and the 12-byte local PPtr `fileID=0,pathID2456` at offset260. This is an exact one-element-array **shape**, not a decoded custom-field TypeTree.

**New independent one-run fail-closed proof — [CI 41540487810](https://github.com/alwansan/raf/actions/runs/41540487810): SUCCESS, commit `cc9749a8424cd4e79c614bfdd8712cc1307af12d`.** Added `scripts/verify_original_fft_array_provenance.py`, three synthetic corruption tests and `.github/workflows/raft-original-fft-array-provenance.yml`. It hydrates exactly **one** original SHA-verified LFS source owner (115978112 bytes), resolves authentic external `globalgamemanagers.assets/MonoScript pathID2305`, verifies the original `ComputeShader[]` CSharp9 source hash and the one-element original array byte layout, checks the authentic FFT ComputeShader object and original `WavesRendererFFT` source-literal identity, **all in one immutable CPU-only run**. It fails on modified SHA, MonoScript or array structure; no project, shader source or game build published.

**Acceptance boundary:** This establishes a strongly source-corroborated original water component -> FFT array object relationship. It does NOT provide a complete custom Unity TypeTree field definition, confirm the proper runtime kernel index, recover all original UltimateWater passes, or prove compute numerical output, mobile GPU limits or rendered water. Unity's documentation notes that compute shader assets can have multiple compiled variants via keywords; do not equate 20 compiled DXBC variants with 20 runtime-addressable kernels: https://docs.unity.cn/es/2021.1/Manual/class-ComputeShader.html . The strict water gate remains fail-closed, and Unity/APK/OBB/XAPK/Release hold remains active.
