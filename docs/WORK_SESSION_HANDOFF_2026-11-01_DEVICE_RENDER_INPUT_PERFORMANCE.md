# Raft Android — authoritative Work transfer: device rendering, input and performance
Date: 2026-11-01. This checkpoint supersedes older status summaries; it does not erase their evidence.

## Authority, scope and reading order
Work ONLY on alwansan/raf branch feature/android-native-port. Never modify, merge or delete main, zip or Unity-Editor. Owner authorizes technical decisions, fixes, small tests, commits and appropriate Actions without asking each step. User has no computer. Main goal: restore complete Singleplayer, original .rgd saves, audio, touch and performance; then phone hosting/joining over LAN or suitable transport. Steam multiplayer is not required.
Read this file completely, AGENTS.md, then docs/WORK_SESSION_HANDOFF_2026-11-01_FMOD_ANDROID.md and the complete docs/WORK_SESSION_HANDOFF.md through their last sections. Read Mesh/dependency reports, VERIFIED_FINDINGS, FMOD_ANDROID_INTEGRATION.md and relevant workflows/scripts/tests. Earlier headers can be stale; newest verified checkpoint wins.
At every continuation inspect remote HEAD, newest Actions and https://github.com/alwansan/CL/tree/main/raft%20log before deciding what to do. That directory is updated by the owner after phone trials.
This transfer is documentation only: new rendering/input/orientation/performance fixes described below are NOT implemented by this checkpoint.

## Current remote/build evidence
Remote HEAD before this documentation commit: f4a41ddcfefb77e9547c26011901f57cab7080a8 (documentation); native implementation source c80fb4d2890a92adf0fafad355c4f5834bfd67d8.
Latest native run inspected: https://github.com/alwansan/raf/actions/runs/41289171484 — completed SUCCESS.
Release: https://github.com/alwansan/raf/releases/tag/android-early-test-41289171484-1
Direct APK: https://github.com/alwansan/raf/releases/download/android-early-test-41289171484-1/Raft-Android-EarlyTest.apk
Asset: 1,323,198,247 bytes; GitHub release asset digest sha256:a911e32d3301b455bebf5f02f86f4d2495fb942bbfe4e4f567fb17199cb6bb86.
This digest is GitHub asset metadata, not a fresh local full-download hash in this transfer. Do not reuse hashes from older APKs.
Run 41257065669 from the initial user prompt is historical, not the newest checkpoint. Prior APK 41282151738 and older crash logs must not be treated as this latest session without matching version/session/time.
Successful ARM64 IL2CPP build is NOT proof of functioning gameplay, water, sound, saves or controls. New phone screenshots prove original menus can be reached. Owner reports mouse and keyboard work; touch does not. No full world creation/load/save or sound acceptance is established.
No heavy build was started just to prepare this transfer. Recheck Actions on resumption; do not duplicate an active run. If only a known >10-minute job remains, provide its link/status and stop waiting.

## Latest actual phone evidence reviewed
Correct screenshots are in CL/main/raft log/img, not the unrelated root img directory. All five screenshots were actually viewed in this session. Tree a27689c0fbedae8ff9e9deccaa4aa1fe6a14da8e.
| Screenshot time in filename (2026-11-01) | Git blob SHA | Observed evidence |
| --- | --- | --- |
| 12-59-22-044 | 1797e899a4af843b3470655e56083ce45fbb24d5 | Portrait original menu; flat washed-out gray/blue background, large blank cream/white rectangles; many main menu labels readable. |
| 13-02-11-828 | 2c06a64bd053924fa7fcb4a5cd12e851a45cc2e5 | Landscape; much of background solid white/black cutouts; UI region visible. |
| 13-12-42-146 | 8f0f6ef5863b7cafa5505898759cee5c8b5a81ec | Create New World modal opens; some text readable, other glyphs scattered/overlapping/corrupt. |
| 13-14-20-351 | 253984d32ecfddfb8c1eb4d02803460f931bfd9f | Load World modal opens; No Worlds Could Be Found readable; some buttons corrupt. |
| 13-15-06-665 | a341b15a27ae08240395bc65421fddb5c3789f5d | Character modal opens; Survivor readable, outfit/character options corrupt; mouse cursor visible. |

