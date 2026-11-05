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
