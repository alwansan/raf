# Raft Android port — autonomous engineering instructions

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