Small logs reviewed: raft log/log.txt blob e8ee46c3eebecc6c13af41301e3b67a1d2ee7dae (50,733 bytes), log2.txt c5c666b7be008e9b23b617f12778911867ea7f93 (49,879 bytes), log3.txt 949246c9fc11f972bb46e81152d4e27378e6f276 (237 bytes).
The first two repeatedly report Invalid pass number (3) for Graphics.Blit (Material "PostFX - Bloom" with 1 passes).
log3 contains the older native libfmodstudio offset 0x101e94; do not conflate it with later managed errors.

Sandbox uploads are under raft log/انتاج مسار  (trailing space), tree 054de5eaa48777af4f6441f91774e31475561d39. Two copies exist: 2/com.alwansan.raft.androidtest/... and storage/emulated/0/Android/data/....
Persistent logger files REALLY exist on the phone. Session 20261101T101210556-048072fa retains segments 0005–0016: ~4 MiB each except final 485,830 bytes. Rotation has already removed earlier segments. Final segment blob 3efc1741a201601f393089a311b2812aa1c2a0b6 was fully read; 396 valid JSONL rows, sequence 54759–55154, UTC10:15:13.451–10:15:20.103. This is a ~6.65-second tail, NOT the entire session.
Counts within this tail only:
- Bloom invalid pass 2:57, pass3:57, pass1:14.
- UltimateWater/Foam/Global pass1 with only1pass:52.
- Hidden/BilateralBlur passes2/3/12:14 each.
- UltimateWater/Spectrum/Water Spectrum passes3/5:13 each.
- UltimateWater/Utilities/Blur (Subsurface Scattering) pass1:13.
- Sandbox/VolumetricLight requestedpass4 but subshader0 only1validpass:13.
- Other unknown-material pass errors also present.
- NullReferenceException first-line group:28; inspected representative stack enters FMODUnity.RuntimeManager.Initialize, get_Instance, GetEventDescription, StudioEventEmitter.Lookup/Play; rethrown SystemNotInitializedException "[FMOD] Initialization failed", then get_CoreSystem / HapticManager.Update. Sound is NOT verified fixed.
- Invalid kernelIndex(6), must be non-negative less than0:13. Stack UltimateWater.Internal.Dx11FFT.ComputeFFT → WavesRendererFFT.RenderMaps → WindWaves.OnWaterRender → WaterCamera.RenderWaterEffects/OnPreCull.
These are concrete active barriers, not hypothetical hardware issues. Do not hide exceptions or clamp missing shader passes to0.

Uploaded profile.id is present (33 bytes); do not print its contents or personal identifiers. Settings.rgd exists (1,643 bytes, blob7aa85cc63877a4bc214e49c4e4427619814566c1). File existence proves settings output, not complete original world .rgd roundtrip.

Large LogFox directory tree f6f96db1efde947eabb5469542787765f66ab969 includes ~1.37MB older log and newer ~28MB/~71MB/~7.5MB/~62MB logs. Split sets (5) and (6) repeat the same three blob SHAs (47,185,920 +47,185,920 +14,681,728 bytes). Deduplicate by blob SHA and read README before concatenation; do not assume zip. Full large newer logs were not all analyzed in this transfer. Prioritize targeted/streamed analysis of startup, graphics device, FMOD first failure and input devices. Do not download LFS or rebuild to read logs.

