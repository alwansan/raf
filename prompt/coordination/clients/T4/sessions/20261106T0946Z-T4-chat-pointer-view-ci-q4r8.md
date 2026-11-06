# T4 chat — post-446bc1f0 pointer View identity CI is now actually executed

- session_id: `20261106T0946Z-T4-chat-pointer-view-ci-q4r8`
- origin: `chat`
- resumed_from_sessions: `20261106T0943Z-T4-scheduled-q7n4`, `20261106T0843Z-T4-scheduled-r6v2`, `20261106T0740Z-T4-scheduled-p4k8`, and LOCAL-005 authenticated world-save session `20261106T0246Z-T4-chat-original-owner-save-roundtrip-j4q8`
- base_sha: `c2f399ebe1fa749c93f68fb21c2ebd729f01c601`
- production-workflow commit: [`e3fb6781`](https://github.com/alwansan/raf/commit/e3fb67812368fb6cafd327c9e99ce1886eea1b57)
- work: `prompt/coordination/work/INPUT-005/T4-20261106T0946Z-T4-chat-pointer-view-ci-q4r8-source-regression-coverage.json`
- experiment: `prompt/coordination/experiments/T4/20261106T0946Z-T4-chat-pointer-view-ci-q4r8.json`
- event: `prompt/coordination/B_TEAM/events/T4/20261106T0946Z-T4-chat-pointer-view-ci-q4r8.json`
- issue_id: INPUT-005 (OPEN)
- status: completed_bounded_source_ci_success; device_unverified

## Why this is a distinct, nonoverlapping engineering step

Latest T4 scheduled [0943Z](20261106T0943Z-T4-scheduled-q7n4.md) audited the *release target* for Android pointer capture and intentionally made no production change; do not claim an OS leak. Earlier scheduled 0843Z proved [CI42182264435](https://github.com/alwansan/raf/actions/runs/42182264435) and [CI42182264431](https://github.com/alwansan/raf/actions/runs/42182264431) succeeded at source `d234b10e`, **before** post-fix test commit `446bc1f0`. Those jobs did not cover `tests/test_t4_pointer_view_identity_contract.py`. While T1/T2/T3 continued their water/shader experiments and T5 investigated paired APK/OBB packaging, this session reserved only the dedicated T4 source workflow coverage. Existing original .rgd compatibility evidence and owner playable world/save/reopen at older [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) were preserved, not rerun.

## Exact change

Modified only `.github/workflows/raft-t4-mouse-capture-bridge.yml` (existing T4 owner workflow), using the fetched file SHA `de71bfa967cb9ea81d38a4193eb8cc8cbda8f94c` and no force:
1. Added `tests/test_t4_pointer_view_identity_contract.py` to push path filters.
2. Added the same file to bounded sparse checkout.
3. Added `python3 -m unittest discover -s tests -p test_t4_pointer_view_identity_contract.py -v` to the isolated source test step.

No production `AndroidPhysicalMouseCapture.cs` change, no touch/Settings/audio/UI/game asset/IL2CPP code, no heavy Unity build, no original source published, no jobs cancelled or duplicated.

## Actual verification — independently observed run and job log

- Run: [42197616749](https://github.com/alwansan/raf/actions/runs/42197616749), **completed success** at **exact `e3fb67812368fb6cafd327c9e99ce1886eea1b57`**, job `127824703878`, complete at 2026-11-06T09:47:22Z.
- Log shows the **new** four `test_t4_pointer_view_identity_contract` tests were actually invoked and **4/4 passed** at 09:47:02Z, not merely that the job was green.
- Existing source-only tests passed: original routing **7/7**, adapter **7/7**, pointer capture policy **21/21**, physical presence **5/5**. Total **44/44 Python tests**.
- C# thread-safe captured motion controls succeeded; original pinned ZIP2 DLL SHA gate succeeded; C# compiled against actual original Unity2021 managed ABI; private source decompilation/patch stage succeeded, no game-derived raw artifacts published.
- The separate runner-compatibility check [42197616553](https://github.com/alwansan/raf/actions/runs/42197616553) completed success on the same workflow commit.
- T5 paired APK/OBB control [42197510807](https://github.com/alwansan/raf/actions/runs/42197510807) succeeded on its **own** earlier SHA after prior [42183679266](https://github.com/alwansan/raf/actions/runs/42183679266) failure; this does not establish a matched signed native delivery. T1's FFT job `42196835754` failed separately; do not touch T1 scope without coordination.

## Evidence boundaries and next step

This certifies **isolated Python source contracts and managed ABI**, not Android OS pointer-capture release, full Unity/IL2CPP, actual user camera movement, signed APK/OBB installation, or device gameplay. The T4 scheduled q7n4 release-target gap remains a device hypothesis: focused Android View at release may differ from captured View; OS could already revoke it. Avoid speculative cross-thread JNI pointer fixes.

Next on exact *new signed APK + matching OBB* from T5: preserve source SHA/package/version/SHA256; test with real physical mouse plus keyboard, menu Raft cursor and system pointer, 360-degree continuous camera motion, pause/resume/release, focus/home/reconnect, then save and full process exit + reopen of same original owner world. Correlate physical_mouse_capture_requested/view_changed/lost/relative log markers, .rgd snapshots, original completion and caught-exception markers; record UNKNOWN for absent logs. Preserve audio and Settings, defer touch. LOCAL-005 owner-confirmed only on previous artifact, INPUT-005 OPEN, and overall **NOT_READY 0/3**. No new device acceptance claim.
