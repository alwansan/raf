# T4 → T5: real original SaveWorld and SaveUser pass derived RGD values

origin: chat; session_id: 20261105T1544Z-T4-chat-original-rgd-precall-slice-w9c3; issue: LOCAL-005.

The exact original immutable 3,211,776-byte ZIP2 Assembly-CSharp.dll SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e` was independently inspected with a bounded .NET8 Mono.Cecil 0.11.5 probe. [CI42058900699](https://github.com/alwansan/raf/actions/runs/42058900699) **SUCCESS 22/22** Python adversarial controls + authentic original DLL/negative-SHA check. No source, payload or original IL was published.

**New bounded fact:** the last non-NOP original compiled instruction immediately before SaveWorld's exact private Save(string,RGD) pushes a `LOCAL_DERIVED_RGD`; SaveUser's equivalent pushes a `FIELD_DERIVED_RGD`. This explains why previous direct `new RGD` census was empty (CI42053882300) without implying missing world data. The derived class identity is intentionally undisclosed.

**Still UNKNOWN:** assignment and control-flow reaching SaveWorld local, initialization of SaveUser field, actual object identity/value, whether either Save method ran or wrote valid/durable RGD, Android world/playability, same-world relaunch. The 2,941-byte shipped StreamingAssets/Data.rgd has a distinct root type from real private world Save(RGD), CI42047540260: never substitute that seed for user world data or invent a fake RGD to pass this test.

**Native boundary:** T5 [run42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) failed at strict water gate in reconstruct, before signed APK/OBB/XAPK; T4 did not retry or modify that workflow. Coordinate next legitimate immutable native candidate with T1/T2 water resolution and B50 Steam guards, B07/T4 firstMoveNext/completion and Save/Load.argumentFileSnapshot diagnostics. Owner must create actually playable local raft, save original world file, fully quit, relaunch same install and reopen playable same world. Source-only CI cannot close LOCAL-005 or count readiness.

Report: `docs/T4_ORIGINAL_RGD_PRECALL_SLICE_2026-11-05.md`; new tool: `android-port/Experiments/T4/OriginalRgdPrecallSlice/`, validator/tests `scripts/t4_validate_original_rgd_precall_slice.py`, `tests/test_t4_validate_original_rgd_precall_slice.py`. Scheduled T4 JSONL UTC-order task is separate and untouched. **LOCAL-005 OPEN, NOT_READY 0/3**.
