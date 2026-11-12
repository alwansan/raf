# GT / Chat-19 — recovered genuine native Raft APK+OBB+XAPK, started latest native rebuild

- session_id: GT-20261112-CHAT-19-SIGNED-NATIVE-RECOVERY-AND-CURRENT-BUILD
- origin: chat
- only writable branch: feature/android-native-port
- original source: ZIP2 pinned SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, NEVER Git LFS.
- Owner stopped T1–T5; GT independent.

## 1. The actual native APK/OBB were completed — packaging disk issue, not Unity

[43205543533](https://github.com/alwansan/raf/actions/runs/43205543533) original run source commit `c86809380ab1e5b95ccf65e30074422a7e744c05`, run number **100**. Its Unity 2021.3.45f2 Android import, ARM64 IL2CPP, original stream audio and native packaging audits ran to completion; source-audited **signed APK** 672,892,355 bytes, SHA256 `2d19627cc38831dec9d4f43463e514a9ad74f81473d7df493401babdc498dd58`; OBB **2,320,414,462** bytes. `apksigner verify` passed, APK structure arm64-v8a/IL2CPP/FMOD passed; original 36 StreamingAssets matched from APK or OBB. Runtime graphics/audio/installation on the owner's Adreno phone NOT proven.

Original run failed specifically in `Package complete owner-authorized APK OBB and XAPK delivery`: `ValueError: Insufficient free disk for complete loose outputs and XAPK` from `scripts/package_android_delivery.py`. It had already saved exact signed outputs as artifact [13954722601](https://github.com/alwansan/raf/actions/runs/43205543533/artifacts/13954722601) and recovery copy [13954832459](https://github.com/alwansan/raf/actions/runs/43205543533/artifacts/13954832459). Do not rerun old Unity merely to copy these files.

## 2. Fresh-runner complete lossless native delivery recovered, confirmed success

Created separate [checkpoint repackage workflow](../../.github/workflows/raft-native-signed-checkpoint-repack.yml), initial `1a64affbdf91105ecea805dc546bf3c78d467844`; first CI [43245809743](https://github.com/alwansan/raf/actions/runs/43245809743) failed source-only synthetic because the sparse checkout omitted the original native Workflow file used by two tests. Fixed targeted checkout [1ed04dd0](https://github.com/alwansan/raf/commit/1ed04dd0669a1d2ba50dbb303b47ebdb23fd25ce). Repeat [43246196803](https://github.com/alwansan/raf/actions/runs/43246196803) **SUCCESS**:
- All 17 actual delivery regression tests passed.
- Downloads signed APK/OBB from original native 43205543533 exact checkpoint; authenticates expected APK byte length, SHA256, OBB byte length, checks `aapt` package/version code **100**, `apksigner` signature.
- Repackages without Unity, without changing original APK/OBB into loose APK, OBB and XAPK plus lossless transport/reassembly; `scripts.package_android_delivery` internally performs ZIP CRC/safe path inspection and source↔XAPK strict check.
- `RAFT_ANDROID_DELIVERY` marker: `logical_files=3`, `transport_parts=7`, `companion_required=true`, `lossless_transport=true`, `device_install_verified=false`.
- Uploaded complete [artifact 13957022329](https://github.com/alwansan/raf/actions/runs/43246196803/artifacts/13957022329) name `raft-native100-recovered-apk-obb-xapk`, archived size **5,986,632,846 bytes** (contains original standalone APK/OBB **plus** XAPK transport; duplication intended). Artifact retention 3 days.

IMPORTANT: source snapshot `c8680938` predates newer GT 9/28/416/50 combined strict gates, Particle108 unbound Vulkan probe, post-build cleanup and latest merges. It is not “all shader/material originals recovered” or all water complete. Around **770 custom Shader Material docs remain Dummy** after approved vendor restores. Original full graphics runtime and device test remain open.

## 3. Fixed future packaging and launched genuinely updated native full build

Added [post-build safe cache removal](https://github.com/alwansan/raf/commit/a1de8f53a78470d952225feda2d16534b1ae861c) **only** to native job step after signed output was checkpointed: deletes `$GITHUB_WORKSPACE/unity-candidate/Library` generated import/IL2CPP cache, provided project and Library are not symlinks, and verifies signed APK still present. Does NOT remove original source, scenes, GUIDs, .meta, APK or OBB. This addresses old runner disk exhaustion before XAPK. Does NOT yet prove enough free disk on next native run.

Owner-authorized latest build request updated `.github/raft-native-build-request.json` by [5b3ddd67](https://github.com/alwansan/raf/commit/5b3ddd674993888dc83bf75586c154e674e2d631) containing valid `[raft-native-build] [raft-device-test]` markers, `requested_from_sha=a1de8f53a78470d952225feda2d16534b1ae861c` and new unique request ID. [Latest native full run **43247161671**](https://github.com/alwansan/raf/actions/runs/43247161671) started in progress. Do NOT claim APK/OBB/XAPK produced by 43247161671 until final signed outputs and package audits pass. Avoid duplicate active native runs. No Git LFS.

## 4. Parallel graphics source proofs already known

[43236578305](https://github.com/alwansan/raf/actions/runs/43236578305): real Unity Android Vulkan Shader AssetBundle compile success, four original-derived variants, **approximate** inline Linear/Repeat SamplerStates. [43242496576](https://github.com/alwansan/raf/actions/runs/43242496576) isolated approximate on-phone Vulkan ARM64 APK SUCCESS (15,767,382 bytes, user provided direct download), not original Material parity. [43243957499](https://github.com/alwansan/raf/actions/runs/43243957499) original DXBC 10 sample instructions, each samplers declared, 0 matched common serialized texture slots. [43245047056](https://github.com/alwansan/raf/actions/runs/43245047056) original source metadata census showed 8 variant blob references, 0 stage-common texture/sampler rows; strict original material runtime mapping remains unproven. Do NOT weaken fail-closed mapping gate.

## Next

1. Check new native run 43247161671. If packaging fails, use existing signed-output checkpoint and proven repackage workflow without rerunning Unity.
2. When user tests true native snapshot 100, request screenshots/logs of offline world, water, sounds, colors, FPS/controller, distinguish source snapshot from latest.
3. Continue source-authentic shader and per-variant blob/texture mapping work; no guessing based on descriptor slot coincidence. Keep (9/28/416/50) source parity and scene/Material/GUID checks.
