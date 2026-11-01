# Raft Android — complete Work session transfer, 2026-11-01

> **LATEST VERIFIED:** FMOD native41259800620 completed SUCCESS including APK/FM​​OD/DEX/original-data byte gates. Detailed bounded log analysis pending; see final section. No phone test.

> **NEWER VERIFIED CHECKPOINT:** native 41257065669 FAILED at the original FMOD resource-platform lookup; exact-path fix 9e5f3635 is running in native 41259800620. Read the newest dated section at the end; earlier IN PROGRESS status is historical.

هذا هو تسليم الجلسة الأحدث. اقرأه كاملاً ثم التاريخ الكامل حتى آخر قسم، وراجع HEAD وActions قبل أي تجربة. لا تطلب ملف FMOD أو إعداد ترخيص Unity من المستخدم مجدداً: ملف FMOD وصل والتحقق الخاص في Actions نجح، والترخيص يعمل.

## 1. Authority and reading order

Repository: https://github.com/alwansan/raf . The ONLY writable working branch is `feature/android-native-port`. Do not modify, merge into, delete or reset `main`, `zip` or `Unity-Editor`.

Read this entire transfer, then the entire [historical handoff](WORK_SESSION_HANDOFF.md), including its final continuation sections. Its old headers describe superseded states. Read [AGENTS.md](../AGENTS.md), [VERIFIED_FINDINGS.md](VERIFIED_FINDINGS.md), [MESH_RECOVERY_FINDINGS.md](MESH_RECOVERY_FINDINGS.md), dependency/reconstruction reports and the actual workflows/scripts/tests named below. Refresh branch HEAD and latest Actions before acting; another session may have advanced the branch.

This file consolidates the latest state; it does not discard the detailed earlier record. Old requests to reinstall Unity licensing, supply FMOD, fix `--min-added 500`, or wait specifically on Recover CSharp helper types are obsolete.

## 2. Owner's standing instructions

- No PC. Use GitHub Actions and Unity **2021.3.45f2**. Existing environment **UNITY_LICENSE** works; do not ask to recreate it or expose its credentials.
- Test phone: **POCO F5 Pro**. Prioritize complete offline Singleplayer: real original gameplay, touch input, original `.rgd` saves, audible sound and practical performance. Then replace Steam multiplayer with phone hosting/joining over LAN or another suitable Android transport.
- Owner authorizes technical decisions, public dependency installation, experiments, small tests and commits on the designated branch without repeated permission questions.
- Preserve original `.meta` bytes/GUIDs, scenes, script identities, serialized fields and systems. Do not remove components, invent game data, replace gameplay with dummy scenes, or suppress errors to force success.
- Minimize LFS. Verify byte sizes/hashes, start with small tests, and never rebuild or fetch multi-GB LFS merely to read logs. The original six-part archive was supplied already; do not ask for it again or assume old extracted temporary files still exist.
- Do not publish raw original assets, decompiled game source, the full FMOD SDK, private keys or license secrets. The owner wants an actual `.apk` directly in Releases eventually, rather than a ZIP, when a meaningful device test candidate is ready. No such readiness or published artifact is established today. Reconcile the owner's explicit eventual APK request with older repository instructions when that milestone actually arrives; do not release now merely because BuildPipeline succeeded.
- Update WORK_SESSION_HANDOFF.md after results/fixes. If ONLY waiting on a known >10-minute job remains, give its exact link/status and stop waiting; owner will report completion. Do useful independent work while it exists, without inventing unnecessary tasks to fill time.
- The earlier exception asking to follow Recover CSharp helper types through completion was fulfilled; normal wait preference is restored.
- Splitting workflows is permitted when it isolates useful tests/dependencies and actually saves work. Existing small workflows do this. Do not split scene semantics blindly or expose raw reconstructed projects as public artifacts.

## 3. Exact live entry point