## Rendering investigation — next work
POCO F5 Pro official specs confirm Snapdragon 8+ Gen1 and Qualcomm Adreno graphics:
https://www.mi.com/global/product/poco-f5-pro/specs/
Common GPU model for this SoC is Adreno730; record the actual device-reported GPU/driver from logs instead of assuming driver/API. ARM64 app already runs. There is no evidence that CPU instruction architecture itself explains white images/corrupt font atlases, nor a magic "add Snapdragon support" switch.
Several unrelated materials have exactly1pass while original callers request many higher passes. Inspect generated shaders, source/export mode, compiled shader subprogram reconstruction and retained original resources first. Map each requested pass to actual original shader semantics; distinguish placeholder/fallback shader export from unsupported backend.
For water, investigate actual compute shader kernel tables/import results and Android graphics API capability: zero kernels is not fixed by a positive supportsComputeShaders flag alone. Windows DX11 shader bytecode is not reusable Android GLSL/SPIR-V. Recover/port actual source when available, or a deliberate functional mobile water path retaining gameplay. Explicitly report unavailable proprietary shader source; never pretend a placeholder pass restores behavior.
Inspect textures and streamed data byte coverage, original formats/UVs, font and TextMeshPro atlases/materials/glyph tables, UI masks/clipping and shader assignments. Restored font GUID references and mesh data do not prove every atlas/texture is intact. Some legible headings alongside corrupt buttons are useful localization evidence.
Record API (Vulkan/GLES), renderer/vendor/version, shader names/support/pass counts, kernel names/counts, relevant material/texture references with bounded logging. Do not indiscriminately disable post-processing/water or all errors. Test minimal shader/data contracts before another native build.

## Required landscape behavior
Owner observed launching while holding phone portrait leaves app portrait. Must always be landscape, including cold start and resume, with no portrait menu frame.
Inspect current Android PlayerSettings/orientation in build script and generated manifest, plus runtime overrides. Set default landscape and restrict autorotation to LandscapeLeft/LandscapeRight (both acceptable); disallow portrait/upside-down. Runtime early initialization should agree with manifest/player settings. Test configuration contracts cheaply, verify final manifest and eventually phone launch/resume. This is a pending fix, not already implemented.

## Input requirements and decision
Owner actually tested external mouse/keyboard successfully. Preserve that behavior. Touch presently does not activate the screen. Bluetooth/USB mouse+keyboard and gamepads/controller hotplug should be supported alongside touch; device-specific mapping still requires testing.
The reconstruction already pins com.unity.inputsystem 1.7.0 in scripts/add_unity_packages.py because original Unity.InputSystem assembly is1.7.0.0. Original project has PlayerInput/InputSystemUIInputModule and legacy MyInput paths. Do NOT blindly replace all input or install latest Unity6 package. First inspect restored actions, bindings, control schemes, EventSystems/modules, UI raycasts, pointer/click references and active input handling.
Official existing package capabilities: https://docs.unity.cn/Packages/com.unity.inputsystem%401.7/manual/SupportedDevices.html
Use compatible existing New Input System for touchscreen UI plus actual on-screen gameplay controls, retaining legacy paths where needed. Correct touchscreen position/press actions, pointer IDs, navigation/submit/cancel and device switching. Distinguish UGUI from IMGUI diagnostics; New Input System does not automatically drive IMGUI. Avoid duplicate event systems/clicks. Touch simulation is not a complete mobile control design.
Gameplay needs simultaneous move/look/action, inventory/crafting/building/interactions/swimming/menus and OS text entry. Keep original gameplay scripts and save schema; implement narrow Android input bridge/adapters. Record bounded device attach/detach/action diagnostics, not every frame/pointer coordinate endlessly. External keyboard/mouse is useful for menu diagnosis but does not prove all gameplay or gamepad support.

## Diagnostics and performance
Actual root is Application.persistentDataPath + /raft-logs:
 /storage/emulated/0/Android/data/com.alwansan.raft.androidtest/files/raft-logs/
