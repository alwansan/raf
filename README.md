# Raft Android — Native Port Research (work in progress)

**This is not a working Android game/APK.** This repository branch contains static research and build tooling for evaluating a native Android port. The source is compiled Windows Unity game data, **not** an original Unity Editor project.

- Base/source: `zip`
- Development branch: `feature/android-native-port`
- Unity engine version identified: **2021.3.45f2**
- Device for planned physical tests: **POCO F5 Pro**
- Multiplayer goal: original PC network removed/replaced; eventual phone-hosted LAN sessions (internet join later)
- **Never merge to `main` without explicit approval.**

## Documents

- [Detailed gated porting roadmap](docs/PORTING_ROADMAP.md)
- [Verified findings and successfully completed audits](docs/VERIFIED_FINDINGS.md)
- [REA evaluation and tool choice](docs/REA_EVALUATION.md)
- [Latest tested reconstruction state, code export and linkage blockers](docs/RECONSTRUCTION_STATUS.md)
- [Android phone-hosted network compatibility and migration design](docs/NETWORK_COMPATIBILITY.md)

## Tools and repeatable tests

- [Safe build inventory](scripts/inspect_raft.py) / [Actions workflow](.github/workflows/raft-inventory.yml)
- [Static Mono metadata analysis](scripts/analyze_managed.py) / [Actions workflow](.github/workflows/raft-managed-audit.yml)
- [REA 6.8 managed assembly static audit](.github/workflows/raft-rea-smoke.yml) — [successful run](https://github.com/alwansan/raf/actions/runs/41020338080)
- [REA native boundaries and selected networking methods](.github/workflows/raft-rea-network-audit.yml) — [full import count run](https://github.com/alwansan/raf/actions/runs/41020808394)
- [Official AssetRipper Linux tool installation smoke test](.github/workflows/assetripper-tool-smoke.yml)
- [AssetRipperCLI tool test](.github/workflows/assetripper-cli-smoke.yml)
- [243-file sample resource export](.github/workflows/raft-asset-probe.yml) — [successful run](https://github.com/alwansan/raf/actions/runs/41017866546)
- [Partial Unity Editor project export](.github/workflows/raft-project-probe.yml) — [successful run](https://github.com/alwansan/raf/actions/runs/41018053143)

### What has actually been verified?

- `Raft_Data/globalgamemanagers` identifies Unity **2021.3.45f2**
- `Assembly-CSharp.dll` is readable as managed metadata: **3032 types, 19512 methods, 16920 fields, 155 native P/Invoke declarations**
- Existing `Unity.Netcode.Runtime` and `AI_NetworkBehaviour_*` references were found
- **18 Git LFS pointers** declare **6.472 GiB** of files *not yet downloaded*
- No Unity `Assets`, `ProjectSettings`, `Packages` editor project exists in the original game distribution; limited probe regenerated `ProjectSettings` and `Packages` but not `Assets`

## Security, rights and billing

- Never execute the included game EXE or untrusted patched Windows binaries in CI.
- All existing analysis CI runs skip Git LFS downloads on purpose.
- ILSpy full Mono export succeeded (2,394 .cs files / 251,725 source lines, TEMP only); five exported Unity scenes contain many unresolved script references.
- **No working Android APK or complete restorable Unity project has been produced.**
- Original Raft game files are commercial third-party content. Do not publish/distribute raw assets, decompiled source or full APK without appropriate permissions; a public repository containing such files can be subject to removal.
- GitHub LFS downloads may consume paid bandwidth; check billing before expanding data-heavy tests.

### Latest breakthrough: MonoScript identity and serialized scene linkage (2026-10-30)

- Original, **non-LFS** `Raft_Data/globalgamemanagers.assets` contains **3,827 MonoScript records**; earlier samples mistakenly omitted it. [UnityPy evidence](https://github.com/alwansan/raf/actions/runs/41023529350).
- With that file included, [AssetRipper linkage export](https://github.com/alwansan/raf/actions/runs/41023760680) recovered **3,810 C# scripts + 3,810 script .meta files** and **5 scenes**. All **13,969** scene `m_Script` GUID occurrences matched exported script .meta GUIDs, with no `deadbeef` placeholder in this sample.
- The latest [full-script Level0 CI experiment](https://github.com/alwansan/raf/actions/workflows/raft-full-script-linked-recovery.yml) is being evaluated. Valid GUID linkage does not yet mean a compiling Unity project or playable APK.
- No LFS downloads or third-party proprietary asset uploads were needed for this fix.

### Reconstructable gameplay code integration

[Verified CI run](https://github.com/alwansan/raf/actions/runs/41024504209) safely overlaid **1,568** name-and-namespace-matched ILSpy gameplay C# files onto AssetRipper's original-script-GUID-preserving export. All **13,969/13,969** script refs in the five-scene sample remained valid. Six fixture-only overlay safety tests passed. This is a **temporary local build-time reconstruction technique**, not a distributable or Unity-compiling game project. See [reconstruction status](docs/RECONSTRUCTION_STATUS.md). A separate [all 40 levels check](.github/workflows/raft-all-scene-links.yml) broadens scene coverage without downloading Git LFS.

### Forty-scene serialized script reference gate

[All levels passed a script-link audit](https://github.com/alwansan/raf/actions/runs/41024647631): `level0..level39` exported **40 Unity scenes** with **64,642/64,642** `m_Script` GUID uses matching exported `.cs.meta` files and no placeholder identifiers. This is a serialized scene linkage milestone, not a runnable game or APK. The full set of other asset dependencies is still being audited without LFS downloads.

### Mesh/geometry dependency milestone

[All regular-Git Unity asset export](https://github.com/alwansan/raf/actions/runs/41025868800) **reduced** unresolved `deadbeef` scene references by **49.4%** (393,450 → 199,156) and mesh placeholders by **52.5%** (198,114 → 94,152), without Git LFS downloads. [Independent original Unity pointer audit](https://github.com/alwansan/raf/actions/runs/41026113254) identified `resources.assets` as the largest original mesh reference target (85,525 uses), followed by `sharedassets30.assets` (42,137 uses) and others.

See [mesh recovery findings, remaining blockers and cost-controlled next gate](docs/MESH_RECOVERY_FINDINGS.md). A [manual-only opt-in Git LFS workflow](.github/workflows/raft-opt-in-lfs-mesh-probe.yml) allows a deliberately approved 106 MiB `resources.assets` test or an optional 217 MiB two-file test. **No LFS downloads run automatically**. Neither a fully compilable Unity Editor project nor Android APK exists yet.

### All exported scene resource GUID placeholders resolved (latest)

[Verified three-file LFS export](https://github.com/alwansan/raf/actions/runs/41028697081) reduced both scene-wide and mesh `deadbeef` references to **zero** across **40 Unity scenes**, retaining **64,642/64,642** script GUID links. Targeted LFS files: `resources.assets`, `sharedassets0.assets`, `sharedassets36.assets` (~322 MiB per combined run), not all 6.47 GiB. [Findings and limitations](docs/MESH_RECOVERY_FINDINGS.md).

[ILSpy decompiled source net8 diagnostic compilation succeeded](https://github.com/alwansan/raf/actions/runs/41028495873), producing a 3.58 MB DLL in the temporary runner. A separate netstandard2.1 diagnostic failed due to framework references, so **Unity Editor import/compile is NOT verified**. Large `.resS` content is still untested.

### Integrated Unity Editor project candidate and offline Android platform adapters

[Integrated full candidate CI — PASS](https://github.com/alwansan/raf/actions/runs/41029351916): all 40 scenes, 3,811 C# files + 3,811 C# metadata files, 64,642/64,642 script GUID matches, **zero** scene deadbeef placeholders, and **1,568** namespace-safe real ILSpy gameplay-source overlays. This is an ephemeral Unity editor project candidate: NOT yet an import/compile pass.

[New Android offline platform adapter — PASS, 7/7 tests](https://github.com/alwansan/raf/actions/runs/41029669318): original `android-port/Runtime/Platform` C# netstandard2.1 library for stable local profile identity, safe isolated save paths and offline-host session semantics. **Not yet wired into Raft_Network/SaveAndLoad.**

[Unity Editor + Android smoke test gate](https://github.com/alwansan/raf/actions/runs/41030164120) checked private activation secret availability, found no Unity license/account credentials and safely skipped the actual build, with **no extra LFS or Docker downloads**. Never claim an APK exists. Unity 2021.3.45f2 Editor import/compile and Android Build Support remain the next hard gate.

### CI runner changes and Unity license prerequisite (October 30, 2026)

- [GitHub Actions issue #14748](https://github.com/actions/runner-images/issues/14748) announces `ubuntu-latest` migration from Ubuntu 24.04 to 26.04 between October 19 and November 19, 2026. All **30 existing Raft workflows** have been explicitly pinned to `ubuntu-24.04`. The [sparse-checkout compatibility guard](.github/workflows/raft-runner-compat-guard.yml) has [passed](https://github.com/alwansan/raf/actions/runs/41032855606) and protects future changes from accidentally using `ubuntu-latest` or unbounded LFS checkout.
- Fixed an obsolete [script-link test](https://github.com/alwansan/raf/actions/runs/41032916108) by including the missing `globalgamemanagers.assets` MonoScript registry; it now passes with **3 scenes, 3,810 scripts**.
- **Only user-dependent CI prerequisite**: legitimate Unity activation. [Arabic instructions for Personal and Pro](docs/UNITY_LICENSE_SETUP_AR.md). Set GitHub repository Secrets without sharing them in chat. The [Unity 2021.3.45f2 Android CI gate](.github/workflows/raft-unity-editor-android-import.yml) now accepts either Personal (`UNITY_LICENSE` + email/password) or Pro (`UNITY_SERIAL` + email/password); it skips expensive operations if credentials are missing.
- A [no-network local RAR extractor](scripts/extract_raft_lfs_from_rar.py) can recover individual game streams from a preexisting privately supplied archive, verifying file size and SHA256 against Git LFS pointers. This method independently verified a 217,498,752-byte `sharedassets25.assets.resS` mesh/texture resource without additional LFS usage; [details](docs/MESH_RECOVERY_FINDINGS.md).
- Actual Unity Editor import, gameplay functionality and Android APK are **NOT yet verified**.
