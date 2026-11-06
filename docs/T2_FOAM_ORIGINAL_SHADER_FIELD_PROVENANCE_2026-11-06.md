# T2 — Original Foam CB0: exact Shader field supplying the Material constructor

Session: 20261106T1326Z-T2-chat-source-Shader-field-51d2; origin: chat. Issue: WATER-001 OPEN / NOT_READY.

## Original authenticity

- Original ZIP2 SHA: 15964ea8f246b6e076ce26b60931ee2e1a9a2385.
- Original Foam asset owner Raft_Data/sharedassets0.assets: 115978112 bytes, SHA256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3.
- Original Assembly-CSharp.dll: 3211776 bytes, SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. The SHA checks occur privately inside CI; original game code was never executed or published.
- Prior [original exact Material store CI42224883549](https://github.com/alwansan/raf/actions/runs/42224883549) proved that the source-original named CB0 receiver Material field gets the product of a typed Material(Shader) constructor, and that its Shader formal is a UnityEngine.Shader instance-field load. Foam asset identity and runtime CB0 upload remained unknown.

## New question and method

Work was registered before changes at prompt/coordination/work/WATER-001/T2-20261106T1326Z-T2-chat-source-Shader-field-51d2.json. This new experiment retains the exact original Shader FieldReference in process memory only and inspects that *same field identity* in the original SHA-authenticated managed DLL. No names, metadata tokens, original shader bytes, source IL or original field hashes are serialized or logged.

A second source scan counts compiled stfld instructions to that field and the number of managed methods containing those writes. Cecil also resolves the exact FieldDefinition and checks public/nonpublic declaration, presence of UnityEngine.SerializeField, the NonSerialized flag, and basic Unity serialization eligibility (nonstatic, nonreadonly, not NonSerialized, public or SerializeField, UnityEngine.Shader type). These are *field declaration properties*, not actual scene/instance values. Public source-free Cecil controls reject a wrong-typed field and verify the exact Shader field is the actual typed Material constructor operand.

[Definitive original CI42225913516](https://github.com/alwansan/raf/actions/runs/42225913516) **SUCCESS**, job 127919252873, source SHA 2e4e4112973b3c29db9b34db233b5f9089a4505d, original source and DLL SHA gates passed. 11/11 source-free Python tests and Cecil positive/negative tests passed, with 19,512 managed method definitions and 491,490 original IL instructions examined.

## Genuine original evidence

| Original source-backed declaration/writer observation | Result |
|---|---:|
| Exact Shader instance field feeding Material(Shader) | 1 |
| Field definitions resolved in original managed DLL | 1 |
| Public original field | 0 |
| Explicit UnityEngine.SerializeField attribute | 1 |
| NonSerialized attribute or flag | 0 |
| Convention-eligible for Unity instance serialization | 1 |
| Original managed stfld write instructions to same exact Shader field | 1 |
| Original managed methods containing this field write | 1 |
| Original Shader object/asset reference is actual Foam | NOT VERIFIED |
| Runtime value / CB0 upload / actual Android water | NOT VERIFIED |

The original nonpublic Shader field is marked SerializeField, is eligible for Unity object serialization by its declared attributes, and also has exactly one compiled managed writer instruction. Consequently, it has both a possible serialized Inspector value and a managed write path. Neither proves what Shader object it holds at runtime or that it is the original Foam shader.

## Next distinct proof

Authenticate the actual value popped by the exact Shader stfld via bounded IL stack analysis. If original Unity scene/prefab data are used, compare the serialized Shader reference by immutable source asset identity rather than merely matching a name. Do not treat SerializeField or a writer site as a working shader binding. The original two-pass CB0 stage-specific larger array loads remain unresolved as upload requirements, and no Android GPU pixel proof exists.

No original .shader, .meta/GUID, Unity scenes/prefabs, audio, Settings, touch, world/save, native workflow or APK/OBB changed by T2. WATER-001 remains OPEN.
