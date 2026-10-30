# Raft Android port — autonomous engineering instructions

> **New ChatGPT Work sessions (2026-10-30):** Start with [docs/WORK_SESSION_HANDOFF.md](docs/WORK_SESSION_HANDOFF.md). It contains the verified compiler/build history, toolchain, licenses, Git LFS constraints and autonomous next steps. The original 155-error snapshot is historical; read its Work continuation sections for the current state. Some older headings below reflect earlier historical states; always refresh the newest GitHub Actions run first. Do not touch main/zip/Unity-Editor.

> **Latest Work milestone:** Unity run [41071111333](https://github.com/alwansan/raf/actions/runs/41071111333) passed C# compilation and reached Android BuildPipeline, then failed due to unset Android CPU architecture. No APK. Latest fixes configure ARM64/IL2CPP and audit newly exposed mesh/asset import issues; read the end of the handoff before acting on historical error counts.

This repository branch is the working record for reconstructing the Windows Unity game data into a **native arm64 Android build**. Not an original Unity Editor project. See `docs/PORTING_ROADMAP.md`, `docs/VERIFIED_FINDINGS.md`, `docs/MESH_RECOVERY_FINDINGS.md` and `docs/RECONSTRUCTION_STATUS.md`.

## Owner direction (2026-10-30)
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
