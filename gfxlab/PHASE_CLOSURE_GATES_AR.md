# GFX-LAB — شروط إغلاق استعادة الموديلات والمواد والشيدر المشترك
10 نوفمبر 2026 — تجربة GFX-MULTI-005 — Source-only

## ما أثبته هاتف المالك
ملف test model.zip احتوى 14 لقطة شاشة و12 JSON COPY LOG تغطي M00–M05 في SOURCE_ALBEDO_STANDARD وSOURCE_PBR_STANDARD_APPROX. جميع التقارير: Xiaomi 23013PC75G / Adreno730 / OpenGLES3 / Unity2021.3.45f2 / Linear؛ errors=0 وfirstError فارغ، originalShaderRestored=false، originalAnimationRestored=false، coloredPixelsAutomaticallyVerified=false.
الصور تؤكد ظهور الألوان والخامات على ستة نماذج في **Unity Standard fallback**، وتشمل M03 بمادتين. M04 يعرض قطعتين تشبهان ذراعين منفصلتين: قد يكون جزءًا أصليًا من الشخصية وليس خللًا. M05 مجسم مركب، لا إثبات أنه prefab كامل.
عدد رؤوس M01: مصدر 5095 مقابل Unity 4721. M04: مصدر 2445 مقابل Unity 2071. لا يكفي نجاح عدد المثلثات لإثبات سلامة تدفقات vertex/UV/tangent.

## الشيدر المستخدم فعلاً
GfxMultiAndroidBuilder.cs يستعمل Shader.Find("Standard") وShader.Find("Unlit/Color")، ويربط _MainTex و_BumpMap و_MetallicGlossMap. لم يستعد Shader48 الأصلي أو Passes الخاصة به على الهاتف؛ Shader48 في المصدر هو Class48 واحد، 2 SubShaders و7 Passes، بسبعة Material slots.

## بوابات الإغلاق قبل تحويل المسار إلى عامل آلي شامل
1. مصدر موثق: mesh/Renderer/submesh/transform/UV/normals/tangents/vertex colors وMaterial slots مطابقة.
2. اللون: Albedo sRGB، Normal DXT5nm channels/tangent، Metallic alpha/smoothness، filter/wrap/mips، tint وUV scale/offset، بدون فرض Standard الافتراضي.
3. الشيدر: لكل Pass أصلي stage IO/semantics، Render States (Blend/ZWrite/ZTest/Cull/ColorMask)، keywords، CB layout، samplers/texture binding؛ إثبات Source-to-Same-Export.
4. Android: برنامج ShaderLab مكافئ حقيقي على Unity2021 GLES3، isSupported/pass/variants/runtime shader identity مؤكدة؛ نجاح compile وحده لا يثبت صحة الصورة.
5. إثبات PC/هاتف: مشهد وإضاءة وكاميرا ومادة ثابتة، مقارنة PNG وخرائط normal/specular/depth، وتقييم بصري من المالك.
6. المجسمات Skinned/المركبة: bindposes/weights/bones/parent transform/Animator، تمييز الجزء المفرد عن prefab كامل.
7. بوابة التسليم: تماثل نموذج واحد end-to-end، ثم عينة متعددة المواد وأجزاء، ثم فقط تصميم عامل استعادة منفصل. الماء/FFT والنار/الدخان/Particles والإضاءة الخاصة مراحل منفصلة.

القرار: سلسلة Mesh+Textures+Standard على الهاتف نجحت في هذه العينة، أما **استعادة Shader الأصلي والـRig ومطابقة صورة PC فلم تُغلق**. GFX-MULTI-005 يقيس وجود بيانات الـPass/Render State/Vertex/Fragment الأصلية من ZIP2 داخل runner، ويخرج COUNTS فقط؛ لا يعلن التكافؤ أو يبني APK.

## GFX-MULTI-005 نتيجة CI المثبتة
[Run 42725841763](https://github.com/alwansan/raf/actions/runs/42725841763): SUCCESS، 48 tests PASS، بنية المصدر 2 SubShaders/7 Passes (4+3) مرتبطة بسبع materials/ستة Mesh، وبيانات Render State/Vertex/Fragment/Program Mask موجودة في **7 من 7 Passes**. هذه **حقول metadata فقط**، ولم نثبت ShaderLab GLES قابل للتنفيذ أو Keywords/CB/Sampler/Pass semantic parity أو صور PC. لا توجد APK جديدة؛ المصدر الخاص حُذف من Runner. Artifact safe summary 13721479793.

## GFX-MULTI-006 (فحص نسخ برنامج الشيدر)
التشغيل الأول 42726475369: source-only SUCCESS، وجد metadata لمنصة مترجمة واحدة وكتلة ضغط واحدة، لكن لم يرَ أي SubPrograms بالطريقة القديمة. **هذه ليست نتيجة فقدان shader**؛ Unity 2021.3 serializedVersion3 يمكن أن يستخدم m_PlayerSubPrograms بدل m_SubPrograms. عُدّل الفاحص لدعم الصيغتين وتشغيل اختبار جديد. لا يزال برنامج Android الأصلي غير مستعاد.

## GFX-MULTI-006/007 تحديثات مؤكدة
[006](https://github.com/alwansan/raf/actions/runs/42726999353): all seven source passes contain original m_PlayerSubPrograms source stage variants and keyword/blob index metadata, source COMPRESSED platform structure exists. This does not prove an Android GLSL executable.
[007](https://github.com/alwansan/raf/actions/runs/42727286357): every original OBJ vertex index is used (zero unreferenced) in six models, including M01/M04; source-vs-Unity 374 vertex delta NOT explained by unused source vertices. [008](https://github.com/alwansan/raf/actions/workflows/gfxlab-multi-obj-attribute-parity.yml) tests whether distinct source indices share identical float32 position/UV/normal attributes which Unity may merge. No claim of exact parity until CI and device independent evidence.

## GFX-MULTI-008 — إغلاق سؤال فرق Vertex count
[Run 42727777657](https://github.com/alwansan/raf/actions/runs/42727777657): SUCCESS و57 اختبار. source→float32 pos+UV+Normal unique tuple يساوي Unity imported vertices في جميع الموديلات الستة. M01 وM04 الفرق 374 مفسَّر بالصفات المتطابقة، وM02 الفرق 4 كذلك؛ لا دليل فقدان faces من فرق الأعداد. **يبقى اختبار reindexed triangles وtangents/rig/scene assembly**. هذا لا يغلق الاستعادة الأصلية للشيدر.

## 2026-11-10 — المرحلة ما زالت OPEN رغم نجاح 7/7 pass CPU
[GFX-MULTI-013](https://github.com/alwansan/raf/actions/runs/42732808109) 7/7 source Shader48 passes have valid representative CPU DXBC→SPIR-V→GLSL ES310 stage conversion and interface location/type parity. No material/texture Register/CB/sampler binding parity, real ShaderLab implementation, full source variant coverage, Android Adreno GPU proof or PC pixel matched comparison yet. Before delegation close one exact source Material+Mesh representative end-to-end, then multi-material and skinned assembly; water/FFT, smoke/fire, dedicated lighting remain separate.
