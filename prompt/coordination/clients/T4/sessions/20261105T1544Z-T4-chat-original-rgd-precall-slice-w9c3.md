# T4 chat — original SaveWorld/SaveUser RGD precall producer family

- session_id: 20261105T1544Z-T4-chat-original-rgd-precall-slice-w9c3
- origin: chat
- status: completed
- base_sha: c4858f5de9369a03ea0256f3d8ca97ab1e4b362b
- resumed_from_sessions: 20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2, 20261105T1440Z-T4-scheduled-q8p3
- work: prompt/coordination/work/LOCAL-005/T4-20261105T1544Z-T4-chat-original-rgd-precall-slice-w9c3-precallslice.json
- experiment_key: t4-zip2-15964-original-sha0a6f-SaveWorld-and-SaveUser-precalls-v1
- resource_key: none (pinned read-only original DLL)
- intended_files: android-port/Experiments/T4/OriginalRgdPrecallSlice/OriginalRgdPrecallSlice.csproj, android-port/Experiments/T4/OriginalRgdPrecallSlice/Program.cs, scripts/t4_validate_original_rgd_precall_slice.py, tests/test_t4_validate_original_rgd_precall_slice.py, .github/workflows/raft-t4-original-rgd-precall-slice.yml, docs/T4_ORIGINAL_RGD_PRECALL_SLICE_2026-11-05.md, prompt/coordination/work/LOCAL-005/T4-20261105T1544Z-T4-chat-original-rgd-precall-slice-w9c3-precallslice.json, prompt/coordination/clients/T4/sessions/20261105T1544Z-T4-chat-original-rgd-precall-slice-w9c3.md

## Coordination and latest actions
T4 scheduled 14:40Z task is active and owns `scripts/t4_verify_device_world_save_log.py` and its tests; this cycle does not touch them. Previous T4 genuine original CIL [CI42053882300](https://github.com/alwansan/raf/actions/runs/42053882300) confirmed exact private Save(RGD) call sites but argument producer unknown. New experiment investigates immediate pre-call **structural IL operand category** and derived relationship without assuming any source code or phone result. T5 immutable native request b0c4b4c and [CI42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) FAILED at strict water gate before APK; T1 owns water, T5 integration. Neither native workflow nor running T1 job cancelled, touched, or duplicated. Native candidate test remains unproven.

## Next
Compile isolated read-only SHA-verified original IL inspector + fail-closed report controls and evaluate exact source. Never publish raw IL or game type/member names. LOCAL-005 OPEN NOT_READY 0/3.

## Completed evidence — 2026-11-05T15:56:56.362Z

- Scope: independent SHA-pinned original compiled SaveWorld and SaveUser pre-call metadata type provenance. No changes to scheduled T4 JSONL UTC ordering sources or tests, Unity/Android project or original .rgd serializer.
- Source pin: original immutable ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385, exact Assembly-CSharp.dll 3,211,776B SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. Output never includes original game source, type/member/field names, raw IL, file contents or payload.
- Created android-port/Experiments/T4/OriginalRgdPrecallSlice/OriginalRgdPrecallSlice.csproj and Program.cs, source-free verifier scripts/t4_validate_original_rgd_precall_slice.py, source-free negative tests tests/test_t4_validate_original_rgd_precall_slice.py, independent path-scoped workflow .github/workflows/raft-t4-original-rgd-precall-slice.yml.
- [CI42058900699](https://github.com/alwansan/raf/actions/runs/42058900699) **COMPLETED SUCCESS** (source SHA commit 71cd16300ab995f4da4e0a7f0be24d1b90fa61e5). **22/22 source-free safety tests** passed; real .NET8 Mono.Cecil 0.11.5 compiled and inspected correct SHA-authenticated original game DLL. Deliberate altered original DLL SHA was rejected before metadata read.
- **New fact:** immediately before the original compiled SaveWorld direct Save(string,RGD) call, the last non-NOP instruction is a local variable load with an original type **derived from RGD**: `LOCAL_DERIVED_RGD`. For original SaveUser it is a field load of type **derived from RGD**: `FIELD_DERIVED_RGD`. This materially resolves the previous `UNKNOWN_PRECALL_SOURCE` result CI42053882300 at a *static metadata relationship* level. It does NOT prove any one particular instantiated RGD object's value, that the local was initialized or the field assigned, or that Save method executed.
- Last cycle CI42047540260 showed shipped 2,941B StreamingAssets/Data.rgd decodes to a different CLR type than private Save(RGD)'s parameter; still true and not contradicted. No user-generated .rgd, successful game Save, process exit/relaunch, local-host world, Android phone or Unity IL2CPP shown.
- Explored a further **not published/not executed** refinement to inspect SaveWorld's nearest lexical local assignment and SaveUser field store-site count; tool rejected atomic publication by a safety check. That attempted code is not an integrated patch; no new CI, feature or provenance should be claimed for it.
- Published report docs/T4_ORIGINAL_RGD_PRECALL_SLICE_2026-11-05.md, handoff prompt/coordination/discussions/LOCAL-005/20261105T1552Z-T4-derived-RGD-SaveWorld-SaveUser-to-T5.md, independent event prompt/coordination/B_TEAM/events/T4/20261105T1552Z-T4-RGD-derived-precall-22pass.json and completed work record prompt/coordination/work/LOCAL-005/T4-20261105T1544Z-T4-chat-original-rgd-precall-slice-w9c3-precallslice.json.
- Parallel native [CI42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) completed FAILURE at **Authentic water gate strict** during reconstruct, after native request and Unity license preflight. This was not a Save/Load source failure and did NOT deliver APK/OBB/XAPK. T1/T5 own water and native integration; no native Actions dispatched/cancelled by T4. Existing owner-installed APK86 predates this source-only CIL proof, audio/Settings preserved, touch deferred.
- Remaining: trace actual RGD subtype population/initializer outside this immediate compiled callsite or consume a fresh T5 native Android build after water gate resolution, with device playable offline create, actual .rgd save, full app exit, same world reopen. Parent LOCAL-005 OPEN, project NOT_READY 0/3. No false flags, fake RGD, schema/GUID modification.
