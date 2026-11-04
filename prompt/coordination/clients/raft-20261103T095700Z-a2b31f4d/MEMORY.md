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


<!-- A2-DISPLAY-003-VALUES-CI41636519603 -->
## Fourth A2 work session: authenticated original CanvasScaler configuration — 2026-11-03T12:36:53.126Z

- Source-only scoped work registered with session a2-continue-20261103120740-de5c9031 and independent DISPLAY-003 work/experiment files. Exact original UnityEngine.UI.dll Git blob `7c31ff89d8525add38b34f218666f6c9d8db0a58`, original scene0/scene1/global MonoScript Git SHA pins from prior run. No other DISPLAY-003 owner wrote competing files; shared docs append-only with SHA conflict-retry.
- Source/test workflow commits [05088480](https://github.com/alwansan/raf/commit/05088480be2d0dd5dd92d91296e0f3a7d0a61189), [a78249f5](https://github.com/alwansan/raf/commit/a78249f522b576e34c6d29dce0e4a2b11486da9f), [b83f51a1](https://github.com/alwansan/raf/commit/b83f51a1c1e921332d610d995db3fcb409255071) and intermediate diagnostics. Authenticated final [GitHub Actions41636519603](https://github.com/alwansan/raf/actions/runs/41636519603), job125918983831 **COMPLETED SUCCESS** 8+8 synthetic tests, original managed UI metadata and 17 authentic serialized CanvasScaler objects validated and decoded. Intermediate CI failures corrected: guessed script PPtr offset20 vs original16; 4-byte editor preset bool misclassified; incorrectly escaped zero padding and synthetic trailer fixtures. Never claim these as device/game failures.
- Original 80-byte component: native typed MonoBehaviour32-byte base, 44-byte ten UI numeric fields, 4-byte [SerializeField] m_PresetInfoIsWorld bool and pad. All17: reference1920×1080, uiScaleMode1, screenMatchMode0, matchWidthOrHeight1 (height); original scaleFactor1 sixteen components, 0.66 one level1; editor preset false. Unity complete custom TypeTree still not independently available; source/bytes/pointers corroborate.
- [Detailed report](../../../../docs/A2_ORIGINAL_CANVAS_SCALER_VALUES_2026-11-03.md) and [STATUS](../../../STATUS.md) + [latest handoff](../../../../docs/WORK_SESSION_HANDOFF_2026-11-03_LEFT_TOUCH_AND_RESUME.md) updated. No original game assets, .meta/GUID, runtime UI code, CL, scheduled tasks, full native build request, Unity/APK/OBB/XAPK or LFS changed by A2.
- Scope experiment **completed**, A2 **paused**. General DISPLAY-003 source-only follow-up requires actual Settings panel to Canvas pointer/callback chain and Android viewport/aspect before changing runtime. WATER-001/RENDER-002/FFT-FORMAT-009 and other build blockers remain; **NOT_READY / 0/3** full immutable candidate reviews.


## A2 Settings owner-link follow-up — 2026-11-03T14:48:37.472Z
- User explicitly resumed paused A2 with session a2-continue-20261103144837-72f30c9a; live SHA 0a1e260bb1e4cbe211cb05c3374bfd0e4d0af696.
- Earlier SHA-pinned CanvasScaler 17/17 authentic serialized values CI41636519603 SUCCESS, but displayed Settings panel to UI Canvas pointer path unverified. This new independently scoped work reads exact original scenes0/1 and source-managed Settings CSharp9 and enumerates candidate raw references without claiming typed pointers.
- Latest branch HEAD/Actions/release/CL checked read-only; current NOT_READY/0 of3 and independent water/render jobs unaffected.


<!-- A2-SETTINGS-OWNER-LINKS-CI41660274964 -->
## A2 original Settings raw-to-native-canvas candidate investigation — 2026-11-03T15:11:45.766Z

- Resumed explicitly by owner after prior state paused, session `a2-continue-20261103144837-72f30c9a`, initial HEAD `0a1e260bb1e4cbe211cb05c3374bfd0e4d0af696`. Read permanent prompts, live branch HEAD/commits/Actions/releases, CL read-only, coordination, own past report; own new work and experiment registered before code at [af85dde9](https://github.com/alwansan/raf/commit/af85dde964781ce6d392e3977520e63005d1d538).
- Code [5214d320](https://github.com/alwansan/raf/commit/5214d3209d3970b69441d7096aebe35586c224ee), independent CPU-only workflow/tests [5006ba9](https://github.com/alwansan/raf/commit/5006ba9cb9d7763d7bcf67c415e24717cd0b3046). Authentic [CI41658552259](https://github.com/alwansan/raf/actions/runs/41658552259) success7/7 with original Settings CSharp9 SHA pin and native scene0/1+global scripts Git pins. Original Settings owner MonoBehaviour one per scene,612 bytes. Raw i32/i64 local pointer 48 byte-pattern hits each:11 GO,34 MonoBehaviour,3 RectTransform; 45 level0/48 level1 hit verified native CanvasScaler ancestry.
- Important failed **hypothesis**: the 48 patterns were not 48 contiguous independent 12-byte PPtrs. Original offsets first52,last600; five8-byte overlapping starts, forty-one12-byte starts, one16-byte gap. [Refined source e7caa10](https://github.com/alwansan/raf/commit/e7caa10d995cc89070dff4a1d09a2d45d9e25faa), success CI41659857942. Added DP disjoint PPtr interval proof [11def7c6](https://github.com/alwansan/raf/commit/11def7c6f33032628bc01f9481ba0b7179ee9978), synthetic negatives [5db3a912](https://github.com/alwansan/raf/commit/5db3a912727c8d2686a3b3301e04b7d80359fe0c), **CI41660274964 completed SUCCESS** job126001319101,10/10 tests + all original SHA-pins; max nonoverlap45 windows,44 mandatory across max sets, candidate targets with scaler ancestry among maximum subsets level0 44–45,level1 45.
- This is only native ***candidate*** raw PPtr structure; no verified original Settings.cs field name/Unity array mapping, opening/UnityEvent/prefab panel reference, or Android runtime defect. Avoid misrepresenting as 48 real references or as a settings aspect root cause. [Report](../../../../docs/A2_ORIGINAL_SETTINGS_OWNER_LINKS_2026-11-03.md). Shared [STATUS](../../../STATUS.md) and [handoff](../../../../docs/WORK_SESSION_HANDOFF_2026-11-03_LEFT_TOUCH_AND_RESUME.md) appended and verified.
- Only feature/android-native-port changed; CL read-only. Did not start Unity/APK/OBB/XAPK, native request, release, LFS; did not change original game runtime/UI/assets/meta/GUID or automated tasks; no peer job altered. DISPLAY-003 OPEN and NOT_READY/0-of-3, pending typed original Settings field/collection layout and actual UI canvas ownership. Own experiment and work completed; state paused until explicit user turn.


## A2 resumed ZIP2 source provider and Settings typed-field experiment — 2026-11-03T22:28:47.961Z
- New session a2-continue-20261103222847-8f51a4d2 resumed from paused A2 after explicit Continue. Current HEAD d9e3a051a623964aed767876972f52511e27b844.
- Owner ZIP2 source provider pinned at 15964ea8; ordinary Git blobs managed DLL/level0/level1/global scripts exactly match prior original A2 pins, no LFS. Fresh independent CPU-only Settings typed field source probe planned, not native build.
- General DISPLAY-003 OPEN and NOT_READY/0 of3; other client water/shader works left unchanged.


<!-- A2-DISPLAY-003-ZIP2-ORIGINAL-CI41733061252 -->
## A2 ZIP2 no-LFS source and original Settings field-type experiment — 2026-11-03T22:46:26.639Z

- User explicitly supplied complete source branch `zip2/Raft`; owner provider instructions read at docs/ZIP2_SOURCE_PROVIDER.md. Pinned SHA15964ea8f246b6e076ce26b60931ee2e1a9a2385, read-only. This A2 cycle registered session `a2-continue-20261103222847-8f51a4d2` and scoped independent work/experiment before edits.
- New source-only script/tests/independent workflow `scripts/probe_a2_settings_typed_fields.py`, `tests/test_probe_a2_settings_typed_fields.py`, `.github/workflows/raft-a2-settings-zip2-typed-fields.yml`. Sparse ZIP2 checkout `filter:blob:none`, lfs:false; verified original four ordinary Git blobs: Assembly-CSharp.dll, globalgamemanagers.assets, level0, level1, plus exact normalized private original Settings.cs SHA `904c52b337fe951f711e2efc15bfafc4fc77f2a8d2cc9c5bee2f7d14075103ad`. No full ZIP2/split files or LFS transferred.
- Final [source a2455448194317481a60a7199d932f85d2c2014f](https://github.com/alwansan/raf/commit/a2455448194317481a60a7199d932f85d2c2014f), [original CPU CI41733061252](https://github.com/alwansan/raf/actions/runs/41733061252) completed SUCCESS with7/7 synthetic tests and original managed/scene SHA checks. Original Settings has14 own-class candidate serializable field declarations:4 known Unity-native ref types,8 custom (6 class names match SHA-locked Assembly-CSharp MonoScript registry,2 not resolved), one collection with unresolved element, one four-byte scalar. Names not printed nor source exported. Interim CI41731684797 failed due short synthetic fixture length; corrected; CI41732159476 initially missing optional UnityPy; corrected. Other original CI41731775311,41732187637 and41732807830 SUCCESS at successive versions.
- Previous original raw Settings byte patterns 48 overlapped; max45 nonoverlap candidates. Do NOT pretend the 14 source declarations map to 14 typed PPtrs, or infer actual Settings page-to-Canvas ownership. Exact type metadata tokens, nested field/array byte schema and effective landscape layout remain open. [Full report](../../../../docs/A2_SETTINGS_ZIP2_TYPED_FIELDS_2026-11-04.md). [STATUS](../../../STATUS.md) and [handoff](../../../../docs/WORK_SESSION_HANDOFF_2026-11-03_LEFT_TOUCH_AND_RESUME.md) updated.
- No original Unity assets, shader/material/gameplay code, .meta/GUID, CL, protected branches, native Unity/APK/OBB/XAPK, Release, other agents' CI or scheduling modified. Bounded experiment complete, A2 paused; DISPLAY-003 SOURCE_REVIEW_REQUIRED and overall NOT_READY/0-of3.


## A2 resumed source-backed managed Settings schema — 2026-11-03T22:54:17.092Z
- Explicit user Continue after previous paused ZIP2 CSharp field inventory. New session `a2-continue-20261103225417-c42fe8d1` from `a2-continue-20261103222847-8f51a4d2`, HEAD `d9440e405a6dc94e3570ba5e963fbddfb592eed9`.
- New independent DISPLAY-003 scope: validate exact original source managed field metadata tokens and typed collection layout using pinned ZIP2 source `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; avoid reading split/LFS or writing any source game assets. Previous CI41733061252 passed seven synthetic tests, but fourteen source declarations and forty-five possible byte PPtr windows not mapped.


<!-- A2-DISPLAY-003-ZIP2-EXACT-FIELDDEF-CI41737541506 -->
## A2 authentic original Settings managed TypeDef/FieldDef identity — 2026-11-03T23:18:14.572Z

- Explicit owner Continue after prior A2 ZIP2 source-only experiment paused; session `a2-continue-20261103225417-c42fe8d1` resumed from `a2-continue-20261103222847-8f51a4d2`. Before code registered independent DISPLAY-003 work/experiment. Only feature/android-native-port edited; immutable ZIP2 source read-only pinned `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- Added `tools/a2-settings-metadata/SettingsMetadata.csproj` + `Program.cs` using Mono.Cecil0.11.6 deferred reading, `scripts/probe_a2_settings_metadata_contract.py`, synthetic `tests/test_probe_a2_settings_metadata_contract.py`, isolated `.github/workflows/raft-a2-zip2-settings-metadata.yml`. Exact ZIP2 original small four Git files and private original CSharp9 Settings.cs SHA checked; temporary private metadata JSON not emitted.
- Important corrected hypotheses: Mono.Cecil Immediate mode cannot deserialize UnityEngine.CoreModule custom attributes without the external engine assembly; changed to Deferred and guarded source kind resolution. Sixteen same-simple-name `Settings` managed types share empty namespace; only exact top-level full name corresponds to original native scene MonoScript; class-name + namespace alone was misleading. Synthetic and original CI failures were diagnostic, not APK/game runtime failures.
- Final [source commit `243771a29d`](https://github.com/alwansan/raf/commit/243771a29db8d5227278f552274b5c3bab76fa2b), [**CI41737541506**](https://github.com/alwansan/raf/actions/runs/41737541506) job126270493239 **COMPLETED SUCCESS, 10/10 synthetic tests**, original scene0/1 exact Settings MonoScript to top-level TypeDef identity and all 4 Git SHA source checks. Managed Settings class 21 FieldDefs, 13 metadata-eligible candidate fields; private source CSharp lexical scanner previously reported 14 but one has NO matching FieldDef. All the other13 names and declaration order match exact metadata tokens. Candidate families 6 source-assembly classes,4 UnityEngine-prefixed,1 external resolved class,1 UnityEngine-prefixed array,1 <=4-byte scalar.
- This resolves original TypeDef identity and field count, **NOT** Unity serialized field offsets, full custom Settings TypeTree, actual array lengths, instantiated Settings UI→CanvasScaler route or Android orientation stretch cause. Original previous raw48 matching pointer byte patterns overlap, no direct typed field proof. [Detailed report](../../../../docs/A2_ZIP2_SETTINGS_METADATA_2026-11-04.md), shared STATUS/handoff and own discussion updated. General DISPLAY-003 OPEN, project NOT_READY/0-of-3.
- No original game source, shader/material, assets, .meta/GUID, LFS, CL, release, native Unity/APK/OBB/XAPK build or scheduled tasks changed; no peer Actions cancelled. Own bounded experiment/work completed, session paused at next checkpoint.

<!-- A2-MEMORY-TOUCHED-BY-W2-20261104T2215 under explicit owner takeover directive -->
## [W2 takeover]route gap completed — 2026-11-04T22:15 (agent W2 92502b76)
- Under the owner's explicit directive W2 reviewed your paused DISPLAY-003 state and completed your listed gap "instantiated Settings UI→CanvasScaler route".
- Proven (count level, docs/W2_SETTINGS_PANEL_ROUTE_2026-11-04.md, own committed artifacts, CI pending in this push): for both scene instances (level0/level1) — manager root Transform node with canvasAncestorsAbove=0; full-page Canvas 1 hop below with CanvasScaler+GraphicRaycaster; GraphicsSettingsBox+ControlsSettingsBox exactly 3 hops below that canvas; 41 scaler-canvas nodes reconcile 41 instantiations; only the 2 route canvases hold settings-family content; resources.assets Settings = dangling null-GO template.
- The byte-window blocker likely was: child edges are child RectTransforms (resolve via child m_GameObject), not child GOs — naive scans enumerate empty branches.
- Yours untouched: typed offsets, full custom TypeTree lengths, orientation-stretch cause.
