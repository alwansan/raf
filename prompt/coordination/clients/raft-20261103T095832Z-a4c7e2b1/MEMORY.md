# A4 HAPTICS-008 — 2026-11-03

- Identity: raft-20261103T095832Z-a4c7e2b1; session a4-20261103T095832Z-71d4c6b8. Registered from live HEAD af354e4154b915a99fd9ba55a37b63ce849a16f5.
- Boundaries: only feature/android-native-port writable; CL read only; no Unity/native/APK/OBB/XAPK, release, scheduled task, proprietary asset or LFS download.
- Read owner requirements, permanent prompts, coordination protocol and other clients. Existing FFT-FORMAT-009 and DISPLAY-003 work will not be overwritten.
- Scope: investigate missing haptics paths from historic APK80 phone logs against actual source; write an isolated falsifiable repair/test if evidence exists; do not misclassify old device logs as newly tested source.
- Next: inspect current implementation, CL exact paths, then validate any fix and update this memory and plan.

## Scope change / coordination

Two additional clients registered HAPTICS-008 while A4 inspected it (afcedabb and a5c842e1). A4 will not write their overlapping haptics assets, code or tests. Shifted to PERF-007 CI memory-evidence integrity. Reproduction target: missing VmRSS appears as measured zero; malformed/negative memory may be accepted. This is a CI diagnostics correction, not a phone GPU-OOM fix.


<!-- A4-PERF007-FINAL-20261103 -->
## Verified A4 result and next checkpoint