Use the /files subdirectory Android supplies, not hardcoded arbitrary external storage or broad storage permissions.
Existing authored components:
- android-port/Runtime/Platform/PersistentDiagnosticLog.cs: threaded managed JSONL sink,queue2048,4MiB×12files (~48MiB),UTC/session/sequence/thread/area/operation/detail,criticalflush,overflowrecords,Unicodeescaping,no Unity-log recursion.
- AndroidRuntimeLog.cs: root,metadata,BeginOperation/EndOperation durations and before/after/exception native stages.
- AndroidTestDiagnostics.cs: capture all Unity log levels; SubsystemRegistration before FMOD; scene/lifecycle events;5s sample frame_ms and GC.GetTotalMemory. Overlay bounded48entries×3000chars and8k preview/full clipboard.
- scripts/instrument_android_runtime_operations.py + config/runtime-operation-traces.json:27 pinned boundaries in SaveAndLoad/Raft_Network/SteamManager/Settings/PlayFabManager, exact source hashes and body/return/rethrow preservation. No passwords/savepayloads; backups outside Unity; metas unchanged.
This is NOT yet full CPU/GPU/RAM/FPS telemetry. The phone proves rotation works but error flood can evict startup evidence; fix logging before adding more volume. Group identical repeated errors with counts/first+last timestamp and periodic summaries while retaining full first stack and critical events. Protect startup/first-failure records separately from rolling routine logs; preserve error visibility and report dropped/aggregated counts.
Add sampled interval FPS, frame percentiles(p50/p95/p99/worst), CPU frame timing and GPU timing only where supported, managed/native/Unity reserved memory and Android process RSS/PSS/available-memory distinctions, GC collections, rendering counters, thermal/battery state when APIs supported, screen resolution/orientation/refresh, graphics driver/API, input devices and scene/operation durations.
Unity FrameTimingManager/ProfilerRecorder support must be checked against2021.3 and actual device; unsupported counters must say unavailable, never fake0. ProcessCPU% differs from CPUframe time; managed heap differs from totalRAM. Do not log JSON everyframe or enable expensive profiler modes indiscriminately. Use small bounded buffers and lowfrequency summaries. Verify no secret/profile/save contents emitted.
Native crashes can bypass C#; critical pre-call flush + LogFox/tombstones remain complementary.

## Reconstruction history and invariants not to regress
- Unity2021.3.45f2, ARM64 IL2CPP, Ubuntu24.04 Actions. UNITY_LICENSE works. No need user PC.
- ILSpy11.2.0.10050/CSharp9:2394 sources,2393 eligible exact coverage. Canonical151Managedproviders; duplicate PlayFab_o excluded only exporter input. Real Mono/Decompiled AssetRipper mode avoids Unknown-backend loss.
-40scenes;64771/64771 script links after129scene-owned SO reembedded into3scenes/264pointers;1203064logical YAMLobjects/metas preserved.
-Mesh83owners,4708meshes (4707finite+1originalempty),2464buffers;1206692otherobjectbodies unchanged;3whole scenestreams; hashes/ranges checked. Not proof all textures restored.
-Font13/13materialrefs restored, SDK9795refs/rewrites149realtypes0requiredunresolved; original metas.
-MicroSplat3 actual float cache/table recovery eliminated33SetPixels exceptions.
-Editor collector guard removed653/654Destroyerrors; old BuildReport663→10 (9compute imports+1Destroy); water OnValidate NullRefs. These are older editor/build counts, not the current phone error counts.
-LocalProfileStore persistent GUID and atomic FileMode.CreateNew claim:8×24thread +12process tests passed; corruptprofiles preserved.
-LocalPlayerIdentity stablepositive nonzero ulong≤long.MaxValue from profileSHA256; consistentnetwork+6SaveID boundaries, not Steam authentication.
-12pinnedsource Android adapter skips nativeSteam/cloud/remoteParty but retains localhost/load/localplayer/RPC; defaultSurvivor,localAppBuild0. Preservemousekeyboard.
-16Windows path literals/7shapes translated with Path.DirectorySeparatorChar. Original SaveAndLoad.Save had Conditional UNITY_STANDALONE_WIN so Android callsites were omitted; added second Conditional UNITY_ANDROID, retainedWindows and originalbody/schema. Harness proves emittedcall, NOT fullworldsave roundtrip. Do not stage experimental LocalSavePaths/world.sav replacement.

