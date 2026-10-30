# REA 6.8.0 adoption decision for Raft v1.1.01 Android research

Date: 2026-10-30. Source baseline `zip`, development branch `feature/android-native-port`.

## Verified findings

- REA official package is `rea-agents@6.8.0` (https://github.com/morluto/rea, https://www.npmjs.com/package/rea-agents).
- Required Node.js range includes 24.22.2, which is the user-supplied tarball version and the version installed by CI.
- GitHub Actions [successful REA managed audit](https://github.com/alwansan/raf/actions/runs/41020338080) installed Node.js v24.22.2 and rea-agents v6.8.0 (176 npm packages) after a storage check and no-LFS checkout.
- It successfully executed `rea inspect-managed-artifact Raft/Raft_Data/Managed/Assembly-CSharp.dll --format json`, producing ~2,189,390 bytes of local JSON evidence. The game DLL was parsed, **not executed**.
- Previous failed workflow attempts were caused by passing unsupported REA 6.8.0 CLI flag `--detail`. The supported and verified rendering option is `--format json`; `--json` / summary examples in older docs should not be assumed to work with this version.
- This is a verified metadata analysis, **not** proof that REA can compile, recover or automatically port a complete Unity game.
- Additional targeted [native boundaries and network member workflow](https://github.com/alwansan/raf/actions/workflows/raft-rea-network-audit.yml) is configured. Evaluate its run logs before calling it successful.

## Tool selection

| Task | Preferred tool | Evidence / reason |
|---|---|---|
| Unity asset and partial project export | AssetRipperCLI v1.0.1 (tested), AssetRipper official 2.0.0 (tested CLI help) | 243-file raw sample exported and 20-file settings/package sample exported |
| Managed Mono metadata, call references, P/Invoke declarations | REA 6.8 and dnfile 0.18 | Both have succeeded on `Assembly-CSharp.dll` without executing game code |
| C# decompilation for manual source repair | ILSpy/ilspycmd (to be tested if authorized and needed) | Mono assemblies; REA metadata inspection does not automatically reconstruct Unity project |
| Android APK DEX/Java/Kotlin | JADX (defer) | Raft PC data are Unity Mono assemblies, not an Android APK |
| Unity Editor + Android Build Support | Unity 2021.3.45f2 (not installed) | Embedded version verified; Editor project still needs reconstruction |
| New phone-hosted networking | Reevaluate built-in Unity Netcode/Transport before Mirror | `Unity.Netcode.Runtime` and `Unity.Networking.Transport` files present; Windows Party P/Invoke requires replacement |

## Tool availability and downloads

- User's previous Library uploads verified by filename: `rea-agents-6.8.0.tgz`, `jadx-headless-mcp-0.7.1-all.jar`, `node-v24.22.2-linux-x64.tar.gz`. They need **not** re-upload them.
- The run successfully installed REA from official npm, so no need to transfer the tgz to Actions right now.
- AssetRipper official v2.0.0 binary downloaded and verified in Actions: https://github.com/AssetRipper/AssetRipper/releases/download/2.0.0/AssetRipper_linux_x64.tar.xz
- The project export tool AssetRipperCLI v1.0.1 was also installed from its official release URL for that community fork: https://github.com/nowl-it/AssetRipperCLI/releases/download/v1.0.1/AssetRipper_linux_x64.zip
- No missing user-supplied archive or software identified in the current investigations.
- **Never bulk-download Git LFS resources without checking free space, LFS billing, permissions and dependency scope.** Current Windows-distribution content alone is **not** an original Unity Editor project.

## Scope and privacy

- Do not commit Unity serialized game assets, original source snippets or raw decompilation results to a public repo.
- Quarantine untrusted OnlineFix, Steam overlay and patched executable components. Never execute them in CI.
- Do not distribute a derivative build using third-party commercial assets without appropriate rights.
- Develop only on `feature/android-native-port`; never merge with `zip` or `main` without explicit instruction.

## Next criteria

1. Verify REA's native-boundary and targeted-member tool actually works on `Assembly-CSharp.dll`, not just the artifact metadata command.
2. Identify which gameplay network features depend on Unity Netcode/Transport versus Windows Party API.
3. Build platform adapter abstractions for offline services and future LAN host.
4. Reconstruct a small verified Unity Editor scene; then run editor import and Android build experiments in a licensed environment.