- Source 1b37647587e94b4e3a7baf6e34865c634a442216 adjusted only `scripts/ci_memory_watch.py` and `tests/test_ci_memory_watch.py`: absent VmRSS no longer fabricates measured zero; negative/malformed units and fake PID prefix excluded; actual 0 remains valid.
- https://github.com/alwansan/raf/actions/runs/41616939992, job125852628608: **COMPLETED SUCCESS**, eight Python tests incl. two new negative controls; live 3-sample runner monitor and 256MiB swap capability PASS. Also [preflight 41616940049](https://github.com/alwansan/raf/actions/runs/41616940049) success on same SHA. Neither runs original game or phone.
- Status/handoff evidence saved in [0b847d4c](https://github.com/alwansan/raf/commit/0b847d4c526b7612f52238de1c5d803a4a078509). HAPTICS code left untouched because concurrent clients registered it; A4 scope moved to PERF-007.
- Multiple transient GitHub GraphQL update_ref errors under moving HEAD were safely re-based with expected SHA. No forced ref update or interrupted jobs.
- No gameplay GPU OOM, water shader/FFT, Unity, phone acceptance, APK/OBB/XAPK or readiness claim; NOT_READY/0-of-3. No .meta/GUID, left Mouse0/500ms, UGUI/controller, LFS, CL or task change. A4 scoped task completed; no asynchronous activity.

<!-- A4-RESUME-CGROUP-20261103 -->
## Resumed A4 / PERF-007 cgroup counter continuity (2026-11-03 UTC14:51)

- Restored explicit previously **completed** A4 identity `raft-20261103T095832Z-a4c7e2b1`, new session `a4-resume-20261103T145128736Z-c29f7d43`, `resumed_from=a4-20261103T095832Z-71d4c6b8`. Source head at registration `b09de2aca410f43b741f94b5353131d47d2d7386`; moving branch requires fresh reads.
- Read unified owner/protocol and original A4 completed work/experiment/discussion/incident; no overlap with A3/A5 HAPTICS-008, other WATER/RENDER/DISPLAY/FFT or native delivery. Previous A4 [CI41616939992](https://github.com/alwansan/raf/actions/runs/41616939992) verified **8 old** tests at previous SHA only.
- New [source commit c9b2cf3](https://github.com/alwansan/raf/commit/c9b2cf3ee6502893f2d61160269c2dbb18365ee6) fixes `scripts/ci_memory_watch.py`: first/last cgroup event counters alone could fabricate a nonzero delta when an intermediate sample reset, disappeared or was corrupt. Both deltas are now null for gaps, bad row types, non-integer/negative counters or resets; valid continuous counters retain their deltas. `null` is unknown, never proof of zero events.
- [Tests commit 10563d4](https://github.com/alwansan/raf/commit/10563d4622a898ee4e2bcc9631bf4f95e3fcd0b2) adds two Python regression methods. Caught and immediately corrected a newline-escape mistake in the new fixture in this commit. Freshly re-read source/test blobs after correction.
- **Executed local bounded copy of the continuity summary routine:** 7/7 cases PASS (normal monotonic, midstream reset, one-counter reset, missing sample, boolean, malformed JSON, null row). **Not** the complete repository 10-test suite nor new GitHub Actions proof. New exact-source Actions discovery returned no runs through the available PR-scoped endpoint; do not assume CI green. Existing old CI success is not validation of this patch.
- No Unity, native APK/OBB/XAPK, release, LFS, game asset, .meta/GUID, signed delivery, CL mutation, job cancellation or automation creation. The change is CI host-memory *evidence* integrity, **not** a GPU OOM or water/gameplay repair. Readiness remains NOT_READY/0-of-3.
- Resume point: verify full exact-source CPU-only suite on new SHA if an Actions run is available, then pursue an independent authentic runtime GPU allocation/lifetime investigation avoiding overlap. Work/experiment paused pending that evidence. Do not claim session execution continues in background.

## A4 resumed: verified cgroup CI and PERF-007 GPU lifetime focus — 2026-11-03T22:44:54.646Z

- Session a4-resume-20261103T224500Z-84e2c91f (resumed_from a4-resume-20261103T145128736Z-c29f7d43); original A4 client status was paused, no claim of background execution. Base HEAD b3ebf3ddd69e44b1f430c1d77a6642f70adbd404.
- Live exact-source [memory CI41658344282](https://github.com/alwansan/raf/actions/runs/41658344282), job125994601312: COMPLETED SUCCESS on 10563d4622a898ee4e2bcc9631bf4f95e3fcd0b2; actual job logs show **Ran 10 tests / OK**, 3 monitor samples, 256MiB swap capability PASS. [Preflight41658343421](https://github.com/alwansan/raf/actions/runs/41658343421) also success on same SHA. Prior 7 local focused cases were not full suite; earlier lack of CI proof is now resolved.
- Started new isolated PERF-007 GPU allocation/lifetime source review: inspect authentic allocation/release paths and evidence before touching runtime code. Existing FFT/WATER and HAPTICS agents own their components; no overlapping code, native build or scheduler edits. Build remains NOT_READY 0/3; older device GPU OOM does not prove newly edited sources executed.

## A4 scene-boundary GPU diagnostics: verified, scoped checkpoint — 2026-11-03T22:52:41.965Z

- Session `a4-resume-20261103T224500Z-84e2c91f`: source change [dac7ba8](https://github.com/alwansan/raf/commit/dac7ba8fffd955d9901c4691c9ce35d584c422ba), [test74df622](https://github.com/alwansan/raf/commit/74df62250c0f4db1bd5f33981ee22d24ee62934a). Partial process/driver memory snapshots are now recorded at sceneLoaded/Unloaded and lowMemory, without per-frame JNI. The existing numeric metrics may be unavailable; they do not represent total GPU VRAM. Details: [A4 PERF source report](../../../../docs/A4_PERF_GPU_SCENE_DIAGNOSTICS_2026-11-04.md).
- Live exact-source [Android platform41734019524](https://github.com/alwansan/raf/actions/runs/41734019524), job126258407653, **COMPLETED SUCCESS**, 10/10 diagnostic source-policy tests PASS including new `test_scene_boundaries_and_low_memory_capture_partial_gpu_counters`; unrelated Android platform checks also green. [Code-head platform41734013639](https://github.com/alwansan/raf/actions/runs/41734013639) and [offline startup41734013814](https://github.com/alwansan/raf/actions/runs/41734013814) **COMPLETED SUCCESS** on `dac7ba8...`. This is source/CPU workflow, not an Android Unity player compile or device memory fix.
- GitHub concurrent ref updates rejected two optimistic atomic commits (GraphQL UNKNOWN); each patch target's unchanged blob was verified, then written through separate contents SHA leases with NO force or overwritten files. Registered work/discussion and separate experiment `scene-boundary-gpu-diagnostics-20261104.json`.
- Original GPU RenderTexture allocation/teardown root cause is **UNVERIFIED**. Other agents own original FFT/Shader resources, and no overlap was introduced. Overall game **NOT_READY, 0/3** readiness reviews; WATER-001/RENDER-002 and broader PERF-007 remain unresolved. No new Unity/APK/OBB/XAPK, ZIP2/LFS payloads, proprietary source, original .meta/GUID/.rgd, scheduler, protected branches or CL writes.
- Session paused after verified checkpoint; no autonomous activity inferred. Next scoped step: source-locked and executable GPU lifetime investigation coordinated with A1/W1/W2/W3.
