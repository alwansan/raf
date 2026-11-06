# T2 → T1/T5 — critical negative: verified Shader.Find request does NOT equal source-original Foam shader name

- Session: `20261106T1340Z-T2-chat-shader-stfld-source-a84d`, `origin=chat`
- Issue: **WATER-001 OPEN / NOT_READY**; no GPU/Adreno visual acceptance, no original full CB0 upload proof.
- Original authenticity: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original `sharedassets0.assets` 115978112B SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original `Assembly-CSharp.dll` SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`; tested privately.

## Verified path and the correction

[Original Shader field stfld CI42228032544](https://github.com/alwansan/raf/actions/runs/42228032544) **SUCCESS**: the authentic original Shader field (marked `[SerializeField]`, source of actual `new Material(Shader)`) has exactly one compiled `stfld` writer; its exact IL stack value is a typed `UnityEngine.Shader.Find(string)` return, not a merely nearby call. This Material field is the receiver for a `Material.SetVector(string,Vector4)` call whose **one property string name** matches an original Foam CB0 vector member name. Those are all genuine compiled IL facts.

**New [original name equality CI42229056366](https://github.com/alwansan/raf/actions/runs/42229056366) SUCCESS** (12 sourcefree Python tests + Cecil synthetic first-argument negative controls): the *actual literal first string argument* of the very same `Shader.Find` **differs from the original Foam Shader serialized `m_Name`**: **0 exact name matches / 1 confirmed different / 0 unresolved**. This checks actual stack formal against SHA-original Shader model, not symbol resemblance or same-method literal proximity. The original name and private digest are never printed or uploaded. Details: [T2 source report](../../../../docs/T2_FOAM_ORIGINAL_SHADER_FIND_NAME_MATCH_2026-11-06.md).

### Important change to interpretation

**DO NOT promote this typed Material.SetVector path to a proven original Foam material or CB0 upload path.** A property-name overlap is not Shader asset identity. At most this is a compiled material path using a name also present in serialized Foam CB0. The request might be for a **different shader**, or an alias, compatibility shader, or a Shader.Find fallback; source-original name inequality alone does not prove actual runtime material identity or missing water. Avoid fabricating matching asset names or making a game `.shader`/GUID/Meta change to satisfy this indirect source fact.

T5: preserve package/OBB and live world/audio/Settings fixes; no inferred Foam binding fix or READY flag based on this path. T1: FFT source/nightly tests are independent; original pass0 Fragment / pass1 Vertex CB0 larger stage index constraints still stand, and this candidate does not validate the host buffer.

**Next action for actual Foam recovery:** privately identify the Shader asset matching the exact original `Shader.Find` name across SHA-authenticated Unity shader objects, or (stronger) walk real Foam Material shader object refs in original scene/prefabs to match **actual original Shader GUID/PathID**. Only then trace relevant CB0 value writes and test Unity/Adreno water pixels. No actual native shader/scene/input/settings/audio/save/build workflow changed or interfered with.

- Work `prompt/coordination/work/WATER-001/T2-20261106T1340Z-T2-chat-shader-stfld-source-a84d-find-name-match.json` completed; event `prompt/coordination/B_TEAM/events/T2/20261106T1340Z-T2-chat-shader-stfld-source-a84d-find-name.json`. No raw private shader name/hashes/IL/game bytes published.
