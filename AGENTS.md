> **LATEST DEVICE/CI CHECKPOINT:** Read docs/WORK_SESSION_HANDOFF_2026-11-01_LOGRAFT_GPU_OOM.md. New LF logs explicitly record Raft GPU-memory OOM at5363928kB versus1572864kB threshold. Full-data native41312218192 FAILED Killed/137 after SDK/FMОD/scenes validated;noAPK. HostOOMsuspected,notkernel-confirmed. Prepared swap/memory telemetry and missing-authenticTMPfallback restoration;verifycheapCIfirst. NeverinterpretoldinstalledParty/kernelerrorsasdevicefailureofunreleasedfixes.

> **LATEST FULL-GRAPHICS CHECKPOINT:** Read docs/WORK_SESSION_HANDOFF_2026-11-01_FULL_GRAPHICS_RECOVERY.md, then the device transfer and history. Full source recovery probe41311076739 PASSED:6.85GB/17objects,4050textures,3948externalextents covered; export STILL Dummy140one-pass shaders. TMPofficial3.0.6restorer and originalFFT exception-lifetime/AndroidParty fixes passed isolated CI41311704761/41311860174. Main candidate now stages all original graphics payloads. Custom water/postFX shader restoration remains a real blocker; do not claim completion or request another FMOD/license setup. Existing branch and publication constraints apply.

> **LATEST DEVICE CHECKPOINT (2026-11-01):** Read [device rendering/input/performance transfer](docs/WORK_SESSION_HANDOFF_2026-11-01_DEVICE_RENDER_INPUT_PERFORMANCE.md) first. Native 41289171484 completed SUCCESS and was released; actual phone logs still show shader-pass failures, zero-kernel water FFT and FMOD Initialize NullReference. Touch/landscape/performance work remains pending. Older summaries below are historical.

# Raft Android port — autonomous engineering instructions

> **OWNER PRIORITY / DEVICE LOGS (2026-11-01):** Continue game restoration and Android compatibility; APK experiments support diagnosis and are not the goal. Inspect CL/raft%20log at every continuation for fresh phone evidence. Persist detailed application operation logs under Application.persistentDataPath/raft-logs (inside the requested Android/data/com.alwansan.raft.androidtest sandbox). Actual versionCode48 phone logs show early libfmodstudio.so+0x101e94 SIGSEGV; CI success did not establish startup/audio. See latest handoff for native-loader, original-save condition and persistent diagnostics work. No need for repeated owner approval or repeated APK tests before independent engineering.

> **LATEST OWNER DELIVERY DIRECTION:** native41275674909/job124757272881 completed SUCCESS including APK/FMOD/original-data/signature; APK not retained, Releases empty. The owner explicitly requests a direct testAPK here. Deliver that already-authorized early-startup prerelease after actual gates; do not add repository-variable permissions or request repeated approval. Raw source/project/loose assets/secrets remain unpublished. Keep explicit-native opt-in and cancel-in-progress:false; never cancel a running native for docs/workflow edits. See newest final handoff.

> **CURRENT OWNER-AUTHORIZED EARLY TEST (2026-11-01):** native41267827866/source1158b473/job124734255994 IN PROGRESS. SAME-source original Android CSharp/RPC/identity41267827880 PASSED; not device proof. Explicit owner directAPK request authorizes configured early-startup prerelease ONLY after actual Unity/APK/FM​​OD/signature gates pass. No raw source/project/assets/keys publication. Read latest final handoff; do not duplicate/cancel the current run. Existing historical broad no-APK instructions do not override this exact new owner-authorized test delivery.

> **LATEST VERIFIED RESULT:** native41259800620 SUCCESS; actual1323172270-byte ARM64 APK includes3FMOD native libraries+Java DEX bridge and36exact original StreamingAssets files;0compressed banks. Log-only41266582283 confirms10residual BuildReport errors,2water OnValidate NullRefs,no tracked Mesh/CSharp regression. No phone test/retained APK. Read final handoff section; older in-progress text below is historical.

