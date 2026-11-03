# A3 RENDER-002 — fail-closed Unity built-in shader path redirection (2026-11-03)

**Scope:** Independent CPU-only safety repair for `scripts/restore_builtin_shaders.py`. Preserves strict original ShaderLab identity/zero-match behavior, original .meta/GUID and vendor SHA verification. No new Unity/native import, APK/OBB/XAPK, release, LFS, original game/shader payload, CL writes or scheduled task changes.

## Confirmed red/green experiment

- **RED source** [e62aedc](https://github.com/alwansan/raf/commit/e62aedc662eb5be9c2c937c1cec2ae908d40557c) [CI41633814002](https://github.com/alwansan/raf/actions/runs/41633814002), job125909790423, **FAILED as expected**: 3/4 synthetic real `restore_project` tests saw `ValueError not raised` when `Assets`, `Assets/StreamingAssets` or `Assets/RaftAndroid` was a symlink to outside the Unity project. Normal nonlinked fixture passed. This proves filesystem redirection in the synthetic setup, not presence of malicious links in the owner's game export.
- **GREEN source** [d93f6aec](https://github.com/alwansan/raf/commit/d93f6aecac8214057debfc1d18eda85b6fa50ce1) adds `_require_safe_asset_path` to check each existing component from Unity `Assets` root to every source shader, accompanying .meta and prospective include/license destination **before backup or write**. Rejects symlinked roots/parents and out-of-root path resolution; existing unmapped ShaderLab names still fail closed.
- [A3 CPU CI41634098552](https://github.com/alwansan/raf/actions/runs/41634098552), job125910766378 **COMPLETED SUCCESS** on the exact fix SHA: **4/4** new A3 tests, **4/4** previously authored A9 declaration-identity tests, **10/10** existing built-in restorer fixtures.
- [Separate A9 workflow CI41634098651](https://github.com/alwansan/raf/actions/runs/41634098651), job125910766652 **SUCCESS** on same SHA, retaining the four and ten safeguards.
- [Official Unity vendor CPU CI41634098559](https://github.com/alwansan/raf/actions/runs/41634098559), job125910766341 **SUCCESS** on same SHA: authentic Unity2021.3.45f2 archive SHA verified and 198 built-in shader identities; five synthetic project shader matches, 29 includes, .meta unchanged, custom sources untouched. No private game shaders published.

## Limits / next checks

This closes the **specific filesystem-symlink redirection** source-tool defect. The earlier actual native [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951), based on **older source**, failed before Unity with *zero matching exported built-in identities*. No retry was made and this guard does **not** create those matches, restore UltimateWater FFT, prove ShaderLab custom pass compatibility or verify graphics/device output. The function performs pre-copy checks, not an atomic defense against a concurrent attacker changing filesystem links after validation. The legitimate build workspace must contain real (non-symlinked) Assets paths.

Global RENDER-002/WATER-001/FFT-FORMAT-009 remain **OPEN**; candidate source SHA absent, independent full readiness reviews **0/3**, overall **NOT_READY**. Future work: authenticate actual exported shader identities and real program/pass/material restoration before coordinator-authorized Unity/native delivery, not weakening strict gates.

## Coordination

A3 continuation `raft-20261103T120645Z-8cde319a` was registered before work and read completed A9 `raft-20261103T113735Z-a93e6c40` source and scope. Only shared production file `scripts/restore_builtin_shaders.py` changed after a live expected SHA check; A9-owned tests/workflow, owner branches, and all originals were left untouched. Source commit used file-blob compare-and-swap via GitHub contents after a parallel-HEAD conflict, with no force or rollback. A3 isolated test/workflow paths and discussion/experiment provide red-green evidence.
