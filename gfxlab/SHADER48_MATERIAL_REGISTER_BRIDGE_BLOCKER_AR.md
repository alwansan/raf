# GFX-LAB — عائق الربط بين خصائص Material وShader48 الأصلي
**2026-11-10 | GFX-LAB | فرع experiment/android-graphics-rootcause | ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385**

## مخطط الأدلة
```text
الأصل الموثق:
Renderer → Mesh → Material21 → Saved TexEnv name → Texture2D original
                                    │
                                    └─ اسم الخاصية موجود في Shader48.m_PropInfo  [PASS, 63/63]

الحلقة المفقودة:
Shader48 property name → DX11 source register t#/s#                   [UNKNOWN]

المسار الثاني المثبت:
DXBC SHDR t#/s# → vkd3d-generated SPIR-V OpName → set/binding         [PASS, 56/56]

النتائج غير المثبتة:
Correct CB byte offsets + normal/tangent/sRGB/smoothness + pass state + real
Unity GLES ShaderLab + Adreno GPU + PC pixel parity                       [OPEN]
```

## أدلة مستقلة وأرقام ثابتة
| Evidence | النتيجة |
|---|---|
| [GFX-MULTI-015 CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) | 14/14 source representative DXBC VS/FS stages بلا RDEF، لكنها تحتوي SHDR |
| [GFX-MULTI-016 CI42736745984](https://github.com/alwansan/raf/actions/runs/42736745984) | 66 CB +29 texture resource +27 sampler declarations (source) |
| [GFX-MULTI-017 CI42737442510](https://github.com/alwansan/raf/actions/runs/42737442510) | فهارس b/t/s الخاصة قابلة للقراءة، بدون duplicate داخل stage |
| [GFX-MULTI-018 CI42738042943](https://github.com/alwansan/raf/actions/runs/42738042943) | 42/42 resource count groups equal SPIR-V، لكن t/s registers أُعيد ترقيمها |
| [GFX-MULTI-019 CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) | source t/s register → translated SPIR-V descriptor: 29/29 +27/27 أسماء مولّدة متطابقة (56/56)، CB name still unknown |
| [GFX-MULTI-020 CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) | 7 original Material21 +63 TexEnv slots (21 bound)؛ 0/14 selected SerializedSubProgram player rows contain m_Parameters |
| [GFX-MULTI-021 CI42741817991](https://github.com/alwansan/raf/actions/runs/42741817991) | 27 Shader48 serialized properties (9 textures)، 63/63 TexEnv property names و21/21 bound property names تطابق؛ لا m_Script text field |

## حدود الاستنتاج
- لا تتخلص من الـ42 null TexEnv الأصلية ولا تصنع dummy material/texture.
- 14 stage = **زوج Source Variant واحد لكل Pass**، وليس كل الـ524 matched variant pairs، لذلك لا يُسمح باستنتاج أن كل البرامج في Raft stripped بنفس الشكل.
- الـNameIndices لا تعني أن ترتيب Shader property list يطابق ترتيب `t#` أو `s#`؛ إنشاء ربط اصطناعي من هذا الترتيب يجعل الصورة تبدو صحيحة جزئياً ولكنه خطأ هندسي.
- تطابق source→SPIR-V OpName لا يساوي تطابق Texture2D content ولا GPU sampling/UV/normal/CB layout/lighting.
- لا يوجد اختبار أصل Shader48 الحقيقي على Adreno حتى الآن؛ الصور السابقة كانت Standard fallback.
- لا تعدّل فرع T-Team أو تعلن الجاهزية قبل إثبات مستقل.

## خطة البحث والإغلاق القابلة للاستئناف
1. **GFX-MULTI-022 (P0):** فحص nonrepresentative Shader48 stage variants عن RDEF وm_Parameters بشكل محدود، مع اختبار مصدر same-export أصلي إن وُجد. فقط جرد آمن؛ لا ترفع shader bytecode أو أسماء الملكية. إن وجدت metadata كاملة، استخدمها لتوثيق NameIndex→t/s مع مقارنات سلبية.
2. إذا استمر غياب الأسماء، ضع `SOURCE_PROPERTY_TO_REGISTER_LINK_BLOCKED`؛ اسأل المالك عن ShaderLab/HLSL الأصلي أو PC capture بنفس المصدر عند الحاجة، بدلاً من تزييف Stage parity.
3. مستقلاً، أكمل Material Texture import flags (Gamma/Linear)، DXT5nm AG Normal/tangent basis، metallic/smoothness alpha، UV transforms، mip/sampling parameters، Mesh/triangle remap وRig/Animation. اختبر كل نطاق على الهاتف دون خلط Shader48 الأصلي وStandard.
4. بعد نجاح semantic resource linking، جرّب Shader48-compatible GLES ShaderLab محدودًا مع GPU readbacks وPC A/B pixels، ثم قبول المالك. الماء/FFT، النار والدخان والإضاءة الخاصة مراحل منفصلة.
5. لا تنشئ العامل العام الآن؛ هذه وثيقة تسليم مُعتمدة للخطط والأفكار حتى يحدد المالك صيغته لاحقًا.

**استعادة الجلسة:** `memory/sessions/20261110-GFX-chat-original-shader-text-source-22.md`، `prompt/graphics-lab/RESTORE_AR.md`، `gfxlab/OPEN_WORK_AND_IDEAS_AR.md`، `memory/STATE.json`، `memory/MEMORY.md`، وتحقق من HEAD وActions الحية قبل بدء أي دورة.


## GFX-MULTI-022 — exhaustive linked-variant reflection sweep (2026-11-10)
[CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) **SUCCESS**, 119 tests; source ZIP2 SHA locked. All **1,435/1,435** original Shader48 stage-variant link rows validated, including legacy and Unity 2021 player records; **524** exact keyword/hardware-tier VS/FS pairs; **1,275** unique referenced stage programs decoded as bounded authentic DXBC. RDEF present **0/1,275**; RDEF absent **1,275/1,275**. Across all 1,435 linked rows: `m_Parameters` blocks 0, texture parameter arrays/entries 0, constant-buffer binding arrays/entries 0, top-level sampler metadata rows 0, top-level constant-buffer metadata rows 0. The first attempt [CI42742873015](https://github.com/alwansan/raf/actions/runs/42742873015) completed the source scan but failed its summary assertion because zero-valued Counter keys were omitted; explicit zero counters fixed it. Private source purge succeeded in both attempts.

**Decision:** `SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_ALL_REFERENCED_VARIANTS`. This is stronger than the 14 representative-stage census, but does not include unreferenced entries in the 1,656-entry compiled table. The 56/56 DX11 t/s→SPIR-V symbolic mapping from GFX019 remains valid; the Material-property→source-register edge remains unknown. No original Shader48 Android runtime, GPU pixels, PC parity, APK, or owner acceptance. Original Shader48 restored=false.

**Next GFX-MULTI-023:** source-only Material/Texture2D semantic census across seven materials and 21 bound textures: role/format/color-space/mip/stream metadata, UV scale/offset, tint/color/float metadata, and role-specific decoded-channel statistics. Use authenticated sparse ZIP2 streams and publish safe aggregates only.


## تحديث العائق بعد المسح الشامل GFX-MULTI-022
[CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) يفحص 1,435/1,435 linked variant rows و1,275 unique referenced DXBC stage programs، لا 14 عينة فقط. 0/1,275 RDEF؛ 0 parameter blocks؛ 0 TextureParams؛ 0 ConstantBufferBindings؛ 0 top-level sampler/CB metadata. النتيجة `SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_ALL_REFERENCED_VARIANTS`.

هذا لا يشمل كل 1,656 compiled table entry؛ العناصر غير المرتبطة لم تدخل المسح. لا نستنتج أنها تحتوي reflection ولا أنها صالحة. الحل لا يزال يتطلب source/sidecar موثوقًا آخر أو PC reference مضبوطًا، ولا يجوز تخمين ترتيب Material TexEnv.

## GFX-MULTI-043 verified original PC managed shader literal provenance (2026-11-10)
- GFX-MULTI-043 [CI42829505370](https://github.com/alwansan/raf/actions/runs/42829505370) **SUCCESS 279 Python tests**, original ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, source runner purge verified. ZIP2 manifest 366 files and **0 named standalone shader-source sidecar extensions** (`.shader/.shaderlab/.hlsl/.cginc/.glsl/.compute/.fx/.spv/.dxbc`), not a proof that binary assets lack embedded source. Source Shader48 **27 properties/9 textures**, 7 Material slots, **63 TexEnv entries/21 bound entries**, 9 distinct TexEnv names/3 distinct bound names. Original `Assembly-CSharp.dll` valid .NET `#US` heap has **4,488 distinct literal strings**, **10 exact authored Shader48 property names**, of which **3** texture property names and **2 of 3** bound original Material texture property names. `Custom.dll` is a valid managed assembly with no `#US` heap and thus 0 literal-string evidence. Assembly-CSharp MemberRef method-name-only weak counts `PropertyToID=1, SetTexture=5, SetFloat=7, SetColor=4, SetVector=5, SetMatrix=3, EnableKeyword=2, DisableKeyword=2`. **Neither standalone method-name existence nor literal co-presence proves that any MethodDef calls the API for a particular Shader48 property; no proven Shader48 property→DX11 t#/s#/b# register or CB byte offset.** Safe persistent `gfxlab/evidence/20261110_gfx043_managed_shader_property_safe_counts.json`; safe-only [artifact13770611847](https://github.com/alwansan/raf/actions/runs/42829505370/artifacts/13770611847) expires 2026-11-17T13:59:35Z. Original Shader48 `originalShaderRestored=false`; Adreno GFX042 synthetic fullframe remains independent.
- **GFX-MULTI-044 potential next**: offline source-private `dncil==1.0.2` disassemble authentic `Assembly-CSharp.dll` CIL methods, resolve `ldstr` instruction operand to `#US`, resolve `call`/ `callvirt` to real UnityEngine.Material/Shader/MaterialPropertyBlock API MemberRef owner+method (not string-only), count exact Shader48 property literals and API references within same method and close instruction windows. This can reveal likely **script-side property usage**, but cannot infer direct dataflow, runtime use, DX11 register identity or byte offset. Do not leak actual source method names, exact literals or IL tokens. If no original Material→GPU link, retain G8 BLOCKED and request genuine original shader source/PC reflection only when available; avoid extra synthetic triangle APK.
- Durable session: `memory/sessions/20261110-GFX-chat-managed-shader-prop-17.md`; experiment: `experiments/20261110-GFX-chat-managed-shader-prop-17.json`; safe count file path listed above. No original ZIP2/PE/owner photos/screenshot/log content published.
