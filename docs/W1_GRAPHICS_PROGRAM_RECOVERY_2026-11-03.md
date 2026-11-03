# W1 original graphics program recovery — 3 November 2026

Source [01f1cfcc335f6756ae1caa1f8ce6abbfd902135a](https://github.com/alwansan/raf/commit/01f1cfcc335f6756ae1caa1f8ce6abbfd902135a); independent CPU-only [run41644979965](https://github.com/alwansan/raf/actions/runs/41644979965), job125947836031 **COMPLETED SUCCESS**. [Aggregate artifact](https://github.com/alwansan/raf/actions/runs/41644979965/artifacts/13235281293); [durable hash/count summary](W1_GRAPHICS_PROGRAM_RECOVERY_2026-11-03.json).

## Actual recovery

Two original owners authenticated independently by exact size/SHA256 before parsing: resources.assets111533516bytes SHA87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c and sharedassets0.assets115978112bytes SHA0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3. Total227511628bytes; no resS download. Retry cache now holds these exact LFS objects; verify every reuse.

Decoded **105 actual original Shader objects /318 serialized passes /105 platform tables /107 compressed segments /15645 entries**. **97 entries reference a nonzero segment**. Segment-aware parser uses each entry's original offset,length,segment triple rather than assuming segment0. Scan found6121 fragment and5912 vertex DXBC containers across entries; these are occurrences, not unique programs or linked runtime variants.

**12 sampled program entries from6 original Shader objects (11 distinct DXBC hashes)** recovered through DXBC -> vkd3d SPIR-V -> SPIRV-Cross private HLSL. Each original translation and each HLSL/glslang roundtrip passed spirv-val Vulkan1.1. Four samples each use lexical water/effect/other categories; these are grouping aids, not proof of exact UltimateWater pass ownership. Original object hashes, owner/pathID, program hashes, HLSL hashes and stage codes are retained in the aggregate JSON. No shader source/binary/name was published, and temporary programs were removed automatically. The checked-in regeneration code plus pinned original inputs preserve the recovery method; the report is not the recovered source itself.

This is actual program-body recovery, **not** an installed ShaderLab repair. No material/texture/vertex color/.meta/GUID changed. No claim that these105 objects are the complete140-file failed-run export; this experiment reads original serialized owners directly, not an AssetRipper project. No assertion that97 nonzero entries caused AssetRipper's failures: its implementation has not been traced here. UnityPy's public converter inspected at Git blobdd3ac1c558ec0bd5fd982bbcac38fec8fe712340 selects the first compressed segment; W1's independent decoder deliberately reads all original segments, but does not replace any upstream converter.

## Validation and tool versions

Three local and same-source CI segment-routing tests passed, including wrong segment/range/table-overlap/truncated-table negative controls. Private authentic run then exercised real compressed segments and program containers. Ubuntu24.04; UnityPy1.25.4; vkd3d-compiler1.2-15build1; spirv-cross2021.01.15+1.3.239.0-1build1; spirv-tools2025.1~rc1-1~ubuntu0.24.04.2; glslang-tools15.1.0-2~ubuntu0.24.04.2. Total job was under one minute after checkout startup, within20-minute budget; per-recovery timeout600seconds. No Unity/GPU execution, APK/native request, Release or task modification.

## Device evidence and limits

Read-only CL still contains four2-Nov LF sessions. Actual205608 summary has71670 invalid-pass,5941 invalid-kernel and35 Haptics-path errors; these are old installed APK80 observations. Two2-Nov screenshots were actually viewed: one shows stretched Settings/menu with some colored props still visible and pale/missing environment; another shows INITIALIZING ASSETS/connecting failure. They do not identify a single universal cause or validate current source fixes. APK80 remains source9462f8edd8cdb5becbccb96521f2876ef9924410, release11assets. Logger releases are separate.

No stage pairing, m_BlobIndex-to-pass linkage, constant/texture binding reconstruction, keyword compatibility, actual render target behavior, semantic/numerical equivalence, Unity compilation or POCO image acceptance has been established. A valid HLSL roundtrip alone cannot establish these. WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; NOT_READY, full reviews0/3.

## Exact next step

For one hash-pinned affected Shader, join each original serialized pass/stage m_BlobIndex and keyword/hardware-tier record to the recovered table entry. Recover original property/binding names from serialized metadata, preserve blend/depth/culling and stage interfaces, and produce a private reconstructed wrapper for an explicit paired render/numeric comparison. Keep generic shader substitution forbidden. Continue independent of A11/A13 diagnostics and A15 active builtin rollback.

Identity: raft-20261103T162900Z-73e8c2a1. Restore by reading prompt/coordination/UNIFIED_PROMPT_AR.md, README.md, this client's state/MEMORY/work/experiment, fresh HEAD/Actions and latest source before writes. Do not infer active-session death from heartbeat alone.
