# T2 chat — exact original Foam RenderTexture[] backing-field metadata

- session_id: 20261105T1434Z-T2-chat-rendertexture-serialization-93ad; origin=chat; issue=WATER-001; status=active
- base_sha: e8aea886cbd0ce0667eddf32f1b0ebd0bb2da23b
- resumed_from_sessions: 20261105T1408Z-T2-chat-foam-four-i4-uniqueness-4e7a, 20261105T1418Z-T2-scheduled-a91c, 20261105T1323Z-T2-chat-index-origin-5c42
- work reserved before edit: prompt/coordination/work/WATER-001/T2-20261105T1434Z-T2-chat-rendertexture-serialization-93ad-metadata.json, commit 7e07c8c28adbca289df9a2f32ffa6c788a364088
- hypothesis: exact compiled Foam RenderTexture[] backing FieldDefinition metadata public/SerializeField/NonSerialized/static/initonly can constrain Unity serialization as an initialization path. Does not prove scene/prefab content or runtime execution. Original DLL SHA pinned.
- experiment_key: T2|zip2-15964ea8|original-dll-0a6f0527|exact-RenderTexture-array-managed-fielddef-serialized-attributes|v1
- intended files: android-port/Experiments/T2/FoamRuntimeStringBridge/FoamFieldSerializationMetadata.cs, android-port/Experiments/T2/FoamRuntimeStringBridge/Program.cs, .github/workflows/raft-t2-foam-managed-literals.yml and own session/work. No game shader/audio/Settings/input edits.
- coordination: T1 Unity Vulkan run42046073285 in progress, no T2 managed run; scheduled T2 JSON producer tests independent.
- first create session attempt hit safe 409 concurrent head advancement. No force or overwrite. Retrying same scoped file from refreshed HEAD.
- next_step: implement fail-closed synthetic Cecil fixture, original SHA-private CI, safe only numeric/boolean result and handoff. WATER-001 OPEN, NOT_READY 0/3.

## Test source and CI checkpoint

- source commit [9b01015a](https://github.com/alwansan/raf/commit/9b01015a9e3aa47718d9b102d31bd8d39d52b638) published by HEAD lease with three owned paths only: new `FoamFieldSerializationMetadata.cs`, `Program.cs`, and `.github/workflows/raft-t2-foam-managed-literals.yml`.
- Exact source-managed Cecil field definition match; public synthetic negatives cover public, private, explicit SerializeField, NonSerialized, static, readonly, missing field. A field modifier-eligible flag is **not** a verified scene or prefab value, so emitted evidence explicitly rejects actual runtime/array contents. No private symbols/indices printed.
- [Original SHA-pinned CI42046650774](https://github.com/alwansan/raf/actions/runs/42046650774) `in_progress` at checkpoint. Own workflow emits only safe metadata booleans / owner direct-base category and previous private four i4 distinct/sign aggregate to job log for independently verifiable values.
- Do not claim source metadata or exact i4 uniqueness until run succeeds and safe output read. T1/T3/T4/T5 paths unchanged, no Unity native build launched by T2.

## Verified original managed source result

- [CI42046650774](https://github.com/alwansan/raf/actions/runs/42046650774) **COMPLETED SUCCESS** (job `127311299326`) on original ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, SHA-authenticated managed DLL `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e` (3,211,776B). All source-free `SerializeField` public/private/NonSerialized/static/readonly/identity negative controls, source exact getter, original four caller trace, cleanup, privacy and original CI gates passed.
- Original exact `UnityEngine.RenderTexture[]` backing field: **one** matched original FieldDefinition, **private**, **no UnityEngine.SerializeField attribute**, **no NonSerialized marker**, **not static**, **not initonly**, `EligibleByFieldModifiersOnly=false`, `OwnerDirectBaseTypeCategory=not_proven_unity_owner_by_direct_base`. These are **compiled metadata facts, not proof of a scene/prefab field value or runtime initialization**.
- Independently read source-private values as safe numeric aggregates from the completed job log `T2_FOAM_FIELD_METADATA_SAFE`: **four** decoded original direct `ldc.i4` values, **four distinct**, **all nonnegative**. Actual original int values were never published, hashes avoided, and no runtime array length/index-inbounds claim.
- Safe-only artifact ID `13424871676`, ZIP SHA256 `4fada83b5337702252c61fdb121350418d99db4fb97dc6f0218cbf50e1269c7f` (1923B). Source commit [9b01015a](https://github.com/alwansan/raf/commit/9b01015a9e3aa47718d9b102d31bd8d39d52b638). Original source/temp hashed names/binaries cleaned before artifact.
- **Conclusion:** a private non-[SerializeField] getter backing array lacks ordinary Unity field-modifier serialization eligibility; this narrows potential initialization, but does **not** prove no serialized values from other mechanisms, nor no indirect population/native plugin/runtime writes. The prior single `stfld ldnull` remains a compiled clear site, not evidence of execution. WATER-001 OPEN, NOT_READY 0/3.
- Next T2: trace original managed owning type ancestry, array-field reads and element-write sites; do not infer array bounds or shader pixels without genuine Unity/device evidence.