## FMOD exact status and tests
Supplied official FMODforUnity2.02.15 already inspected; ARM64 libraries+Java bridge privately provisioned. Do not request download/upload/license setup. FMOD_ANDROID_RUNTIME_KEY exists in UNITY_LICENSE environment. Never expose it or full private SDK.
Sealed10-file runtime/license/meta subset,3ARM64libs+fmod.jar. BCD0x20215/131605. Original Windows managed providers retained. PlatformAndroid resources exact15names:1Android/1default,0manufactured,OBBfalse,empty StreamingAssets subfolder.
36original StreamingAssets files exact bytes/SHA;5banks123817498bytes,compressedBankFiles0. MasterBank101600960bytes,LFSsha10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339.
Original Windows RuntimeManager lacked Android Java init. Authored bootstrap adds explicit java.lang.System.loadLibrary fmod then fmodstudio before original Memory.GetStats/Studio.Util.parseID and org.fmod.FMOD.init, plus core create/getVersion/release versionprobe and flushedstages. This mirrors supplied2.02.15 Android order without publishing SDK.
Olderphone nativeSIGSEGV0x1a0/libfmodstudio+0x101e94 promptedthis. ELFPC not within any exported symbol; nearestprevious CriticalSection_IsLocked0x101d68 size8 is NOT cause attribution. New phone menu evidence does NOT prove FMOD ready: currenttail explicitly shows RuntimeManager.Initialize nullreference. Diagnose first missingobject/settings/resource/platform callback against original exactsource and earlylogs; do not invent settings or suppress exceptions.
Isolated CI source13fb918b791fa2951ffe726f785aa08f2d8fea7d:
-41288919084/job124795884021:14real disklogger tests pass.
-41288918979/job124795883486:3trace+6adapter+4path fixtures;12originalsource compile/27traces pass, RPC/save-call probes.
-41288918950/job124795883731:14FMOD originalprovider compile/order tests pass; no JNIexecution.
-41288918987/job124795883863:18authenticated runtime/ELFfixtures +10files pass.
Read current tests/workflows; small contracts are not substitutes for hardwareverification.

## Actions/publication/security constraints
Native build only explicit [raft-native-build] marker or appropriate dispatch; cancel-in-progress:false avoids accidentally killing long reconstruction. Do not editworkflow while expecting sameactive run to survive ifoldcancellationconditionscouldapply.
[raft-device-test] allows direct testAPK only after APK/FM​​OD/DEX/originaldata/hash/signature gates; short-lived retainedartifact, separatepublisher job contentswrite; reconstructioncontentsread; onlyallowedbranch.
User explicitly authorizes direct APK Releases, no fabricated RIGHTS_CONFIRMED approval gate. Keep rawdecompilation/assets/keys/licenses out of publicrepo/logs/releases. Do not expose gameassets except authorizedbuiltAPK. No LFSdownload solelyforlogreading.
Packagecom.alwansan.raft.androidtest/productRaft Android Test/versioncodeworkflowrun_number. Buildrequires exactly40enabled distinctexisting.unity scenes.
Update handoff after each verifiedresult/fix. Full Singleplayer first; LAN later; no claimfinishedgamefrombuildsuccess. Do not make repeatedAPKtrials the main developmentgoal.

