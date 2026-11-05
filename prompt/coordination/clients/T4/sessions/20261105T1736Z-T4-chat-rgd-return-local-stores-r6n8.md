# T4 chat — exact original world RGD factory returned-local write provenance

- session_id: 20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8
- origin: chat
- status: active
- base_sha: 72e59de980ca8803e08e7ad1ad9edb9b35c54313
- work: prompt/coordination/work/LOCAL-005/T4-20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8-factory-return-local-stores.json
- experiment_key: T4-original-ZIP2-15964ea8-SHA0a6f-zeroarg-SaveAndLoad-derivedRGD-factory-single-ret-local-stloc-value-categories-v1
- resource_key: none
- resumed_from_sessions: 20261105T1713Z-T4-chat-original-rgd-return-sites-j7q4; 20261105T1640Z-T4-scheduled-r8k2

## Source-real baseline
CI42072718216 SUCCESS 50/50 at b1203fb30fa91eab56ec0507e720574d7aa75ecf. Exact original ZIP2 original Assembly-CSharp.dll 3,211,776B SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. A genuine zero-argument SaveAndLoad instance method returning derived-RGD has one compiled ret immediately following a derived-RGD typed local, 2 RGD-derived locals, 1 derived constructor, 1 return-typed call, 34 conditional branches, 10 ldnull loads. Not SSA/control-flow/runtime data. SaveUser original field 1+2 write contexts separately.

## Scope
Inspect original factory local slot loaded just before ret, count direct earlier lexical stloc for that exact slot, categorize immediate preceding instruction (null literal, derived-RGD constructor, call, local, field, other) and optionally bounded branch-target ambiguity, without disclosing private details or asserting execution. Strict fail-closed synthetic tests; no changes to native Unity project or save serializer. T4 scheduled 1640Z JSONL overflow audit is distinct; T5 native 42058825739 Unity import at last verified check. LOCAL-005 OPEN NOT_READY 0/3.
