# T4 LOCAL-005 — real original Data.rgd CLR deserialize and actual SaveAndLoad.Load<T> (2026-11-05)

## Ground truth and why this experiment differs

Until now A10 and B37 safely decoded the shipped original `Data.rgd` through `System.Formats.Nrbf`, without constructing an original game object. T4 independently executed actual SHA-authenticated original `FileManager` create/open on a disposable synthetic filename in [CI42020039305](https://github.com/alwansan/raf/actions/runs/42020039305), but no original `.rgd` payload was deserialized. The following two experiments **actually deserialize the shipped original RGD** and subsequently invoke the genuine compiled original `SaveAndLoad.Load<T>` on that same seed.

This report does **not** conclude the original saved world in APK86 loaded or that Android offline local-host creation is fixed. Shipped `Data.rgd` has not been proven identical to any user-generated game save.

## Immutable exact original sources

- ZIP2 read-only original provider `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- `Raft/Raft_Data/StreamingAssets/Data.rgd`: **2,941 bytes**, SHA256 `b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba`.
- `Raft/Raft_Data/Managed/Assembly-CSharp.dll`: **3,211,776 bytes**, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- **151** sibling `Managed/*.dll` files from pinned feature commit `02e9fba7fb42b83579595885391be636ee3b56e8`; no LFS or game source modification. Both SHA-authenticated primary inputs staged in ephemeral private CI, checked *before* loading CLR objects. A deliberately wrong seed SHA is rejected before running any deserializer.
- `.NET 8` managed runtime on `ubuntu-24.04`; opt-in `EnableUnsafeBinaryFormatterSerialization=true` for an exact known historical payload only, under one isolated job with no upload, no persisted credentials, original-source-only checkout, timeout and disabled crash dumps. This test does **not** claim equivalent Mono/.NET Framework or Android IL2CPP behavior.

## Actual code and proofs

[`android-port/Experiments/T4/OriginalRgdRuntimeLoad/Program.cs`](../android-port/Experiments/T4/OriginalRgdRuntimeLoad/Program.cs) loads the **exact original DLL into CLR**, uses a bounded simple-assembly-name resolver restricted to the 151 sibling `Managed` DLLs, then performs exactly one direct `BinaryFormatter.Deserialize` on the **SHA-verified shipped seed**. It records only whether an object was created and whether its type is defined by the actual original `Assembly-CSharp.dll`, without exposing the object, private name/member/values, stack trace or input bytes.

In its separate `--original-loadt` mode, *after* successful direct original object reconstruction identifies a trusted CLR root type, the same executable selects a unique original **static generic** `SaveAndLoad.Load<T>(string filename)` from the loaded original game DLL by reflection signature, binds `T` to that original root type, **invokes the compiled game method with the same exact original seed path**, and reports whether a non-null object of that same CLR type was returned. This is original method execution, not a decompiler-only inspection or simulated C# Load. It does **not** call `SaveGame`, serialize new game state, create a world, or test Android.

Source-free, strict status contracts [direct formatter validator](../scripts/t4_validate_original_rgd_runtime_load.py), [actual original loader validator](../scripts/t4_validate_original_rgd_loadt.py), [18 formatter controls](../tests/test_t4_validate_original_rgd_runtime_load.py) and [18 loader controls](../tests/test_t4_validate_original_rgd_loadt.py) reject wrong original SHA, missing runtime invocation, skipped game method, private fields, fabricated playable world, fake process restart and native/Android/IL2CPP claims. A deserialization error would be a bounded category, not proof the save is corrupt.

## Verified CI — real original object was reconstructed and returned by original game loader

- [**CI42042814576 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42042814576) on fixed-source mode: **18/18 controls**, exact seed+DLL authenticated, 151 siblings, original `.NET8 BinaryFormatter.Deserialize` **created an object**, and `deserialized_root_defined_in_original_dll=true`; `bounded_runtime_category=NONE`. An invalid seed SHA was refused. Direct formatter path only; `original_SaveAndLoad_LoadT_invoked=false`, as reported explicitly.
- [**CI42043768798 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42043768798) extended this to the genuine compiled original generic loader. **18/18 direct controls plus 18/18 Load<T> controls**; first the direct formatter again produced an object of the actual original game type, then **`original_SaveAndLoad_LoadT_invoked=true`**, `original_LoadT_method_signature_verified=true`, `original_LoadT_returned_matching_seed_type=true`, `original_LoadT_result_category=NONE`. Wrong SHA again rejected. Thus a source-authentic, genuine original typed load completed in this isolated managed runtime.
- The first two bounded [CI42042350875](https://github.com/alwansan/raf/actions/runs/42042350875) and [CI42042563929](https://github.com/alwansan/raf/actions/runs/42042563929) **FAILED** due the experiment's attempted file-size limit for dumps causing `SIGXFSZ / exit153`, *before* a managed result was emitted, after both source SHA checks passed. T4 removed the misleading file-size quota, disabled CLR crash-dump generation and privately captured any fatal stdout/error, while retaining original SHA, the runtime timeout and no-private-log publication. Both subsequent exact-input CIs passed. These two early failures do **not** constitute RGD incompatibility.

## Interpretation and next necessary device proof

The older A10/B37 findings remain correct: the seed root's serialized metadata showed a field-name mismatch and stored assembly-version difference compared with the later original DLL metadata. **Those metadata differences did not prevent actual object deserialization or the original generic `SaveAndLoad.Load<T>` from returning a matching original CLR type in the tested .NET8 environment.** This refutes the proposition that such metadata differences necessarily cause an exception under that runtime; it is **not** evidence they are irrelevant on Unity Mono/Android IL2CPP or for all generated RGD files.

Still **unverified**: using the real Raft local-host path to reach an interactable raft, running original `SaveGame` and serialized user/world data, durable storage over a full Android process exit, reopened **user-generated** world in the same native game, any Adreno shader/FFT behavior, Unity 2021.3 ARM64 IL2CPP, and owner phone acceptance. Existing Android-only source traces `WorldHasBeenLoaded.firstMoveNext`, `originalCompletionAssigned`, `Save.argumentFileSnapshot`, `Load.argumentFileSnapshot`, `Load.caughtException` should be used for the next T5-coordinated signed diagnostic candidate. A nonzero filename snapshot alone is not acceptance. Original `.rgd` contents, save source, Steam guard, GUIDs, audio, Settings and deferred touch have **not** been changed.

**LOCAL-005 remains OPEN; project NOT_READY, 0/3 immutable native acceptance reviews.** No native APK/OBB/XAPK or additional scheduled task was created; no other Actions canceled.
