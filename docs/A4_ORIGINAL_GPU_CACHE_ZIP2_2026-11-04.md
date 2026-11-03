# A4 — Original ZIP2 GPU cache allocation and release paths

**Client:** A4 (`raft-20261103T095832Z-a4c7e2b1`); session `a4-resume-20261103T231050Z-7d96e2a1` on `feature/android-native-port` only. No native build, original-game asset edit or ZIP2 branch write.

## Authenticated original input and prior mismatch

Read only owner-supplied immutable ZIP2 original commit [15964ea8](https://github.com/alwansan/raf/tree/15964ea8f246b6e076ce26b60931ee2e1a9a2385/Raft). Independently rechecked manifest exact entry and full `Assembly-CSharp.dll` bytes: **3,211,776 bytes**, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. No Git LFS or 7.79GB checkout: Git sparse partial retrieval of this one DLL and manifest. Pinned `ilspycmd 11.2.0.10050 -p -lv CSharp9_0` privately decompiled original to the runner temp directory, never published the private output.

The earlier source-script cache SHA `4157076c3e4bddc27ac5b24da768d29ff9e6c227c4da07a9e2f55ae9ff6b8245` did **not** match these verified and pinned decompiler bytes. [First CI41737632456](https://github.com/alwansan/raf/actions/runs/41737632456) failed closed; [hash-only CI41737805027](https://github.com/alwansan/raf/actions/runs/41737805027) safely measured the current output source SHA256 `44af5fbb2e0bf9d08de9a4848fd33d62604e52247aaa0ae3c0f0588428d0dc0b`. The old/new text discrepancy's precise cause is unknown, **not proof of a changed binary**. [Pinned tool output patch24c0a0c](https://github.com/alwansan/raf/commit/24c0a0c28e996c8b529b6c60b96ed466d1216cfb) retains source hash fail-closed while requiring the independently authenticated original DLL provider.

## Actual original cache lifecycle structural evidence

[Exact-source GitHub Actions41737956653](https://github.com/alwansan/raf/actions/runs/41737956653) **COMPLETED SUCCESS** on source `24c0a0c28e996c8b529b6c60b96ed466d1216cfb`: six synthetic false-positive/negative source-guard tests PASS plus original CSharp9 source-check. Original `RenderTexturesCache` analysis returned **one** `new RenderTexture` site, **one** `.Create`, **two** `.Release`, **two** `Destroy`, **two** `.Dispose`, **one** `.Clear`, **one** `GetCache` callsite and **two** `GetTemporary` method categories in **eight** relevant methods. The `Release` method is among the original cleanup paths. No `finally` appeared in the analyzer's bounded matched cache methods.

These are masked-source lexical and structural observations, not proof all allocation branches release, that Unity calls cleanup on every scene reload, a leak, or sufficient memory capacity. `Release` may run elsewhere through callers, and errors may propagate. The game previously exhibited a *separate* direct phone GPU-memory OOM with an older APK; no current patched device runtime was executed. Do not remove water resources or force texture resolution reduction based on these counts.

## Follow-up caller ownership

Added `scripts/a4_gpu_cache_owner_callpaths.py` plus five independent synthetic tests to inspect original FFT owner types for typed-cache Release/Dispose callsites and Unity lifecycle callbacks, reporting counts and source hashes but no original identifiers/source. Follow-up [source-owner CI41738337389](https://github.com/alwansan/raf/actions/runs/41738337389) **COMPLETED SUCCESS** on SHA `098867a7678b31f115f2fbace8771e9ff6821e66`. Five original owner files were located and SHA recorded: `RenderTexturesCache`, `GpuFFT`, `Dx11FFT`, `WavesRendererFFT`, `WindWaves`. Original `GpuFFT.Dispose` contains a destroy call; `WavesRendererFFT.Dispose` includes 5 Destroy and 3 Dispose expressions, while `WavesRendererFFT.OnDestroy` has **no direct dotted member-call** caught by that first generic inspector. That alone does **NOT** mean OnDestroy neglects cleanup.

Crucial disambiguation: the independent [explicit OnDestroy->Dispose callgraph CI41738673806](https://github.com/alwansan/raf/actions/runs/41738673806), source `20a7dbd8d1c2a6e81f439c531f8e421383b83ed8`, **COMPLETED SUCCESS**. Five adversarial synthetic tests PASS, plus authenticated ZIP2 CSharp9 analysis of `WavesRendererFFT.cs` SHA256 `2db9943277431ae23930e7ef0753a4575466ab7d68f5df435871724c1270d276`. Its `OnDestroy` contains **one direct unqualified local `Dispose()` call**, and the same-class lexical graph reaches the declared Dispose method in two nodes (source has 23 method names). The first tool's dotted-member-only pattern therefore caused an **observability blind spot**, not an established missing release call.

**Engineering decision:** do **not** inject another `Dispose()` into OnDestroy. It is already present in original CSharp9; an extra call could double-release. This source evidence does not establish runtime invocation timing, actual exception safety, idempotence, scene-load memory behavior or mobile GPU VRAM totals.

## Limits and next engineering decision

Original binary input authenticated; original GPU cache allocation/release methods structurally located. **Concrete GPU lifetime defect, repeated allocation/scene survival, exception-safety and actual phone VRAM use remain UNKNOWN** until caller/behavior evidence. No Unity Editor, APK/OBB/XAPK/release, original .meta/GUID/.rgd, water/shader/material changes, memory quality degradation, new LFS, CL mutation or scheduled task change. Only feature branch scripts/tests/workflow/coordination/docs edited. **WATER-001, RENDER-002, PERF-007 OPEN; NOT_READY, 0/3.**

Next: run a source-locked executable exception/repeated-scene resource-lifecycle harness and inspect allocation transfer. The direct OnDestroy→Dispose source call is already confirmed: do not inject duplicate Dispose. Avoid overlapping A1/W1/W2/W3 FFT/shader work.