## Concrete next-session sequence
1. Read newesttransfer/history/AGENTS and inspect freshHEAD/Actions; inspect updatedCL logs/images and deduplicate uploadedcopies bySHA. Preserve this checkpoint's distinctions.
2. Target neweststartup FMOD firstfailure and graphicsdevice/backend from largeLogFox or preserveddiagnostics. Investigate originalshader/export pipeline and zero-kernel water path with originalsource evidence. Treat deviceFMODInitializeNullRef as active barrier.
3. Implement boundeddiagnostic aggregation/protectedstartup and meaningful sampledtelemetry so nexttrial is informative; add landscapeconfiguration and inputUIbinding fixes with narrowtests. Do not interleave an unreviewable wholesalegame rewrite.
4. Verify sourcehash/GUID/meta/scene/data invariants, appropriatefocusedtests and adaptedoriginalcompile; then nativebuild onlywhen useful. Inspect buildlogs/APK/libs/manifest/settings/datahashes and publishauthorizeddirectAPK ifappropriate.
5. Continue touchgameplay/controller support and full restoration; owner can checkphonewhenuseful, not mandatory aftereverypatch. Confirm originalworldcreate/save/load and soundwithactualevidencebefore claimingworks.
If needed dependency cannot be obtained through repository, existingprivateartifacts or Actions, tellowner exactly what remainsmissing, officialsource/version/license and step-by-stepdownload/upload/fork instructions plus targetpath/hashvalidation. No unavailabledependency is newlyestablished by this documentationreview, so do notaskforarbitrarySDK or assetupload now.


## Work continuation — 2026-11-01: bounded evidence, landscape and measured frame intervals
Refreshed allowed HEAD4a088d02 and latest Actions: no newer native than completed41289171484. CL raft-log directory and nested tree fingerprints still match the device checkpoint above; no newer phone sample inferred.
Implemented Android build autorotation limited to both landscape directions, and matching early runtime/resume settings. Enabled Frame Timing Stats for future native validation. This is source configuration, not yet final APK manifest/device orientation proof.
Implemented identical Unity error/exception grouping (128 bounded identities, full first stack, repeated count/first+last UTC every5s, unknown-capacity errors pass through). Critical audio/operation boundaries are never grouped. Overlay receives first error rather than thousands of duplicates. A separate startup/ directory keeps up to four bounded256KiB launch evidence files outside routine rotation; routine4MiB×12 retention remains. No automatic upload.
Added five-second interval FPS, bounded2048-frame p50/p95/p99/worst, sample overflow count, latest CPU/GPU FrameTiming only when positive/available, managed/Unity allocated/reserved/unused memory, GC count, process VmRSS, screen/orientation/refresh and GPU driver/API/compute/CPU metadata. ProcessCPU%,PSS,thermal,draw calls explicitly unavailable; Unity allocation is not processRAM. FrameTiming samples are latest, not interval GPU averages. Native/device support remains unverified.
Added real disk-rotation/startup-retention and10000-parallel-repeat-count regression cases. Existing7 diagnostics/40scene policy fixtures pass locally; new CSharp checks await Actions (no local dotnet). No native request yet. Original.rgd schema, metas, scenes and gameplay bodies untouched.
Renewed session-only encryption recipient for no-LFS original input/FMOD/compute private inspection, targeting actual native job124796660828. Private key outside repository. Only ciphertext may be transported; never publish raw decompiled source. FMOD Initialize NullReference, zero water kernels, shader pass loss, font texture coverage, touch/gamepad actions and full Singleplayer remain OPEN. Do not describe this infrastructure work as resolving them.


