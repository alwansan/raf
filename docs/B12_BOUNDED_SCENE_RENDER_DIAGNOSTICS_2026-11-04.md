# B12 — Bounded Android scene renderer/shader diagnostic and mesh coverage

4 November 2026. Session 20261104T2243Z-B12-bounded-tree-a9; source-only/managed scope, **not Android device proof**.

## Why this changed
The previous B12 `ReportSceneShaderSnapshot` claimed a 512-renderer cap but called `root.GetComponentsInChildren<Renderer>(true)` before checking it, creating an entire renderer array for each root and potentially causing avoidable managed GC pressure in large Raft scenes. `renderer.sharedMaterials` separately returns a new array per renderer. This was a provable source allocation pattern, **not an observed new OOM**.

## Actual production source changes
- [2c15dfb](https://github.com/alwansan/raf/commit/2c15dfbf8ccc356eaebef3102a7f79c583ebadda): bounded nonrecursive `Transform` traversal, `Scene.rootCount` preflight (max1024), visited transforms<=4096, pending array<=1024, active enabled renderers<=512, inspected material slots<=4096; emits `truncated`, `limit_reason`, root/node counts. Overlarge root count avoids fetching any root array and explicitly marks sample truncated. No mesh vertices or shader pixel readback and no material mutations.
- [cdec4c6](https://github.com/alwansan/raf/commit/cdec4c65add78518942fc8609d32687c1257637d): uses reusable `GetComponents<Renderer>(List<Renderer>)` and Unity2021.3 `Renderer.GetSharedMaterials(List<Material>)` to avoid full-array creation per component/renderer. Preserves white-shader, missing material, MeshFilter.sharedMesh, SkinnedMeshRenderer.sharedMesh classification and ambient/light context, with existing exception logging.
- Test contracts updated in [3bed5bd](https://github.com/alwansan/raf/commit/3bed5bd26d4319b2db91d04bb50169865b5c7f20), [37f52c9](https://github.com/alwansan/raf/commit/37f52c90e85b9beacfeb925783aa38cce3d00513), [8e4cbce](https://github.com/alwansan/raf/commit/8e4cbce0a84128c0c3c861442851a24494a40b26). The source parser avoids false matches in explanatory comments.
- [B12 production-method fixture](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/b12_scene_render_harness.py) extracts exactly the production coroutine and any co-located same-source quality helper. Synthetic Unity C# stubs test eight cases and fail if unknown source budget contracts drift. [Dedicated CI workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-b12-scene-render-snapshot.yml) is no-LFS, no Unity/player, 6-minute timeout and distinct noncancelling concurrency.

## Verified results
[41929419050](https://github.com/alwansan/raf/actions/runs/41929419050) **COMPLETED SUCCESS**, commit02030b21dea84bd6c9923897add70567ea821f9b, job126922207852:
- 8 actual CLR synthetic C# scenarios using extracted production coroutine: normal shader/mesh categories, root overflow, wide pending stack, deep node overflow, renderer cap, material cap, inactive hierarchy and unloaded scene.
- 11 B12 source-policy tests and 11 existing runtime-operation tracing tests passed.
- Previous original managed gameplay compile and local RPC/identity harness [41928807641](https://github.com/alwansan/raf/actions/runs/41928807641) **SUCCESS** on cdec4c6. These do NOT prove Unity Editor shader import, Vulkan runtime, Android/Adreno memory improvement, GPU OOM reduction, pixels, or World/.rgd.
- First failed CI fixture attempts and exact correction are preserved in [B12 incident](../prompt/coordination/incidents/B12/20261104T2256Z-source-fixture-and-quality-helper.md). One unrelated Android startup CI41928829509 failed on Raft_Network tracing manifest SHA, outside this change and not misrepresented as B12 C# failure.

## Next evidence
When a new **real Raft** APK/OBB (not LogRaft) includes cdec4c6 or descendant, compare B12 `render.scene_shader_snapshot` root_count/visited_transforms/limit_reason/truncated/mesh/shader counts with same-scene screenshot and memory/GC/Frame stats. If truncated=true, do not treat zero missing meshes/shaders as total coverage. Fix authentic water/shader/material mismatch on direct evidence instead of dummy resources. Current game APK86 predates this change; WATER-001/RENDER-002/LOCAL-005/PERF-007 remain OPEN, NOT_READY and full reviews 0/3.

No audio, owner-working Settings, deferred touch, original assets, .meta/GUID, .rgd, native build requests or protected branches were edited by B12. B12's scoped work completed during this session; no asynchronous activity claimed.
