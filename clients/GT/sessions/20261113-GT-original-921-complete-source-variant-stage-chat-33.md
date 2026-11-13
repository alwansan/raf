# GT Chat-33 — Full source-only recovery of the 921-slot Shader48 original variants (2026-11-13)

**Agent GT** · Writable branch `feature/android-native-port` only. Read `clients/GT/OWNER_DIRECTIVE_RESTORE_FIRST_AR.md` FIRST. ZIP2 immutable `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; no LFS, no invented/changed .meta or GUID. No new full APK/OBB/XAPK or compatibility test.

## Exact completed work

- Added `scripts/gt_original_921_all_variants.py` and `tests/test_gt_original_921_all_variants.py`; added dedicated source-only workflow `.github/workflows/raft-gt-original-921-all-variants.yml`. Commits `8111c074`, `e68c1871`, `d5a2ccad`.
- **[CI43357332292 SUCCESS](https://github.com/alwansan/raf/actions/runs/43357332292)** checked out SHA-pinned ZIP2 read-only, reconstructed four original Shader owners (269,007,288 bytes), verified six genuine scenes, and passed 7 synthetic negative/positive tests before using original UnityPy assets.
- Source-selected the uniquely highest-use original Shader48 with exactly 921 Renderer Material slots in the six-scene sample. Authenticated **4/4 original Passes**, **33 exact VS/FS variant permutations paired by player bucket + hardware tier + keyword indices**, **8 genuine unmatched vertex variants** (not silently fabricated fragment programs), and **58 unique original D3D11 program binaries**.
- **58/58 original DXBC stages passed Vulkan 1.1 validation, HLSL extraction, and HLSL→SPIR-V Vulkan1.1 round-trip** via vkd3d-compiler, spirv-cross, glslangValidator, spirv-val. An original-pass/variant/metadata linkage manifest and all recovered stages were placed ONLY in runner-private scratch, then deleted by cleanup; uploaded safe counts only as Artifact **14006268247**.
- This is **not** original ShaderLab equivalence or game-project restoration: 4-Pass Authored ShaderLab, fixed render states, all original Properties/Keywords, texture/sampler/CB0 register wiring, same-export Shader .meta/GUID replacement and full 770 Dummy Material recensus all remain OPEN. Unity Editor compile and Adreno pixel correctness NOT verified.

## Remaining owner-directed restoration, in order

1. Use the persistent recipe to generate a 4-Pass shader from the **complete** 33 private stage pairs, recover exact source keyword routing/pass state/Property and Sampler/CB0 registers (preserve eight unmatched original VS variants explicitly), and prove no silent variant omission.
2. Integrate into an existing SHA source→same-export **original Shader GUID** without altering .meta, then run actual full-source postvendor Dummy Material census (baseline 770 documents, not 770 distinct Shaders). Verify Renderer→Material→Shader and Texture/Sampler links; do not claim fixed white raft before evidence.
3. Repeat by original source Shader identity for other affected materials and all 165 Shader objects; finish Spectrum/Foam/Depth/FFT/9 ComputeShader, Mesh/Texture mip/rig/animation/fire/particles/shadows/PostFX/TMP before G0–G6.
4. **Never request first comprehensive Android XAPK until restoration and integration done**, per owner directive. Source-only/isolated Shader tests are allowed.

**Persistent records:** `clients/GT/state.json` proof Chat33; `RESTORATION_PLAN.json` P04/P05 evidence; `RESTORATION_PLAN_AR.md`, `SUMMARY_AR.md`, `MEMORY.md`, `RESTORE_AR.md`. No original program bytes or protected game identifiers in public logs.

## Source keyword/property lineage follow-up (same Chat33)

- [CI43358097452 SUCCESS](https://github.com/alwansan/raf/actions/runs/43358097452): extended runner-private packet to preserve **entire source ParsedForm**, all original source Shader properties, keyword names and flags; numeric receipt reported 27 names and 35 Properties, 58/58 HLSL/Vulkan11 unchanged. Temporary synthetic CI43358094762 failed because tests had not yet received new required input; next commit corrected tests; that red run did not reach original source, and is not a genuine Shader fault.
- [CI43358489426 SUCCESS](https://github.com/alwansan/raf/actions/runs/43358489426): eight synthetic positive/negative tests plus real ZIP2 stage. Verified 27 original Keyword Names, 27 Flags, **14 distinct used source keyword indices** across 74 original program metadata records, all in source name-table bounds, one source player bucket, 35 original source Property definitions; 58/58 genuinely round-trip Vulkan1.1. Source/global/local pragma flags and Sampler/CB0 remain UNKNOWN. Current restoration-stage proof is **not** same-export original ShaderLab or Android game integration.
- Script follow-up commits `04cb3590`, `947f0297`, `d5c2ccef`, `d8af7ad8`; source-only CI does NOT produce any XAPK. Latest next action: build source-original keyword state router for all four Passes; prove original register/sampler/permutation topology, compile isolated ShaderLab; install only in existing source-export GUID, then re-run full 770 Dummy Material census.
