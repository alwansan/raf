# GFX-LAB — المهام والأفكار الدائمة
**المسؤول:** GFX-LAB | **فرع الكتابة:** experiment/android-graphics-rootcause | **آخر تحديث:** 2026-11-10

هذه القائمة مشروعٌ حيّ وليست تقرير نجاح. حدّثها **بعد كل دورة** مع `prompt/graphics-lab/RESTORE_AR.md` وملف الجلسة و`memory/STATE.json` و`memory/MEMORY.md`. لا تفترض إتمام أي بند بلا CI ودليل مستقل.

## الحقائق التي لا يجوز نسيانها
- صور المستخدم والـ12 Log للموديلات M00–M05 تثبت ظهور Mesh/Textures/الألوان على الهاتف تحت **Unity Standard fallback** فقط. `originalShaderRestored=false` و`originalAnimationRestored=false`.
- [CI42727777657](https://github.com/alwansan/raf/actions/runs/42727777657): تطابق الستة أعداد رؤوس float32 position+UV+Normal المميزة مع Unity، لكن indexed triangle remap والـrig لم يُثبتا.
- [CI42731206453](https://github.com/alwansan/raf/actions/runs/42731206453): 1435/1435 رابط مصدر DX11 صحيح داخل 7 Passes، DXBC أصلي وليس GLES جاهزًا.
- [CI42732808109](https://github.com/alwansan/raf/actions/runs/42732808109): 7/7 Passes ممثلة بزوج VS+FS أصلي لكل واحد تُترجم DXBC→SPIR-V→GLSL ES 310 وتمر بفحص CPU. **ليس** جميع 524 Variant ولا اختبار Adreno.
- [CI42733664716](https://github.com/alwansan/raf/actions/runs/42733664716): DXBC الأصلي لعينة Pass0 VS/FS **بلا RDEF**. أعداد CB والـBinding الأصلية غير معروفة `null` وليست صفرًا؛ SPIR-V reflected: VS5 UBO، FS7 UBO/7 images/6 samplers. لا يعني تعادل الـregisters.

## الأولويات التالية
1. **DONE (source-only), GFX-MULTI-015:** [CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) SUCCESS 80 tests: all 14 representative authentic Shader48 stages lack RDEF; each has SHDR+input/output signatures. Counts originally undefined => null; this result is for one matched pair per Pass, not all variants.
2. **P0، GFX-MULTI-016:** عند غياب RDEF، استخدم declaration tokens من SHDR/SHEX أو Reflection مستقل مثبت للحصول على خريطة DX11 `b# / t# / s#` وربطها بمخرجات SPIR-V، مع اختبارات سلبية؛ تجنب افتراض أن `binding=0` هو `b0`.
3. **P0، GFX-MULTI-017:** تدقيق دلالات Material الأصلية: tint وTexEnv/UV scaling، sRGB BaseColor، DXT5nm AG Normal swizzle/tangents، metallic/smoothness alpha، sampling wrap/filter/mips، flags الخاصة بكل Pass.
4. **P0، GFX-MULTI-018:** إثبات ShaderLab/GLES3 حقيقي بمختبر منفصل و`shader.isSupported` وPasses/Keywords/Binding، بالتنسيق قبل أي APK؛ لا تخلط Shader Standard مع Raft الأصلي.
5. **P1، GFX-MULTI-019:** صورة مرجعية PC مقابل الهاتف بنفس Mesh/Material/Camera/Light/Linear، والـnormal/specular/depth مع عتبات واضحة.
6. **P1، GFX-MULTI-020:** مقارنة face index بعد merge للـMesh، والتحقق من submesh/material slots وSkinned bone weights/bindposes/parent hierarchy وM04 كقطعة أو مجموعة.
7. **P1، GFX-MULTI-021:** تغطية بقية 524 original matched stage variant pairs وحالات keywords/tier، وحالات Blend/ZWrite/ZTest/Cull/ColorMask والـRenderQueue.
8. **P2، GFX-MULTI-022:** نموذج جديد غير مشمول بالستة وnegative controls، لصياغة وصفة توقف عند mismatch ولا تخلق Dummy أو Fake shader.
9. **Handoff لاحقًا فقط:** بعد نموذج end-to-end ناجح وPC/GPU/owner proof، ضع وصفة عامل استعادة متخصص؛ **لا تنشئ العامل** قبل تعليمات المالك.

## أفكار منفصلة لا تضيع
- لا تخلط shader واحدًا مرتبطًا بست مواد مع أنواع shader أخرى؛ اربط بالهوية المصدرية لا الاسم.
- جرّب مقاييس mapping للـsampler والـCB offsets وبرامج shader stripped بلا RDEF؛ سجّل unknown بدل أصفار مزيفة.
- قارن Unity C# Runtime model flags بنص shader الفعلي، وافصل boolean build-time عن pixel evidence.
- الماء/FFT، الرغوة، النار، الدخان، والإضاءة/post-processing مراحل مستقلة؛ لا تدخل فرع T1–T5.
- احتفظ ببوابات: ORIGINAL_SOURCE / SAME_EXPORT / UNITY_IMPORT_COMPILE / GPU_EXPERIMENT / ANDROID_GAME_PIXELS / OWNER_ACCEPTANCE.

**آخر جلسة توثيق:** `20261110-GFX-chat-persistent-roadmap-15`. **آخر تجربة مصدر:** GFX-MULTI-014، والتالية GFX-MULTI-015. **ZIP2 المثبت:** 15964ea8f246b6e076ce26b60931ee2e1a9a2385.


## تقدم هذه الدورة
- بدأت `GFX-MULTI-015` (جلسة `20261110-GFX-chat-rdef-seven-pass-source-16`) للتحقق من RDEF في 14 Stage من المصدر الحقيقي؛ الحالة `CI_PENDING` حتى يثبت التشغيل.
- عند النجاح/الفشل، حدّث هذا البند واذكر رابط CI، ولا تختزل غياب RDEF إلى صفر CB.


## التجربة الحية — GFX-MULTI-016
- `20261110-GFX-chat-shdr-declaration-census-17`: parser fail-closed للتعليمات SHDR/SHEX لدى Shader48 الحقيقي؛ opcode indices 88/89/90/161/162 مصدرها Microsoft DirectX-Headers، 14 stage، CI pending.
- *نتائج المصدر ليست register binding semantics*؛ لا تعتقد أن عدد DCL يكفي لإثبات CB offset أو normal/metallic Texture sampler.


## نتيجة مثبتة — GFX-MULTI-016
- [CI42736745984](https://github.com/alwansan/raf/actions/runs/42736745984) SUCCESS 85 tests: original seven-pass SHDR declarations in 14 source stages => 66 CB, 29 Resource, 27 Sampler (0 raw/structured). First pass VS 5 CB and FS 7 CB/7 Res/6 Sampler matches SPIR-V counts. **REGISTER NUMBERS, SAMPLER MAPPING AND CB LAYOUT STILL UNKNOWN**. سجل الجلسة `20261110-GFX-chat-shdr-declaration-census-17`.
- الخطوة التالية الدقيقة: **GFX-MULTI-017** parse each original DCL operand into private DX11 register slot index and CB array-size with strict operand-type/dimension/index-representation guards; compare independently to SPIR-V descriptors and original material TexEnv, report only match/mismatch aggregates.


## التجربة الجديدة — GFX-MULTI-017
- جلسة `20261110-GFX-chat-original-register-operands-18`: استخراج مقيّد وفحص private register slot shape من أصل SHDR (CB b#, texture t#, sampler s#)، مع positive/negative controls على type/dimension/relative-index. الحالة CI_PENDING.
- **لا تخلط استخراج رقم السجل بـMapping صحيح**: يجب بعد ذلك مطابقة DX11 registers مقابل SPIR-V descriptors وSource Material/CB layout/texture sampler semantics.


## GFX-MULTI-017 مثبت
- [CI42737442510](https://github.com/alwansan/raf/actions/runs/42737442510) SUCCESS 89 اختبارات: 14 stage، 66 CB register slots ذات أحجام معلنة غير صفرية، 29 Resource slots، 27 Sampler slots، بلا أي slot duplicate داخل نفس stage. الأرقام الأصلية خاصة، لا تُنشر. هذا يثبت إمكانية استخراج slot indexes فقط، **لا يثبت** ارتباطها بمواد Unity أو معاني Binding بعد التحويل.
- **التالي GFX-MULTI-018**: مقارنة private original b#/t#/s# register set مع SPIR-V descriptor bindings التي يرجعها independent SPIRV-Cross، مع negative controls لمواضع تصادم sampler/CB. أبق النتيجة UNKNOWN إذا وجدت register remapping، ولا تُعلن Android GPU بدون اختبار.


## GFX-MULTI-018 — قيد الفحص
- `20261110-GFX-chat-source-vs-spirv-binding-19`: مقارنة private DX11 source CB/texture/sampler register slots بـSPIRV-Cross descriptor `set/binding` في 14 stage من المصدر؛ report safe numeric group parity/overlap/duplicates فقط، لا نشر البايتات أو الأرقام الخاصة. CI pending.
- إذا mismatch: صمم mapping مثبت بدل إعادة ترقيم عشوائية؛ إذا numeric match: لا تعلن أن material/CB/sampler semantic equivalence مثبتة قبل اختبار المصدر وGPU.


## GFX-MULTI-018 نتيجة حاسمة
- [CI42738042943](https://github.com/alwansan/raf/actions/runs/42738042943) SUCCESS، 93 tests؛ مصدر 122 DCL declarations مقابل 122 reflected SPIRV resources، 42/42 مجموعات متساوية **بالعدد فقط** وبدون binding مجهول أو مكرر.
- 14/14 CB group source register slot numerical sets تساوي SPIRV binding sets؛ **لكن Fragment Texture sets 0/7 تطابقًا رقميًا وSampler sets 0/7**. لا تنسَ أن 28/42 مجموعات تطابق رقمي تشمل 14 مجموعة فارغة في Vertex.
- **P0 التالي GFX-MULTI-019:** استعادة خريطة DX11 `t#/s#`→SPIRV `set/binding` بشكل مثبت من سجلات المصدر/الترجمة، وربط الأصل `Material TexEnv` وSampler semantics. لا تربط الصور افتراضيًا بأرقام DX11 القديمة داخل GLSL؛ هذا خطر color/normal corruption.
- بعدها تحقق CB bytes/offsets، DXT5nm AG/tangent، metallic/smoothness وUV/tint، قبل طلب اختبار GPU على Adreno. لا تعتبر مرحلة Shader كاملة.


## GFX-MULTI-019 بدأ — تحويل رقم السجل إلى اسم Binding مُثبت
- `20261110-GFX-chat-symbolic-binding-map-20`: فحص source DX11 DCL register indices مع أسماء `OpName` التي يولّدها vkd3d داخل SPIR-V، ثم تطابقها مع `spirv-cross --reflect` `set/binding`، عبر سبعة Passes و14 Stage أصلية. أسماء المصدر والفهارس الخاصة لا تُنشر. CI pending.
- بعد استخراج mapping رمزي لا تخلطها مع مطابقة Content/CB Offset/Material TexEnv. مرجع الكود العام: `spirv_compiler_get_register_name` في vkd3d، وحفظ الأدلة السلبية للمسارات غير المعروفة.


## GFX-MULTI-019 اكتملت خريطة t/s الرمزية (source-only)
- [CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) SUCCESS 98 unit tests. 29/29 original source texture/resource `t#` and 27/27 original samplers `s#` accurately matched vkd3d-generated SPIR-V names and descriptor bindings, all 56 numerically remapped (not equal original slot). CB original 66 source names not matched to reflected names; numeric binding parity from GFX018 is not name parity. Do not claim original Shader48 on phone.
- **P0 GFX-MULTI-020**: derive independent source property→shader register mapping from original `SerializedSubProgram.m_TextureParams` and `m_Samplers` metadata, original Shader48 parameter-name pool and 7 Material m_TexEnvs. Compare register slot identities to 56 proven generated t/s name mappings; report only counts, validate null TexEnv handling. Never infer via material property list ordering.
- Afterwards cover CB original `m_ConstantBufferBindings` + `m_VectorParams/m_MatrixParams` byte offsets, normals/tangent DXT5nm, RenderStates and Android GPU.


## GFX-MULTI-020 — ربط TextureParam الحقيقي بخاصية المادة (CI pending)
- جلسة `20261110-GFX-chat-original-material-texenv-21`: مصدر Unity 2021.3 Shader48، `m_Parameters.m_TextureParams` لكل Stage، جدول `m_NameIndices` الأصلي لكل Pass، ومطابقة `m_Index` مع DX11 t# و`m_SamplerIndex` مع s# ثم اسم الخاصية مع Material موقّع بنفس source SHA والـTexEnv bound/nonbound.
- أرقام أو أسماء مصدرية لا تُنشر، ولا نخلط source property metadata مع shader GPU sampling correctness؛ إن كانت بيانات m_Parameters ناقصة نصرح بوجود نقص ولا نخمن.


## GFX-MULTI-020 — ميتاداتا TextureParam غير موجودة، لا نخمن
- [CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) SUCCESS 103 tests. سبع مواد من ستة موديلات أصلية: **63 TexEnv slots، 21 bound، 42 null**. Shader48 الأصلي: 27 serialized properties و7 Passes مع m_NameIndices (29/17/6/10/23/15/9). لكن stage rows الـ14 كلها بلا `m_Parameters` و0 TextureParam metadata. وبالتالي 0 source Material name→t/s register link مثبت.
- هذا يؤكد النقص السابق في GFX-MULTI-006. مهم: 21 Texture2D مرتبطة صحيح بالمادة؛ النقص بالـShader program parameter metadata فقط.
- **P0 GFX-MULTI-021**: افحص إن كانت `m_Script` أو مصدر Shader غير مضغوط أو reflection/sidecar من same-export الأصلي يحوي تعريفات أسماء Texture/register، مع SHA مربوط وهوية Shader48 واضحة. إذا ما موجود، دوّن BLOCKED_SOURCE_NAME_TO_REGISTER_MAPPING ولا تخمّن ترتيب m_TexEnvs.
- لا ترفع حالة shader restoration؛ خصائص shader runtime-setting ممكن تكون خارج m_SavedProperties وفق Unity، ويجب التمييز.
