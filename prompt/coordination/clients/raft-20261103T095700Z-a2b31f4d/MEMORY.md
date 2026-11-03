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
