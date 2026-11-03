# W1 exact generated-reader and embedded engine mapping — 4 November 2026

W1 identity: raft-20261103T162900Z-73e8c2a1. Only feature/android-native-port is writable. This supersedes the unresolved generated-name/embedded-database part of W1's preceding ZIP2 diagnostic; it does not certify the full export or rendering.

## Verified result
[CPU run41736103335](https://github.com/alwansan/raf/actions/runs/41736103335), exact source7eed8dbada2472e928be14eb860d1f7dd672cee2, job126265602490, artifact13278408659: **COMPLETED SUCCESS**.

The actual AssetRipper.SourceGenerated1.3.2.0 assembly selects Shader_2021_3_35 for Unity2021.3.45f2. Reflection of the actual ReadRelease and ReadEditor method bodies proves their final instruction sequence copies m_ParsedForm.m_Name into m_Name. Thus empty raw names seen by UnityPy do not imply the runtime exporter has no shader name. Assembly SHA256:7aedba39a03b7d3fa4837a4a47fb2795780c1670a71b2c4dbca88613b8d231fd.

The same assembly's actual EngineAssetsTpk stream was decoded with the pinned CLI's Tpk1.1.0 and Mining.PredefinedAssets1.5.0 packages and the exact version-selection algorithm. Dataset selected for the target:2021.2.0b14;6default+190extraShaderrecords. TPK SHA256:be9863e90b424b3cbe42caea675e5ae36179d62df2c55d41ef19d217992a8b12. Selected JSON SHA256:72370e5ba37150a4cba193a5c5eca7ebfaece93f97730b5405e9152100c4fc93. This is the exact tool's selected database, not a fabricated2021.3database or the incomplete raw canonical-owner typetrees.

Two original game owners contain105Shaderobjects. All9objects whose names match the SHA-authenticated official Unity2021.3.45f2 built-in archive also match **exactly one** actual embedded engine key by name AND ordered property list.96other keys do not match. All18wrong-name/wrong-property controls were detected;5new synthetic positive/negative/privacy-schema tests passed,37localW1tests passed. Raw private engine names, file IDs and original shader programs were not uploaded.

## Reproducibility and repaired tool setup
The SourceGenerated internal package declares no NuGet dependencies and runtime reflection initially failed to find AssetRipper.Assets1.3.1.0. Run41735797767 failed before any original shader comparison; it is not renderer failure. The probe now builds the host AssetRipper.Assets/IO.Files model from the exact CLI commit036098ab525a3f9f693dc101edeb21faad4d32d8, matching its1.3.3host model and unchanged1.3.2generated library. No shader identity check was relaxed.

All4original ZIP2 owners were reused from W1's cache and reauthenticated against their independent sizes/SHA256 (233,281,064bytes total); lfs_used=false and all4cache_hit=true. ZIP2 remains pinned15964ea8f246b6e076ce26b60931ee2e1a9a2385, read-only. No original resource/GUID/material source was overwritten.

## What this establishes
Pinned exporter source EngineAssetsExporter+PredefinedAssetCache+SingleRedirectExportCollection redirects matching shader objects into engine pointers and emits no loose.shader. The exact reader and database now account for all9official-name shader objects in this two-owner sample. This is a justified explanation to investigate for the old native export's zero-loose-builtin matches. It does NOT by itself verify all165original game shaders, actual full-exportMaterial PPtrs, Unity's current engine IDs, Android compilation, on-device material colors or water.

The production zero-match gate and strict water/FFT gate remain unchanged. No full native retry or request was made. Native41687765928 remains FAILED beforeUnity/noXAPK. NOT_READY, full immutable-candidate reviews0/3.

## Bounded Unity follow-up
Owner-authorized targeted experiment [41737038201](https://github.com/alwansan/raf/actions/runs/41737038201), immutable sourcebe740083d8faeea55ed2ba030cceea0d239e5f60, validates9positive original engine-pointer materials against9different-valid-pointer controls, original property layout, and an AndroidVulkan-only material bundle in Unity2021.3.45f2.30mincap,12GiBDocker,20GiBdiskgate, shared raft-native-engine mutex, cancel-in-progress:false/queue:max. No gameproject/APK. Its result MUST be inspected live; launch is not evidence of binding success. Only reader/mapping/Unity aggregate summaries are uploaded; private dataset, expectednames, materials and bundle stay private.

Next: inspect actual Unity binding/property counts and compilation. If successful, verify the complete real export's engine-material references and original shader inventory before correcting the zero-loose-match rule; water/FFT authenticity remains separate. Do not repeat unchanged full native or the already completed CPU mapping.
