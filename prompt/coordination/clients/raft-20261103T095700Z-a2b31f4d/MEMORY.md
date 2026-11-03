# A2 session — display/Settings investigation

- Identity: raft-20261103T095700Z-a2b31f4d; session a2-20261103T095700Z-b7e41c2f.
- Base HEAD: 84843b8c21847faf663126dc399c6b7947f8a0e8; only feature/android-native-port writable.
- Starting scope: DISPLAY-003 orientation/Settings aspect source review; no Unity/APK/OBB/XAPK/release and no automation edits.
- Coordination protocol, AGENTS, permanent owner requirements read. Other active client owns FFT-FORMAT-009 butterfly-storage hypothesis; avoid shared files until reading current plan and coordinating.
- Incoming actions and CL logs are read-only. Other clients, work/experiments, and STATUS to be reviewed before implementing.
- Next: read handoff and existing settings/orientation code/tests, select a falsifiable CPU-only case.


<!-- A2-DISPLAY-003-CI41616959190 -->
## Verified A2 checkpoint — 3 November 2026

- Source-only original Settings UI investigation commit: [b4ab727](https://github.com/alwansan/raf/commit/b4ab7275cdadead58081d188cea305d8aa814766). Original CSharp9 SHA-pinned CPU-only [CI41616959190](https://github.com/alwansan/raf/actions/runs/41616959190) **COMPLETED SUCCESS** job125852692510. Four Python synthetic fixtures passed. Private original 2,394 C# source files scanned, 8 Settings-related,20 lexical sites; ControlsSettingsBox contains direct sizeDelta setter at line110, GraphicsSettingsBox known Screen.SetResolution line565, DynamicResolution calls at37/55. No direct CanvasScaler matching setter within selected eight files. Actual cause of owner Settings UI stretching still unknown; this is not gameplay/Unity/phone repair. [Report](../../../../docs/A2_DISPLAY_SETTINGS_LAYOUT_SOURCE_2026-11-03.md).
- Reviewed concurrent FFT-FORMAT-009, HAPTICS-008, WATER-001 and INPUT-005 plans; no known competing DISPLAY-003 work. All changes confined to A2 isolated scanner/test/CPU workflow and own records; shared checkpoint/handoff/display audit appended without overwriting prior text. Prior CL read-only 2 Nov folders unchanged; last old game APK80 source9462f8e (11 assets).
- Work experiment completed; **DISPLAY-003 remains SOURCE_REVIEW_REQUIRED**, game NOT_READY and full candidate reviews0/3. No Unity/APK/OBB/XAPK or Release; no source asset/.meta/GUID/touch, native-request or scheduled-task changes.
- Next useful work: source-lock original ControlsSettingsBox.cs method around sizeDelta110 and inspect actual serialized Settings CanvasScaler/RectTransform components; only repair confirmed defect, then CPU test. Do not assume lexical references are executed call paths. Session state should be paused after documentation; no continued execution promised.


## A2 resumed source investigation (2026-11-03T10:49:21.557Z)
- Resumed same paused identity raft-20261103T095700Z-a2b31f4d in new session a2-continue-20261103T104921-f42c8a91; no other DISPLAY-003 plan at review. SHA pinned original ControlsSettingsBox b64ba19e2d55fe503045e523c3c8658adb4ca3ededaccfecf6521bad1600ef92; previous CI41616959190 success on original 2394 files.
- Proposed independent scope: bounded original sizeDelta setter target and method context, without private source printing. Only class/source semantic evidence before editing game UI. Read-only CL roots unchanged. Existing original guard remains intact. All nonterminal Actions and scheduled native builds absent in snapshot; refresh before experiment.


<!-- A2-DISPLAY-003-CONTROLS-CI41623586923 -->
## Completed A2 follow-up

[CPU-only original-source CI41623131096](https://github.com/alwansan/raf/actions/runs/41623131096) at [ee8b11e](https://github.com/alwansan/raf/commit/ee8b11e88aee10530f16b927e09d4f37af5694d4) and [refined CI41623586923](https://github.com/alwansan/raf/actions/runs/41623586923) at [b9ec97d](https://github.com/alwansan/raf/commit/b9ec97d2776e8504a0c5d71f1b226e29f320707c) both COMPLETED SUCCESS (refined nine synthetic tests plus original CSharp9 source SHA pin).

Original ControlsSettingsBox SHA256 b64ba19e2d55fe503045e523c3c8658adb4ca3ededaccfecf6521bad1600ef92. Its unique executable `.sizeDelta` write at line110 belongs to method106–112. Receiver matches a `RectTransform` declaration elsewhere in same owner class (not a method RectTransform/Transform parameter); RHS is a simple identifier, not a Vector2 parameter or direct screen-width/height reference. This method has no direct Screen.SetResolution/CanvasScaler scale-property writes or explicit same-owner invocation, and is not a recognized lifecycle method. Lexical context is not causal/serialized scene proof.

DISPLAY-003 SOURCE_REVIEW_REQUIRED, NOT_READY/0 of3; no runtime, Unity/APK/OBB/XAPK, GUID/.meta, LFS, touch, tasks, native requests or release changed. Next inspect authenticated serialized Settings UI CanvasScaler and opening/UnityEvent path.

- Separate work and experiment closed; A2 state paused. No work continues between turns.


## A2 third turn — serialized Settings scene investigation
- Resumed only after user Continue from paused state at 2026-11-03T11:24:00Z; new session a2-continue-20261103T112400-f7a82190.
- Source from branch 3fa646ed1dca28071d2b65c6394f0003231362e6; no other DISPLAY-003 active work. Prior CSharp9 Controls CI41623586923 success; Settings stretch not proven.
- New experiment uses 6 original non-LFS Unity binary scenes, exact Git SHA1 blobs; avoids all LFS, CanvasScaler/RectTransform unknowns explicitly retained and no game runtime changes.
- One independent native build41624581951 was in_progress on older source c7254f7d during review; do not cancel/alter or infer any device proof.


<!-- A2-DISPLAY-003-SCENE-CANVAS-CI41629641835 -->
## Completed A2 third-turn original serialized UI experiment — 2026-11-03T11:45:56.088Z
- Registered this resume as session a2-continue-20261103T112400-f7a82190 in scoped DISPLAY-003 work record. Only feature/android-native-port modified; peer work unchanged.
- Code/test commits [8feac3e](https://github.com/alwansan/raf/commit/8feac3e6921f260ab5098a4e77d6279a3883bc3e), [0a2eee0](https://github.com/alwansan/raf/commit/0a2eee0dcf0c9ea73ded43f1c744e82f195541dc), [86bd9a0](https://github.com/alwansan/raf/commit/86bd9a0ec84df9f9764b649680d11478afabcf59), [db9ba867](https://github.com/alwansan/raf/commit/db9ba867619a67bbb05f047fcf17fddd632dfbb2). Independent no-LFS CPU runs41628388766 (8),41628772940 (11),41629163061 (11+5),41629641835 (11+7) all SUCCESS. Last job125895634545 on exact code db9ba867.
- Six non-LFS source scene Git OIDs and original global MonoScript OID verified. Scene0 Canvas4/Rect1644; scene1 Canvas56/Rect3033. Verified original UnityEngine.UI.CanvasScaler class, 4 scene0+13 scene1 MonoBehaviour script PPtrs; all 17 same GO as native Canvas. One Settings-class-name MonoBehaviour on Settings-named GO per scene, neither verified native ancestor has scaler (another Settings-named scene0 GO is inside native Canvas). Custom MonoBehaviour UI scale fields not decoded; no actual owner Settings aspect defect proven. [Detailed report](../../../../docs/A2_ORIGINAL_SCENE_UI_CANVAS_2026-11-03.md).
- Shared checkpoint [STATUS](../../../STATUS.md) and handoff updated with **NOT_READY/0-of-3**, DISPLAY-003 SOURCE_REVIEW_REQUIRED. No original game assets, .meta/GUID or C# runtime touched; no Unity/native request, APK/OBB/XAPK release, LFS hydration, CL write or scheduled automation; independent older native CI was left untouched.
- This work and experiment now completed; A2 paused. Next: only source-locked authentic CanvasScaler custom parameter decoding and page-to-canvas runtime reachability. Do not override all UI scaler settings speculatively.


## A2 resumed CanvasScaler raw-schema investigation — 2026-11-03T12:07:40.695Z
- Resumed after explicit user Continue, new session a2-continue-20261103120740-de5c9031; previous state paused and DISPLAY-003 earlier scoped work completed. Current SHA 034abfbc4fce60bf4be2466b126d10984f2ea19b. No other DISPLAY-003 plan observed; other source clients working water/render/inputs.
- New scoped work: original UnityEngine.UI.dll (Git blob 7c31ff89d8525add38b34f218666f6c9d8db0a58) + existing non-LFS exact scene/source pins; test raw serialized UI scaler parameters only when backed by matching metadata/length. Otherwise mark UNKNOWN, never inject runtime changes speculatively.
- Other native build41624581951 previously failed on unrelated older source; no cancellation/rebuild initiated by A2.
