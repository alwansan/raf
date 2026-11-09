# T1 — Android15 Mini GLES local512 complex butterfly source integration

- session_id: `20261109T1915Z-T1-chat-mini-butterfly-a9f3`
- origin: `chat`
- status: `source_ci_verified_waiting_T5_single_mini_build`
- resumed_from_sessions: `20261109T185616Z-T1-chat-fft-audit-run-34c243`, `20261109T1806Z-T1-scheduled-provenance-presence-q5n8`
- base_sha: `6c5aaab4db64c3d021ce32e9eb5ab6d6049fa960` work reservation (first branch inspection `abf1ede6bbea3b9073c9ab20b826be46dd486c93`; plan recorded before source modifications)
- issue_id: `WATER-001`
- work_id: `prompt/coordination/work/20261109T1915Z-T1-chat-mini-butterfly-a9f3.md`
- experiment_key: `t1-shared-mini-ssbo-butterfly-two-pass-local512-source-only-android15-adreno730-v1`
- resource_key: `shared-mini-testpack` coordinated with T5, **not held** after source integration
- run_urls: https://github.com/alwansan/raf/actions/runs/42682971944 ; https://github.com/alwansan/raf/actions/runs/42683061084 ; https://github.com/alwansan/raf/actions/runs/42683658745
- updated_at: `2026-11-09T19:30:33Z`

## Owner requirement / what was already true

Owner asked T1 to use simplified Android shared Mini tests for measurements impossible on this environment, and to notify T5 + persist need for a real game XAPK only if necessary. Existing owner upload CL/test/shared-20261108-232759-468049775 contains fresh **T1-01..04 PASS** from shared `0.2.13-shared`, source `e7a6248...`, pack v1 SHA256 `6e19b...`. Phone reports GLES ES3.2, Adreno 730, max invocations 1024, but no original Raft FFT runtime proof. Original WATER-001 remains open / NOT_READY0/3.

## Scope and independent hypothesis

The earlier tests only verified 16-word SSBO/simple two-stage + capabilities + compiler negative, not a larger 512-invocation complex arithmetic pipeline. A real Android OpenGL ES3.1 test could falsify the hypothesis that a larger but simple FFT-like GPU group, float arithmetic, or two-pass storage barrier is inherently failing on this phone. It cannot restore original D3D11 shader variants, Unity GUID/kernel name/FindKernel, or prove original Raft GPU output. **No original compute shader/mesh/source is exported** and no external JSON can inject executable GLSL.

## Code changed

