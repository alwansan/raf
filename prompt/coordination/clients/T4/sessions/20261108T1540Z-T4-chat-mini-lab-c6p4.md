# T4 chat — physical mouse mini APK baseline, 8 November 2026

- session_id: `20261108T1540Z-T4-chat-mini-lab-c6p4`
- origin: `chat`; worker: `T4`; issue: `INPUT-005`
- base_sha before scope: `5e2020b135adf3b7c989337c256d72278e90eca7`
- scope reservation commit: `615b19729e20af76df0f326a1959d20cd88188e5`
- resumed_from_sessions: `20261108T1439Z-T4-scheduled-k5r9`, `20261108T1536Z-T4-scheduled-route-analyzer-n8q4`
- work: `prompt/coordination/work/INPUT-005/T4-20261108T1540Z-chat-mini-lab-c6p4.json`
- experiment_key: `T4-android-physical-mouse-button-scroll-host-0.1.0-capture-on-off`
- intended files: separate request `.github/raft-mini-lab-build-request.json`, T4 own lab README and own TEST_CENTER row (only after real artifact); this session. **No shared host Java edit**, no Raft Unity/game source edit, no overlap with scheduled route-analyzer scripts.
- existing mini-lab host: `apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/MainActivity.java` source-only prototype; logs `dispatchTouchEvent`, `dispatchGenericMotionEvent`, view touch/generic and captured pointer callbacks, `actionButton`, `buttonState`, `AXIS_VSCROLL/HSCROLL`, with capture request/release and persistent private JSONL + MediaStore export; T4 testpack contains nine cases. Build is not proven until Gradle CI.

## Device evidence and safe hypothesis
Owner 8 Nov: mouse camera moves with pointer capture, but left, right, middle and wheel are inoperative in game. Relevant CL summary: LogRaft-20261108-164850-270. This proves observation only, not Android callback absence nor Unity bridge fault. Existing T4 epoch classifier CI 42472339258 is source regression only; scheduled T4's 15:36 route analyzer operates on `scripts/t4_analyze_mouse_lab_routes.py` and tests, separate from this mini build.

This chat session will request **one independent T4 mini APK** solely to distinguish Android callback delivery with capture ON/OFF from Unity bridge consumption, without losing camera movement. Avoid Unity full build and avoid touching `.github/raft-native-build-request.json` or another worker's files.

## Build gate and handoff
No `.github/raft-mini-lab-build-request.json` currently exists; no in-progress/queued Actions on branch at initial check, and no T4 mini APK known. Request must be single file dedicated commit with `[raft-mini-lab]`, `requested_from_sha=HEAD^`. **Do not tell owner to install until artifact exists and package/bytes/SHA checked.** After run inspect success/failure and update T4 row only, preserve history and record exact run/source SHA, APK SHA256 and expected log/case steps. If build fails, log genuine blocker; no false READY.

Status at checkpoint: `active`; not yet a device or build success; LOCAL-005 save remains separate and original .rgd untouched.

