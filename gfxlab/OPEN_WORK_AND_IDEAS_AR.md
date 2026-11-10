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


## GFX-MULTI-021 جارٍ — تحقق Source Shader text بديل
- `20261110-GFX-chat-original-shader-text-source-22`: فحص `Shader48.m_Script` الأصلي من ZIP2: هل يوجد أي كود أصلي CGPROGRAM/HLSLPROGRAM أو `register(t#)`؟ ومقارنة أسماء المواد المرتبطة مع 27 shader property (لا تُنشر الأسماء). CI pending.
- **If missing**: source Text register binder BLOCKED؛ لا تحوّل أسماء shader property بالترتيب إلى t#/s#، واطلب أصل ShaderLab/PC reference ذا SHA مستقل إذا توفر؛ استمر بفحص ألوان/Normal/UV/Textures والـRig بشكل منفصل.


## GFX-MULTI-021 — نتيجة إيجابية للـMaterial، سلبية للمصدر النصي
- [CI42741817991](https://github.com/alwansan/raf/actions/runs/42741817991) SUCCESS 107 tests، من أصل ZIP2 SHA مثبت: Shader48 27 properties منها 9 Texture، **63/63 Material saved TexEnv keys** تطابق مصدر Shader properties، و21/21 actual bound names (7 albedo +7 normal +7 metallic). المصدر يحتوي 42 null slots أصلية، لا تُملأ بـdummy.
- `m_Script` غائب في Shader48، 0 text bytes ولا CG/HLSL/register markers. GFX020 0/14 original parameter metadata وGFX015 14/14 representative DXBC بلا RDEF. إذن **Material property name→t#/s# register evidence BLOCKED in tested source fields**؛ رغم وجود 56/56 t/s→SPIRV map من GFX019.
- **P0 GFX-MULTI-022**: ابحث في بقية source Shader48 variants غير الممثلة (524 matched stage pairs) عن استثناءات m_Parameters/RDEF أو مصدر ShaderLab مستقل أصلي وسليم identity. لا تدعي عدم وجوده عالمياً من 14 Stage فقط. إن غاب، اطلب reference PC أو shader source شرعي من المالك عند الحاجة؛ لا تستبدل الربط بتخمين ترتيب الصور.
- **P1**: جهّز تجارب مستقلة لـNormal DXT5nm AG/Tangent وUV Scale/Offset وTexture sRGB/Metallic/Smoothness وCB packing/Pass State، ونموذج جديد خارج الستة؛ المياه/النار/الإضاءة منفصلة. لا تنشئ العامل العام حتى تعليمات المالك.


## GFX-MULTI-022 — exhaustive linked-variant reflection sweep (2026-11-10)
[CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) **SUCCESS**, 119 tests; source ZIP2 SHA locked. All **1,435/1,435** original Shader48 stage-variant link rows validated, including legacy and Unity 2021 player records; **524** exact keyword/hardware-tier VS/FS pairs; **1,275** unique referenced stage programs decoded as bounded authentic DXBC. RDEF present **0/1,275**; RDEF absent **1,275/1,275**. Across all 1,435 linked rows: `m_Parameters` blocks 0, texture parameter arrays/entries 0, constant-buffer binding arrays/entries 0, top-level sampler metadata rows 0, top-level constant-buffer metadata rows 0. The first attempt [CI42742873015](https://github.com/alwansan/raf/actions/runs/42742873015) completed the source scan but failed its summary assertion because zero-valued Counter keys were omitted; explicit zero counters fixed it. Private source purge succeeded in both attempts.

**Decision:** `SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_ALL_REFERENCED_VARIANTS`. This is stronger than the 14 representative-stage census, but does not include unreferenced entries in the 1,656-entry compiled table. The 56/56 DX11 t/s→SPIR-V symbolic mapping from GFX019 remains valid; the Material-property→source-register edge remains unknown. No original Shader48 Android runtime, GPU pixels, PC parity, APK, or owner acceptance. Original Shader48 restored=false.

**Next GFX-MULTI-023:** source-only Material/Texture2D semantic census across seven materials and 21 bound textures: role/format/color-space/mip/stream metadata, UV scale/offset, tint/color/float metadata, and role-specific decoded-channel statistics. Use authenticated sparse ZIP2 streams and publish safe aggregates only.


## خطة الدورة التالية — GFX-MULTI-023 (P0)
- افحص 7 Materials أصلية و21 Texture2D مرتبطة بالـroles الثلاثة (7 BaseColor / 7 Normal / 7 Metallic) من نفس ZIP2 SHA.
- افحص حقول Texture2D المصدرية: format، color-space metadata، mip count، dimensions، streaming flags/settings، filter/wrap/aniso. لا تفسر enum رقميًا قبل مرجع موثوق.
- افحص Material: tint/color/floats/ints، وكل TexEnv UV scale/offset، مع حفظ أسماء الخصائص والقيم الخاصة داخل runner فقط.
- أعد hydration لقطع Git blob الأصلية المطلوبة فقط عبر `model_plan` و`fill_sparse_authenticated_streams`; لا تنزل stream كاملًا ولا ترفع PNG/OBJ أو source IDs.
- احسب channel variability/summary للـNormal والـMetallic (خصوصًا A/G/R/B) داخل runner. هذه إشارة إلى packing فقط، لا تثبت DXT5nm decode أو معنى smoothness دون مصدر shader أو PC reference.
- التقرير العام: أعداد حسب role/format/mip/color-space/UV/tint/channel family، مع fail-closed guards وsource SHA. لا APK ولا claim GPU.

## قرار بعد GFX-MULTI-022
- لا مزيد من إعادة فحص الـ14 representative stages؛ GFX022 وسّع الفحص إلى جميع 1,435 link rows و1,275 unique referenced DXBC programs.
- لا نعتبر بقية compiled table entries مستخدمة أو خالية من RDEF؛ لم تدخل في linked-variant sweep. لا نوسع هذا المسار إلا بدليل مرجعي محدد.
- إن احتجنا shader semantics لاحقًا، نطلب PC reference ثابت أو authoritative source/sidecar من المالك؛ لا نركّب mapping بالتخمين.


## GFX-MULTI-023 — original Material/Texture2D semantics and channel census (2026-11-10)
[CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) **SUCCESS**, 128 tests. Pinned ZIP2 source; six models, seven original Materials, 63 TexEnv slots (21 bound / 42 null), seven BaseColor + seven Normal + seven Metallic textures. All **21/21** original Texture2D images decoded with exact dimensions; 53,477,376 pixels examined privately. Only 15 authenticated stream chunks / 707,788,800 selected bytes were hydrated; safe aggregate artifact uploaded and all private source/texture/stream data purged.

Material facts: 14 color slots, 112 float slots, 0 int slots; all seven authored tint slots are identity white; all 21 role-specific UV scale/offset transforms are identity. Thus non-white tint and UV transforms do not explain the current material appearance differences.

Texture code distributions (raw serialized codes; do not infer color-space or format semantics from these counts alone): format code BaseColor 10×5 + 12×2, Normal 12×7, Metallic 12×7; color-space code BaseColor 1×7, Normal 0×7, Metallic 1×7; mip-count code BaseColor 11×3/12×4, Normal 11×3/12×4, Metallic 11×5/12×2; filter-mode code 1×21. Texture settings, anisotropy and mip-bias fields were present on all 21. Generic `m_WrapMode` code was unavailable in this type tree; axis-specific wrap fields still need inspection.

Channel census: BaseColor R/G/B variable 7/7; Alpha variable 2/7 and fully opaque 5/7. Normal R constant 7/7 while G/B/A variable 7/7; tested A+G with constant R+B signature candidate 0/7, so the conventional DXT5nm hypothesis is not supported by this simple channel signature. Metallic Alpha variable 7/7; this is only a candidate channel for additional data such as smoothness, not proof of shader semantics.

The first attempt [CI42743969290](https://github.com/alwansan/raf/actions/runs/42743969290) successfully planned the exact 15 chunks but failed when the audit re-read the manifest after sparse checkout intentionally excluded it. The correction reuses previously SHA-verified staged owner assets; [CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) then completed all steps and private purge successfully. Artifact [13730562085](https://github.com/alwansan/raf/actions/runs/42744204412/artifacts/13730562085), expires 2026-11-17T02:40:48Z UTC.

**Limits:** raw numeric texture format/color-space codes are not yet semantically mapped; axis-specific wrap fields and float-property meanings remain open. No shader bytes, source names, pointers, raw pixels or image files were exported. No Shader48 execution, PC/GPU pixel parity, Adreno proof, APK or owner acceptance. `originalShaderRestored=false`; `actual_android_original_shader_pixels_verified=false`; `phase_closed=false`.


## GFX-MULTI-024 — الخطوة التالية
- افحص 112 float slots و14 color slots عبر المواد السبع، وصنّف الخصائص المعروفة داخلياً (metallic/smoothness/gloss/bump/emission/cutoff وغيرها) مع إبقاء الأسماء والقيم داخل runner. انشر counts وranges/category counts فقط.
- افحص TextureSettings حقول WrapU/WrapV/WrapW (وليس m_WrapMode فقط)، وFilter/Aniso/MipBias، مع عدم الخلط بين field absent وfalse.
- اربط أكواد TextureFormat وm_ColorSpace بمرجع Unity 2021.3 موثوق قبل تسميتها DXT1/DXT5 أو sRGB/Linear؛ أبقِ القيم الخام فقط حتى يثبت المرجع.
- بعد ذلك قرر هل نحتاج Android GPU channel probe صغيراً يعرض قنوات R/G/B/A للـ21 texture للتحقق من Unity GLES، من دون ادعاء استعادة Shader48.


## 2026-11-10 — GFX-MULTI-024 confirmed
[CI42745536309](https://github.com/alwansan/raf/actions/runs/42745536309) SUCCESS 139 tests. Source six models have **seven Renderer Material slots but six unique Material21 objects**, and **21 Texture2D references but only 18 unique Texture2D objects**. This repairs a source accounting assumption exposed by failed [CI42745345599](https://github.com/alwansan/raf/actions/runs/42745345599). All 112 Float and 14 Color saved-property labels match the original Shader48 27-property declaration; 33 float zeros, 58 ones, 21 between 0 and 1. Colors: seven identity-white (including seven white tints) and seven nonidentity secondary colors (role unknown). Unity 2021.3 official enums show original BaseColor DXT1×5 + DXT5×2, Normal/Metallic DXT5×7 each; BaseColor/Metallic sRGB×7 each and Normal Linear×7. All 21 source texture links have Bilinear, Repeat U/V/W, Aniso=1 and MipBias=0. [Official Unity 2021.3 enums](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs). No source-to-DX11 constant buffer offset mapping or Shader48 Android runtime. No APK. Private source purged.

## GFX-MULTI-025 next
- **P0**: inspect the seven nonidentity secondary Color slots: source property-label matches and safe semantic classification (e.g. emission candidate). No raw property strings or numerical colors in public files. Do not infer emissive GPU effects.
- **P0**: privately map which M00–M05 Renderer Material slots share the same Material21 and which of the 21 Texture role links reference the same Texture2D; publish only anonymized pair/set-size counts, not source PPtrs/GUIDs, and preserve real identities in Unity asset transfer.
- **P1**: establish deterministic import policy that preserves original TextureFormat/ColorSpace, sampler wrap/filter/aniso/mip, and UV/tint/secondary color values without falsely claiming Shader48 parity. Metallic sRGB is *source authored*; don't silently convert data to Linear based on common PBR assumptions.
- **P1**: resolve original shader property→CB offsets/material→DX11 registers via independent authentic PC/reference evidence, not fabricated order. Then decide minimal GPU channel experiment; separate ORIGINAL_SOURCE/UNITY/GPU/OWNER gates.
- **P2**: original rig/skinning, M03 dual materials, water/FFT, smoke/fire remain independent open scopes. T1–T5 and main/zip2 read-only.


## GFX-MULTI-025 — 2026-11-10 original color and asset sharing verified
[CI42746455458](https://github.com/alwansan/raf/actions/runs/42746455458) SUCCESS / 146 tests, private original ZIP2 SHA-pinned source. Material slot identities: 7 Renderer slots → 6 unique Material21 objects (five single-use, one shared across models). Texture links: 21 → 18 unique Texture2D objects (fifteen single-use and three shared twice across models); zero links shared across roles. All fourteen Color saved-property labels are declared in the authentic original Shader48: seven **white base tints** and seven exact `_EmissionColor` property candidates with **black RGB and Alpha=1**. Thus GFX024's secondary nonwhite Color entries were black emission colors, not failed Albedo tint. Names, raw numeric values, object pointers and image/shader data remained private; runner purge complete. No original Shader48 GPU shader or pixel equality. [Safe artifact 13730829715](https://github.com/alwansan/raf/actions/runs/42746455458/artifacts/13730829715).

## GFX-MULTI-026 — current next priority
- Audit exact original Shader48 seven serialized Pass render-state metadata: Cull, Blend, ZWrite, ZTest, ColorMask, effective queue/pass tags, and presence/missing fields using original SHA-pinned source, without inventing unsupported values. Source-only metadata cannot establish runtime GPU state.
- Audit original seven Material slot references' source `m_CustomRenderQueue`, shader keyword fields, instancing flags, and whether shared objects preserve state across slots.
- Return only safe state availability/category counts, never raw proprietary original shader names, material IDs, vectors or code; compare against Unity 2021.3 official enum reference. Maintain `originalShaderRestored=false`, `android_gpu_pixels_verified=false`.
- Later: controlled original-source→Unity→Adreno/PC comparison with genuine original Shader48 inputs and property→register/CB semantics, avoiding guesswork; do not modify T1–T5, main, zip2.

## GFX-MULTI-026S original seven-pass state census — CI42749148702 SUCCESS (2026-11-10)
Source-only, pinned ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, **154 unit tests** passed after an initial CI42749035585 sparse-checkout test setup failure (4 Unity contract tests looked for omitted Unity assets; source-free-only tests now skip Unity-only contracts when files are intentionally absent). Verified all **7/7** Shader48 source Pass rows have an `m_State` dictionary and tags, with metadata for Cull, ZWrite, ZTest, zClip, Blend separate, alphaToMask, stencil and fog; direct `rtBlend` and generic `colorMask` keys absent. Presence does NOT prove a correct runtime render state or effective Blend/ColorMask behavior. Seven original Material slot rows: instancing enabled 7, shader-default queue -1 in 5, explicit nonnegative queue in 2; `m_ShaderKeywords` direct field absent in 7/7 (not proof there are no keywords in alternate metadata). All source values and IDs private; runner purge successful. Safe artifact [13732363372](https://github.com/alwansan/raf/actions/runs/42749148702/artifacts/13732363372) expires 2026-11-17T03:24:33Z.
- **GFX-MULTI-026 APK build currently NOT completed:** [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) started at commit 818298ce8fcb71d7906f977c5d03cc8d619db57e, Unity 2021.3.45f2 real import/build IL2CPP ARM64 GLES3 is in progress. Six original SHA-authenticated models, 21 texture role links, original color-space vs forced linear diagnostic channel probe added. Package `com.alwansan.raft.graphicslab.channels`, Android minimal standalone APK only. Verify BuildPipeline, signature, package name, SHA256/CRC, artifact, purge before declaring APK issued.
- **Negative evidence:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `devicePixelsVerified=false`, `PCPixelParityVerified=false`. The new channel probe shader `Hidden/GfxLab/ChannelProbe` is independent diagnostic-only GLES3, **not Shader48**. WATER-001, RENDER-002 remain OPEN.

### Next after GFX-MULTI-026 APK
- Once CI terminal success: user installs separate `com.alwansan.raft.graphicslab.channels`, test M00–M05 / PBR + channel GPU diagnostics for BaseColor/Normal/Metallic with SOURCE COLORSPACE vs FORCE LINEAR, record screenshot and COPY LOG of per-model/surface/role/channel.
- Source-only state census needs decoded precise Cull/Blend/ZWrite/ZTest and mapping property→DX11 registers/CB semantics; these are not solved by the channel APK. Compare controlled PC/device pixel reference with original source shader separately. Do not ask T1–T5 for merged game or create an agent.


## GFX-MULTI-028S — كشف قيم render state دون استنتاجات GPU (جارٍ)
- `20261110-GFX-chat-renderstate-enum-28`: المصدر الأصلي في ZIP2 يؤكد وجود م_State لـ7 Passes من GFX026S؛ نفحص هل قيم Cull/ZWrite/ZTest ثوابت enum مسموحة رسميًا أو named override ديناميكي، ونقيس m_ValidKeywords/m_InvalidKeywords بدل اعتبار m_ShaderKeywords الغائب دليل انعدام Keywords. تقرير aggregate فئوي فقط، وليس نسخة ShaderLab جاهزة. CI pending.
- لا نعدل GFX-MULTI-026 Android channel APK الجارية؛ عند نجاحها اختبر owner 6 meshes وتوابع texture channels وصور الهاتف وCOPY LOG قبل إغلاق أي GPU gate.


## GFX-MULTI-026 APK — SUCCESS (2026-11-10)
[CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) verified real Unity 2021.3.45f2 IL2CPP ARM64 OpenGLES3 build, single signed APK, valid AndroidManifest/classes.dex/arm64 libunity.so/ZIP CRC, apksigner/aapt verified `com.alwansan.raft.graphicslab.channels`, and private asset purge. APK: `GfxLab-Multi-Six-Channel-Probe.apk`, 65,963,109 bytes, SHA256 `8fef68d82748cd214b1f5f5f9c0b3903a80f343513ccb15fc35e12649c02ad52`. [Artifact 13733300521](https://github.com/alwansan/raf/actions/runs/42748792585/artifacts/13733300521), expiry 2026-11-17T03:32:17Z. 6 original meshes, 21 original Texture links; diagnostic `Hidden/GfxLab/ChannelProbe` displays SOURCE/LINEAR imported sampled RGB/R/G/B/A per BaseColor/Normal/Metallic. **Never call diagnostic shader restored Shader48.** Phone test/PC pixel parity/rig/Shader48 register-identity `OPEN`; `originalShaderRestored=false`, `ownerDeviceTestPending=true`. Session: `memory/sessions/20261110-GFX-chat-sevenpass-channel-apk-27.md`, test instructions `gfxlab/DEVICE_TEST_GFX_MULTI026_AR.md`.

## GFX-MULTI-028S VERIFIED CI42749968983 — source-only negative GPU gate
- [CI42749968983](https://github.com/alwansan/raf/actions/runs/42749968983) COMPLETED SUCCESS, **159** unit tests; authenticated ZIP2 Shader48 (source SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385) 7 Pass state records and seven source Material21 slots.
- **7/7** Passes for each `culling`, `zWrite`, `zTest`, `alphaToMask` have `name` dynamic parameter override; `val` is not safe to interpret as fixed effective GPU enum without resolving material/source property. No static Cull/Depth/AlphaToMask state was proven. **7/7** have `rtSeparateBlend=false`; direct `rtBlend` field absent 7/7, which is not evidence that Blend is disabled.
- `m_ValidKeywords` nonempty in **7/7** source material slots, `m_InvalidKeywords` empty in **7/7**, direct legacy `m_ShaderKeywords` absent in **7/7**. Therefore old metadata absence must not be interpreted as source keyword absence.
- Ground enum names: official [Unity 2021.3 GraphicsEnums.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs). Fail-closed unit tests cover numeric enum fallback, invalid/unrecognized value and named dynamic override. Original numeric state values, private property names and source Shader48 bytes never exported; runner purge verified.
- OriginalShader48Restored=false; actual Android diagnostic channel APK (GFX026 [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585)) is a separate shader `Hidden/GfxLab/ChannelProbe`, not original Shader48; owner GPU channel images/COPY LOG remain pending. Signed APK checksum documented by parallel delivery owner in RESTORE and `gfxlab/DEVICE_TEST_GFX_MULTI026_AR.md`.
- Next **GFX-MULTI-029S**: verify each dynamic `m_State.{culling,zWrite,zTest,alphaToMask}.name` is a true Shader48 `m_PropInfo` property and occurs in original seven Material `m_SavedProperties.m_Floats`/typed property tables. Reject mismatched alias and unknown parameter; do not guess enum from numeric fallback or source property array order.


## GFX-MULTI-029S — قيد الفحص: named Cull/ZWrite/ZTest → Material Float
- `20261110-GFX-chat-passstate-material-binding-29`: قارن private metadata `m_State.name` مع `Shader48.m_PropInfo.m_Props` و`Material21.m_SavedProperties.m_Floats` في السبع Material slots. تحقّق من أن الرقم المخزّن ضمن enum عند وجوده دون نشره أو استخدامه كدليل GPU state. Source CI pending؛ لا تعديل لـGFX026 APK.


## GFX-MULTI-029S — خلاصة معلّمة عدم الإغلاق
- [CI42750996280](https://github.com/alwansan/raf/actions/runs/42750996280) SUCCESS 164 tests: source Shader48 7 Passes، dynamic named `Cull/ZWrite/ZTest/AlphaToMask` موجودة؛ matching إلى Shader property + Material Float يفشل لـCull/ZTest/AlphaToMask (0/7 each, 0 slot matches)، ونجح ZWrite فقط في 2/7 Passes مع 14 slot-value matches (2×7)، وكلها allowed enum.
- **P0 next GFX-MULTI-030S:** تحقق من أسمائها بالـ`m_NameIndices` الحقيقي لكل Pass أو مصدر metadata مستقل (اسم خاصية/keyword مؤكد)، ولا تنسب numeric fallback إلى runtime state. إن غاب الدليل، وثّق BLOCKED_SOURCE_DYNAMIC_RENDER_STATE_BINDING، واطلب PC/Android GPU reference قبل إنشاء ShaderLab نهائي.
- **P0 device**: نسخة GFX026 signed Android channel APK جاهزة، لكن لا يوجد log/لقطات مالك على الهاتف، وShader48 original=false. [Test handoff](https://github.com/alwansan/raf/blob/experiment/android-graphics-rootcause/gfxlab/DEVICE_TEST_GFX_MULTI026_AR.md).


## 2026-11-10 — GFX owner ZIP review and original Shader48 gates (CI success, NOT CLOSED)
- Owner private `test model(1).zip` SHA256 `adc08713ad67a987d0b30ac01b1b6e9004342b359aeb97ed1ee61866fecc4238`: CRC PASS; 16 JPG photos (2400×1080), 13 COPY LOG JSON, latest runtime report and 10 Android UnityShaderCache files inspected locally only. **No original images, ShaderCache bytes, IL2CPP or source shader code committed to GitHub.** Device POCO F5 Pro Xiaomi 23013PC75G Adreno730 GLES3.2 Unity2021.3.45f2 Linear; M00–M05 each have Albedo/PBR Standard logs; 13/13 error count zero in those snapshots (not full logcat). Preview photos show Normal/Metallic but 13/13 copied states are BASECOLOR/RGB/SOURCE/sample Surface0 only, no ForceLinear or M03 Surface2 logs.
- [GFX-OWNER-001 CI42752583864](https://github.com/alwansan/raf/actions/runs/42752583864) SUCCESS **171 tests**: added independent safe ZIP auditor and synthetic tests. Aggregate owner evidence `gfxlab/evidence/20261110_gfx026_owner_safe_counts.json`.
- [GFX-MULTI-030S CI42753634633](https://github.com/alwansan/raf/actions/runs/42753634633) SUCCESS **176 tests**; exact original SHA ZIP2 2 SubShaders /7 Passes. `m_NameIndices` metadata present with strings 7/7 but **0/7 direct exact name matches** for each Cull/ZTest/AlphaToMask/ZWrite dynamic names. Original Shader property/Material saved Float matches only ZWrite 2/7 Pass×7 Renderer slots =14; other 3 fields all 0/7. Source program/CB binding and Android Shader48 still BLOCKED.
- [GFX-OWNER-002 CI42754132240](https://github.com/alwansan/raf/actions/runs/42754132240) SUCCESS **179 tests**: source saved `_Glossiness` exists seven slots and mismatches Standard fallback hardcoded 0.45 in **7/7**. Original Metallic Texture2D sRGB×7 differs Standard import Linear×7; original saved `_Metallic=0`, `_BumpScale=1`, `_GlossMapScale=1` seven slots. These are source/fallback differences, not a license to force gamma or claim original Shader48 runtime equivalence. Source private purge verified.
- **Decision NOT CLOSED**: static geometry/color/M00–M05 Standard preview and source texture roles PASS/PARTIAL; missing original Shader48 GLES3 program, 524 exact variant/tier pairing GPU parity, Material→DX11 t/s/CB offset mapping (RDEF absent 1275/1275), dynamic PassStates, original skinned bones/weights/animation, exact source Material import and PC-vs-Adreno pixel reference.
- Canonical phase gate and deferred worker playbook `gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md`; latest source session `memory/sessions/20261110-GFX-chat-material-delta-03.md` and parent owner sessions. Never create a worker before user gives agent instructions and G7–G12 actually pass. Independent water/FFT, fire/smoke, lighting and PostFX remain separate future phases. 


## GFX-MULTI-031 current auto-test capture after owner feedback
- [Source-free ZIP parser CI42801864098](https://github.com/alwansan/raf/actions/runs/42801864098) **SUCCESS, 191 tests**. `gfxlab/tools/auto_log_zip_audit.py` parses GFX-MULTI-031 owner ZIP with `sessions/*/events.jsonl` and `sessions/*/snapshots.jsonl`, reports per-model, role/channel/source-vs-linear/surface coverage, errors and missing/dropped records. Unlike old clipboard reports it does not require individually copied state messages and publishes no proprietary owner full error text.
- User wants direct `/storage/emulated/0/Download/Games/cl/test/g/` output. Java `GfxDownloadsBridge` uses Android `MediaStore.Downloads` on API29+, verifies published `RELATIVE_PATH` and file size, or displays failure and retains private ZIP. No broad storage permissions. GFX-MULTI-031 separate package `com.alwansan.raft.graphicslab.autologs` to coexist with GFX026 previous signing.
- Unity C# compile failure [CI42801247423](https://github.com/alwansan/raf/actions/runs/42801247423): ambiguous `CompressionLevel`; fixed explicit `System.IO.Compression.CompressionLevel`. The next real six-model signed build [CI42802005319](https://github.com/alwansan/raf/actions/runs/42802005319) is running Unity2021.3.45f2 Android IL2CPP ARM64. Do not claim finished until APK/signature/artifact passes.
- Detailed operating/owner-testing instructions: `gfxlab/ANDROID_AUTO_LOG_EXPORT_AR.md`. Exact MediaStore behavior on Xiaomi Adreno/Android 15 not yet tested by owner. This only solves test-log evidence capture, not original Shader48/GPU semantics/pixel parity. Next source steps in `gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md`, RENDER-002 OPEN.

## GFX-OWNER-003 — owner ZIP parsed and outstanding first-stage blockers (2026-11-10)
- Uploaded GFX-MULTI-031 auto export SHA256 `154f2367d12bf5be258d89c0517af8fecbf0c562b11feb5c03e33226161bb26d`, CRC PASS, 1 session/77 event/67 snapshot/0 Unity errors or dropped. All models M00–M05 and four fallback modes; diagnostics for Normal/Metallic/R/G/B/A/ForceLinear only on M00. M03 second surface absent.
- DEX signed APK validation [CI42806407666](https://github.com/alwansan/raf/actions/runs/42806407666) SUCCESS; ZIP parser per-model/M03 false-positive fix [CI42806757535](https://github.com/alwansan/raf/actions/runs/42806757535) SUCCESS, 193 tests. Safe aggregate `gfxlab/evidence/20261110_gfx031_owner_safe_counts.json`.
- P0 OPEN: Shader48 original 7-pass genuine shader program, 524 exact keyword/tier pairs and Material→source b/t/s/CB byte offsets, dynamic PassStates, rig, PC pixel matched reference. The fact that standard fallback has no Unity errors does NOT resolve them.
- P0 next: `GFX-MULTI-032` scan **381 unreferenced** Shader48 compiled programs (1656 original table -1275 unique referenced) for independent RDEF DXBC and possible alternate metadata, with type/identity guard and aggregate-only output. If no credible source map exists, keep `BLOCKED_NO_AUTHENTIC_MATERIAL_TO_CB_MAP`, never guess property ordering.
- P1 next owner test (only after true original shader candidate/mini GPU test): M03 surface2 and Normal/Metallic/RGBA SOURCE-vs-FORCE_LINEAR per model as separate stable logs; source Shader48, not Standard screenshot.

## GFX-MULTI-032 active evidence gap closure
- 381 original Shader48 compiled programs outside the 1,275 linked entries in GFX022; source-only bounded stage/RDEF table census `gfxlab/tools/multi_shader_unreferenced_reflection.py`, workflow [CI42807637443](https://github.com/alwansan/raf/actions/runs/42807637443).
- If unused RDEF present: report as **unlinked candidate metadata only**; still need independent source Pass/variant relationship and property→register matching. If absent: explicit `UNREFERENCED_RDEF_BRIDGE_NOT_FOUND`, request exact PC/ShaderLab/RenderDoc reference instead of filling gaps by inferred order.
- No new APK, work limited to source-private CI; retain phase G7–G12 blocked.

## GFX-MULTI-032 SUCCESS — exhaust remainder of Shader48 compiled table
- [CI42807637443](https://github.com/alwansan/raf/actions/runs/42807637443) SUCCESS 198 tests. Unused compiled Shader48 records: 381 = **112 empty** + **269 non-DX11 typed** + **0 DX11 with valid DXBC/RDEF**. This is not evidence that 269 non-DX11 programs are authentic Android Shader48 variants: all selected seven Passes and 524 exact variant pairs link to previously reviewed DX11 programs.
- P0 next **GFX-MULTI-033**: bounded non-DX11 candidate format census and search for *authentic* metadata links to an exact source Pass/keyword/tier. Keep unlinked type labels as unverified; no fabricated mapping or Android APK.
- P0 external dependency if no source program/Material binding emerges: genuine PC shader/material reflection or original ShaderLab with exact b/t/s + constant-buffer layout and pass-state information, plus reproducible matched capture.

## GFX-MULTI-033 outcome and GFX-MULTI-034 P0
- [GFX-MULTI-033 CI42808967835](https://github.com/alwansan/raf/actions/runs/42808967835) **SUCCESS**, 205 Python tests, authentic ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` and private purge. Of 381 unreferenced Shader48 compiled entries, 112 empty and **269 typed non-DX11 with code**: generic compiler type families **GLES 139, GLCore 120, D3D9 9, OTHER 1, Vulkan 0**. All 269 had no *leading* GLSL #version/SPIR-V magic, which does not exclude wrapped/embedded GLSL text. 7 original Passes have 28 alternative prog* fields but **zero** extra stage-variant rows and no linked unused entries. No exact Material property→register/CB proof; Shader48 Android runtime/restoration still FALSE. Safe aggregate [artifact 13762361127](https://github.com/alwansan/raf/actions/runs/42808967835/artifacts/13762361127) expires 2026-11-17T11:37:47Z.
- The 139 GLES / 120 GLCore **original table entries are unlinked to original seven Passes by serialized variant records**. Do not dismiss them based on absent *leading* #version: UnityPy's ShaderSubProgram exporter treats GL/GLES program bytes as text source. Investigate bounded UTF8/GLSL syntax + property-token overlap privately, preserving compiler/source-specific semantics and full source purge.
- If typed source text contains known property identifiers, this remains **candidate evidence** until exact program-to-Pass/keyword/tier mapping, CB layout, sampler binding, render-state and PC pixel tests. Do not convert names to guessed registers or create claimed full Shader48 APK.

## GFX-MULTI-034 success — next GFX-MULTI-035 framed source byte probe
- [GFX-MULTI-034 CI42809913702](https://github.com/alwansan/raf/actions/runs/42809913702) **SUCCESS**, 210 source-free tests, SHA-pinned original ZIP2, private cleanup passed. Across **139 unlinked GLES** type entries, strict UTF8 54, invalid UTF8/binary 85, embedded NUL 115. Across **120 unlinked GLCore**, strict UTF8 33, invalid UTF8 87, embedded NUL 106. Neither family had verifiable simple GLSL `#version`, `void main`, `uniform` or `sampler` declarations under full strict UTF8 plus comment-stripped matching. GLES only: 6 programs with exact source Shader48 property-token occurrences (3 unique authored properties, 3 unique texture properties, 1 unique bound texture property); **0 authentic Uniform property bridges**. GLCore 0 property tokens. No exact original Pass/keyword/tier links, no DX11 t/s/CB map, no GPU/PC pixel parity. Source bytes/proprietary names remain private. Artifact [13760603589](https://github.com/alwansan/raf/actions/runs/42809913702/artifacts/13760603589) expiry 2026-11-17T11:45:19Z.
- Hypothesis: GL code has binary framing or embedded strings; strict UTF8 whole-payload checks miss localized text. GFX-MULTI-035 should scan bounded original byte arrays privately for `#version`, `void main`, `uniform` and `sampler` ASCII markers, and optional source Material property token boundaries, plus safe offset buckets and embedded binary/NUL proportions. Do NOT publish raw snippets or original property names/identifiers.
- If markers absent, do not assume code can be built as GLSL; retain source evidence blocker and look for original PC capture or legal source ShaderLab. If positive, next require exact linked Pass/keyword/tier and CB/sampler mapping before Unity or Android original shader claims.

## GFX-MULTI-035 result — binary program resource names, no GLSL declaration identity
- [GFX-MULTI-035 CI42810629895](https://github.com/alwansan/raf/actions/runs/42810629895) **COMPLETED SUCCESS, 216 Python tests**, pinned original ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; private source purge passed. Among **139** unlinked GLES programs: **82** contain exact original Shader48 authored property byte tokens, **76** contain original bound material tokens; 14 distinct authored labels, 5 distinct texture labels, **all 3 bound material property labels**. Among **120** unlinked GLCore programs: **61** have authored property tokens, **60** have bound material tokens; same 14 authored /5 texture /3 bound distinct labels. **ZERO** `#version`, `void main`, `uniform`, sampler markers or 32-byte contiguous printable ASCII windows in either family; **zero** matched bound property tokens within uniform declarations. Embedded NUL in GLES 115/139 and GLCore 106/120. Thus binary payloads contain property-name tokens but **not verified plain GLSL or uniform binding**. No source Pass/keyword/tier link, Material→DX11 register/CB offsets, Android original shader runtime, PC pixel parity. Safe artifact [13762103464](https://github.com/alwansan/raf/actions/runs/42810629895/artifacts/13762103464) expires 2026-11-17T11:51:10Z; no original assets uploaded.
- **P0 next GFX-MULTI-036**: identify legitimate Unity 2021 GL compiled-program binary envelope and any documented constant-buffer / sampler / property binding records; verify source byte offsets/types/lengths first, then Shader48 source property names→real register/descriptor using authoritative format. A mere raw byte hit near a name is **not** resource binding. Use SHA-pinned private original source, bounded scans, no public raw code or source names.
- If there is no verifiable format, record `BLOCKED_SOURCE_GL_BINARY_RESOURCE_BINDINGS_UNDOCUMENTED` and request original PC shader/material reflection or original legally obtainable ShaderLab asset; do not make an APK claiming Shader48 success. Other independent first-phase gates: dynamic PassStates, exact 524 variant links, 100-bone rig & original animation, PC vs Adreno pixels.
