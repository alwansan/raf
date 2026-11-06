# T5 — Actual original signed main OBB Jar resource paths for FMOD and Haptics

**Worker:** T5; **session:** `20261106T1541Z-T5-chat-obb-routes-b8a1`, `origin=chat`, **issue:** INTEGRATION-001, writable branch `feature/android-native-port` only.

## Context, provenance and why this differs from prior tests

The owner confirmed world entry/save/exit/re-entry using artifacts of [native build 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) at immutable source `e9c358eda01785b65e4eb14f18723da426635628`. Earlier [CI42228262902](https://github.com/alwansan/raf/actions/runs/42228262902) verified complete old signed APK SHA and v1/v2 signature, [CI42230326050](https://github.com/alwansan/raf/actions/runs/42230326050) hashed all **2,301,256,312 bytes** of the original signed main OBB and matched its source delivery SHA256 + outer CRC32, and [CI42243852483](https://github.com/alwansan/raf/actions/runs/42243852483) found `assets/unity_obb_guid` **in APK only** (not the companion OBB). The six owner CL log blobs [CI42119428667](https://github.com/alwansan/raf/actions/runs/42119428667) recorded 3 **optional patch.89** OBB GUID warnings, 0 main OBB GUID warnings.

**New question:** whether the *actual signed OBB ZIP* has exactly the `assets/<name>` FMOD bank and `assets/Haptics/<name>` WAV entries that the existing production `AndroidFmodBootstrap`, `AndroidFmodBankLocator`, and `AndroidStreamingAssets.ReadAllBytes` request. Earlier source haptic tests validated original WAVs in constructed temporary archives, and earlier whole-file SHA verified the outer OBB identity; neither result by itself measured this exact runtime asset-path inventory inside the actual old signed OBB.

## Genuine source verdict

[CI42248117179](https://github.com/alwansan/raf/actions/runs/42248117179), job `127995625188`, source commit `6c4c7363b703cb0e0aa4d8940f0d5afd550afd75`, **COMPLETED SUCCESS**:

| Actual signed main OBB member property | Source-pinned result |
|---|---|
| ZIP member count | **39** |
| Exact `assets/<bank>` entries required by Android FMOD bootstrap | **5/5 present** |
| FMOD entry uncompressed lengths match `AndroidOriginalBankIdentity` | **5/5 true**, combined **123,817,498 B** |
| Exact `assets/Haptics/<wav>` entries against pinned source manifest | **29/29 present** |
| WAV entry uncompressed lengths match immutable Git-blob-anchored manifest | **29/29 true**, combined **32,733,104 B** |
| Entries prefixed `assets/bin/Data/` with nonzero Unity data | **1** |
| Largest Unity data entry over **128 MiB** audio-reader bound | **true** (this audio helper is **not** the Unity bulk asset reader) |
| Largest Unity data entry over **Java 32-bit array bound** | **false** |
| Required archive paths and indexed local headers | **pass** |
| Synthetic positive/negative source-free controls | **17/17 passed** |
| Raw original remote bytes needed for metadata scan | **6,991 B** via **86** HTTP 206 range requests |
| Full FMOD/Unity resource payloads individually hashed in **this** scan | **NO** |
| Original complete OBB source payload hash | independently previously verified by CI42230326050 |
| Device mounted OBB, actual FMOD audio events/haptics, Unity graphics | **NOT TESTED** |

The *outer GitHub signed-checkpoint ZIP member* basenames did **not** literally match the logical names from `delivery.json` (`outer_signed_apk_member_basename_matches_delivery=false`, likewise OBB). This is **a wrapper/transport member-name distinction, not proof of wrong installed package version or damaged bytes**: the exact immutable GitHub artifact ID, run, source SHA, byte sizes, member types, and already-verified whole signed APK+OBB payload hashes anchor the old source. The verifier records the difference without silently assuming the transport ZIP basenames are the Android deployment filenames. It does **not** change the actual `main.89.com.alwansan.raft.androidtest.obb` logical delivery contract.

### First failed source gate, precise correction

- [CI42247829378](https://github.com/alwansan/raf/actions/runs/42247829378) passed **17/17 tests** then blocked the *real* original metadata probe at `original_signed_checkpoint_member_drift`: first version incorrectly required the GitHub transport ZIP member filenames to be literal delivery filenames.
- The corrected probe still enforces two unique APK/OBB source members, their exact old byte lengths, unencrypted STORED local headers, authenticated immutable artifact source and strict ZIP bounds; it **separates** outer wrapper basename parity as truthful booleans. [CI42248117179](https://github.com/alwansan/raf/actions/runs/42248117179) then passed real source + all 17 tests. No signed game artifact or actual OBB content was edited.

### Implementation and privacy

- New isolated `scripts/t5_probe_signed_obb_asset_routes.py`, `tests/test_t5_probe_signed_obb_asset_routes.py` and `.github/workflows/raft-t5-signed-obb-asset-routes.yml` using only pinned original Haptics `config/original-haptics-manifest.json` Git blob SHA **88df20f0c64ae5f46f057939d4d6d96773a33ef8** and exact five original FMOD bank lengths from production source `AndroidOriginalBankIdentity.cs`.
- Reads only the signed checkpoint's original OBB ZIP central/local member metadata through bounded original `ZIP_STORED` archive ranges. **16 MiB** maximum read budget; no original 2.3GB OBB download, no original WAV/Bank/game binaries checked out or written to disk, no original resource payloads printed, no credentials/redirect URLs uploaded.
- Tests reject fake/absent/case-mismatched paths, shadow names, duplicate/traversal entries, missing Unity data, changed bank/WAV size, local filename corruption, unacceptable outer compression, source size drift, invalid manifest and range-budget bypass. This is genuine original **path and uncompressed-length parity**, **not** runtime readability or Unity game logic validation.

## Interpretation / next engineering boundary

This narrows the old phone ambiguity: the owner-tested signed OBB physically **contains the exact indexed FMOD and Haptics audio paths requested by RaftAndroid's source loader**. Source packaging does not support a missing-original-`assets/Haptics` or missing-bank-`assets/MasterBank.bank` hypothesis for *these archived bytes*.

**Still unproven:** Android's actual installed `main.89` file path/size/full SHA, `getObbDir()` return, Android storage permissions, `Application.streamingAssetsPath` at runtime, actual `AndroidStreamingAssets.ReadAllBytes` success on the phone, FMOD event and haptic sound behavior, Unity C++ OBB mounting, game scene resource GUID binding, water/FFT/shaders/material and device frames. Do not equate a valid ZIP member with a valid device file or create a fake optional `patch.89` OBB. The separate Unity `assets/bin/Data/` entry exceeds the **128MiB audio-only reader cap**, and **must not** be routed through that audio helper; Unity consumes bulk game data through its own loader.

Next discriminating action: correlate exact *device* main OBB SHA/size and `AndroidRuntimeLog` categories `audio/fmod.bank_root`, `fmod.expansion_bank.*`, real `AndroidStreamingAssets` errors, and Unity `jar:file:/...obb!/assets/bin/Data/...` read outcome on a shared session. If no new device evidence is available, assist T1/T2 WATER-001 and T3 RENDER-002 original shaders without re-running successful old source provenance checks.

**Game readiness remains `NOT_READY 0/3`, owner-tested old source only.**
