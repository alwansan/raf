# A12 original Subsurface Blur — authenticated pass/stage graph

**Date:** 3 November 2026. **Owner:** A12 `raft-20261103T184205Z-a12d793c` / `feature/android-native-port`. **Issue:** WATER-001, RENDER-002; remain **OPEN / NOT_READY**.

## Owner-requested experimental build failure

[Full native preview 41687765928](https://github.com/alwansan/raf/actions/runs/41687765928) on source `a8e04dd2aa2bfcd8bf449abcbc139745619424fa` **failed before Unity Editor**. Original shader export at that exact stage contained 142 parseable ShaderLab declarations, of which **0** matched the 198 SHA-authenticated Unity built-in shader identities. No APK, OBB or XAPK was delivered. Built-in-shader substitution with guessed names, zero-match bypass, or relaxation of the strict water gate would conceal the blocker. The next mandatory `scripts.verify_water_render_contract --strict` also cannot validate authenticated Unity water kernels and is independently unresolved.

## A12 genuine original water-source experiment

Initial two-owner run [41695272821](https://github.com/alwansan/raf/actions/runs/41695272821) intentionally reported **FAILURE**: the exact original Blur target was absent from the two owners `resources.assets` and `sharedassets0.assets`. An intermediate [41696108919](https://github.com/alwansan/raf/actions/runs/41696108919) failed only because source `--repo` became required before the already-running workflow snapshot was updated; this interface-race is recorded, not misrepresented as source corruption.

The expanded, isolated [A12 CI41696171379](https://github.com/alwansan/raf/actions/runs/41696171379) (source `c8ddf9c3e921757e852929dc3e8d0339ba73927c`) finished **COMPLETED SUCCESS** with **11/11** synthetic red/green source/privacy/pass-graph tests. It inspected precisely all **14** Shader-bearing original serialized owners from W3's independently authenticated 82-owner inventory. Full 14-owner source bytes **488,439,356**, exact SHA/Git-registered identity verified for every owner before UnityPy; **165** original Shader objects re-enumerated. Reused W1's cached two LFS owners and hydrated only the third required original source, not all game data.

This authenticated the original `UltimateWater/Utilities/Blur (Subsurface Scattering)` object:
- Original object SHA256 `c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52`
- Original parsed-form SHA256 `865e5529986469f18fd3158612f925647599e8b5126187be0c87d490ff6d2aa3`
- One original subshader with **two passes**, satisfying the logged minimum pass index1.
- Four genuine serialized vertex/fragment stage programs, **two** exact permutation-matched pass-stage pairs.
- **Four distinct stage programs**, no nonnormal pass, no keyword permutations, no missing pairing or unresolved parameter-table index layout.
- All source/private graphics bytes and original `.meta`/GUIDs unchanged; no private source or HLSL logged/uploaded.
- [Safe aggregate artifact 13260453184](https://github.com/alwansan/raf/actions/runs/41696171379/artifacts/13260453184).

The proven original pass/stage graph is **not yet installed shader source**. It does not validate parameter value meaning, full ShaderLab, Unity compilation, Adreno GPU, original materials, FFT kernels or numerical equivalence. Original WATER-001/RENDER-002/FFT-FORMAT-009 remain open; no build candidate, three full independent readiness reviews **0/3**, project NOT_READY.

## Next independently scoped source action

A12 prepared [private original Blur ShaderLab wrapper code](../scripts/a12_build_original_blur_wrapper.py) and [synthetic refusal tests](../tests/test_a12_original_blur_wrapper.py). It must preserve original two-pass layout, state, vertex semantics and all shader resources, reject unknown property/parameter shapes, privately validate roundtrip programs as Vulkan1.1, and publish only hashes/counts. Passing synthetic tests does NOT mean Unity player program compatibility. The independent CPU workflow is [raft-a12-original-blur-wrapper.yml](../.github/workflows/raft-a12-original-blur-wrapper.yml). Full native build replay of a known-incomplete candidate is not evidence of repaired water.
