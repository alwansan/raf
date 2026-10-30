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

## Tools and repeatable tests

- [Safe build inventory](scripts/inspect_raft.py) / [Actions workflow](.github/workflows/raft-inventory.yml)
- [Static Mono metadata analysis](scripts/analyze_managed.py) / [Actions workflow](.github/workflows/raft-managed-audit.yml)
- [Official AssetRipper Linux tool installation smoke test](.github/workflows/assetripper-tool-smoke.yml)
- [AssetRipperCLI tool test](.github/workflows/assetripper-cli-smoke.yml) / [tiny Unity asset import/export experiment](.github/workflows/raft-asset-probe.yml)

### What has actually been verified?

- `Raft_Data/globalgamemanagers` identifies Unity **2021.3.45f2**
- `Assembly-CSharp.dll` is readable as managed metadata: **3032 types, 19512 methods, 16920 fields, 155 native P/Invoke declarations**
- Existing `Unity.Netcode.Runtime` and `AI_NetworkBehaviour_*` references were found
- **18 Git LFS pointers** declare **6.472 GiB** of files *not yet downloaded*
- No Unity `Assets`, `ProjectSettings`, `Packages` editor project exists in this game distribution

## Security, rights and billing

- Never execute the included game EXE or untrusted patched Windows binaries in CI.
- All existing analysis CI runs skip Git LFS downloads on purpose.
- Original Raft game files are commercial third-party content. Do not publish/distribute raw assets, decompiled source or full APK without appropriate permissions; a public repository containing such files can be subject to removal.
- GitHub LFS downloads may consume paid bandwidth; check billing before expanding data-heavy tests.
