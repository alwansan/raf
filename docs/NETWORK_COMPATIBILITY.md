# Raft network subsystem: first static evidence and Android migration design

Last updated 2026-10-30. **Technical architecture hypothesis**, not a confirmed working port.

## Verified evidence

The following observations come from `Raft/Raft_Data/Managed/Assembly-CSharp.dll`, **without executing game binaries**, via successful REA 6.8.0 GitHub Actions:
- [Native boundaries audit](https://github.com/alwansan/raf/actions/runs/41020808394): 155 P/Invoke imports in this game assembly:
  - **131** `PartyWin32`
  - **21** `PartyXboxLiveWin32`
  - **3** `lz4unity`
- The assembly also has **271** rows classified as native implementation records by REA; this number is **not** 271 additional Windows DLL calls and should not be conflated with P/Invoke.
- `Unity.Netcode.Runtime.dll` and `Unity.Networking.Transport.dll` are present in `Raft_Data/Managed`; the game assembly references `Unity.Netcode.Runtime`.
- Selected type `AI_NetworkBehaviour`: **14 methods, 9 fields, 27 call edges, 19 field accesses**. Method names include:
  - `Initialize`, `SetNetworkIndexes`, `get_Network`, `get_ConnectedToSpawner`
  - `UpdateHost` and `UpdateRemoteclient`
  - `OnRestoreStart`, `OnRestoreFinished`, `Create_SaveData`
  - Unity lifecycle `Awake`, `Start`, `Update`, `OnDestroy`.
- Other network-related type names are present for shark, animal and boss behaviors. This does **not** prove those components can be reused unmodified.

**Interpretation:** game networking and world-state restoration are coupled to custom behavior, with a distinct host vs remote-client update path. There are numerous Windows Party native calls, but the location of each call site and whether it can be replaced without restructuring must still be mapped. Simply deleting Party DLLs or swapping in Mirror will almost certainly be insufficient.

## Two-layer migration approach (proposed)

1. **Offline adapter / single-player boot**: put the platform-specific session and identity API behind a gameplay interface. Provide a local-only implementation for solo mode and remove the need for Steam/Party at startup. Keep the original gameplay save semantics where they can be safely understood.
2. **Networking transport**: first evaluate reusing existing Unity Netcode/Unity Transport serialization and NetworkBehaviour contracts. Implement an Android-safe LAN UDP transport **only if** actual project reconstruction confirms those contracts can be compiled and decoupled from Party/Steam.
3. If original Netcode gameplay proves inseparable from platform-specific hooks, isolate state models and implement a replacement with a supported networking framework (Mirror/UTP/custom only after tradeoff testing). This is a contingency, **not** a selected framework yet.
4. A phone hosts the authoritative world. Other clients join through manual local address; Wi-Fi discovery later. No original PC matchmaking required.

## Android LAN first, P2P internet later

- Phase 1: host/client on the same Wi-Fi, manual IP, IPv4 and compatible UDP port; use real-device testing rather than assuming an emulator simulates network conditions.
- Phase 2: optional Android NSD/mDNS discovery and hotspot experiments; account for Android permissions and multicast restrictions.
- Phase 3: state replication for raft transforms/physics, debris, items, inventories, crafting, AI, island/world events and player attributes; host validates all inventory mutations and persists saves.
- Phase 4: reconnect, network version checks, corruption protection, duplicate item tests, backgrounding, thermal throttling, power and data usage.
- Phase 5: Internet connectivity requires signaling and often relay/TURN/ICE because inbound direct P2P can fail under carrier-grade NAT; do not promise universal direct P2P.

## Blocking questions for further REA and Unity inspection

- Which exact game methods call `PartyWin32` and `PartyXboxLiveWin32`? Which use `Unity.Netcode.Runtime` methods?
- Is the `Unity.Networking.Transport` assembly actually used at runtime and via what transport configuration?
- What do `UpdateHost` and `UpdateRemoteclient` read/write? Which objects own authority for AI, raft movement and item interactions?
- How are world saves and player saves split? How does reconnect restore state?
- Are FMOD/platform integrations independent of game startup or tightly coupled?
- Which scripts have broken serialization, GUIDs and runtime references after AssetRipper recovery?

**Before making a network framework choice**: gather per-method call graph evidence, compile a minimal Unity project in Unity 2021.3.45f2, build an offline Android vertical slice, then conduct a LAN prototype.

## Do-not-merge and distribution safeguards

- Work only on `feature/android-native-port`. Do not merge `main` or `zip` automatically.
- Do not execute patched Windows game binaries or ship Windows DLLs with Android APK.
- Do not publish decompiled commercial source, proprietary extracted assets or derivative full APK without appropriate permission.
- GitHub LFS downloads require a storage and usage-budget check before any expansion.