### Verified isolated CI and actual FMOD resource-loader root cause
Implementation b5bc834796775bde522a306b530a978a3b97dabd: persistent storage41299961656/job124828669179 PASSED; original Android-macro compile/RPC/save instrumentation41299961615/job124828669101 PASSED; encrypted inspection41299961644/job124828669366 PASSED. Packet115files decrypted privately and every manifest hash verified. No proprietary source published.
Actual original FMOD Settings.OnEnable calls PopulatePlatformsFromAsset, which clears Platforms and executes Resources.LoadAll<Platform>("FMODStudioSettings"). The flattened exported sibling assets are invisible to that lookup, so DefaultPlatform and FindCurrentPlatform can be null before RuntimeManager dereferences SampleRate. The earlier Editor validator's independent15file lookup did NOT establish that vendor runtime graph was populated. This is a confirmed source/layout mismatch consistent with the phone NullReference, not native-loader failure.
New narrow restore_fmod_resource_layout.py moves exactly15 original platform asset+meta pairs into Assets/Resources/FMODStudioSettings/, keeping the root FMODStudioSettings.asset, all payload/meta bytes/GUIDs and GUID-based references. All destinations validated before moving; rollback on failure; idempotent. No substitute settings, platform defaults, reflection patch or competing FMOD SDK. Editor validator now uses the corrected resource paths AND requires vendor Settings.Platforms to contain every original platform, DefaultPlatform nonnull and Android present. Four topology safety fixtures plus3resource-policy fixtures pass. Real Unity import/runtime verification pending.
Read full61636248-byte LogFox file(4), originalblob44ffee41b687d01411e6c2da63ab5e40053b3bb8. Same Raft process1854/thread5661 identifies AdrenoVK Vulkan driver0615.95,compilerEV031.36.08.30,applicationRaftAndroidTest,engineUnity,requestedAPI0x00401000(Vulkan1.1). Other processes also use GLES; do NOT attribute them to this game. Actual GPU model string is still absent from this sample. Native/Java success marker at1793527872.017 reports nativeVersion00020215; first managed FMOD Initialize NullRef1793527881.373. Thus original native-loader/version gap is demonstrably past in this launch, while FMOD Studio/audio still fails. DeviceSingleplayer/audio/save/touch not accepted.
One deliberate native validation is justified by this concrete original-resource-topology fix plus already compiled diagnostics/orientation changes. Keep all existing fidelity/40scene/source/meta/FMOD/originalbanks/signature gates. A new release is evidence vehicle only; not gameplay completion. Inspect actual failed gate or vendor platform graph result before any further build.


### Active native validation41300265252 — owner wait checkpoint
Source81bab94c3784984bca4cccca87e88e03d747b75c, https://github.com/alwansan/raf/actions/runs/41300265252 . License124829562980 SUCCESS; reconstruction124829584909 IN_PROGRESS at original CLR-provider validation(step5); preceding synthetic tests passed. Original-source full Android-macro compile41299961615 SUCCESS. Actual persistent-log run41299961656 reports224checks passed, including10000-parallel repeat counts, protected startup under rotation and bounded4launch retention. These are isolated CI results, not phone metrics.
New move/policy fixtures4+3 and delivery5 passed locally; YAML/embeddedPython/no-cancel validated. Render contract scanner adds bounded shader-pass/kernel histograms; Editor adds actual InputActionAsset touch/mouse/keyboard/gamepad binding totals. These are inventories, not touch/gameplay fixes. The original vendor resource loader must actually populate15platforms/default/Android in Unity; if the new directory/file resource-name topology still fails that strict gate, inspect exact Unity Resources semantics rather than weakening the check. No native success/audio fix claimed.
Actually viewed create-world screenshot13-12-42 again: headings/main menu mostly legible, button glyph regions noisy/corrupt, background largely white with black cutouts; no invented texture/shader restoration. Log4 whole-fileGitblobSHA1 verified44ffee41b687d01411e6c2da63ab5e40053b3bb8. Latest native remains pending; if only waiting>10minutes remains, stop and give this run. Do not duplicate/cancel; first inspect step20 source-layout and step36 real Unity graph/diagnostic inventory, then first actual failure or APK gates. No user dependency/license/FMОD upload is needed.


