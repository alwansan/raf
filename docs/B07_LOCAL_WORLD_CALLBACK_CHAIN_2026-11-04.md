# B07 LOCAL-005 — authentic world callback and SaveGame reachability (2026-11-04)

Session `20261104T2112Z-B07-6e51`. Original Raft data/provider: ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original Assembly-CSharp.dll 3,211,776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. All original code is decompiled privately in ephemeral CI and never committed/published.

## Verified source evidence (not device success)

[Isolated B07 original-source CI41914637539](https://github.com/alwansan/raf/actions/runs/41914637539) **SUCCESS**, 8/8 synthetic negative controls, authenticated ILSpy11.2 original source. A SHA-pinned `Raft_Network.WorldHasBeenLoaded` structural probe reports a scene broadcast before the completion assignment. Authenticated `GameManager.OnWorldRecieved` includes **three** distinct executable `SaveGame(...)` callsites, not one. `SaveAndLoad.SaveGame` includes one original `SteamUserStats.StoreStats` callsite (guarded separately by B50 in the Android adaptation). For original class source fingerprints and method bodies see B07 safe CI summary or `scripts/b07_probe_original_world_callbacks.py`; no proprietary bodies were logged.

Early hypotheses/error evidence are retained: [41913966195](https://github.com/alwansan/raf/actions/runs/41913966195) failed because the incorrect one-call hypothesis refused the genuine three-call original. [41914221999](https://github.com/alwansan/raf/actions/runs/41914221999) failed on a diagnostic-only regex escape defect; fixed. [41914364998](https://github.com/alwansan/raf/actions/runs/41914364998) logged safe counts and the new original method SHA, then correctly rejected the old assumption. [41914637539](https://github.com/alwansan/raf/actions/runs/41914637539) is the first complete authentic source-check success.

## B07 Android code path

Integration plan: add the original `GameManager.OnWorldRecieved` method to `config/runtime-operation-traces.json` with the pinned original source/body hashes and a special `wrap_original_world_callback` adapter that preserves the original callback body and all three SaveGame branches. It uses existing `AndroidRuntimeLog.BeginOperation/EndOperation` with catch/rethrow. The method is a void callback; do **not** apply this wrapper to the iterator `WorldHasBeenLoaded` because inserting a catch around `yield` can invalidate C# and because coroutine completion must not be forged.

Native staging already calls `scripts/instrument_android_runtime_operations.py --manifest config/runtime-operation-traces.json --apply`; this adds diagnostics to an actual Android source reconstruction path, not merely to a demo. The adapter changes no world readiness flags, networking, Steam behavior, `.rgd` serialization, audio, Settings, touch, shaders or resources. Any source/body mismatch aborts instrumentation before import.

New [bounded B07 original callback CI41915466470](https://github.com/alwansan/raf/actions/runs/41915466470) is pending/being checked as this note was written; do not infer a passing integration until its test/CI result is confirmed. It covers synthetic branch-preservation and the privately SHA-authenticated original callback, but **does not compile Unity or produce/test APK**. If this run fails, fix based on exact log and retain failures in the experiment.

## Acceptance and next steps

`LOCAL-005` stays **OPEN**, overall **NOT_READY 0/3**. Latest actual game release `android-early-test-41812889049-1`, source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`, phone APK86. CL snapshot `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29` shows `steam_api64` missing from the old SaveGame path; B50's offline StoreStats and Cheat identity guards are source-level only and **not in that phone install**. To prove a playable local world, make a coordinated newer signed Android test build, capture `world/OnWorldRecieved` operation transitions and any exceptions alongside the real save path, then create/save/close/reopen an actual `.rgd` world on device. Do not hide the Connecting error, inject `WorldHasBeenRecieved`, or claim that a completed log callback proves a playable world.
