# T2 — Source-original Foam CB0 Vector4 constructor and scalar IL provenance

Session: 20261106T1218Z-T2-chat-cb0-setvector-operands-4d79 (origin=chat). Issue WATER-001 **OPEN**, game **NOT_READY**.

## Original source evidence
- Original ZIP2 pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385.
- Original Foam asset owner Raft_Data/sharedassets0.assets 115,978,112 bytes, SHA256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3, raw Foam Shader PathID2420 SHA256 67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1.
- Original Assembly-CSharp.dll 3,211,776 bytes SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. All source and managed bytes authenticated in GitHub Actions private staging; original game assembly never executed.
- Previously [source-authentic exact first-formal CI42210166957](https://github.com/alwansan/raf/actions/runs/42210166957) proved that one of five original CB0 vector parameter names is the actual first string argument of exactly one Unity Material.SetVector(string,Vector4) typed original compiled IL call.
- Previously [typed second-operand CI42217370118](https://github.com/alwansan/raf/actions/runs/42217370118) proved its second argument comes from a newobj opcode; its instance Material receiver remains pre-literal-unknown.

## New typed original constructor proof

Code: android-port/Experiments/T2/FoamCb0ManagedLiterals/Program.cs; isolated CI: .github/workflows/raft-t2-foam-cb0-managed-literals.yml. Registered dedicated scope in prompt/coordination/work/WATER-001/T2-20261106T1218Z-T2-chat-cb0-setvector-operands-4d79-vector-ctor.json prior to modifications.

Within the bounded 24-instruction straight-line private source-name-to-SetVector path, the conservative Cecil interpreter requires exactly one newobj after the source-authentic literal, and checks its declaring type and method are UnityEngine.Vector4 constructor. It records declared constructor formal count/types and the actual IL stack operand-source categories. Multiple newobj, a mismatched constructor or an unsupported/branch path cannot prove a unique typed constructor. Synthetic Cecil tests test real four-scalar numeric pushes, wrong type and multiple constructors, as well as the earlier false-positive branch/nearby-name controls. Only public Unity method type classifications and bounded aggregate counts leave CI.

**Final source-authentic [CI42218712162](https://github.com/alwansan/raf/actions/runs/42218712162)**, job 127895095363, source commit a5293ce4e8057b1b64102350ac4c8f4ac4d9e92e: **SUCCESS**, 11/11 Python source-free tests, Cecil constructor positive/negative selftests, original exact SHA gates, managed scan 19,512 method definitions and 491,490 IL instructions all passed. An initial synthetic multi-constructor fixture had invalid operand stack and failed [42218492467](https://github.com/alwansan/raf/actions/runs/42218492467); fixed by 8233ba2fe7fdc9ccb86a4827dc19cc2aaeb26a13. Subsequent authentic [42218557922](https://github.com/alwansan/raf/actions/runs/42218557922), [42218644533](https://github.com/alwansan/raf/actions/runs/42218644533) and final 42218712162 succeeded.

| Original compiled IL fact | Count/class |
|---|---|
| Source-authentic name direct Material.SetVector(string,Vector4) first-formal links | 1 |
| Unique original UnityEngine.Vector4 constructor producing that same second argument | 1 |
| Constructor formal count | 4 |
| All formal declared types | 4 × System.Single (float) |
| Constructor scalar argument immediate IL origin: instance field load | 3 |
| Constructor scalar argument immediate IL origin: numeric literal | 1 |
| Receiver Material instance provenance before source ldstr | pre_literal_unknown |

This proves the original compiled value is constructed from three field-read float operands and one numeric IL literal, not the field contents, numeric literal value, field owners, runtime reachability, actual receiving Material or Material.shader identity. The entire original 160-byte CB0 upload to pass0 Fragment and pass1 Vertex larger stage layouts remains unverified; previous [source-authentic stage index CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) remains a blocking independent constraint.

No original private field/name/hash/IL/game DLL/shader byte sequence or literal number disclosed. No game shader/Meta/GUID/assets, native Unity, APK, Settings, FMOD, input or world/save changes.

**Next:** trace authenticated original instance-field value producers and pre-ldstr Material receiver, then match genuine Foam Material Shader identity and CB0 host upload size and timing before any Unity2021 import/Adreno device claims. WATER-001 OPEN.
