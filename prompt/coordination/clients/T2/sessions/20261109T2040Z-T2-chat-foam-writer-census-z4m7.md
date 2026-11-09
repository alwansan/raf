# T2 | SHA-original Foam pass0 destination CIL field-store census and pass1 writer co-location

- session_id: `20261109T2040Z-T2-chat-foam-writer-census-z4m7`, origin: **chat**
- branch: `feature/android-native-port` (**ONLY writable branch**)
- base_sha: `c85b46697df05eb5ba1e75e2c34295a44440a0ad`
- prior sessions: `20261109T2020Z-T2-chat-foam-onehop-return-r8c5`; `20261109T2002Z-T2-chat-foam-declared-field-flow-c9n4`
- work scope reserved **before editing**: `prompt/coordination/work/WATER-001/20261109T2040Z-T2-chat-foam-writer-census-z4m7.json`; commit `7410282dc45bb9d9b7e0afabf6303d697a19ccf5`. Follow-up declared before extending original pass1-site co-location: commit `e85df17653b3d88d7366d0d93faed6ad74322ed9`.
- experiment_key: `original-Foam-pass0-managed-destination-FieldDefinition-CIL-store-census-plus-pass0-pass1-lexical-colocation-v1`; resource `T2-original-FoamBlitOriginalProducers-Cecil-source-only`
- workfiles: `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs`, `scripts/t2_foam_original_blit_report.py`, `tests/test_t2_foam_original_blit_report.py`, own session/work/experiment/event and own safe report. T1 FFT, T3 shader, T4 input, T5 XAPK/mini code and assets untouched.
- baseline: authenticated [original Cecil CI42693501006](https://github.com/alwansan/raf/actions/runs/42693501006) PASS, 21 source-free Python tests, `field_no_match_with_null` both direct and one-hop, not a same-object or device proof.

## Original independently verified new result

Commit `a3a63adc197271cc798de3c7a0bbe06bf3617ecf`: SHA-pinned original managed IL exact **declared pass0 RenderTexture field** `stfld`/`stsfld` writer census (zero/one/multiple **resolved** direct stores), whether writers share a method with pass0 Foam Blit, and whether authenticated two Foam Blit sites reside in the same lexical managed method. Privacy-safe finite categories only; no raw method/field names, tokens, paths, instruction bytes, game assets or original shader revealed. Synthetic C# fixtures exercise zero, one, many, nonmatching unsaved RID0 field writes and separate/same Blit method structure. Strict Python schema and negative privacy tests guard output.

Authentic [CI42695789057](https://github.com/alwansan/raf/actions/runs/42695789057), source `a3a63adc`, job `129427157145`, completed **SUCCESS**: **24/24** Python tests; `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`, original ZIP2 SHA-authenticated Assembly 3211776 bytes and owner 115978112 bytes, purge and safe export.

```text
T2_FOAM_PASS0_DEST_FIELD_CIL_STORE_CLASS multiple_resolved_direct_stores
T2_FOAM_PASS0_DEST_FIELD_CIL_STORE_PLACEMENT stores_only_in_other_methods
T2_FOAM_PASS0_DEST_FIELD_SINGLE_STORE_ADJACENT store_predecessor_not_unique
T2_FOAM_PASS0_PASS1_BLIT_LEXICAL_RELATION blit_sites_in_distinct_methods
```

**Interpretation**: original exact pass0 RenderTexture destination declared field has multiple explicitly resolved managed CIL store instruction sites, **all outside** method containing pass0 Foam Blit. Pass0 and pass1 Foam Blit sites occur in **distinct** methods. No claim of executed writes, same frame, initialized resource, receiver alias, actual texture identity or Adreno phone graphics.

## Further distinct original pass1 site refinement

Check whether direct stores to this exact pass0 declared field are located in the **unique managed method containing original pass1 Foam Blit**, and if so whether the store opcode is lexically before, after, or both sides of pass1 call. This distinguishes an immediate pass1 caller alias hypothesis from lifecycle writers in other methods. C#/Python schema commit `57b8f10be4f91af7b37b0b8eeec73c7e9b775b0c` added strictly lexical, fail-closed classifications and tests. Its first [CI42696515826](https://github.com/alwansan/raf/actions/runs/42696515826) FAILED at a synthetic Python fixture expecting the *later* traced-destination error while a prior direct/one-hop return-relation consistency gate correctly failed first. No original evidence from failed run. The fixture-only correction is commit `fbe24922a60b895f88fd1ef0e4a2ed15a67a6a2d`. The new [CI42696649931](https://github.com/alwansan/raf/actions/runs/42696649931) was in-progress when this checkpoint was written. **Do not claim verified pass1 writer relation until its authentic original stage succeeds**.

Separately, other agents' workflows are active, including T5-owned [native full XAPK CI42696228231](https://github.com/alwansan/raf/actions/runs/42696228231). Do not cancel, dispatch another full build, or interfere. WATER-001 remains OPEN / NOT_READY 0/3. Next: review CI result, preserve privacy, record finite pass1-field writer tag; then decide whether actual runtime alias still needs original per-frame tracing or Android test.

## Final authenticated refinement — 2026-11-09T20:55Z

The SHA-original second-stage [CI42696649931](https://github.com/alwansan/raf/actions/runs/42696649931), final T2 code `fbe24922a60b895f88fd1ef0e4a2ed15a67a6a2d`, job `129430174641`, **COMPLETED SUCCESS** after the fixture-only correction. **26/26** source-free Python tests, `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`, original ZIP2 authenticated DLL **3211776** bytes and shader owner **115978112** bytes, safe-only report and purge all PASS.

```text
T2_FOAM_CROSSPASS_DECLARED_FIELD_RETURN_RELATION field_no_match_with_null
T2_FOAM_CROSSPASS_ONEHOP_FIELD_RETURN_RELATION field_no_match_with_null
T2_FOAM_PASS0_DEST_FIELD_CIL_STORE_CLASS multiple_resolved_direct_stores
T2_FOAM_PASS0_DEST_FIELD_CIL_STORE_PLACEMENT stores_only_in_other_methods
T2_FOAM_PASS0_DEST_FIELD_SINGLE_STORE_ADJACENT store_predecessor_not_unique
T2_FOAM_PASS0_PASS1_BLIT_LEXICAL_RELATION blit_sites_in_distinct_methods
T2_FOAM_PASS0_DEST_FIELD_WRITES_VS_PASS1_BLIT_IL pass1_method_no_direct_field_store
```

**New conclusion:** The exact *declared pass0 Foam RenderTexture destination field* has multiple resolved direct managed CIL stores in private original Assembly-CSharp, all outside the pass0 Blit method, AND the separate pass1 Blit method has **no direct CIL store to that exact field**. Hence the observed explicit CIL store sites for this original field are outside **both** Blit methods. These are conservative lexical/source structure facts, not proof of executed stores, actual field values, same-frame ordering, same receiver, image heap-object alias, ShaderLab/CB0 or Android water pixels. Prior pass1 original null literal category remains a path family and is not proof runtime null.

Safe report updated at `docs/T2_FOAM_ORIGINAL_RETURN_VALUE_FLOW_2026-11-09.md`, commit `18b79ba2d6736353670c159cdd0a08c8e1aa740b`. Work scope `prompt/coordination/work/WATER-001/20261109T2040Z-T2-chat-foam-writer-census-z4m7.json` marked `completed` with results at commit `40995753a4b6816d49c821f10ec46e9ed670bff4`. Experiment archive `prompt/coordination/experiments/T2/20261109T2040Z-T2-chat-foam-writer-census-z4m7.json` commit `8c69f6f0b5ec8d811e79845a914baf92db17f997`. T2 canonical event with explicit `event_id`, `owner`, `at`, `type` at `prompt/coordination/B_TEAM/events/T2/20261109T2040Z-T2-chat-foam-writer-census-z4m7.json`, commit `9503570ad43758407640cee588c28af1d001f733`.

No modifications to owner original raw game files, Unity scenes, shaders, T1 FFT, T3 graphics, T4 mouse, T5 mini/full APK tools, CL user logs or other workers' sessions. No T2 APK/XAPK requested; T5-owned native full build [CI42696228231](https://github.com/alwansan/raf/actions/runs/42696228231) was in progress during this cycle and was left untouched.

### Handoff

**T2 narrow scope completed**, WATER-001 overall **OPEN / NOT_READY 0/3**. Next genuinely distinct source-private experiment: inspect exact *writer methods* and their bounded RHS/receiver/call edges, distinguishing managed initialization/rebind and direct field-to-field copy from opaque Unity/engine sources. Report only finite categories and keep actual field names, tokens, IL and original resource bytes inside private runner. Do not infer dynamic alias or Android rendering from declared CIL and do not repeat unchanged SHA-original CI. Existing canonical summary blockers in other workers' inherited events must be owner-fixed; do not edit other worker ledgers to make shared summary green.