The pending experiment is [native41257065669](https://github.com/alwansan/raf/actions/runs/41257065669).

| Item | Value |
| --- | --- |
| Experiment source | `705dda0ae6e6928172bdae495be990612f29d5ab` |
| Reconstruction job | `124702391661` |
| License preflight | `124702370849`, SUCCESS |
| Live state at transfer refresh | IN PROGRESS — step13: Restore scene-owned ScriptableObjects before Unity can import invalid cross-scene assets |
| Runner compatibility guard | `41257065663`, SUCCESS |
| Offline prototype checks | `41257065654`, SUCCESS; prototype is still not gameplay integration |
| Last HEAD before documentation transfer | `d5d622ec3678d84e6e93930b89fb1c6170cf07cb` |

This ONE deliberate experiment stages verified FMOD ARM64 runtime/Java bridge, the tested Android startup adapter, original StreamingAssets/banks and strict original-settings/importer/APK gates. Its actual FMOD/Unity/APK result is **not yet known**. Do not attribute the previous APK's 10 errors, size or checksum to this run.

At initial transfer inspection, steps through original export completed, step13 scene-owned restoration was running, and FMOD staging steps29–30 plus real Unity step34 were pending. The table above records the final refresh. Always fetch current jobs first; do not restart a completed or still-running experiment automatically.

## 4. Last completed native baseline — verified, not playable proof

[Native41250543603](https://github.com/alwansan/raf/actions/runs/41250543603), source `f82b9427e2608d250fef52f3f4912671607e3686`, job `124682991227`, completed SUCCESS. [Log-only comparison41256473225](https://github.com/alwansan/raf/actions/runs/41256473225), job `124700595547`, verified its metrics against float-property baseline41243408540 without rebuilding.

| Evidence | Actual result |
| --- | --- |
| BuildPipeline | Succeeded; ARM64 IL2CPP; 40 enabled original scenes |
| BuildReport summary.totalErrors | **663 → 10** |
| Edit-mode Destroy diagnostic hash `00e21d8b1e9fa243` | **654 → 1** |
| Unsupported compute-group-name hash `e2444b0b258c8bec` | 9 remain |
| BuildReport message aggregation | 46 occurrences: other10, shader9, standalone_target_assertion27 |
| Actual APK size | **1165384169 bytes** |
| Actual APK SHA256 | `92f85801354200540df5908957b9329c6d0d03d1c3e97a29bd6c509e98934cb8` |
| Payload | 3 validated AArch64 libraries; 11 Unity Data files |
| Android FMOD native present | **false** — this is the pre-FMOD experiment |
| Scene script GUID links | 64771/64771 |
| SDK identities/references | 149 types; 9795/9795 rewritten; 0 required unresolved; original script metas unchanged |
| Font materials | 13/13 resolved |
| Mesh descriptors | 4708: 4707 finite + 1 genuinely original empty |
| Recovered external Mesh buffers | 2464; 3 complete scene streams |
| Tracked CSharp/Mesh/nonfinite errors | 0 |
| Float property recovery | 3 original tables, 3 caches, 3 actual SDK getter calls; original values/metas/Float32 bytes preserved; 0 original textures removed |
| Retained downloadable APK | None |
| Install/audio/gameplay/touch/save testing on phone | Not performed |

BuildReport message counts are not the same accounting as summary.totalErrors. Two original water OnValidate NullReferences remain: `UltimateWater.UnderwaterIME.OnValidate` and `UltimateWater.WaterDropsIME.OnValidate`. The current code does not hide them.

The 9 compute imports concern RenderTextureToBuffer, Blurs, EyeHistogram, Gauss, Ripples Setup/Simulation/Transfer, DX11 FFT and ConvertDepthToArray. The message is `unsupported platform: couldn't get group name for target %i`; corresponding shaders were not imported correctly. Rendering/runtime implications remain unresolved. Do not delete them or declare that graphics work merely because the APK built.

## 5. Important completed fixes — do not regress them

### Original Mono fields and CSharp helper coverage

The original provider/AssetRipper import correction preserves PlayFab assembly identity and avoids Unknown fallbacks. Bodies of 788 CSharp files were restored without manufacturing `.meta` files. The newer coverage gate compares **2393 original sources** to ILSpy CSharp9 text; total original decompiled sources are2394. Recovering empty source bodies and supplementing helper types is completed work. The old `--min-added 500` and Timeline/hyphen template classification issues are not current blockers.

Use ILSpy11.2.0.10050 with **CSharp9_0**, not default Latest. Preserve namespace conversion, SDK template isolation, managed closure and original-source coverage checks. Do not stage a second competing SDK implementation just to quiet the compiler.

### Scene-owned ScriptableObjects and threaded reader failure

Native41212679068 expired at65minutes and extended41219464019 also timed out. Actual root diagnostic was repeated `Do not use ReadObjectThreaded on scene objects!`, approximately292168 occurrences/1.136GB log, rather than simply an insufficient timeout.

`scripts/reembed_scene_bound_assets.py` and13 tests restore uniquely scene-owned class114 assets to their owning scenes. Real isolated [probe41233952996](https://github.com/alwansan/raf/actions/runs/41233952996) passed:129 objects into3 scenes,264 pointer rewrites,1203064 logical YAML objects before=after, installed fingerprints verified, original metas preserved/backed up. Resources/editor/binary/string consumers and ownership ambiguities are rejected. Do not externalize these objects again.

Real native41235457822 succeeded after that correction; the threaded-read loop disappeared. Increasing the timeout alone was not the solution. Current main job retains a150-minute cap as a bound, not an excuse to wait forever.

### Full original Mesh recovery

Keep the verified range manifest, strict HTTP range/fingerprint checks, restored stream identities and finite-position audit. A completed latest baseline used352 remote chunks/682806164 remote range bytes,695019600 verified range bytes with provider reuse; no whole-object fallback. Three selected LFS assets are111533516,115978112 and110149324bytes, not a default full6.47GiB checkout.

2464 original Mesh streams were inlined;1206692 other serialized objects were verified unchanged;3 full scene streams restored. This is narrow data fidelity evidence, not proof of all game visuals/collisions. One empty Mesh is original and must not be filled with invented vertices.

### MicroSplat derived property textures

33 Texture2D.SetPixels exceptions came from unsupported exported cached PropTex formats. Authoritative original Color[] values and maxTextures survive. `android-port/Recovery/PropertyTextures/PropertyTextureCore.cs` and `MicroSplatPropertyTextureRecovery.cs` regenerate derived RGBAFloat cache subassets, preserve HDR/negative/fractional Float32 values, back up original asset/meta, save/reimport/reload, compare all other source fields/metas, and call the actual original SDK GetTexture. Original exported textures are retained.

13 pure tests passed in41243084386; real Unity native41243408540 verified3 tables/caches/getter calls and eliminated all33 exceptions. BuildReport errors696→663. Do not clamp data to0–1 or replace original arrays/defaults. Its APK1165386966bytes is an older comparator, not the latest baseline.

### Narrow Editor Mesh collector lifetime guard

Private source inspection plus no-LFS scene metadata found653 original `MeshCombineStudio.GarbageCollectMesh` components,9 MeshCombiner and1 WaterCamera.40 scenes have64772 MonoBehaviours:64771 non-null scripts resolve and1 original script pointer is null. Custom Mesh field schemas were unavailable; counts alone did not prove persistent ownership.

`scripts/adapt_editor_mesh_cleanup.py` pins the normalized original collector source SHA256 `fe9a12ef6ab19b988b571793111c1a37bbd0986188bc2ec2a0cb2afd57bc9680`. It inserts ONLY an Editor conditional: outside Play Mode protect persistent Mesh assets; immediately clean nonpersistent meshes only when original SkipGC permits; return before inappropriate delayed editor destruction. Original player/runtime source remains character-exact after removing the guard; original.meta is required and byte-preserved; backup lives outside imported project. Unknown revisions/duplicate types/backup overwrite fail.

5 safety tests and24 original/adapted policy cases passed in41250446550; actual native41250543603 then eliminated exactly653 of654 Destroy diagnostics. Do not globally replace Destroy with DestroyImmediate. The remaining one is not yet attributed or fixed.

## 6. FMOD acquisition is solved — do not ask the owner again

Owner supplied `fmodstudio20215.unitypackage`,114556928bytes, package SHA256:

`b157d6e298bed0eb54b9c07246cb4de51ce9de10f850d7dc0c494ccaee664c48`.

The source wrapper's constant131605=`0x00020215` means **2.02.15**, not2.02.21. FMOD uses BCD patch numbering. Earlier decimal interpretation was explicitly corrected. Official fmod-for-unity source excludes native binaries; forking it alone cannot provide them. No new login/download is currently required.

| Audited release file | Bytes | SHA256 |
| --- | --- | --- |
| libfmod.so | 1158480 | cf592e9519862feb3c6d65a0231536f22e08ae3ee27a757fb3fb80342881b75e |
| libfmodstudio.so | 1112104 | 0576c81ad5b3f6e947efe2a52896e0294acd6da81e2501d16d737a372c210b1d |
| libresonanceaudio.so | 831152 | 98a4152eabdb47e265f1cac9884aa5b7ebbe1f4b7dc42ebbd8c151fa669bcb23 |
| fmod.jar | 10053 | 94db450fce32ed830dc8c9d3f1f79667c7b77af5d745f74725113c62752501fe |

Actual package audit verified exact header version; ELF64/DYN AArch64 identity; real defined dynamic core/Studio API exports and reachable dependency closure; real `org/fmod/FMOD.class`. Standard Android system dependencies include libc, libdl, liblog, libm and libstdc++. These metadata checks are not native getVersion/device-audio execution.

Only3 release libraries, Java bridge, vendor LICENSE.TXT and their5 exact original metas are needed now:10 files/3121241 plaintext bytes. Full SDK, debug libraries, demo content and competing CSharp sources are not staged or published. Original native importer metas select Android ARM64 and disable Editor/Any. Preserve vendor notices and eventual in-game attribution.

### Durable private transfer

- Public repository contains only authenticated ciphertext: `android-port/Dependencies/fmod-2.02.15-android-arm64.aesgcm` (1240819bytes).
- Exact file hashes/size/provenance are in `config/fmod-android-runtime.json`.
- Random32-byte AES256-GCM key is already provisioned as **FMOD_ANDROID_RUNTIME_KEY** in the EXISTING **UNITY_LICENSE** environment. This is not an FMOD login or a Unity license. Never print, commit, read back or put the key beside the ciphertext.
- Owner completed secure GitHub sign-in; the secret was added and verified through UI. Original3 Unity secrets/protection rules remained untouched. Routine code/log operations should use the GitHub connector; there is no reason to repeat browser login now.
- `scripts/stage_fmod_android_runtime.py` authenticates key/cipher/AAD/version/allowlisted file scope/hashes before writes, rejects links/traversal/duplicates/conflicting assets/metas, and never imports CSharp SDK source.
- [Actual preflight41251245329](https://github.com/alwansan/raf/actions/runs/41251245329), retry job124687318069, SUCCESS: all10 real files staged with exact hashes/ARM64 identity,0 original metas overwritten,0 competing sources;6 staging+12 package fixture tests passed. Initial attempt job124685026306 skipped actual stage before the secret existed; that older skipped state is superseded.
- `docs/FMOD_ANDROID_INTEGRATION.md` carries acquisition/provenance notes. It may describe integration as unverified because current real Unity experiment is still pending.

### Original managed bootstrap gap and authored adapter

Original FMODUnity.dll SHA256 `d956f100e6afd41cddb7b3b8a43b4f84ee67b25bca716a55592298fbc7c17bcb`. Private inspection proved RuntimeManager, RuntimeUtils, Settings, Platform, PlatformDefault, PlatformWindows AND PlatformAndroid exist. Do not say the Android platform class is absent.

The Windows-compiled RuntimeManager enforces native library order then initializes FMOD, but its Java `org.fmod.FMOD.init(UnityPlayer.currentActivity)` block was compiled out. Official same-version Android SDK source contains that block. Original PlatformAndroid supplies `file:///android_asset` when AndroidUseOBB=false; Windows RuntimeManager lacks the OBB loadFromWeb path.

New own code:

- `android-port/Runtime/Audio/FmodAndroidStartup.cs`: ordered/idempotent success gate; explicit library/Java/version failures; exact expected version0x00020215.
- `android-port/Runtime/Audio/AndroidFmodBootstrap.cs`: Android-only, non-Editor AfterAssembliesLoaded initialization; original RuntimeUtils library order, currentActivity/Java init, temporary core-System create/getVersion/release with checked results. Does not start substitute game logic or create replacement FMOD settings.
- `android-port/Tests/Audio/Audio.csproj` and Program.cs: actual Android code compiled against original FMODUnity/UnityEngine.CoreModule/AndroidJNIModule;14 ordering/idempotence/error/wrong-version cases.
- [Startup workflow41256626829](https://github.com/alwansan/raf/actions/runs/41256626829), job124701056528, SUCCESS. Tests do not call Unity JNI/native libraries under .NET; actual Android startup log `RAFT_FMOD_ANDROID_BOOTSTRAP` is still unobserved.

## 7. Original StreamingAssets and current experiment gates

Five original banks total123817498bytes:

| Original bank | Bytes | Storage |
| --- | --- | --- |
| MasterBank.bank | 101600960 | LFS, exact SHA256 below |
| MasterBank.strings.bank | 29530 | regular Git |
| VO_logs_english.bank | 11455008 | regular Git |
| VO_npc_english.bank | 8180896 | regular Git |
| VO_olof_english.bank | 2551104 | regular Git |

MasterBank SHA256 `10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339`. Other original StreamingAssets include Data.rgd (2941bytes), haptic WAVs and UnityServicesProjectConfiguration.json (1820bytes). Do not confuse StreamingAssets/Data.rgd with replacing the player's original save schema.

Earlier AssetRipper export explicitly ignored StreamingAssets; no complete sound claim was justified. Current experiment fetches ONLY the one additional101600960-byte bank LFS object and stages all tracked original StreamingAssets with Git/blob/LFS/hash checks.

`scripts/stage_original_streaming_assets.py` validates complete tracked source identities and all destinations BEFORE writing, refuses unhydrated/wrong LFS pointers or conflicting original files/metas, requires5 banks+Data.rgd, and verifies copied bytes.6 local Git-backed tests passed. It does not fabricate assets or alter bank codecs/data. Exact staging report is temporary `original-streaming-assets.json`; no raw data upload.

`android-port/Editor/FmodAndroidValidation.cs` is a new strict real-Unity gate, not yet verified in the running experiment:

- Uses Resources.Load rather than Settings.Instance, which can manufacture default settings.
- Checks original resource Platform identifiers for ambiguity and requires one Android platform, one default platform and the original FMODStudioSettings object.
- Reads serialized private fields `identifier` and `CurrentVersion` via SerializedObject; version must be0x00020215. Public original fields/properties are AndroidUseOBB, ImportType and TargetSubFolder.
- Requires OBB=false, StreamingAssets import and empty bank subfolder for the currently implemented original-root bank path. Other layouts must be investigated, not silently rewritten.
- Checks actual vendor PluginImporter Android ARM64 compatibility and Editor disabled for3 native libraries.
- Original vendor Settings.OnEnable can delete duplicate platform assets; the new code checks ambiguity before explicitly requesting settings. Actual Unity lifecycle/resource behavior still needs this experiment; do not claim an untested gate passed.
- Main Build requires all5 original banks. No replacement settings/serialized values/components are generated to make it pass.

Current main workflow stages runtime+Java helper before Unity; bank staging is intentional-native-only. Current Unity entry calls SDK rebind, property texture recovery and FMOD original-settings validation, then bank existence validation before BuildPlayer.

Actual APK follow-up additionally requires3 FMOD ARM64 libraries with defined API exports, Java descriptor in real DEX and exact size/SHA256 of EVERY copied original StreamingAssets file. It reports compressedBankFiles for a performance follow-up. A descriptor's presence does not prove initialization; metadata does not prove bank codec compatibility, DSP behavior or audible output. If banks are ZIP-compressed, investigate memory/startup impact and packaging properly rather than ignore it.

## 8. Current workflows, triggers and small checks

Primary workflow: `.github/workflows/raft-unity-editor-android-import.yml`. Ubuntu24.04, Unity2021.3.45f2, environmentUNITY_LICENSE, bounded150-minute reconstruction job. Ordinary watched pushes use SDK validation; ONE intentional commit containing `[raft-native-build]` requests native Build. workflow_dispatch supports explicit sdk-bindings/native. Concurrency cancels older same-branch runs: do not touch primary watched inputs casually while an important experiment is running.

Useful isolated workflows:

- `raft-native-log-summary.yml`: existing completed logs, no Unity/LFS; current comparison BEFORE124661841900, AFTER124682991227. For current FMOD result change AFTER to124702391661 and appropriate BEFORE baseline deliberately, without requesting native.
- `raft-runtime-source-inspection.yml`: private original source/diagnostics inspection, encrypted before any artifact/log publication; no LFS. See privacy notes below.
- `raft-property-texture-tests.yml`:13 pure CSharp9 checks, no Unity result implied.
- `raft-editor-cleanup-probe.yml`: original scene component identities, no LFS; explicit null-script accounting and unavailable schema counts.
- `raft-editor-mesh-policy.yml`: original/adapted cleanup policy CSharp9 cases; no actual Unity asset destruction test implied.
- `raft-fmod-package-tests.yml`:12 read-only package fixtures.
- `raft-fmod-runtime-preflight.yml`:6 authenticated staging fixtures plus actual secret-backed runtime metadata stage.
- `raft-fmod-startup-tests.yml`:14 startup cases and actual original-provider compilation.
- Runner compatibility guard and offline prototype workflows can pass independently; they are not proof of playable integration.

Selected local tests in a full branch checkout:

```bash
python3 -m unittest discover -s tests -p test_reembed_scene_bound_assets.py -v
python3 -m unittest discover -s tests -p test_adapt_editor_mesh_cleanup.py -v
python3 -m unittest discover -s tests -p test_audit_fmod_unity_package.py -v
python3 -m unittest discover -s tests -p test_stage_fmod_android_runtime.py -v
python3 -m unittest discover -s tests -p test_stage_original_streaming_assets.py -v
```

Cryptography50.0.2 is the pinned authenticated staging dependency, UnityPy1.25.4 and dnfile0.18.0 are existing pinned readers, ILSpy11.2.0.10050 uses .NET10/CSharp9; standalone tests use .NET8/CSharp9. Verify only what changes; do not repeat every already-passing test after documentation edits.

## 9. Private inspection and scratch continuity

Public original Assembly-CSharp identity is SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Source is inspected privately, never committed/logged raw.

Existing encrypted inspection workflow has a public RSA recipient certificate; private3072-bit key was local only. Packets are zipped, SHA256-manifested and AES256 CMS-encrypted before public Actions artifact/base64 transport,1-day retention. Only encrypted content is exposed. Original source callbacks/snippets must not be copied into public fixtures or documentation.

If this scratch workspace survives, it is `/workspace/scratch/8111aa7069a6`:

- Uploaded package: `upload/fmodstudio20215.unitypackage`.
- Intermediate selected runtime/cipher/key/manifest: `private-fmod-runtime/`; key is private and must not be printed.
- Private inspection recipient: `private-runtime-inspection/key.pem`; decrypted source directories source through source7 are temporary.
- Latest verified packet source7 contains93 files; private FMOD inventory/source came from run41252106516/job124687580349.
- Source6 contains66 lifecycle candidates. The original collector is in its hashed lifecycle filename; do not publish it.
- Working directory is a scratch staging area, not necessarily a complete git clone. Many files were fetched/committed through GitHub APIs. Use the repository branch as authority, not whatever happens to be on disk.

Scratch may disappear. Do not depend on it. Runtime ciphertext+manifest+existing CI environment secret are durable; CI can stage without recovering the secret locally. Original FMOD Library identity is `libfile_e32b7f9806a481918d40dbd10690788b` if an unattached future session actually needs the complete package; use appropriate Library routing, not another owner upload request. If a new message provides a local attachment, use that directly instead.

If the private inspection key is gone/expired, generate a NEW local recipient key/certificate, commit only the public certificate on the allowed branch and rerun the cheap no-LFS inspection. Never recover secrets by logging them, derive encryption keys from public hashes or place a decryption key next to ciphertext. Don't request Unity account/license setup again. Do not execute original Windows Raft.exe/OnlineFix64.dll.

GitHub connector supports code/tree/ref operations, jobs/log reads and job reruns. Large direct job log fetches may return Transport closed; this is not a game build error. Use the existing bounded log-only workflow, which streams/parses inside Actions. Do not download raw logs to the public repo or rebuild the game for diagnostics. Mutations used expected_sha leases; refresh HEAD before committing and never force-push over another session's work.

## 10. Actual Android gameplay work still outstanding

There is no proven complete Singleplayer yet. Offline startup, original Steam/Party removal/replacement, coherent Android player identity, original .rgd save paths, touch controls, pause/audio lifecycle, graphics/compute adaptation, memory/thermal/performance and phone testing remain genuine work. Steam networking is not required; preserve local RPC/gameplay semantics while changing transport later.

Private original-source facts already verified:

- SteamManager.Awake initializes native Steam and can quit on missing library. Do not fake Steam authentication or mark Steam initialized without a real backend. Local mode should keep it false and adapt callers deliberately.
- Raft_Network has default localSteamID1, native Party/Steam callbacks and polling. HostGame/LeaveGame and local ParseLocalMessage dispatch must remain coherent; do not disable all network/RPC processing just to achieve offline startup.
- SaveAndLoad has4 Steam user-ID uses; RGD_User and RGD_Users have1 each. Seven distinct Windows save path literal shapes need careful adaptation.
- Preserve original serialization keys and structure including SteamID, WorldGuid, Player, Users; never replace original.rgd saves with the unintegrated prototype's world.sav.
- `android-port/Runtime/Platform` prototype tests exist and pass but do not establish integration into original gameplay or actual saves.
- JNI/runtime getVersion, Java bridge init, source settings resource correctness, original bank/DSP loading and actual audible output remain separate evidence layers even when the present build gates eventually pass.

Do not report a successful Unity build as proof that an APK launches or the game is complete. No current APK has been retained for download or tested on POCO F5 Pro.

## 11. Next session's exact first actions

1. Refresh HEAD and native41257065669/job124702391661. Do not rerun while active. If only waiting >10minutes remains, report link/status and stop.
2. If failed, read the FIRST actual failed step. Possibilities include authenticated stage, original tracked bank identities, real CSharp/Editor API compile, original FMOD resource/settings layout/importers or real APK byte checks. These are possibilities, not established failures. Fix the observed failure with a small faithful test; never relax the gate or fabricate source data to pass it.
3. If succeeded, run bounded completed-log comparison against native41250543603; inspect original setting/importer/staging markers, all prior Mesh/font/scene/source/float guards, residual errors, actual FMOD APK files/exports/Java descriptor, original bank/data hashes and compressed-bank count. A successful Actions status alone is insufficient.
4. Preserve original providers and fix remaining concrete platform/lifecycle issues. Resolve the final cleanup caller and9 compute imports without blanket removal. Proceed to actual offline/.rgd/touch/device requirements in a controlled order.
5. Update the historical handoff AND current transfer as appropriate after results. Keep document headers current so later sessions do not stop at an obsolete FMOD download request or old in-progress status.

## 12. Commit provenance for this continuation

| Commit | Purpose |
| --- | --- |
| 95514555efb78f9ff3015ad9c26b9506c7b53eb5 | Private lifecycle candidate inspection |
| ca334b00872a74739cac3d02db3225d539eaf579 | Original scene cleanup identity probe |
| e2be496f37fa68542398669cdc4a0f8a6f657ff1 | Explicit null script accounting / bank inventory |
| 97b0415662e19fd10debd69a696c1904c15d8482 | Original collector policy safety tests |
| f82b9427e2608d250fef52f3f4912671607e3686 | Successful real collector native experiment |
| 9024743972e32fec45fe0639fdc91c025720b7b8 | Supplied FMOD verified and sealed runtime prepared |
| 1b02570fc34ab52ecca69b314f29c36a5357b89a | Private key provisioning checkpoint |
| 336ebdd58d1ca7483c87d745366b579297b89e62 | Original FMOD platform bootstrap private inspection |
| a71a52a99721cc50f1fc1ae5a2caad5371718a7d | Managed Java bootstrap gap recorded |
| 3920a1e1d0051c478346acd83339dba360bed43b | Bounded collector log comparison |
| eac5834ad42bdb371bfb22c98802493fd1cd8e70 | Android Java bootstrap and14-case original-provider compile |
| 705dda0ae6e6928172bdae495be990612f29d5ab | Current FMOD native integration experiment |
| d5d622ec3678d84e6e93930b89fb1c6170cf07cb | Previous owner wait checkpoint |

This transfer itself is documentation-only. It must not trigger/cancel another heavy native experiment. Current build source remains705dda0..., even though branch HEAD will advance with these documents.

## 2026-11-01 — FMOD native failure diagnosed and exact resource-path fix launched

**Verified result, not an inference:** [native 41257065669](https://github.com/alwansan/raf/actions/runs/41257065669), source `705dda0ae6e6928172bdae495be990612f29d5ab`, reconstruction job `124702391661`, completed **FAILURE** at Unity Editor step 34 (2026-11-01 00:53 UTC). Steps 1–33 passed, including authenticated FMOD ARM64 runtime staging (10 files), original StreamingAssets staging, SDK and GUID structural validation, and Unity import; no CSharp compiler errors were seen in this job. No APK was produced, and post-build APK/FM​​OD audit steps 35–36 were skipped.

The **first fatal error** is `RAFT_FMOD_ORIGINAL_SETTINGS settingsPresent=True resourcePlatforms=0 androidPlatforms=0 defaultPlatforms=0 manufacturedSettings=0` followed by `BuildFailedException: Original FMOD settings/platform resource layout is incomplete; no defaults substituted.` Unity's import log actually shows original `Assets/Resources/FMODStudioSettingsPlatform.asset` and `FMODStudioSettingsPlatform_0.asset` through `_13.asset` (individual original GUIDs retained). The validator mistakenly called `Resources.LoadAll<FMODUnity.Platform>("FMODStudioSettings")`, which searches a resource path named for Settings rather than sibling `FMODStudioSettingsPlatform*.asset` files. This is a **validated path-selection bug**; whether the original assets deserialize to the correct platform subclasses still requires a real Unity rerun. The file-name-vs-internal-object-name warnings during import are not by themselves proof of invalid assets.

**Fix committed:** [9e5f3635a660f85bb492dee6c91bc57bc80aa730](https://github.com/alwansan/raf/commit/9e5f3635a660f85bb492dee6c91bc57bc80aa730). Editor validator now enumerates only exact original root `FMODStudioSettingsPlatform*.asset` files, checks each through both `AssetDatabase.LoadAssetAtPath<FMODUnity.Platform>` and `Resources.Load<FMODUnity.Platform>` by filename, refuses unresolved/ambiguous resources, and still validates identifiers before loading original vendor Settings. No original asset, .meta, GUID, settings default or bank was modified/fabricated. Added three **static policy regression tests** (`tests/test_fmod_resource_path_policy.py`) to the pre-LFS CI gate; they do not substitute for Unity import.

**Next intentional native experiment:** [41259800620](https://github.com/alwansan/raf/actions/runs/41259800620), source `9e5f3635a660f85bb492dee6c91bc57bc80aa730`, **IN PROGRESS at last refresh**. Do **not** launch an equivalent duplicate. At next check read the new run's jobs/steps, the test result, and the first fatal Unity diagnostic if any. If platform assets fail typed lookup, inspect original imported script GUID/provider mapping and serialized platform identifiers without synthesizing replacements. If gate passes, verify actual ARM64 APK, original bank hashes, FMOD ELF/Java descriptor and the remaining graphics/runtime issues. This docs-only checkpoint does not request a build. No phone test or public APK release; no user intervention required for this gate.

## 2026-11-01 05:09 Baghdad — independent offline identity concurrency regression PASSED

- Live native FMOD exact-resource fix experiment [41259800620](https://github.com/alwansan/raf/actions/runs/41259800620), source `9e5f3635a660f85bb492dee6c91bc57bc80aa730`, reconstruction job `124710556393`, remains **IN PROGRESS** in Unity step34 at this checkpoint. Steps1–33 passed, including 10 authenticated FMOD runtime files and original StreamingAssets. Do **not** launch a duplicate or treat preflight success as Android audio proof. Latest accessible partial job log ended in Unity asset import at 01:38 UTC, without `RAFT_FMOD_PLATFORM_RESOURCE_LOOKUP` or a final BuildReport yet; that partial log is not a failure determination. Prior prefab import produced 3 NullReference lines; their root cause/impact is not yet established.
- Independently strengthened the unintegrated offline-platform prototype's save-identity regression in [commit b4716c791a9c481b70e3097120ac69daaf14c455](https://github.com/alwansan/raf/commit/b4716c791a9c481b70e3097120ac69daaf14c455): 24 concurrent first-launch callers must converge on the same durable local profile ID, leave no temporary identity files, and retain that ID after restart. No original game script, scene, `.meta`, GUID, FMOD asset, or save schema was changed.
- Independent [platform test run 41263936272](https://github.com/alwansan/raf/actions/runs/41263936272), job `124722674985`, completed **SUCCESS**: netstandard2.1 platform library compiled, smoke tests **8 passed / 0 failed**, including the new concurrency regression. It did not trigger/cancel the active Unity native run; no new native build or LFS download was requested.
- Next: refresh the native run's final Unity result and first fatal error, if any. If successful, inspect actual ARM64 APK/FM​​OD/DEX/original-bank audits and residual graphics errors. Then prioritize integrating real offline Steam/RPC and original `.rgd` paths without substituting prototype `world.sav`. No phone test, public APK or user intervention is established.


## 2026-11-01 — FMOD corrected native completed; bounded evidence extraction

Native [41259800620](https://github.com/alwansan/raf/actions/runs/41259800620), source `9e5f3635a660f85bb492dee6c91bc57bc80aa730`, reconstruction `124710556393`, is verified COMPLETED SUCCESS. Unity step34 completed at02:26:21UTC; actual APK structural audit35 and FMOD/DEX/original-StreamingAssets-byte audit36 both passed. This establishes those configured gates passed, not phone startup/audio/gameplay. APK size/hash, actual settings/platform counts, compressed-bank count and remaining diagnostic totals await bounded log extraction; do not reuse pre-FMOD metrics. Direct connector log read returned Transport closed.

Extended existing aggregate parser to retain original FMOD resource/settings/configuration/importer markers and actual APK audio audit, preserving deviceAudioVerified=false and compression counts.12 local parser tests passed, including two new executed-versus-echoed FMOD evidence cases. Workflow YAML and embedded Python AST passed. Cheap log-only comparison now reads collector baseline124682991227 and completed FMOD124710556393; no Unity run, LFS transfer, game source publication or APK release requested. Next inspect this diagnostic result, then address the first established graphics/audio/runtime integration barrier. Original Steam/offline/.rgd/touch/device integration remains incomplete.


## 2026-11-01 — actual FMOD APK evidence PASSED, residual graphics/runtime inspection

[Bounded comparison41266582283](https://github.com/alwansan/raf/actions/runs/41266582283), job124730530756, inspected completed native41259800620 without Unity/LFS.12 geometry/FMOD parser tests,4 exception tests and1 ownership test passed. Actual native result: ARM64 IL2CPP,40scenes,10reportedErrors (unchanged), APK1323172270bytes SHA256`ff09a00b9f088dd5733c3309b2c6bb6c6cce5f21da8149316ba1d401cee6cd10`,6validated AArch64 libraries,11UnityData files,FMOD native=true.15/15original FMOD platforms load through exact filenames,1Android+1default,0manufactured settings; version131605/2.02.15,OBB=false,StreamingAssets,empty bank subfolder.3Android ARM64 importers disable Editor. Actual DEX Java descriptor/required native exports passed; ALL36original StreamingAssets files match exact size/SHA256; compressedBankFiles=0. This does not prove JNI/native-version execution, bank codec/DSP/audio or gameplay on phone. APK was not retained or released.

64771/64771 scene-script links,9795/9795 SDK rewrites,149resolved types,0required unresolved,original metas unchanged.13/13 font materials,4708Mesh (4707finite+1original empty),2464inlined original buffers,129scene-owned objects retained. No tracked Mesh/nonfinite/Quickhull/inaccessible collision/ReadObjectThreaded/CSharp regressions.3float tables/caches/real SDK getter calls still preserve original values/meta/rawFloat bytes. Residual diagnostic hashes unchanged:1edit-mode Destroy+9unsupported compute imports.2anchored NullReference origins:UltimateWater.UnderwaterIME.OnValidate andWaterDropsIME.OnValidate;3null-reference log lines are a different count.

Next cheap encrypted private inspection renews the expired-workspace recipient certificate and targets actual native job124710556393. Existing source scope extended only to original ComputeShader callers,ShaderUtility,UnderwaterIME,WaterDropsIME; existing startup/offline/save sources retained. Private3072-bit recipient key stays ONLY in current scratch private-inspection/key.pem; only public certificate and encrypted packet transport are committed. YAML/embedded Python/scope/job assertions passed. No heavy native rerun,extra LFS,source publication,license/key change or release requested. Inspect actual source and residual contexts before a narrow verified fix; do not silence graphics errors or invent missing shaders/settings. Original offline Steam/RPC,.rgd,touch/device work remains unfinished.


## 2026-11-01 — private runtime source verified; original save-path portability candidate

Encrypted inspection[41266677872](https://github.com/alwansan/raf/actions/runs/41266677872),job124730808745,SUCCESS. Locally decrypted107files and verified every manifest SHA256; original Assembly-CSharp hash unchanged. Water shader access uses ShaderUtility.Instance singleton; its resource-loading base still needs focused inspection, so no null guard or invented shader is applied.9actual compute import failures confirmed; final Destroy stack still lacks an attributable original caller. Preserve these as unresolved.

Independent observed Android blocker: original SaveAndLoad contains16Windows-backslash path literals across7distinct shapes. Added scripts/adapt_original_save_paths.py: pins full original normalized sourceSHA256`b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb`; wraps ONLY those exact original string expressions with char-based System.IO.Path.DirectorySeparatorChar replacement; original string values, all other source text,rgd schema,Steam/user fields and backup naming remain intact. Requires exact inventory, refuses unknown source/misplaced prior edits; idempotent; original.meta required/preserved and backup outside project for future application. Not integrated into main reconstruction yet: Steam identity and network/offline startup remain unfinished.

4local source-safety fixtures pass. Actual privately recovered original source adapted16expressions, exact non-path source roundtrip and idempotence passed. New no-LFS/no-Unity workflow validates pinned original source from fresh ILSpyCSharp9 and compiles/runs14CSharp9 Unix/Windows expression checks for7original path shapes under.NET10. This is an isolated source/path check, not original game compilation or real.rgd save/load. Await actual CI result before main integration; no heavy native run or public APK requested. Next combine deliberately with coherent offline identity adaptation, retaining original serialization and local RPC semantics.


### Verified save-path gate41266858910 PASSED

[Original save-path test41266858910](https://github.com/alwansan/raf/actions/runs/41266858910),job124731353292,source64f0e6738832b25e733b3b22103b9a9de5a22b3e,completed SUCCESS.4source-safety fixtures passed; fresh original CSharp9 source matched exact pin;16path expressions adapted with exact non-path source preservation/idempotence. Actual CSharp9/.NET10 expression program compiled and ran14Unix/Windows checks for7original literal shapes. No Unity/Android execution,original.rgd roundtrip,local identity integration or main pipeline application is implied. Runtime save-path candidate is ready to combine with coherent original offline identity/RPC integration; no duplicate native/LFS run requested.


## 2026-11-01 — Android local identity/startup candidate, isolated original-source gate

HEAD refreshed aa269509; no newer native build than verified FMOD41259800620. Extra encrypted source inspection41267230604 passed,115packet fingerprints verified privately. Prepared pinned12-source Android-only adaptation: durable local profile-derived positive nonzero ulong shared by Raft_Network and6original save-ID callsites; no cloud-auth success fabricated. Preserve original SteamManager singleton lifetime while skipping native initialization on Android; preserve settings/input initialization, scene host/load/local-player creation and local RPC dispatch, bypass only unavailable Steam/Party platform paths. Steam avatar/callback/character-default/build-ID boundaries explicitly handled; simulateMouseWithTouches enabled only for Android local mode. Original player .rgd fields/serialization keys/backups retained. Existing16path-expression portability applied before identity changes. Unknown source/callcount/meta/backup states fail;12sources validated before mutation.

5local adapter fixtures passed and all12actual original source pins/transforms passed privately. New cheap no-LFS/no-Unity integration workflow decompiles original CSharp9 privately, exercises actual adapted RPC/SendP2P bodies with throwing remote-transport doubles plus durable identity/corrupt-profile checks, and compiles full original adapted gameplay against original managed providers. This is not Unity/Android execution. Main reconstruction not modified until this gate completes. Source snippets/keys not published. Local achievement persistence, complete native-call coverage, touch gameplay, graphics/water/compute and real device behavior remain open. Owner reiterates eventual directAPK test release; no test APK readiness claimed by source fixtures.


### Original offline integration41267465031 PASSED; Android diagnostics compile follow-up

[41267465031](https://github.com/alwansan/raf/actions/runs/41267465031),job124733144821,source4da6d6172ef1228932b4b6614aaa4324f5e663a1,SUCCESS: all12pinned original sources adapted,9source/path safety fixtures passed, actual adapted RPC/SendP2P test bodies preserved local All delivery, excluded Other, delivered direct-local, and avoided throwing cloud transport; durable positive local ID/corrupt-profile preservation passed. Full adapted original gameplay compiled against original managed providers under.NET10/CSharp9. This is not Unity compilation/runtime.

Follow-up explicitly compiles UNITY_ANDROID+UNITY_5_3_OR_NEWER branches, including local-only AndroidTestDiagnostics: persistent test-report button, bounded last48errors/RAFTmarkers, copy-to-clipboard device/scene/report. No diagnostics upload or secrets are captured intentionally; user controls sharing. This supports an early startup testAPK once actual Unity/APK gates pass; complete movement/touch,local achievements,graphics/audio/save runtime remain unverified. Do not call it a playable release.


## 2026-11-01 — Android branch compile PASSED; one explicit early startup APK experiment

[Android-macro source test41267598711](https://github.com/alwansan/raf/actions/runs/41267598711),source9b6d81b35d2d7ffc19fa35e6881d135ce8d852e8,completed SUCCESS: full adapted original gameplay compiles under UNITY_ANDROID+UNITY_5_3_OR_NEWER against original managed providers,including diagnostic UI; RPC/identity checks passed. Still .NET10/CSharp9 diagnostics,not Unity/native execution. Refined source staging to select only Assembly-CSharp names (SDK Settings homonym retained),preserve all existing metas and allow genuinely unlinked helper sources without manufacturing metas.6local fixtures pass,including SDK homonym/absent-helper-meta preservation. Diagnostic capture registers before FMOD startup,UI object before scene load.

Integrate tested12-source local startup+6consistentID uses+16filesystem separators immediately after exact original source coverage,before other original-source adaptations. Stage ONLY LocalProfileStore,LocalPlayerIdentity,AndroidTestDiagnostics; prototype world.sav/session code not copied. Original game scenes,source bodies,all existing metas and serialization remain. Use dedicated test package com.alwansan.raft.androidtest; no oldAndroid app data migration. Buildcode follows workflow run number.

Owner explicitly reiterates directAPK testing. This ONE intentional [raft-native-build] [raft-device-test] experiment requests early startup-device candidate,not complete gameplay. Preserve all prior Mesh/font/source/SDK/float/FMOD/StreamingAssets/APK gates and add real apksigner verification. Only on explicit allowed-branch native/device-test opt-in and ALL reconstruction gates passing,retain ONLY APK for1day and publish directAPK prerelease in separate contents-write job; reconstruction remains contents-read. No source/project/raw assets/keys/license files uploaded. New tag includes runID+attempt,no overwrite. User-facing prerelease notes explicitly state incomplete touch,local achievements,graphics and device sound/save testing; local Test report button copies bounded device/error/audio markers.

Workflow YAML/all embedded Python and source-order/release-scope assertions passed locally;6adapter fixtures passed. No new Unity result,download link,installed app,working sound/.rgd roundtrip or playableSingleplayer is claimed until real evidence. Baseline remains FMOD41259800620 (10BuildReport errors+water OnValidate). Inspect first current failure; do not rerun heavy merely for logs. Owner waits if only >10minute native job remains.


### Current early-device APK run41267827866 — owner wait checkpoint

[Native41267827866](https://github.com/alwansan/raf/actions/runs/41267827866),source1158b473aa39f45c18b1ac08c65c19221a1f9064,reconstruction124734255994,is IN PROGRESS. Licensepreflight124734236148 SUCCESS; pre-LFS fixture/provider gates and3source-header transfers passed; active at step7verified stream restoration on latest refresh. Step20source adaptation,35Unity,36APKstructure,37FMOD/originalbytes,38signature,39APKretention and separate publish-early-test remain pending. Do not claim anAPK/download or launch a duplicate native job.

Companion actual Android-branch original source/RPC/identity test[41267827880](https://github.com/alwansan/raf/actions/runs/41267827880),job124734236159,completed SUCCESS at SAME1158b473 source:10path/source fixtures plus real adapted RPC/identity harness and full original managed compile. Existing prototype netstandard smoke also scheduled independently; it is not gameplay integration proof.

If this native completes ALL gates,the explicitly authorized prerelease job publishes directRaft-Android-EarlyTest.apk to https://github.com/alwansan/raf/releases with local diagnostic-report UI and explicit early-startup limitations. Tag android-early-test-RUN_ID-ATTEMPT is generated ONLY on successful delivery; no exact asset URL yet. If any stage fails,inspect FIRSTactual failure beforeanotherbuild; signature/delivery failure does not imply originalUnitybuild failed. Owner waits on this known>10minute job; stop polling when no independent useful work remains. This documentation-only checkpoint does not trigger/cancel it.


## 2026-11-01 06:10 Baghdad — bounded Android device diagnostics while early APK runs

- HEAD before this independent change: `f2eb8855394c216ce2af1bef5f7c85f599367c40`. Active native early-startup candidate remains [41267827866](https://github.com/alwansan/raf/actions/runs/41267827866), source `1158b473aa39f45c18b1ac08c65c19221a1f9064`, reconstruction job `124734255994`, **IN PROGRESS** at step10 pinned external Mesh buffer restoration on last refresh. Do NOT cancel/duplicate. The native run uses its original source snapshot, so the diagnostics change below will not be inside that already-running APK.
- Found a bounded but real test-overlay performance issue in authored `AndroidTestDiagnostics.OnGUI`: it rebuilt and laid out the entire report twice per IMGUI event, potentially up to 48 × 3000 log characters even when no log changed. No phone profiler trace is claimed.
- [a33a05dd](https://github.com/alwansan/raf/commit/a33a05dd06b8dd86e64e07def09545e7181a939d) now caches report by log revision and scene name, limits only the on-screen preview to 8000 characters, and retains the full captured report for the explicit Copy button. The 48-entry/3000-character-per-entry capture bounds, Android-only guard, local-only reporting and original game data are unchanged. Null message/stack inputs are handled defensively. No original scene, gameplay source, GUID, .meta, FMOD runtime, or .rgd schema changed.
- [acbc0003](https://github.com/alwansan/raf/commit/acbc0003fbc14cde916d9119352a6c3c23a1ed95) adds four cheap source-policy regressions; [1132271f](https://github.com/alwansan/raf/commit/1132271f6e53105e2aa14fbec1ef4a6dc9fe167c) adds them to the small platform CI; [bea3e2ab](https://github.com/alwansan/raf/commit/bea3e2ab1b2035c30d53625f02a8efef0fd7d049) triggers the existing original-source Android macro compilation on diagnostics changes. Older platform [41268027512](https://github.com/alwansan/raf/actions/runs/41268027512) SUCCESS, but predates the new source-policy test. New [41268045075](https://github.com/alwansan/raf/actions/runs/41268045075) and [41268050416](https://github.com/alwansan/raf/actions/runs/41268050416) were IN PROGRESS at last refresh; inspect final results before claiming they passed. These tests are not Android device performance measurements.
- Next: inspect final native41267827866 and independent CI results. If native succeeds all APK/signature gates, inspect whether the early prerelease job actually completed and whether distribution rights allow a public binary. Distinguish APK structural/signature success from real POCO F5 Pro installation, FMOD audio, original .rgd save/load, touch and gameplay. No APK link or phone success is established by this checkpoint.


## 2026-11-01 06:12 Baghdad — actual concurrent offline identity race found and fixed

- New independent [platform run41268045075](https://github.com/alwansan/raf/actions/runs/41268045075) FAILED specifically on the existing 24-way first-launch regression: `Concurrent launch generated multiple profile identities`. The four new Android diagnostics source-policy tests PASSED and netstandard2.1 compiled; the identity test exposed an intermittent, pre-existing creation race, not a diagnostic overlay regression. Prior single passing run was insufficient to establish concurrency safety.
- Root cause: the original `LocalProfileStore.GetOrCreateProfileId` used temp-file `File.Move(temp, profile.id)` after an existence check. On Unix, concurrent rename/check timing can replace an identity another caller has already returned. This violates stable original .rgd player-ID assumptions. No actual Android save/load test has yet been run.
- [d204704d](https://github.com/alwansan/raf/commit/d204704dac16ef94840e62511609c16265cd082a) replaces this with an atomic `FileMode.CreateNew` claim on the final profile path, exclusive writer share, and bounded retry only for in-progress sharing/IO errors; existing corrupt profiles are still never silently replaced. No temporary profile file is needed. [2610a25d](https://github.com/alwansan/raf/commit/2610a25d67275069aa7d5d12eea42751363d6c4b) strengthens the 24-way test to 8 separate fresh roots (192 concurrent callers total), with no leftover temp files and stable reopen checks.
- Verified [41268119274](https://github.com/alwansan/raf/actions/runs/41268119274) SUCCESS with first fixed-source run. More importantly [41268126838](https://github.com/alwansan/raf/actions/runs/41268126838), job124735112436, **SUCCESS**: four bounded-diagnostics policy tests, netstandard2.1 build (0 errors, one pre-existing unused-field warning), eight platform smoke tests including the strengthened 8×24 first-launch regression (8 passed,0 failed). Original Android-macro/source compile for the diagnostics change [41268050416](https://github.com/alwansan/raf/actions/runs/41268050416) SUCCESS. These checks do not prove Android runtime saves or phone gameplay.
- Active heavy [native41267827866](https://github.com/alwansan/raf/actions/runs/41267827866), source1158b473/job124734255994, remains **IN PROGRESS** at Mesh restoration on last refresh. It predates both fixes and must not be restarted/cancelled merely to incorporate them. If its APK passes, treat it as an early startup experiment using the original pre-fix profile creation and uncached diagnostic UI. After device findings, a new intentional native build can include these changes if justified.
- Next: inspect native final first failure/success and release job; do not assume an APK exists until all gates and rights conditions are satisfied. No original game source/scene/.meta/GUID or proprietary payload was committed in this fix.


## 2026-11-01 07:10 Baghdad — distribution-rights guard and native CI cancellation regression

- Live branch before changes: `9664cac1d431453b620406d17fd1167fbcb84ac8`. Native early startup [41267827866](https://github.com/alwansan/raf/actions/runs/41267827866), source `1158b473`, had passed stages 1–34 and was at stage 35 Unity Editor import; **no early APK or release existed**. The original workflow used `concurrency.cancel-in-progress: true`, and any edit to its YAML triggered a full reconstruct when Unity license was available, even without `[raft-native-build]`.
- A safety update to the same workflow [09820756](https://github.com/alwansan/raf/commit/09820756fc612fca3ae70fff13d88e393c8fcc89) **unintentionally triggered** new native [41271844647](https://github.com/alwansan/raf/actions/runs/41271844647), which cancelled the hour-long original [41267827866](https://github.com/alwansan/raf/actions/runs/41267827866) during Unity step35. This cancellation is a real CI design regression and was not an intentional request to replace the early APK candidate. No old APK was produced or retained. Do not misreport it as a Unity compiler failure.
- The safety change itself is necessary because this public repository contains third-party commercial game data: owner request for testing is not proof of redistribution rights. The retention step and public `publish-early-test` job now require explicit repository variable `RAFT_ANDROID_DISTRIBUTION_RIGHTS_CONFIRMED == 'true'`, with a second runtime check before `gh release create`. Default/unset is fail-closed. This applies to future workflow snapshots only; it cannot retroactively alter a running job. New [41271844647](https://github.com/alwansan/raf/actions/runs/41271844647) has no `[raft-device-test]` marker, so its snapshot does not request a public APK release.
- [c119a112](https://github.com/alwansan/raf/commit/c119a1120d94599d3ade39b213b745ddd9908e46) corrects the CI root cause: `cancel-in-progress: false` and `reconstruct` requires either explicit `workflow_dispatch build_mode=native` or a push commit containing `[raft-native-build]`. Ordinary workflow/tests/docs changes no longer launch a heavy reconstruction or cancel an active one. The next deliberately requested native build can include the offline identity race fix and bounded diagnostic overlay, which are not in the old early-startup source.
- [65dcb350](https://github.com/alwansan/raf/commit/65dcb350c3d328549a4b9976a1629196e19ee62f) and [02afa862](https://github.com/alwansan/raf/commit/02afa86206b2842fe169b0e4f28204af6028fec3) add five static regression checks for release rights, explicit native opt-in, and no-cancel concurrency. [3ef02067](https://github.com/alwansan/raf/commit/3ef02067262db094e0683bb453d8e66aa9daccd0) runs them in cheap platform CI when workflow policy changes. [41271860486](https://github.com/alwansan/raf/actions/runs/41271860486) passed the initial four tests; the expanded fifth check must be confirmed from its newer run.
- At this checkpoint the unintentionally started native [41271844647](https://github.com/alwansan/raf/actions/runs/41271844647), source `09820756`, was IN PROGRESS at selected LFS staging. It has no APK release opt-in. The later workflow-only [41271916751](https://github.com/alwansan/raf/actions/runs/41271916751) was pending; with its new explicit gate, it must skip reconstruct and must not cancel [41271844647](https://github.com/alwansan/raf/actions/runs/41271844647). Do not launch another native build. Inspect current jobs and cheap policy CI first.
- No user/device validation, FMOD playback, .rgd save/load, touch controls, playable singleplayer, or legal right to publish commercial game payload is established by these workflow changes. Continue gameplay engineering after the active build, but no public APK unless actual redistribution rights are confirmed. Do not repeat the cancellation mistake.


## 2026-11-01 08:05 Baghdad — native job outcome and 40-scene integrity guard

- Refreshed branch at `ff0a32def0dff54fff6e73bbe3854934fe3dd3b7`. No in-progress or queued Actions at inspection. [41271844647](https://github.com/alwansan/raf/actions/runs/41271844647) completed SUCCESS but was **SDK-only**, despite the reconstruct job's name: its Unity step35 ran `ValidateSdkBindings`, logged `RAFT_SDK_VALIDATION_COMPLETE noAndroidBuildRequested=true`, and all actual APK/StreamingAssets/full-Mesh/signature steps were skipped. No APK was built, retained or published. [41271916751](https://github.com/alwansan/raf/actions/runs/41271916751) completed SUCCESS with reconstruct skipped as intended by the opt-in gate; platform policy [41271929274](https://github.com/alwansan/raf/actions/runs/41271929274) SUCCESS. The original early device-test run [41267827866](https://github.com/alwansan/raf/actions/runs/41267827866) was cancelled, not failed by Unity.
- Found a native build safety gap: `AndroidNativeBuild.Build()` accepted any nonzero enabled-scene count, so a partial export could silently yield a misleading Android APK. Guard now requires exactly **40** enabled, distinct (case-insensitive), existing `.unity` scenes and logs `RAFT_ANDROID_SCENE_GATE`. It does not edit original scenes, assets or GUIDs. Three cheap source-policy regression tests added to platform CI. Local static checks verified exact gate placement and preserved `BuildPipeline.BuildPlayer` scene array; await CI for independent confirmation.
- This commit intentionally carries `[raft-native-build]` to request **one** full native reconstruction using the current offline-identity race fix and cached diagnostics. It does **not** carry `[raft-device-test]` and will not request a public release. First verify the new run's actual job/steps; do not duplicate while active. If native succeeds, audit 40 scenes, FMOD, original banks, ARM64, signature and residual water/compute errors. Real POCO F5 Pro testing remains absent. Public distribution remains gated by confirmed third-party game redistribution rights; obscurity or planned deletion is not such confirmation.

### Live continuation after the scene-gate commit (2026-11-01 08:07 Baghdad)

- Scene integrity guard and three regression tests landed atomically at [cb47ff69](https://github.com/alwansan/raf/commit/cb47ff69a989a18e7d9f5864ca5dde0cb385c9c5), no original asset/meta/source modified. Native build request was deliberately opt-in, with no release marker.
- New native [41275674909](https://github.com/alwansan/raf/actions/runs/41275674909), reconstruction job **124757272881**, is IN PROGRESS after license preflight SUCCESS. The run uses source cb47ff69 and should execute full selected Mesh, original bank, Unity ARM64 IL2CPP, APK and FMOD audits if each stage passes. **Do not start a duplicate or cancel it**. First inspect actual step and final result at the next cycle; previous SDK-only success is not a build.
- New cheap platform policy [41275674904](https://github.com/alwansan/raf/actions/runs/41275674904) was IN PROGRESS at netstandard2.1 compile; runner guard [41275674930](https://github.com/alwansan/raf/actions/runs/41275674930) completed SUCCESS. Do not call platform tests passed until final status is checked.
- No retained/public APK from this new run is yet established. The repository is PUBLIC and the rights-confirmation gate remains unset/unverified; the owner's intention to delete the repository later does not itself grant distribution rights for third-party game assets. Continue private CI validation and original gameplay engineering regardless of release eligibility.

- Final cheap test verification: [41275674904](https://github.com/alwansan/raf/actions/runs/41275674904) COMPLETED SUCCESS. Job124757251423 logged all three new scene-gate tests `ok`, netstandard2.1 build `0 Error(s)`, and platform smoke `TOTAL passed=8 failed=0`. Native41275674909 remained IN PROGRESS at CLR provider preflight on the last inspection; its full APK result is not yet known.
