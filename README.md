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
- No working Android APK or complete restorable Unity project has been produced.
- Original Raft game files are commercial third-party content. Do not publish/distribute raw assets, decompiled source or full APK without appropriate permissions; a public repository containing such files can be subject to removal.
- GitHub LFS downloads may consume paid bandwidth; check billing before expanding data-heavy tests.
