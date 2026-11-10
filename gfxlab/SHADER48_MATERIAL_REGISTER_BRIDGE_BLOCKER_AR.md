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
