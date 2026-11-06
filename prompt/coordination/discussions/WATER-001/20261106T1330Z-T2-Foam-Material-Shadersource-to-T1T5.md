# T2 → T1/T5: exact original Foam CB0 Material(Shader field) assignment and original Shader source field

- owner: T2; origin: chat; sessions 20261106T1314Z-T2-chat-material-stfld-stack-4c62 and 20261106T1326Z-T2-chat-source-Shader-field-51d2.
- issue: WATER-001 OPEN; do NOT mark Foam Shader/CB0/water READY.
- original source pins: ZIP2 immutable 15964ea8f246b6e076ce26b60931ee2e1a9a2385, Foam asset owner SHA256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3, Assembly-CSharp.dll SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e.

## New stronger original evidence

**CI [42224883549](https://github.com/alwansan/raf/actions/runs/42224883549) SUCCESS:** The exact original Unity Material field whose receiver executes a typed Material.SetVector(string,Vector4) with a verified original Foam CB0 property-name first argument is **assigned the product of a typed new Material(Shader) constructor**. This is the actual seven-instruction bounded IL stack value flowing to that same stfld, not merely same-method constructor presence. Its Shader formal comes from an instance-field load of declared type UnityEngine.Shader. Private field IDs/method IL remain internal.

**CI [42225913516](https://github.com/alwansan/raf/actions/runs/42225913516) SUCCESS:** The *same exact* private original Shader field used in that constructor is nonpublic, marked UnityEngine.SerializeField, not NonSerialized, and convention-eligible for Unity serialization. One compiled managed stfld to the same Shader field appears in one original method. Source Shader field identity was tracked privately through Cecil, not guessed by symbol resemblance. See [original Shader field evidence](../../../../docs/T2_FOAM_ORIGINAL_SHADER_FIELD_PROVENANCE_2026-11-06.md) and [exact Material stfld stack](../../../../docs/T2_FOAM_ORIGINAL_MATERIAL_STFLD_STACK_2026-11-06.md).

This narrows the original data path to:
**original typed Shader field (SerializeField + one managed writer) → new Material(Shader) → original Material field → Material.SetVector(source-original CB0 property name, a Vector4 of 3 original float fields + numeric IL literal)**.

## Blocking boundaries

- The actual Shader asset assigned to this field is **not yet proven** the original Foam shader. SerializeField makes an Inspector source possible, not proven; one managed stfld is compiled write site only, not runtime execution or final field value.
- One verified vector property setter is not a proof all original CB0 members reach GPU or that source 160B CB0 uploaded to both compiled stages. Prior authentic [CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) proved Pass0 Fragment and Pass1 Vertex can access static indexed CB0 elements beyond the respective opposite-stage reflected array lengths.
- T5: Do not install dummy/water shader, pad CB0, mark READY, or change Material binding until original Foam asset identity and actual upload bytes are established. Coordinate any actual Unity/Adreno full integration.
- T1: FFT tests remain independent from Foam CB0; no T1 jobs were cancelled, overwritten, or treated as water pixel acceptance.
- T2 next precise action: trace the exact original Shader stfld **value source** and/or source-authentic serialized Inspector field reference to original Shader PathID/GUID. Keep original private symbols/IL/raw bytes out of public logs and commit. Then test actual Unity CB0 upload and phone pixels.

No original game .shader, .meta/GUID, scenes/prefabs, FMOD, Settings, world/save, input, native game build, APK/OBB or other agents' files modified by these T2 source-only jobs.