## 2026-11-01 continuation: confirmed shader contract loss and complete-payload recovery
Owner reports persistent image glitches and world creation stalls/other loggers terminating; authorizes required Git LFS analysis within approximately10GiB. Only feature/android-native-port writable. Refreshed HEAD3e44546d; native41300265252 COMPLETED SUCCESS, published, source81bab94c. Cheap existing-log run41310589604 SUCCESS at423fca22 (no Unity/LFS rebuild).
Actual native contract:140exported shaders; every shader1sourcePass. Water Spectrum/Foam,VolumetricLight,BilateralBlur,Bloom all1pass. No .compute source files (compiled ComputeShader .assets must be distinguished). Vendor FMOD runtime graph15platforms/default/Android linked passed.2InputActionAssets142bindings include3touchscreen/14mouse/46keyboard/49gamepad; this does NOT prove functional UI or touch gameplay. APK1323195499bytes,sha2561bf8fba346348c516bdb7767ead444ceba06de0e600d0189e313461ba558b57b;40scenes64771links,0trackedmesh/CSharp diagnostics;10BuildReport errors remain. Default AssetRipper dummy shader export and incomplete original streamed textures are now primary restoration investigations, not a magic GPU support switch.
New CL trees:img130a4a84,logfoxe5e21da4,sandboxa58852f7. Downloaded/hash-verified7unique newer sessionJSONL files3671942bytes and3uniqueLogFox files117886435bytes (file1==file2SHA,also overlapping time ranges). Logs identify actual Adreno(TM)730,Vulkan1.1.0[512.615.95],computeTrue,shaderlevel50,8ARM64cores,11159MiBdeviceRAM. All7newer sessions have0RuntimeManager.Initialize errors (not proof audible sound). All show PartyWin32 DllNotFound throughPlayFabMultiplayerManager.InitializeImpl. Last4world/loadattempts reachMainScene and manyAdditiveLandmarkscenes;Unityreserved~1.65–1.71GiB,allocated~1.3–1.51GiB. OwnRSSfalls whileallocationstayshigh;cannotinferPSS or physicalfreememoryfromthat. LogFox showsmultipleLMKDbackgroundkills(memorypressure);noverifiedRaftfatalstack/LMKDkillofRaftinretrievedsamples. Thus reportspressure/stall,notinventedGPUcrashcause. Uploaded original .rgd loadboundary returnedwithoutescapingexception;notafullsave/worldacceptance.
New screenshot15-38-13 actuallyviewed: stretchedUI,largefontatlas-lookingquads,flatgraybackground and blackcutouts. Width1440height3200 despite orientationLandscape in logs is an unresolvedresolution/orientationoverride;priorPlayerSettingsaloneisnotdeviceacceptance.
Implemented owner-authorized wholegraphicsLFS hydration planner: onlytrackedresources/sharedassets/scene.resS payloads,10GiBcap,GitpointerSHA256+sizeverification,neverWindowsnativeexecution or bank/executablefetch. Dedicated45minfull-graphics-recovery workflow restores full payloads, validates EVERYTexture2D external extent, then realcanonical151provider AssetRipperexport andshadercontractcounts;noUnity/APK/rawsourceorassetpublication.35GiBdiskgate,4fixtureextents+pointer/allowlistbehaviors tested via2unitcases. This isolates source-data-loss fromshader-recoverylimitations beforeanotherAPKcycle.
Improved nextcandidate diagnostics: group identicalWarnings too (cursorformatwarningrepeats everyframe);AndroidApplicationExitInfo last4selfprocessdeaths reason/status/time/RSS/PSS,5sPSS/smaps_rollup+available/total/threshold/lowMemory,UnitylowMemoryflush. UnsupportedAndroidcounters explicitunavailable;skipstartup/resumefirstframe in liveFPSstats. ActualAndroidmacrocompilationpending;noJNIexecutionunder.NETclaim.
DXVK translatesD3D8–11toVulkan underWine;VKD3D-ProtonimplementsD3D12;FEXemulatesx86onARM64Linux. CurrentAPKisalreadyARM64UnityVulkan,soaddingtheseDLLsdoesnotrepairlostUnityshaderpasses/atlases. TheycouldsupportaseparateWindowscompatibilityproject,notanativeAPKdropin. Officialreferences:github.com/doitsujin/dxvk,github.com/HansKristian-Work/vkd3d-proton,github.com/FEX-Emu/FEX. OfficialAssetRipperDummyShaderTextExporter andPremiumFeaturesdocumentshader/computeexportlimits. MoonlitGamesUltimateWaterofficialrepoisissue/docs-only;noactualshadersourceacquired. Continueexact-source/bank/datarecoveryandprivateanalysis,neverfakepasses/clampkernelsto0.
