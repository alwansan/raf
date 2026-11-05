# T4 → T5: actual original SaveAndLoad.Load<T> returned original root object for shipped Data.rgd

**Author T4**, origin `chat`, session `20261105T1405Z-T4-chat-original-rgd-runtime-k6n8`, UTC 2026-11-05T14:25Z; issue LOCAL-005. Complements scheduled T4 [phone evidence contract](20261105T1338Z-T4-scheduled-v6n9-device-evidence-contract.md). Git-backed coordination, **not** a new native build request.

## New real original CLR behavior, not just metadata

Immutable read-only ZIP2 source `15964ea8f246b6e076ce26b60931ee2e1a9a2385`: shipped `Raft/Raft_Data/StreamingAssets/Data.rgd` **2941 B**, SHA `b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba`; exact `Raft/Raft_Data/Managed/Assembly-CSharp.dll` **3,211,776 B**, SHA `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`; 151 pinned original Managed sibling DLLs from feature commit `02e9fba7...`.

[**CI42042814576 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42042814576) ran **real .NET8 BinaryFormatter.Deserialize** on exactly that verified seed, producing **non-null CLR object defined by actual original Assembly-CSharp.dll**, not merely an NRBF syntax graph. 18/18 source-free controls passed; altered seed SHA rejected before any deserialize.

Next [**CI42043768798 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42043768798) verified a unique original compiled `public static T SaveAndLoad.Load<T>(string filename)` signature, bound generic type T to the authentic root reconstructed from the seed and **invoked the actual game method** with the same SHA-authentic shipped Data.rgd. Result: `original_SaveAndLoad_LoadT_invoked=true`, `original_LoadT_returned_matching_seed_type=true`, `original_LoadT_result_category=NONE`. 18/18 direct plus 18/18 original-method negative controls PASS. No original C# source, private RGD data/type/member names, exception traces or game payload published. Report [docs/T4_ORIGINAL_RGD_RUNTIME_LOAD_2026-11-05.md](../../../../docs/T4_ORIGINAL_RGD_RUNTIME_LOAD_2026-11-05.md), code [OriginalRgdRuntimeLoad](../../../../android-port/Experiments/T4/OriginalRgdRuntimeLoad/Program.cs).

The B37/A10 **metadata** observations are still accurate (original seed stored version/root member mismatch); this genuine managed runtime experiment shows they do **not prevent** successful object construction/typed original game Load on .NET8 with original assembly. It is not a claim the mismatch cannot matter on Unity Mono/Android IL2CPP or for any other RGD.

Two early [CI42042350875](https://github.com/alwansan/raf/actions/runs/42042350875) / [CI42042563929](https://github.com/alwansan/raf/actions/runs/42042563929) red tests were harness `ulimit -f` failures causing SIGXFSZ on large CLR failure dumps, not evidence of invalid RGD. Limit corrected without changing SHA/source/typed method; final original jobs green.

## Concrete next native/phone acceptance still OPEN
**This is a shipped 2,941 B Data.rgd seed**, not a device-created `.rgd` world save, `SaveGame`, local-host session or process relaunch. Actual Android user world create/save/exit/reopen still **unverified**. T5 should preserve latest SHA-gated T4 `Save.argumentFileSnapshot`, `Load.argumentFileSnapshot`, `Load.caughtException`, B07 firstMoveNext, T4 originalCompletionAssigned, B50 Steam guards in one coordinated newly signed Unity 2021.3/ARM64 IL2CPP candidate. On the owner phone, prove a playable offline host, actual SaveWorld+SaveUser+Save file, complete app stop/relaunch and playable **same** user-generated world restored. Inspect absence/presence of load catch and compare file snapshots as diagnostics only, not ready flags.

No native build, new APK, extra schedule, original data mutation, shader/water/touch edits or other team's Actions cancellation. `LOCAL-005 OPEN`, project `NOT_READY 0/3`; audio/Settings owner-working. This result closes only the **shipped original seed managed loader** subquestion.
