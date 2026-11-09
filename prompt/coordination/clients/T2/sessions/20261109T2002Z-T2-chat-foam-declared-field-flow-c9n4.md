# T2 — SHA-original Foam crosspass declared-field return provenance

- session_id: `20261109T2002Z-T2-chat-foam-declared-field-flow-c9n4`
- origin: `chat`
- base_sha: `be69f74c1f4d902e7c731e4a17cc4bd3c7609ff0`
- resumed_from_sessions: `20261109T1946Z-T2-chat-foam-equality-predicate-m4q9`, `20261109T1916Z-T2-chat-foam-constant-branch-p8v6`
- issue: WATER-001 OPEN / full game NOT_READY 0/3
- work scope reserved **before source edits** at `prompt/coordination/work/WATER-001/20261109T2002Z-T2-chat-foam-declared-field-flow-c9n4.json`; commit `f5ad62764d380a0b20280cffe060213857e82689` and report-schema expansion recorded in `22086153464d7ed46e61a2abd832b2e13ca9d94b`.
- experiment_key: `foam-original-managed-crosspass-destination-field-token-vs-pass1-return-value-flow-null-opaque-20261109-v1`
- resource_key: `T2-original-FoamBlitOriginalProducers-Cecil-source-only`
- modified source: `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs`, `scripts/t2_foam_original_blit_report.py`, `tests/test_t2_foam_original_blit_report.py` (T2-only).
- other agents: T1 FFT, T3 shader, T4 mouse, T5 shared Mini / packaging untouched. No Unity, APK, XAPK, original shader, private IL/data, or other worker files modified.

## Inherited, corroborated baseline

Authenticated [CI42686782993](https://github.com/alwansan/raf/actions/runs/42686782993) proved finite CIL constant-equality guard and 17 source-free Python tests. Original pass0 source is RenderTexture typed field and pass1 source is Texture typed call-return. Pass1 callee original conservatively reachable flow `value_mixed_with_explicit_null_literal`, **not** actual runtime null. No same-instance crosspass identity or original Android water pixels proven.

## Distinct hypothesis and implementation

The original private managed CIL can sometimes expose a *declared FieldDefinition token* common to pass0 Blit destination and one or more conservatively reachable field-origin return paths in the pass1 Texture callee. This would be narrower than previous type-only evidence but **still would not prove** matching receivers, intervening writes, matched frame, same heap RenderTexture instance, or GPU pixel parity. Conversely absence of a direct field-origin token cannot exclude indirect/nested aliases.

First source commit `c780271d7689e2b0ce8327183b590aef864db3b0` adds bounded pass0 destination CIL stack tracking (depth=2), original pass1 callee return provenance across CFG/local joins with private token comparison, finite public-safe relation tags and explicit `original_crosspass_destination_to_source_identity_proven=false`. Cecil RID0 zero-token comparison was hardened to use reference identity or nonzero unique original tokens to prevent false equivalence for synthetic in-memory fields.

Initial [CI42689721185](https://github.com/alwansan/raf/actions/runs/42689721185) **FAILED during strict JSON report validation** because new fields had not yet been added to Python's strict allowlist; C# source compilation succeeded and real analysis ran, but original diagnostic is NOT yet claimed validated. No CI re-dispatch or duplicate old test.

Atomic follow-up `6f09eddcf788050035a767d21999c75a6ebebdc1` updated *three T2 files together* with exact-source selftests for same vs different declared field tokens, literal-null return, unknown conditional field/null path, and field mention popped before return. Python strict JSON permits only finite field status labels and forces **no heap identity claim** even if field tokens match. Real original authenticated [CI42690309016](https://github.com/alwansan/raf/actions/runs/42690309016) **in_progress** when checkpoint saved. Auto unrelated platform [CI42690309050](https://github.com/alwansan/raf/actions/runs/42690309050) also running; no cancellation.

## Decision and handoff

Check final job logs for `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`, 19+ Python checks, SHA-verified original DLL 3,211,776 bytes and shader owner 115,978,112 bytes, safe scratch purge and `T2_FOAM_CROSSPASS_DECLARED_FIELD_RETURN_RELATION <finite tag>`. A positive token match means only matching original **declared field** provenance category; it must **not** be presented as proved object identity or restored water. If validation fails, fix only T2 report/fixture contracts after inspecting precise logs, and rerun on changed code. Document original result in safe report and independent experiment/event. Source-original result cannot close WATER-001 or justify XAPK without separate team decision and device proof.

Latest owner CL/test shared-20261108-232759-468049775 T2-01..04 synthetic GLES FBO controls PASS, unrelated to authentic Foam pixel acceptance. External canonical summary blocker T3-owned missing event_id retained untouched.

## Completed authentic result and boundaries — 2026-11-09T20:13Z

- [CI42690309016](https://github.com/alwansan/raf/actions/runs/42690309016), SHA `6f09eddcf788050035a767d21999c75a6ebebdc1`, job `129408001123`: **COMPLETED SUCCESS**. 19/19 Python source-free privacy tests, C# Cecil synthetic selftest PASS, original DLL 3211776 and Shader owner 115978112 bytes authenticated, original private data purged before safe output. Original safe tag: **`T2_FOAM_CROSSPASS_DECLARED_FIELD_RETURN_RELATION field_no_match_with_null`**. Pass1 flow still `value_mixed_with_explicit_null_literal`; pass0 is RenderTexture field, pass1 source is Texture-returning call.
- [Platform CI42690309050](https://github.com/alwansan/raf/actions/runs/42690309050) also **SUCCESS** on that SHA; not a Unity/Android Foam pixel test.
- Work marked completed at `prompt/coordination/work/WATER-001/20261109T2002Z-T2-chat-foam-declared-field-flow-c9n4.json` (commit `d4b36db725c2bb75be72a6cd0724fc774125d209`). Safe report updated at `docs/T2_FOAM_ORIGINAL_RETURN_VALUE_FLOW_2026-11-09.md` (commit `5bef3f2cffb94aa6d30d9d9f08219e47ea9135ba`).
- Important distinction: **No DIRECT original pass1 callee return from the same declared field token as pass0 Blit destination** in the analyzed CFG. This is NOT evidence that runtime textures differ. Separate fields and distinct receiver objects can reference the same heap texture; nested getters/calls and intervening writes remain opaque; an explicit null category is not evidence of executed phone null. `original_crosspass_destination_to_source_identity_proven=false`, original ShaderLab, CB0, Adreno water pixels unverified.
- The initial strict-report mismatch was rectified and documented; no duplicate unchanged CI and no full game/mini APK or owner phone action requested.
- This narrow T2 scope **completed**. WATER-001 overall OPEN / NOT_READY 0/3. Next distinct source-private question: inspect actual receiver and indirect alias/call chain between original pass0 destination and pass1 callee return, or explicitly establish static undecidability. Preserve other workers' scopes.
