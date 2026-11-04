# B37 — original RGD inherited-field and assembly-version proof — 2026-11-04

Original source is read-only ZIP2 ref 15964ea8f246b6e076ce26b60931ee2e1a9a2385. The 2,941-byte Raft_Data/StreamingAssets/Data.rgd has SHA256 b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba. The original 3,211,776-byte Assembly-CSharp.dll has SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e.

[Final original CI 41928767833](https://github.com/alwansan/raf/actions/runs/41928767833) **SUCCESS**, source fc42e65b458ea317b2dea4e494671e978effc153. CPU-only B37 program tests/b37-rgd-inherited-field/ uses System.Formats.Nrbf 10.0.14 and .NET PEReader metadata. All FOUR negative controls passed (wrong RGD SHA, wrong assembly SHA, damaged NRBF header and truncated payload). No original game type constructed; no BinaryFormatter.Deserialize, Unity, Android, original source values or field/type names published.

## Exact original findings

| Property | Authenticated result |
| --- | --- |
| Original saved root members | 1 |
| Resolved original CLR root class | 1, unique |
| Root type Serializable flag | true |
| Direct declared fields / direct matching names | 1 / 0 |
| Eligible nonstatic serialized fields / matching names | 1 / 0 |
| Inherited type definitions walked | 1 |
| Inherited fields / matching field names | 0 / 0 |
| Full base chain resolved | true |
| Saved root assembly simple name matches original game managed assembly | true |
| Saved root assembly version matches original managed version | **false** |

This rejects the hypothesis that a same-name field hidden in an inherited original class explains A10's direct root-member/field mismatch. **The stored assembly version mismatch is real**, but a historical seed with a different encoded version does not prove a corrupted save or an Android runtime load failure. Do not infer a .rgd schema bug, change save data, suppress exceptions or force migration.

## CI failures (harness-only, not evidence of original data corruption)

- [41928084203](https://github.com/alwansan/raf/actions/runs/41928084203) .NET10 warnings-as-errors for deprecated serialization enum symbols, fixed with direct ECMA-335 metadata bits at source 2a3e38b.
- [41928221064](https://github.com/alwansan/raf/actions/runs/41928221064) and [41928382242](https://github.com/alwansan/raf/actions/runs/41928382242) argv mismatch from dotnet run --nologo being forwarded to the app; workflow corrected at source 7ca4053.
- [41928548263](https://github.com/alwansan/raf/actions/runs/41928548263) disposed NRBF input stream while checking full payload; correction at fc42e65 uses Decode(..., leaveOpen: true).
- [41928767833](https://github.com/alwansan/raf/actions/runs/41928767833) PASS for authentic input and 4 negative controls.

## Next action and limits

This 2,941-byte original Data.rgd is a shipped seed, **not verified** as the particular user-generated saved world in APK86. Trace original SaveAndLoad.Load<T>, RGD producer and consumer, and any original binder/version aliases to decide whether the version/name mismatch is compatible. A future appropriately justified Android candidate must create, save, reload and play an actual .rgd world to close LOCAL-005. Do not edit original .rgd, scripts, audio, Settings or touch. The game did not build or run on Android in this B37 probe. WATER-001, RENDER-002 and LOCAL-005 remain OPEN; NOT_READY, independent acceptance 0/3.
