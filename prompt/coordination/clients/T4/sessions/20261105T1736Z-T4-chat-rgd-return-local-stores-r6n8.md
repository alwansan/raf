# T4 chat — exact original world RGD factory returned-local write provenance

- session_id: 20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8
- origin: chat
- status: completed
- base_sha: 72e59de980ca8803e08e7ad1ad9edb9b35c54313
- work: prompt/coordination/work/LOCAL-005/T4-20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8-factory-return-local-stores.json
- experiment_key: T4-original-ZIP2-15964ea8-SHA0a6f-zeroarg-SaveAndLoad-derivedRGD-factory-single-ret-local-stloc-value-categories-v1
- resource_key: none
- resumed_from_sessions: 20261105T1713Z-T4-chat-original-rgd-return-sites-j7q4; 20261105T1640Z-T4-scheduled-r8k2

## Source-real baseline
CI42072718216 SUCCESS 50/50 at b1203fb30fa91eab56ec0507e720574d7aa75ecf. Exact original ZIP2 original Assembly-CSharp.dll 3,211,776B SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. A genuine zero-argument SaveAndLoad instance method returning derived-RGD has one compiled ret immediately following a derived-RGD typed local, 2 RGD-derived locals, 1 derived constructor, 1 return-typed call, 34 conditional branches, 10 ldnull loads. Not SSA/control-flow/runtime data. SaveUser original field 1+2 write contexts separately.

## Scope
Inspect original factory local slot loaded just before ret, count direct earlier lexical stloc for that exact slot, categorize immediate preceding instruction (null literal, derived-RGD constructor, call, local, field, other) and optionally bounded branch-target ambiguity, without disclosing private details or asserting execution. Strict fail-closed synthetic tests; no changes to native Unity project or save serializer. T4 scheduled 1640Z JSONL overflow audit is distinct; T5 native 42058825739 Unity import at last verified check. LOCAL-005 OPEN NOT_READY 0/3.

## Completed source-authentic evidence — 2026-11-05T17:41Z

- [CI42076494669](https://github.com/alwansan/raf/actions/runs/42076494669) **COMPLETED SUCCESS** on immutable source SHA `961e637a5236ed900c179fe41b96e5f65a26084b`, **67/67 source-free controls**, .NET8 Mono.Cecil compiled, original SHA/size authenticated and changed-source SHA rejected. Exact original owner ZIP2 `Assembly-CSharp.dll` 3,211,776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- **New original CIL fact:** exact zeroarg SaveAndLoad factory returned local, loaded before the one lexical `ret`, has **one direct preceding `stloc`**, and immediate previous instruction is **`newobj` for RGD-derived type**. `factory_return_local_nearest_lexical_store_source=DERIVED_CONSTRUCTOR`. No direct original lexical `stloc` to this returned local from a null literal, derived call, other local, field or unresolved source. Prior 34 conditional branches and 10 `ldnull` loads still exist elsewhere in method.
- This is **instruction adjacency and lexical store count only**, **not executed control flow, transitive stack/SSA, actual returned object identity or non-null**, and not genuine world save or Android phone. Original game Save/Load/RGD bytes and Unity never executed. No original private IL/method/type/field names or payload uploaded.
- Changed only `android-port/Experiments/T4/OriginalRgdInitContext/Program.cs` `56febeb463799881dc561c609f3b55a59faf825a`, `scripts/t4_validate_original_rgd_init_context.py` `a7366262b312bbfb2b92934fbd82c61a944871f9` then `961e637a5236ed900c179fe41b96e5f65a26084b` (source-free declaration-order fix), and `tests/test_t4_validate_original_rgd_init_context.py` `c4b0a987a7c367d31ca6f23766d34dd18b1d6353`. Added 17 original-free adversarial controls, 50→67; used existing narrow CI without Unity/native build.
- Transitional CI42076168719, CI42076257372, CI42076369962 failed before source/test/report patches matched. Last failure was Python NameError from referencing FACTORY_RETURN_LOCAL_FIELDS before its declaration, fixed without relaxing SHA/authenticity/device proof guards. Matched final CI42076494669 passed.
- Report `docs/T4_ORIGINAL_RGD_RETURN_LOCAL_STORES_2026-11-05.md`, T5 handoff `prompt/coordination/discussions/LOCAL-005/20261105T1740Z-T4-original-return-local-stores-to-T5.md`, event `prompt/coordination/B_TEAM/events/T4/20261105T1740Z-T4-RGD-return-local-constructor-67pass.json`, independent work record `prompt/coordination/work/LOCAL-005/T4-20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8-factory-return-local-stores.json` completed.
- T4 scheduled 1640Z JSONL source/evidence overflow audit and its owned files remain unchanged. T5 original native Unity import run42058825739 not cancelled or duplicated. Audio/Settings unchanged, touch deferred, original host/serializer/.rgd compatibility and .meta/GUID preserved.
- Next prioritize actual T5 signed APK/OBB/XAPK status and owner device test for playable offline world, authentic .rgd save and full-exit same-world reopen. If native evidence implicates factory, investigate reachable original constructor path, not fake flags. **LOCAL-005 OPEN, NOT_READY 0/3.**
