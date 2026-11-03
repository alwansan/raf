# A4 PERF-007: Android scene-boundary GPU-memory diagnostic evidence

**Date:** 4 November 2026 (Baghdad local). **Client:** `raft-20261103T095832Z-a4c7e2b1`; **session:** `a4-resume-20261103T224500Z-84e2c91f`. **Writable branch:** `feature/android-native-port` only.

## Previous A4 cgroup correction verified

- Exact-source [memory CI 41658344282](https://github.com/alwansan/raf/actions/runs/41658344282), code/test commit `10563d4622a898ee4e2bcc9631bf4f95e3fcd0b2`, job `125994601312`: **COMPLETED SUCCESS**, log confirms **Ran 10 tests / OK**; three actual monitor samples and 256MiB runner swap-capability PASS. [Same-SHA preflight 41658343421](https://github.com/alwansan/raf/actions/runs/41658343421) SUCCESS. This validates the cgroup sample-continuity parser, NOT phone GPU OOM.

## Current scoped source change and verified CI

- [Code dac7ba8](https://github.com/alwansan/raf/commit/dac7ba8fffd955d9901c4691c9ce35d584c422ba) modifies only `android-port/Runtime/Platform/AndroidTestDiagnostics.cs`: reuses already present `ProcessPss()`, `ProcessRss()`, `AndroidGraphicsMemoryKb()` and `UnityGraphicsDriverBytes()` in a small `GraphicsMemoryAtBoundary()` helper. Scene load/unload and the existing `Application.lowMemory` callback now write scoped snapshots. They are discrete events, not added per-frame JNI allocations. Existing landscape, touch, Xbox, logging, scene identifiers, quality and resource ownership unchanged. The Unity driver counter remains **unavailable** outside development players, and Android `summary.graphics` is a partial per-process metric, not total GPU VRAM.
- [Policy test 74df622](https://github.com/alwansan/raf/commit/74df62250c0f4db1bd5f33981ee22d24ee62934a) adds a negative/positive source-policy case requiring scene loaded/unloaded, lowMemory snapshots, preserving fallback and rejecting additional periodic probes.
- Exact test-head [Android platform CI 41734019524](https://github.com/alwansan/raf/actions/runs/41734019524) **COMPLETED SUCCESS**, source `74df62250c0f4db1bd5f33981ee22d24ee62934a`, job `126258407653`. Log: **10/10** Android diagnostic-policy tests PASS including `test_scene_boundaries_and_low_memory_capture_partial_gpu_counters`; other platform source/test steps PASS. Separate code-head [Android platform 41734013639](https://github.com/alwansan/raf/actions/runs/41734013639) SUCCESS and [offline original startup 41734013814](https://github.com/alwansan/raf/actions/runs/41734013814) SUCCESS on code `dac7ba8...`.
- Two attempts to publish an atomic branch commit were rejected by GitHub GraphQL under rapidly moving HEAD. Fresh source-blob comparison showed no concurrent edits to the two owned files; applied each with GitHub contents optimistic blob-SHA update, without force/ref overwrite. The resulting code and test commits above are the published evidence, not the abandoned object SHAs.

## Limits and follow-up

This fixes a **diagnostic temporal blind spot**, NOT a proven render-resource leak, GPU memory overuse, water rendering, shader/kernel correctness, FPS or Android device stability. Source-policy checks do not compile this Android-only Unity MonoBehaviour in a real Unity Android player. No new APK/OBB/XAPK/Release, Unity build, new LFS, ZIP2 mutation, original source/asset/metadata, scheduler, main/zip/Unity-Editor or CL mutation. Last device game build is still APK80, older than these commits. **PERF-007 gameplay acceptance OPEN; WATER-001/RENDER-002 OPEN; overall NOT_READY, 0/3 readiness reviews.**

Next prove a concrete original GPU resource allocation/teardown defect with private authenticated source and executable harness, avoiding overlap with A1/W1/W2/W3; use the added event-boundary logging only after a legitimately coordinated later device build.
