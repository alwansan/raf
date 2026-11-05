# T5 — original FileManager compiled IL call-edge recovery (2026-11-05)

## Grounded problem and provenance
T4's authentic [CI41942655373](https://github.com/alwansan/raf/actions/runs/41942655373) found one lexical `FileManager` call in original `SaveAndLoad.Load<T>` and one in original `Save`, yet the *restricted ILSpy C# block-declaration regex* recognized **zero** original target method bodies. T4 correctly left presence and actual System.IO paths UNKNOWN. Its successful declaration-shape controls are not a compiled metadata resolution.

T5 inherited those exact observations without modifying T4's sources or scripts, then implemented a **separate actual compiled metadata/IL oracle** in [FileManagerMetadataBridge](../android-port/Experiments/T5/FileManagerMetadataBridge/Program.cs) using pinned `Mono.Cecil 0.11.5`. The bridge authenticates the original 3,211,776-byte `Raft/Raft_Data/Managed/Assembly-CSharp.dll` from ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` with full SHA-256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e` **before** reading its metadata.

It resolves actual compiled call operands (not decompiled C# surface syntax) for source-call roles LOAD and SAVE, validates that targets are declared on the exact in-module FileManager type and contain actual IL bodies, and reports only bounded counts and booleans. Neither names of private methods, original source/IL, type/signature strings, game textures, nor raw managed DLL are uploaded. A separate strict [schema verifier](../scripts/t5_validate_filemanager_metadata.py) rejects missing evidence, fabricated device success, extra private fields, ambiguous calls and malformed reports.

## Actual original-data result
[**CI42012597665 — SUCCESS**](https://github.com/alwansan/raf/actions/runs/42012597665), integration commit [7159dba5](https://github.com/alwansan/raf/commit/7159dba501f4ee2615b92009c2b4622dd8d39f34):

| Bounded, original compiled-IL observation | Read target | Write target |
|---|---:|---:|
| Exact direct call sites in SaveAndLoad role | 1 | 1 |
| Target resolved in original FileManager | true | true |
| Exact class / static / executable IL body | true | true |
| Method parameters | 2 | 1 |
| IL instructions | 14 | 13 |
| Direct System.IO method calls | 1 | 1 |
| Exception handlers | 1 | 1 |

Read/write resolve to *different* metadata method tokens; no names or tokens were printed. **11/11** synthetic fail-closed report tests passed. No raw original payload or tool logs were uploaded. This refutes any inference that original called FileManager methods are absent *merely because* the current C# regex fails to recognize their declarations. It does **not** establish precisely why ILSpy formatting defeats that parser, nor that the method returns a durable on-device file.

## Limits and next executable gate
- Direct System.IO calls and exception handlers are **compiled original source observations**, not execution of FileManager against Android application storage.
- The original assembly has been SHA-verified, but no `.rgd` file was created or round-tripped through the native Android build; save permissions/paths and serialization remain open.
- This test does not prove Unity Editor import, IL2CPP AOT compatibility, world host creation, Steam persistence guards at runtime, or renderer/FFT/Adreno correctness.
- Preserve B07/B14/B19/B37/B50 and T4 evidence/provenance. Do not silently rewrite T4's production parser or assume missing method bodies. With T4, compare exact original read/write argument count/path intent to **current adapted FileManager calls**, then validate create/save/close/relaunch/reopen in a future phone-test build.

Project remains **LOCAL-005 OPEN; NOT_READY 0/3**. Latest actual Raft game release remains APK86 from older source. Owner-reported working audio/Settings unchanged; touch/buttons/layout remain deferred. T1's GameCI activation comparison was already active, so T5 explicitly refrained from duplicate Unity work.
