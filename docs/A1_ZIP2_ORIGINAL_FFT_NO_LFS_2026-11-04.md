# A1 — authenticated ZIP2 no-LFS FFT source recovery and executable verification

**Date:** 4 November 2026 (Iraq local; run UTC 3 November). **Writable branch:** `feature/android-native-port`. **ZIP2 read-only source SHA:** [`15964ea8f246b6e076ce26b60931ee2e1a9a2385`](https://github.com/alwansan/raf/tree/15964ea8f246b6e076ce26b60931ee2e1a9a2385/Raft). **A1 identity:** `raft-20261103T222730Z-a17b2c91`.

## Actual source recovery

Original Raft source is available in the owner-provided `zip2/Raft` without Git LFS. In `zip2`, the authentic `Raft_Data/sharedassets0.assets` is a *directory* containing `part-00000` (47,185,920 bytes), `part-00001` (47,185,920 bytes), and `part-00002` (21,606,272 bytes) plus README, not a directly loadable Unity `.assets` file. `RAFT_FILE_MANIFEST.tsv` separately pins **115,978,112 bytes** and SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` for this resource, matching A1's previously authenticated original FFT owner pin.

A1 added `scripts/stage_zip2_fft_owner.py`. It parses the ZIP2 manifest and requires the *independently pinned* original SHA/size; checks all three chunk names and full/intermediate chunk lengths, rejects symlinked parts, extra/missing parts, wrong manifests and mismatched hash, and atomically stages only a checked restored file into an **isolated runner temporary directory**, never over an existing LFS pointer or original source. Negative/positive synthetic fixtures `tests/test_stage_zip2_fft_owner.py` cover corruption, chunk permutation, missing/extra chunks, symlinks, manifest mismatch and no-overwrite.

**Source changes:** [scoped ZIP2 helper `eac1f62caf79`](https://github.com/alwansan/raf/commit/eac1f62caf7960357568535bbd91a84ca338a9a3), [10 tests `c1ff199162ef`](https://github.com/alwansan/raf/commit/c1ff199162eff751b94fc6eac2fae272123dc805), [A1 workflow provider migration `14ba21e93af3`](https://github.com/alwansan/raf/commit/14ba21e93af3dac3623265a9230afeccea6986ce).

## Runner acquisition method

The existing `.github/workflows/raft-a1-fft-software-vulkan.yml` now checks out just A1 diagnostic scripts/tests on the feature branch. A **separate sparse Git partial checkout** fetches read-only `zip2` pinned `15964ea8...` with `--filter=blob:none`, then restores *only* three `sharedassets0.assets/part-*` chunks and `RAFT_FILE_MANIFEST.tsv`. It verifies checkout HEAD == pinned SHA **before** staging. No `git lfs install`, `git lfs pull`, full 7.79GB checkout, original game asset replacement, or Unity import is performed. Existing original source validator independently rechecks the staged binary, and the *unchanged* private A1 FFT pipeline then authenticates the object at `pathID=2456` by raw-object SHA `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`.

## Verified real GitHub Actions outcome

[GitHub Actions run **41731607739**](https://github.com/alwansan/raf/actions/runs/41731607739) **COMPLETED SUCCESS** on exactly source `14ba21e93af3dac3623265a9230afeccea6986ce`. Jobs:

- **126250116759 synthetic-vulkan-canary SUCCESS:** pre-existing A1 bounded result schema 8/8; new ZIP2 staging synthetic tests **10/10**; actual CPU Vulkan known-addition positive and intentional subtraction negative controls both detect the expected outputs.
- **126250329499 authenticated-original-fft-on-software-vulkan SUCCESS:** Git sparse original ZIP2 source pin printed `15964ea8...` and `original_git_lfs_used=false`. Atomic reassembler reported **3 chunks**, **115,978,112 reconstructed bytes** and **exact independently pinned SHA256**. Original source validator passed. Python tests **8/8 +10/10** again. Original `ComputeShader/pathID2456` was SHA authenticated; **20/20** compiled FFT original-versus-roundtrip SPIR-V pairs executed, across **3 deterministic RGBA32F workload/dispatch scenarios each = 60/60** matched written pixels and numerical output, **maximum absolute difference=0, maximum relative L2=0**, zero inconclusive cases and no mismatched write coverage.

This establishes that ZIP2 is an authenticated **no-LFS replacement for A1's original FFT input**, not that Git LFS is empty or unusable for unrelated paths. The original software Vulkan comparison had already succeeded via authenticated LFS at source `3406dd12`; this run independently confirms same original hash and numerical behavior from the new source provider.

## Scope limits and next real restoration

This exact-source outcome is CPU Mesa lavapipe Vulkan on RGBA32Float images. It does **not** prove original Unity runtime kernel index selection, `RGHalf/RGFloat/ARGBHalf` resource equivalence, true full two-pass FFT water rendering, ShaderLab pass/CB/texture semantic recovery, physical Adreno GPU, or installed Android visuals. Reassembly verifies the one FFT owner, **not all 7.79GB**, and does not automatically migrate workflows owned by other clients. Existing `feature/android-native-port/Raft` LFS pointers must remain until individual consumers can be safely migrated. Existing signed APK80 does not include this source change.

**WATER-001, RENDER-002, FFT-FORMAT-009 and other real blockers remain OPEN, game NOT_READY, independent full immutable-candidate reviews 0/3.** A1 did not change `zip2`, `main`, `zip`, `Unity-Editor`, CL, `.meta`/GUIDs, original assets/.rgd, input Mouse0/500ms/UGUI/Xbox, native build requests, scheduled tasks, Unity/APK/OBB/XAPK, signing or Releases.

**Next:** use similarly authenticated ZIP2 sources to recover the actual Unity shader/material/water kernel binding contracts and test RGHalf/ARGBHalf precision, coordinating with W1/W2/W3's original graphics recovery; do not claim feature completeness from source acquisition alone.