## CI checkpoint — 2026-11-08T15:43Z
- Trigger `7ba0068ee26a925030571cde1e37ab7514c1027b`: [run 42496084526](https://github.com/alwansan/raf/actions/runs/42496084526) **FAILED** after request gate, safe testpack validator and JDK setup passed; `android-actions/setup-android@v3` invokes `sdkmanager tools` (deprecated removed package), fails with `Failed to find package 'tools'`. No Gradle/APK started.
- Scope-specific minimal fix `6ab099095d3fdca135214c8c01f8fb85e3b2ad44`: set `packages: 'platform-tools'` explicitly in mini workflow; no Unity runtime, full build or game change. This matches current upstream documentation. Source-only runner compatibility CI 42496200510 SUCCESS for fix commit, not an Android build.
- New unique request `7069e9db0c433c894eb5781eda045bd0e04ecffe` exactly one-file commit with parent `6ab0990...` and `[raft-mini-lab]`; [run 42496238418](https://github.com/alwansan/raf/actions/runs/42496238418) **in progress** at this checkpoint. No actual APK yet; defer TEST_CENTER READY and owner instructions pending artifact.

## Second compile barrier and third run — 2026-11-08T15:46Z
- [CI 42496238418](https://github.com/alwansan/raf/actions/runs/42496238418): Android SDK now passes, Gradle javac **FAIL** at `MainActivity.java:137` (unclosed char literal caused by `'\\\\n'` / `'\\\\r'` in T5 asynchronous digest method). This source had been pinned before T5's own repair.
- T5 independently fixed the exact Java escape in `db8f507af7b1`; no duplicate MainActivity patch by T4. Source separation is intentional while T4 scheduled script analyzes routes and T5 improves shared host hashing.
- Third **unique** request commit `dd9a5de9225d4330e0c7513564879615dd9d481d` parent `a4578ff4cd7f7d7928038abdb1d076d514096da8`; [run 42496449259](https://github.com/alwansan/raf/actions/runs/42496449259) in progress. No authenticated APK/bundle digest as of this checkpoint.

## Actual mini APK delivered — 2026-11-08T15:53Z
- The third attempt [42496449259](https://github.com/alwansan/raf/actions/runs/42496449259) failed javac in **T1** `T1ComputeProbe.java:93` (`final observation` definite assignment). T1 independently repaired in `ae450f1f84ef4956f577df29cb21214517a8f065`; T4 did not edit T1 source. Original shared MainActivity Java escape was repaired by T5 `db8f507a`, after earlier pinned request. All failed runs preserved for provenance; no duplicate running/queued host build cancelled.
- One additional source-changed request `1beab49d26aa31a6cc4765f0c6020c2d552cce7b` parent `ae450f1f84ef4956f577df29cb21214517a8f065` triggered [CI 42496622364](https://github.com/alwansan/raf/actions/runs/42496622364) **SUCCESS**: request identity, nine-case safe testpack validation, JDK17, Android SDK35, Gradle `:app:assembleDebug`, APK SHA256, upload-artifact all completed.
- GitHub Actions Artifact **13623563385**, real name `raft-mini-lab-T4-1beab49d26aa31a6cc4765f0c6020c2d552cce7b`, ZIP bytes **35,398**, `expired=false` on verification, expiry `2026-11-15T15:49:08Z`, ZIP SHA256 `4f356e648b29a35db8a22fdba049cd1ee83d1fe1e9c648bd261a7e213b1bc0a3`; **APK SHA256** `a5a42b89642c75946f7d3fd5e46fab83b1f16ee800cbd7c2056a7ab74f3e2849`. Package `com.alwansan.raft.lab.t4`, versionCode1, versionName `0.1.0-source-prototype`, independent from actual Raft. Nine-case pack SHA `0d708913a7274507798843c27a10e2005844d33c7890663cd0ec055c8ef8702a`.
- Published **only T4 row** in `apk-for-testing/TEST_CENTER.md` at commit `b03eac1a99d5ae70e918eae88904bb95d867251e` and full test/expected evidence/historical failures in `apk-for-testing/workers/T4/README.md` commit `7939a0b98fe16a71eb47e96e3fdfea45cb355449`. Updated work complete at `3fd5e6f29f31b2b572c52217deb2ad788954cd1f`.
- Test pack must be imported via Android file picker to show all T4-01..09; generic host includes three default mouse cases only. Current app saves JSONL privately and exports to `Download/Games/cl/test` by MediaStore, not the extra `raft log` folder segment in the owner's latest expanded request. Do not misstate this. Coordinate any shared-host path change with T5 in a separate scope and rebuild before claiming exact compliance.
- **Device status still untested. INPUT-005 OPEN.** Owner result is camera-relative working, mouse left/right/middle/wheel not working in game, not proof of Android event loss. Next cycle: collect exported T4 ON/OFF JSONL and screen recording, run `scripts/t4_analyze_mouse_lab_routes.py`, compare with Raft input bridge by immutable APK source SHA; preserve camera movement, keyboard, touch and full Raft .rgd. No XAPK, Unity or game-source edits were made here.