> **LATEST RESULT (2026-11-01):** Native 41257065669 FAILED at Unity FMOD resource-platform lookup, not at licensing or runtime-key staging. The original platform assets exist under `Assets/Resources/FMODStudioSettingsPlatform*.asset`, while the validator queried the settings path. Exact-filename typed-lookup fix [9e5f3635](https://github.com/alwansan/raf/commit/9e5f3635a660f85bb492dee6c91bc57bc80aa730) is under new native validation [41259800620](https://github.com/alwansan/raf/actions/runs/41259800620). Read the newest sections of both handoffs; the older IN PROGRESS header below is historical.

> **LATEST AUTHORITATIVE WORK TRANSFER — 2026-11-01:** Start with [docs/WORK_SESSION_HANDOFF_2026-11-01_FMOD_ANDROID.md](docs/WORK_SESSION_HANDOFF_2026-11-01_FMOD_ANDROID.md), read it fully, then read the full history to its final section. Current FMOD native41257065669/source705dda0ae6e6928172bdae495be990612f29d5ab/job124702391661 is IN PROGRESS at last observation, NOT a completed result. Last completed native41250543603 succeeded with10reported errors after653cleanup diagnostics eliminated; no phone test/retained APK. Owner supplied official FMOD2.02.15; private runtime preflight and key setup already passed. Do not ask for Unity licensing, FMOD download or the original archive again. Refresh HEAD/latest Actions first. Older dated status quotations below are retained history, not current blockers. Only feature/android-native-port is writable.

> **New ChatGPT Work sessions (2026-10-30):** Start with [docs/WORK_SESSION_HANDOFF.md](docs/WORK_SESSION_HANDOFF.md). It contains the verified compiler/build history, toolchain, licenses, Git LFS constraints and autonomous next steps. The original 155-error snapshot is historical; read its Work continuation sections for the current state. Some older headings below reflect earlier historical states; always refresh the newest GitHub Actions run first. Do not touch main/zip/Unity-Editor.

> **LATEST VERIFIED STATUS — Work transfer 2026-10-31:** [Native41212679068](https://github.com/alwansan/raf/actions/runs/41212679068), sourcee38bd72738513b6abdd8cc6588a4e49acd6378ac, job124570812882, is IN PROGRESS at step30 **Unity Editor Android import/compile**. Steps18 helper coverage,25 real SDK/stub audit and28 scene/GUID validation completed SUCCESS. The --min-added500 and false Timeline/hyphen-filename blockers are fixed; do not repeat them as current failures. No completed new APK is claimed. Last built APK41200696376 predates restored Mono field fidelity and is not device-tested. Read the newest top AND final section of [docs/WORK_SESSION_HANDOFF.md](docs/WORK_SESSION_HANDOFF.md), refresh live Actions, and use [Arabic resume message](docs/WORK_NEW_SESSION_PROMPT_AR.md).

This repository branch is the working record for reconstructing the Windows Unity game data into a **native arm64 Android build**. Not an original Unity Editor project. See `docs/PORTING_ROADMAP.md`, `docs/VERIFIED_FINDINGS.md`, `docs/MESH_RECOVERY_FINDINGS.md` and `docs/RECONSTRUCTION_STATUS.md`.

## Owner direction (2026-10-30)
- **Wait preference (2026-10-31):** If the only remaining activity is waiting for a job known to take more than 10 minutes, stop waiting and give its exact run link/status. The owner will wait and send a completion message. Continue independent useful work while it exists; do not create unnecessary work merely to fill the wait.
- **Work autonomously:** the owner authorizes choosing engineering approaches, downloading required public tools and dependencies, running technical experiments, creating/updating workflows and making commits on the designated development branch without repeatedly requesting approval.
- The owner can test Android APKs on **POCO F5 Pro**; desktop/emulator testing is optional, not a prerequisite to sharing an APK.
- If a needed dependency cannot be installed/downloaded after reasonable attempts, report its exact version and direct official download URL for optional user upload. Do **not** request reuploads of already available REA, Node.js or JADX archives.
- Prioritize actual experiments, code, tests and GitHub runs over narrative planning. Always check disk space before large downloads or extraction, and minimize LFS bandwidth usage.
- **Work on `feature/android-native-port` only. NEVER merge into `main` or alter the source `zip` branch unless the owner explicitly changes this constraint.**
- Desired networking: fully playable offline/single-player on Android first; later an independently adapted host-phone LAN multiplayer system. No requirement to preserve original Windows Steam matchmaking or Xbox Party transport.
- Avoid irreversible repository/financial/admin/security changes or entering/unlocking private credentials. Technical autonomy does not grant access to secrets or unrestricted spending.

## Important verified baseline
- Engine version **2021.3.45f2**, Windows Unity Mono.
- All **40 serialized level scenes** exported, with **64,642/64,642 script GUID** references matching generated C# `.meta` files when `globalgamemanagers.assets` is included.
- ILSpy reconstructed **2,394** C# source files. Namespace-safe overlays of **1,568** C# files preserved all sampled script links.
- A temporary .NET 8 **diagnostic** compilation of recovered `Assembly-CSharp` passed, producing a ~3.58 MB assembly with original managed library references, after suppressing legacy `SYSLIB0011` BinaryFormatter diagnostics. **This is NOT Unity Editor or Android compilation; do not ship BinaryFormatter unsupported/insecurely.**
- Expanded regular Git assets reduced `deadbeef` placeholders: **393,450→199,156**, mesh **198,114→94,152**.
- Selective LFS `resources.assets` produced **37,111** total placeholders / **8,631** mesh.
- Selective LFS `resources.assets` + `sharedassets0.assets` produced **6,697** placeholders / **3,233** mesh. All remaining placeholders in that run appeared in the `Landmark_Utopia` scene. The 3-file `sharedassets36.assets` experiment is being verified separately.
- None of the above establish a working imported Unity project or a valid APK.

## Toolchain rules
- For Unity assets use checksum-verified AssetRipperCLI / UnityPy or equivalent suitable tools; for Mono code REA 6.8, dnfile, ILSpy; for Android DEX only use JADX if/when an actual Android APK exists.
- Prefer complete registered `MonoScript` identities from `globalgamemanagers.assets` over synthesized `deadbeef` placeholders.
- Do not publish proprietary raw assets, decompiled game C# sources, APKs with game content or untrusted patched Windows executables. Keep analysis output temporary and publish only aggregate statistics.
- GitHub LFS can consume billable quota. Fetch only narrowly selected paths where expected benefit is grounded; enforce byte and SHA256 checks. Avoid full 6.47 GiB LFS checkout by default. The owner gave broad project autonomy; still minimize potential charges.
- Do not execute original `Raft.exe`, `OnlineFix64.dll` or other untrusted game binaries.
- Mark findings verified vs inferred, and attach GitHub Actions run URLs. Never claim a Unity build or APK exists without actual compiler/build/test evidence.
- Account secrets and Unity activation are not in source control. Never embed private credentials, license files or signing keys.

## Suggested next gates
1. Resolve remaining Utopia mesh/resource links, confirm fidelity of `.resS` streams, and map missing non-script assets.
2. Reconstruct a single coherent Unity Editor project with DLL/script assembly and source GUID integration, then run a real Unity 2021.3.45f2 import/compile test.
3. Replace Windows Steam/Party and platform-dependent save ID/bootstrap. Preserve a safe offline save format and test.
4. Add Android ARM64 touch input, audio, rendering optimization and device diagnostics; build the first native single-player APK.
5. Implement host-phone LAN networking only after single-player gameplay and save/load work.

## Newly verified progress (2026-10-30)

- [Three targeted LFS objects](https://github.com/alwansan/raf/actions/runs/41028697081) eliminated ALL `deadbeef` placeholders across exported scenes: **0** missing sentinel references, including **0** `m_Mesh`, with 40 scenes and 64,642/64,642 script links.
- [Full ILSpy Mono source diagnostic net8 compile](https://github.com/alwansan/raf/actions/runs/41028495873) passed after suppressing only legacy BinaryFormatter obsolete errors for the experiment. [netstandard2.1 separately FAILED](https://github.com/alwansan/raf/actions/runs/41028896726) due to framework reference mismatches; do not mistake the net8 result for Unity Editor/Android compilation.
- The next concrete milestone is an integrated Unity Editor project build candidate combining those 3 LFS asset containers and GUID-preserving ILSpy source overlay; then real Editor import/compile. Check `.resS` payload fidelity before calling graphics usable.

## Current state to carry forward

- [Integrated Unity project candidate succeeded structurally](https://github.com/alwansan/raf/actions/runs/41029351916): 40 Unity scenes, 3,811 CSharp files/metas, 64,642 script links, **0 deadbeef scene placeholders**, **1,568** original game code overlays. Did **not** run Unity Editor or compile an APK.
- [Android offline platform adapter compiled + 7/7 tests](https://github.com/alwansan/raf/actions/runs/41029669318) in `android-port/Runtime/Platform`, not yet wired to game.
- [Unity license-gated import test](https://github.com/alwansan/raf/actions/runs/41030164120) checked the repository's activation secrets, found them unavailable and skipped all heavy work. **Unity 2021.3.45f2 activation remains a real prerequisite for genuine Android export**; never fabricate license credentials or claim an APK.
- At least 278/724 sampled Unity Mesh assets point to external `.resS` stream content, so mesh link completeness is not visual fidelity completeness. LFS default reset to NO, avoid billing surprises.

## Language compatibility lesson

- Always decompile `Assembly-CSharp.dll` for Unity 2021 with ILSpy `-lv CSharp9_0`, not ILSpy default Latest. Verified [2,394 CSharp9 sources with no two formerly failing CSharp12 primary constructors](https://github.com/alwansan/raf/actions/runs/41057568426).
- Retain namespace compatibility guard and AssetRipper invalid script template fixes. Do not alter script `.meta` GUID bytes during code fixes.
- Language syntax compatibility is not a guarantee of Unity Editor successful import or Android APK creation.
