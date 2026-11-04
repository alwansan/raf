# B14 RENDER-002 — restore source CI coverage for delayed scene diagnostics (4 November 2026)

## Observed regression
The Android offline platform workflow run 41918822026 FAILED at `test_android_diagnostics_policy.py`: test_scene_boundaries_and_low_memory_capture_partial_gpu_counters raised IndexError because the test searched for `private static void SceneLoaded(`. Since B12 added a bounded read-only post-scene shader/material/mesh snapshot coroutine, the production method is correctly an instance `private void SceneLoaded(Scene scene, LoadSceneMode mode)` and calls `StartCoroutine(ReportSceneShaderSnapshot(scene))`. Reverting this to static would break the production diagnostic.

## Production test change and proof
- The first test-only commit https://github.com/alwansan/raf/commit/5ef3f839aad50098d16aaf7b200dc485ad40e9ca changed the stale callback signature match, maintained 2 scene-boundary graphics-memory probes, and asserted the 3-second delayed, <=512 Renderer read-only diagnostic. GitHub Actions 41928540784 FAILED at a newly overbroad test assertion: it counted the loaded callback's intentional boundary graphics-memory sample while examining the coroutine. This was a B14 test-scope error, not production runtime evidence.
- Follow-up test-only commit https://github.com/alwansan/raf/commit/9ba6990cbd30fe5f6fdc97c000b7cd24a57333e6 properly isolates the body of `ReportSceneShaderSnapshot` before asserting that it does not call `GraphicsMemoryAtBoundary`. The normal SceneLoaded/SceneUnloaded and LowMemory callbacks must and do retain their partial process/driver counters.
- https://github.com/alwansan/raf/actions/runs/41928677980 COMPLETED SUCCESS on exact source 9ba6990c. Job 126919715017 `platform-tests` PASS, including `Guard bounded Android diagnostic UI source policy`, source policy and independent storage/identity/offline-session smoke tests.

## Correct limits
This is test harness maintenance following B12's actual code integration; no Unity player source, shader, material, texture, mesh, .meta, GUID, FMOD, Settings, touch mapping, virtual controller, native request, or device build changed in these B14 commits. It retains rather than emulates the original scene snapshot; the future APK must still collect real scene_shader_snapshot and Adreno pixels to diagnose white materials. RENDER-002, WATER-001, LOCAL-005 remain OPEN; NOT_READY, full readiness reviews 0/3. Owner-reported working sound and Settings untouched; touch/layout deferred.

## Reproduce
`python3 -m unittest discover -s tests -p test_android_diagnostics_policy.py -v`, or full `.github/workflows/raft-android-offline-platform.yml` source-only pipeline if its current name/path is verified. This passes no original Raft binary and does not claim on-device fps/render outcome.
