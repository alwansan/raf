# A15 — authenticated original serialized Shader pass topology — 4 November 2026

**Session:** `A15-20261103T225613-66d7040c`. **Issue:** RENDER-002, bounded original-data recovery, no Unity/native APK build.

## Primary source and verification

Read-only original input `zip2` at immutable commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, staged via the already verified `scripts.w1_stage_zip2_owners` without LFS. Each source file was checked against an independently pinned exact size and SHA-256:
- `Raft_Data/resources.assets`: 111,533,516 bytes, SHA-256 `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c`;
- `Raft_Data/sharedassets0.assets`: 115,978,112 bytes, SHA-256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.

Four total W1 staged owners were reauthenticated (233,281,064 bytes, all cache hits, `lfs_used=false`). A15 decoded exactly these **two** game shader owners (227,511,628 bytes) with UnityPy 1.25.4, reading original `Shader.m_ParsedForm.m_SubShaders[].m_Passes[]`. No raw original ShaderLab programs, names, per-object IDs, code or assets were published.

**Source change:** [392b18f8](https://github.com/alwansan/raf/commit/392b18f85b199645013834ca8e29d1833c7aff21), including new `scripts/a15_probe_original_shader_passes.py`, 10 deterministic synthetic positive/negative controls, and isolated CPU-only `.github/workflows/raft-a15-original-shader-passes.yml`.
**Exact-source Actions:** [run 41735321157](https://github.com/alwansan/raf/actions/runs/41735321157), **COMPLETED SUCCESS**, artifact `13278681723` (`a15-original-pass-aggregate-392b18f85b199645013834ca8e29d1833c7aff21`), 10/10 tests, ZIP2 source authentication, private UnityPy actual serialized extraction and aggregate-only upload successful.

## Actual authenticated original serialized results

| Original owner | Shader objects | Serialized Pass records |
|---|---:|---:|
| resources.assets | 47 | 128 |
| sharedassets0.assets | 58 | 190 |
| **Total** | **105** | **318** |

- Original `SubShader` records: **123**. Per-Shader SubShader-count histogram: `{1:91, 2:10, 3:4}`.
- Per-Shader Pass-count histogram: `{1:41, 2:14, 3:11, 4:23, 5:2, 6:3, 7:4, 8:2, 9:4, 16:1}`.
- Exactly **64/105** original shaders have more than one serialized Pass; no Shader with zero Passes was found in these two owners.
- Checks included invalid/missing parsed forms, invalid/duplicate identities, malformed Pass/SubShader arrays, legitimate repeated path IDs in different owners, and not disclosing private names in the aggregate.

## Meaning, limitations and next engineering action

The genuine serialized original graphics data demonstrates substantial multi-pass source structure within these two specific owners. The separately observed full native preview41687765928 reported 142 parseable loose exported .shader declarations and zero official built-in name matches before Unity. These are **different scoped/staged populations**. One must **not** subtract 142 from 318 or claim 176 missing passes: original serialized Shader objects are not yet individually joined to that same-stage complete loose export, and engine-redirected built-in Shader objects may not export as loose ShaderLab files at all. No claim that full-game exported passes are necessarily lost follows solely from this numeric result.

Next: use exact generated Shader read/name and engine asset mapping from W1's separate work, plus authenticated complete same-phase full export object-to-asset GUID/owner mapping, to establish per-object pass preservation with true provenance. Do not use name guesses or bypass the official built-in zero-match gate; preserve shader program, subshader/pass, material, GUID, color and FFT authenticity. Actual GPU numerical/water/phone tests remain pending.

No original project, metadata, Unity, APK/OBB/XAPK, CL, Releases, LFS or scheduled tasks changed. **RENDER-002/WATER-001/FFT-FORMAT-009 remain OPEN, full game NOT_READY, candidate 0/3 independent reviews.**
