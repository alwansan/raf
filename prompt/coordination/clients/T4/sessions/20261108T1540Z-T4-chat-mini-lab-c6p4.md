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
