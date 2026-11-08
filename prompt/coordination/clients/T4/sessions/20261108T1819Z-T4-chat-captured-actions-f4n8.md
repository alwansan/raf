# T4 chat — captured physical mouse button and wheel callback evidence (8 Nov 2026)

- **session_id:** `20261108T1819Z-T4-chat-captured-actions-f4n8`
- **origin:** chat; **worker:** T4; **issue:** INPUT-005; **status:** completed **for source-only diagnostic scope**, not gameplay acceptance.
- **base_sha (initial):** `7bb7b0452d56f05dbb39d02d400a39729feaa49b`; **source commit parent:** `1a2d73179616f36fbfb33f867bb5955e7f93ef68`. Latest verified source of own changes: `3be65eb53427359abeeb4950685699e7dc2979a1`.
- **resumed_from:** `20261108T1746Z-T4-scheduled-scroll-action-p8v3`, `20261108T1640Z-T4-scheduled-button-edges-m7q2`, `20261108T1540Z-T4-chat-mini-lab-c6p4`.
- **work:** `prompt/coordination/work/INPUT-005/T4-20261108T1819Z-T4-chat-captured-actions-f4n8.json`.
- **experiment_key:** `T4-captured-button-scroll-callback-contract-android15-20261108`; **resource_key:** none, CPU/source-only.
- **scope:** T4 Android native `onCapturedPointer` nonmoving action **observation**, not game button injection, camera/touch/keyboard changes or another mini APK.
- **owner evidence:** 8 Nov camera relative motion inside Raft works under pointer capture; LEFT/RIGHT/MIDDLE/WHEEL V/H fail. Prior 42058825739 owner world/save/reopen applies **only** to old artifact; no device callbacks in this session. CL water and cursor warnings are not button-delivery proof.

## Actual engineering
1. `b89ccb9b2247f7c22937dca30a600619b7dfe8f4` — added `PhysicalMouseActionEvidence` into already-copied `PhysicalMouseMotionSource.cs`, avoiding new Unity-staged dependency. The mouse listener records only physical-source BUTTON_PRESS/RELEASE, ambiguous DOWN/UP and nonzero ACTION_SCROLL 9/10, gated by current capture epoch under lock; reports sparse counts/masks on Unity main thread and final counts on release, resets after capture loss. Returning **false** for all non-MOVE means normal Android View/Unity route remains active. No synthetic InputSystem events. Existing captured camera MOVE, source classification, legacy fallbacks unchanged.
2. `b89ccb9b` C# regression: source guard/touchscreen rejection, three buttons, press vs release vs held, ambiguous DOWN/UP, scroll axes and outlier rejection, reset.
3. [CI42509831117](https://github.com/alwansan/raf/actions/runs/42509831117) initial source-policy failure: test asserted obsolete literal `getActionMasked") != 2`; not a C#/Unity failure. No test disabled.
4. `3be65eb53427359abeeb4950685699e7dc2979a1` — updated T4 static policy to require non-MOVE callback branch **plus return false and no queue-state injection**, preserving original test meaning.
5. [CI42510026195](https://github.com/alwansan/raf/actions/runs/42510026195) **SUCCESS** on exact `3be65eb5...`: 21/21 Python static/source controls, **68 C# actual assertions**, real original ZIP2 DLL SHA gate, Unity2021 Android managed bridge compilation and Editor-target compilation, original mouse routing private staging. [Platform adapter42509831023](https://github.com/alwansan/raf/actions/runs/42509831023), [T5 original byte-equality42509831039](https://github.com/alwansan/raf/actions/runs/42509831039), [T4 classifier42509830933](https://github.com/alwansan/raf/actions/runs/42509830933) also source-only success on earlier `b89ccb9b` SHA.

## Coordination / builds / truth
- Latest owner directive: ONE T1–T5 shared mini APK and pack, T5 owns build and signing. No T4-only mini requested. T4 updated own row in `apk-for-testing/SHARED_BUILD_READINESS.md` to **NO_BUILD** (no T4 changes to compiled shared lab; team’s other independent NEED_BUILD votes preserved), vote commit `af59b15061875d5f37ada854f9ef2da9ac2a2731`.
- T5 shared one-mini [CI42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) had completed **SUCCESS** when reviewed, source `3555bafae757bb0523e00e171582530ab4193b32`; artifact/package/signature/download and phone proof belong to T5. Do not present as Android-device test, nor assume it includes these later GAME source edits.
- No Unity full game, native build request, ZIP2, .rgd, Settings, audio, touch, CL or another team worker file changed; no CI cancellation, no force.
- **Limitations:** we have **not proven Android actually fires button/wheel callbacks in a captured Unity View**; nor Unity `Input.GetMouseButton`, `Mouse.current`, horizontal/vertical scroll consumption. Android View false does **not** promise Unity game mapping. `INPUT-005 OPEN`; full readiness NOT_READY 0/3.

## Next
Use one shared T4-01..09 actual phone session and fresh current-game signed-build input markers. Compare Android captured callback fields, Unity consumption and physical buttons for each capture ON/OFF phase. Fix only observed dispatch gap, preserve camera/cursor/touch/keyboard and no duplicate Mouse0, perform Unity/player/device regression before any claim of click or scroll success. Do not demand five mini APKs.