- [`2f627cb`](https://github.com/alwansan/raf/commit/2f627cb415422a5f0fba8e5e5232db4f4c83d78c) NEW `apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1FftButterflyProbe.java`: fixed synthetic GLSL #version310 ES initial + butterfly stages, exactly **512 local invocations** and one workgroup per pass; 512 complex samples (4KiB SSBO), `glMemoryBarrier(SHADER_STORAGE_BARRIER_BIT)` between passes, mapping actual GPU buffer and checking **1024 floats** vs independent CPU arithmetic, float tolerance **0.00003**. Uses `glGetError`, real map/unmap, finite checks, explicit PASS/FAIL and `original_raft_compute_executed=false`, resources cleaned on exceptions. No original game data.
- [`c11097e6`](https://github.com/alwansan/raf/commit/c11097e6f8754f46163740a529e151ec04a31b2d) `T1ComputeProbe.java`: T1-05 automated child execution, same T1 GPU context and bounded startup, preserves first four cases.
- [`67710964`](https://github.com/alwansan/raf/commit/677109649fd8b0d6727fc2c5001edc77fe15c37c) host `MainActivity.java` routes one additional trusted auto ID; [`dbfdcdd5`](https://github.com/alwansan/raf/commit/dbfdcdd515577a1244d368b1e6eefd4bd84ed0a2) `UnifiedLabActivity.java` accepts only T1-01..05 under compiled driver.
- [`de4b607`](https://github.com/alwansan/raf/commit/de4b607bbb24aa00b406f23f09e4155605a783d0) Arabic `T1-05` explanation and expected outcome; [`a3beeceb`](https://github.com/alwansan/raf/commit/a3beeceb3628386aad6db9cd4b891448c0e251d5) T1 driver fingerprint includes new Java class.
- [`b642215`](https://github.com/alwansan/raf/commit/b6422154140b8ed53635b4bbd8bc29967946476e) single embedded `team-testpack.json` revision 2 with **30** cases total (one new T1-05, existing 29 IDs unchanged), plus `scripts/validate_unified_testpack.py` T1 mapping and `tests/test_unified_testpack.py` exact counts. Pack is data-only, no program downloads.
- [`601ff6f`](https://github.com/alwansan/raf/commit/601ff6f8a136fe39d2381bc219f0ce7083b30e6b) 10 source/safety regression tests incl. counterfeit original-proof and size/barrier/mapping negative controls; [`63c0ccf`](https://github.com/alwansan/raf/commit/63c0ccf084ec040bfd751d408250db9f4a5f2ece) isolated source/Android compile workflow with cancellation disabled and NO APK build.

## Actual GitHub Actions results (not device GPU)

- **[CI42682971944](https://github.com/alwansan/raf/actions/runs/42682971944) SUCCESS**, source `63c0ccf084ec040bfd751d408250db9f4a5f2ece`: 7/7 shared pack tests, 10/10 T1-05 source tests, actual Android `:app:compileDebugJavaWithJavac` BUILD SUCCESSFUL. This does **not** run GLES on real device, assemble APK, or assert water fix.
- Previous T1 context regression [CI42682527399](https://github.com/alwansan/raf/actions/runs/42682527399) initially FAILED because old test hardcoded T1-01..04. Corrected `tests/test_t1_compute_context_gate.py` at [507f8baa](https://github.com/alwansan/raf/commit/507f8baa86cd6e09e545bafee3cf2ff6acfaa743); **[CI42683061084](https://github.com/alwansan/raf/actions/runs/42683061084) SUCCESS** for old original bounded context route and new case.
- T5 Arabic coverage [CI42682659801](https://github.com/alwansan/raf/actions/runs/42682659801) and [CI42683569390](https://github.com/alwansan/raf/actions/runs/42683569390) initially FAILED due old 29 hardcode in Python/JVM (first without new pack, second JVM still expected29). Updated `tests/test_t5_arabic_portrait.py` and `tests/java/com/alwansan/raftlab/ArabicLabStringsTest.java`, preserving original 29 + requiring T1-05. **[CI42683658745](https://github.com/alwansan/raf/actions/runs/42683658745) SUCCESS**: 4/4 Arabic Python, actual JVM `PASS ArabicLabStrings coverage=30` and Android Java `BUILD SUCCESSFUL`. Intermediate failures retained, never relabelled PASS.

## T5 handoff and current build decision

- Before changes reserved work and sent independent [T5 discussion](../../discussions/WATER-001/20261109T1915Z-T1-chat-mini-butterfly-a9f3-to-T5-shared-mini-fft.md). Updated discussion at [2dc50fed](https://github.com/alwansan/raf/commit/2dc50fedb9eec34883fd85c6362747f40028879a) with actual CI evidence and single-Mini request, without modifying T5-owned `.github/raft-mini-lab-build-request.json`.
- **T1 voted `NEED_BUILD`** at [f3ded4d](https://github.com/alwansan/raf/commit/f3ded4d7934a9741734fedb7841491e85038cedb) in T1 row only of `apk-for-testing/SHARED_BUILD_READINESS.md`, round `shared-20261108-r4`. T5 to review HEAD, running jobs, signature, source fingerprint, then create **one** combined Mini build if authorized. No direct APK link or new APK exists yet; do not represent source compile job as user download.
- [Arabic owner guide](https://github.com/alwansan/raf/blob/feature/android-native-port/apk-for-testing/workers/T1/T1_05_OWNER_GUIDE_AR.md) describes running `تشغيل T1 تلقائيًا`, inspecting PASS/FAIL/first_mismatch and exporting `events.jsonl`/`summary.json` to **CL/test**, no screenshot needed.
- A new Raft **full game XAPK is not requested for this synthetic GLES-only check**; it would NOT prove original Unity FFT mapping. At the next independent owner/team-authorized full Raft build T5 should preserve already integrated original `Dx11FFT` 16-call trace hooks, and only then can real phone water errors be correlated. Existing separate full XAPK 5/5 policy unchanged. `WATER-001 OPEN / NOT_READY0/3`.

## Exact next step

T5 reviews T1 NEED_BUILD + successful CI and makes the one shared Mini build using the canonical request SHA+pack SHA path; if it publishes a real APK, verify bytes, signer and actual download before sending owner link. Owner runs T1-05 on POCO F5 Pro and uploads CL/test, then T1 matches `case_result` fresh event with actual GLSL readback status; PASS means synthetic GPU work only, FAIL details first broken stage. If no new APK, do **not** ask owner to import new 30-case pack into v0.2.13; old binary lacks T1-05 and would reject it.

No asset/mesh/original shader data, touch, Settings, audio, T2/T3/T4/T5 device driver, full game build request, CL write or other branch was changed.
