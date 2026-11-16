# التقدم وما بقي والفحوص

لقطة 15 تشرين الثاني 2026. المراحل أدناه تعرّف بالضبط نطاق كل نتيجة.

## نتائج مؤكدة

- التصدير الكامل طابق 4,708 Mesh و4,903 قيمة لون عبر 1,536 مادة. طابق أيضاً 28 خانة مواد للتسع مصفوفات و416 Texture PPtr بين 82 حاوية مصدر. نجح فحص وجهات Shader48 في نفس التصدير. [التصدير الكامل](https://github.com/alwansan/raf/actions/runs/43650105238) · [أحدث تصدير وجرد](https://github.com/alwansan/raf/actions/runs/43651736236)
- داخل حزمة Unity Android، تطابقت بيانات BC3 الأصلية لكل مستويات mip في 50 طبقة، 69,906,400 بايت، وإعدادات أخذ العينة. المجموعة 9 مصفوفات و52 طبقة منطقية. مصفوفة واحدة لها طبقتان بلا بيانات بكسل streamed من المصدر وتشير لها 20 من الخانات الـ28. [فحص الحزمة](https://github.com/alwansan/raf/actions/runs/43650541516)
- ثبت FFT على نفس GUID في فحص التصدير الكامل. حزمة Unity Vulkan سجلت النوى العشرين بترتيبها، وأثبت اختبار الاستيراد أن مراجع YAML من نوع 2 تحتاج النوع 3 عند تحويل الأصل إلى ‎.compute. [فحص FFT](https://github.com/alwansan/raf/actions/runs/43597273405)
- مسار إعادة بناء أندرويد فيه استعادة BlockPaint وDirtPile وVegetation وGrassPlot وShimmer وSailPaint وHair_Amplify، كل واحد 33 مساراً؛ Skin_Amplify له 23. فحص الحزمة لكل واحد تحقق من الرؤوس والبكسل. [BlockPaint](https://github.com/alwansan/raf/actions/runs/43623765635) · [DirtPile](https://github.com/alwansan/raf/actions/runs/43623908891) · [Vegetation](https://github.com/alwansan/raf/actions/runs/43624204417) · [GrassPlot](https://github.com/alwansan/raf/actions/runs/43624034479) · [Skin](https://github.com/alwansan/raf/actions/runs/43650416069) · [Shimmer](https://github.com/alwansan/raf/actions/runs/43650691520) · [SailPaint](https://github.com/alwansan/raf/actions/runs/43650804611) · [Hair](https://github.com/alwansan/raf/actions/runs/43650911142)
- مؤثرات Particle108 وSmoke34 وCandle16 وParticleShader مدموجة في مسار إعادة البناء. فحص ParticleShader المصحح اجتاز ترجمة حزمة Vulkan وتطابق البصمة لأربع تركيبات، وهو نفس الاستعادة المعروفة في الكود باسم Particle20. [ParticleShader](https://github.com/alwansan/raf/actions/runs/43651595674)

## الأرقام اللي تحدد الأولوية

جرد التصدير الخام على 8ca634490 أحصى 786 مادة على 64 معرّف شيدر مؤقت. تقرير البصمات يضم 62 اسم شيدر مميزاً لأن التجميع حسب الاسم قد يجمع أكثر من معرّف. جرد استعادة TMP/PostFX/Volumetric القديم خفّض الرقم إلى 770 قبل تثبيت دفعات المشروع الحالية. عدد المواد المتبقية بعد دمج كل الشيدرات **بعده غير مقاس**.

| شيدر | مواد التصدير الخام حسب بصمة الاسم |
| --- | ---: |
| Skin_Amplify | 208 |
| Shimmer | 96 |
| BlockPaint | 87 |
| ParticleShader | 48 |
| Vegetation | 29 |
| Hair_Amplify | 9 |
| BillboardFade | 5 |
| DirtPile، GrassPlot، SailPaint | 1 لكل شيدر |

هذه أعداد وثائق المواد، وتختلف عن عدد خانات استخدامها المتكررة في المشاهد. مثال BlockPaint مرتبط بـ921 خانة في عينة المشاهد. [الجرد الكامل](https://github.com/alwansan/raf/actions/runs/43651736236)

## مفتوح وفحوص مطلوبة

- **BillboardFade:** اجتاز المصدر 19 برنامج DXBC و9 أزواج و18 مرحلة و6 خصائص. نجح فحص Unity Android Vulkan المعزول في التشغيل [43723487222](https://github.com/alwansan/raf/actions/runs/43723487222): تمريرتان ForwardBase/ForwardAdd و9 مسارات [4,5]، وأخطاء المترجم صفر، وتحقق جدول البرامج/مداخل VS وFS. أضيف التثبيت في مسار الإنتاج مع فحص البصمة وحماية `.meta` وGUID في [d2d00b9](https://github.com/alwansan/raf/commit/d2d00b9810de1724248f95601d8f91a86e757654). **لم يثبت بعد تنفيذ تلك الخطوات على التصدير الكامل.** [دليل الحزمة](../../evidence/20261115_gt_billboard_unity_bundle.json) · [تقرير المصدر](../../evidence/20261115_gt_billboard_source.json)
- **دمج فعلي كامل:** إعادة بناء المشروع مع **كل** خطوات التثبيت ثم فحص مواد المشروع بعد الاستعادة. أضيف `--rank-dummy-targets` إلى جرد الإنتاج بعد خطوات الاستعادة لكي يسجل عدد المواد المتبقية حسب بصمة اسم الشيدر. **786 خام و770 بعد Vendor فقط**، ولا توجد إلى الآن قيمة مؤكدة بعد دمج كل شيدرات المجسمات وBillboardFade؛ لا تطرح الأرقام حسابياً بدل القياس. اختبارات Unity المعزولة وفحص وجهة الـGUID لا تثبت هذا الدمج.
- **تكافؤ بصري وقت التشغيل:** فحص ظهور الألوان والمواد، الغطاء الأسود حول النار، الماء والرغوة واختيار مسارات الشيدر وربط الـCB والـsampler على الجهاز. فحص حزمة Vulkan لا يثبت إخراج البكسلات أو دعم GLES.
- **قبل تسليم XAPK:** أحدث Commit في CL هو `3c26bb5d0f4de2cbffd42197dae9ae1372721659` بتاريخ 13 نوفمبر 2026، ولا توجد صورة جهاز أحدث تثبت التكافؤ. فحص BillboardFade إضافي **من دون XAPK** بدأ برقم [43759121385](https://github.com/alwansan/raf/actions/runs/43759121385) (الحالة عند تدوين الملاحظة: قيد التشغيل). لا يبدأ XAPK حتى إتمام الاستعادة. الأنيميشن مؤجل حسب توجيه المالك.

## تنفيذ 15 تشرين الثاني — فحص التكامل دون لعبة

- اكتمل فحص BillboardFade المعزول الثاني [43759121385](https://github.com/alwansan/raf/actions/runs/43759121385) بنجاح، شاملاً اختبار رفض إيصال ناقص لمسار ForwardAdd وحماية GUID الأصلي.
- أُضيف في [f7fcd808](https://github.com/alwansan/raf/commit/f7fcd808e08ba4d3bcccd033b4694fa59bfa8ba7) مسار تصدير كامل من ZIP2 لتجميع شيدرات المجسمات التسعة داخل Unity Vulkan وتثبيتها بنفس export instance، **من دون بناء APK/OBB/XAPK**.
- بدأ التشغيل [43759856414](https://github.com/alwansan/raf/actions/runs/43759856414)، وكانت مرحلته عند التوثيق تنزيل ZIP2، والحالة النهائية مجهولة. اختبار ما بعد التثبيت يتحقق من ثبات بصمات جميع ملفات Material/YAML و`.meta`، ويصدر جرداً رقمياً جديداً لبصمات أسماء شيدرات Dummy الباقية.
- **لا تجعل 786 أو 770 نسبة الإنجاز الحالية**؛ الجرد الجديد ينتظر نجاح كل مراحل التشغيل المذكور. إذا فشل أي شيدر، أصلح سبب الفشل قبل اعتماد أي عدد.

## متابعة 16 تشرين الثاني 2026 — شفافية المؤثرات

- تحقق حي من تشغيل الدمج الكامل [43759856414](https://github.com/alwansan/raf/actions/runs/43759856414): تم فحص الـZIP2 الحقيقي، مطابقة المصدر، إعادة بناء الـMesh والخامات، واستعادة BlockPaint وDirtPile وVegetation على GUID الأصل في نفس التصدير. آخر قراءة للوظيفة كانت عند استعادة GrassPlot؛ لا تتجاوز ما تثبته خطوة Actions المكتملة.
- أضيف الفاحص `scripts/gt_particle108_export_alpha_diagnostic.py` ونجحت اختباراته الصناعية في [43762000860](https://github.com/alwansan/raf/actions/runs/43762000860). يحدد الـ3 Texture2D الحقيقية لسلسلة Particle108 (5 مواد و10 مراجع) عبر Trace واحد، ويقيس شفافية الصور المصدرّة وإعدادات importer من دون تعديل الأصل أو تسريب الصور. **لم يُنفذ الفاحص على تصدير اللعبة الحقيقي بعد**؛ لا تعتبر المربع الأسود حول النار مُصلحاً.
- [دليل مرحلة الفحص](../../evidence/20261116_gt_particle108_alpha_static_test.json). اختبار الهاتف محجوب حتى اكتمال استعادة بقية الرسوم حسب قرار المالك، والأنيميشن مؤجل.

- **تشخيص فعلي مستقل لشفافية Particle108:** أُطلق تشغيل [43762318768](https://github.com/alwansan/raf/actions/runs/43762318768) على مسار `.github/workflows/raft-gt-particle108-alpha-real-export.yml` (SHA `6a8162423f086782e803ae70af58b842ebe51528`). يستخدم ZIP2 الكامل وAssetRipper ونفس-instance Texture GUID Trace لفحص 3 Texture2D. النتيجة لم تكن متوفرة عند التوثيق؛ لا تخلط نجاح اختبار Pillow الصناعي مع إثبات Alpha حقيقي أو Pixel Vulkan على الهاتف.

## نتيجة نهائية مثبتة للتشغيل 43759856414 — 16 تشرين الثاني

- **التشغيل:** [43759856414](https://github.com/alwansan/raf/actions/runs/43759856414) انتهى **SUCCESS**. شيدرات BlockPaint/DirtPile/Vegetation/GrassPlot/Skin_Amplify/Shimmer/SailPaint/Hair_Amplify/BillboardFade اجتازت استعادة المصدر، Unity Android Vulkan، والتحقق والتثبيت على GUID نفس التصدير. **لا APK/XAPK**.
- **جرد المواد الحقيقي:** 1536 مستند Material، منها 750 Builtin و786 Custom. Custom المستعاد = **453**، والمتبقي Dummy = **333**، يشير إلى **51 شيدر Dummy متميز مرتبط بمواد فعلياً**. خام التصدير 786 Dummy، وبعد Vendor فقط 770، وبعد التسعة الأصلية 333. تغطية 453/786 = **57.6% من مواد Custom**، لا من رسوم اللعبة كلها.
- **سلامة الروابط:** SHA تحقق أن **29213** ملف Material/.meta/YAML ظل ببايتاته نفسها أثناء تثبيت التسعة، و0 مراجع Shader مكسورة أو مجهولة.
- **ترتيب المتبقي:** أعلى Material links إلى Dummy shader حسب بصمة اسم مجهولة: 48، 30، 26، 23، 23، 18، 17، 15 ثم 11 وغيرها؛ نحتاج private source-to-export join قبل استعادة الشيدرات التالية، ولا نعتبر عدد المواد عدد مجسمات بيضاء.
- **الدليل:** [قبول الدمج التساعي](../../evidence/20261116_gt_nine_original_shader_same_export_acceptance.json). تكافؤ Adreno الفعلي، النار والماء مفتوح. تشغيل فحص Alpha الحقيقي الأول [43762318768](https://github.com/alwansan/raf/actions/runs/43762318768) فشل من دون تصنيف المرحلة، وأضيف failure_stage وشُغّل [43763158214](https://github.com/alwansan/raf/actions/runs/43763158214) لإصلاح السبب.

### متابعة بعد استعادة الشيدرات التسعة — 16 تشرين الثاني

- نجح [43763883804](https://github.com/alwansan/raf/actions/runs/43763883804): مطابقة بصمة اسم Shader أصلي لـ8 مصادر Shader48 فريدة من ستة مشاهد مع 101 مستند Material Dummy من أصل 333. أوزان Material links هي 48/26/11/7/4/2/2/1، وأوزان Renderer Slots المقابلة 20/16/108/1/1/34/1/1. بقيت 232 مادة خارج نطاق المطابقة. **هذه مطابقة اسم وليس إثبات source-to-export GUID.**
- انطلق [43764506277](https://github.com/alwansan/raf/actions/runs/43764506277) بعد إضافة شيدرات Particle108 وParticle20 وSmoke34 وCandle16 إلى اختبار التصدير الكامل بعد التسعة، مع Unity Vulkan وإعادة جرد المواد وفحص بقاء 29213 ملف Material/meta ثابتاً. لا APK/OBB/XAPK. النتيجة النهائية مفتوحة.
- فحص Alpha الأول [43762318768](https://github.com/alwansan/raf/actions/runs/43762318768) فشل. الفحص الثاني [43763158214](https://github.com/alwansan/raf/actions/runs/43763158214) حصره في مرحلة join_same_export_Texture2D28_GUID. أضيف فحص عددي آمن لتمييز غياب المصدر/التكرار/نوع مؤشر GUID وأطلق [43764070678](https://github.com/alwansan/raf/actions/runs/43764070678).
- [دليل المصدر](../../evidence/20261116_gt_333_remaining_original_scene_shader_correlations.json) و[تقرير التسعة الناجح](../../evidence/20261116_gt_nine_original_shader_same_export_acceptance.json).

### إثبات شمول جميع مصادر Shader48 — 16 تشرين الثاني

- [43766412259](https://github.com/alwansan/raf/actions/runs/43766412259) نجح: في الـ82 أصل ZIP2 المدقق SHA توجد 165 كائن Shader48 في 14 مالكاً و163 اسماً. من 333 مادة Dummy بعد التسعة: **330** تحمل أسماء أصلية فريدة (48 هدفاً)، و**3** تحمل اسماً مكرراً لدى 3 كائنات Shader48، و**0** أسماء خارج الأصل. هذا دليل وجود مصدر لكل اسم وليس استعادة GPU أو GUID النهائي.
- [43766959343](https://github.com/alwansan/raf/actions/runs/43766959343) يفحص برامج D3D11 الأصلية للأسماء الـ12 الأعلى أثراً ويصدر أعداد SubShader/Pass/VS-FS variant pairs فقط، دون ملفات مصدر أو XAPK؛ لم تثبت نتيجته النهائية حتى الآن.
- [43766815679](https://github.com/alwansan/raf/actions/runs/43766815679) يعيد اختبار Alpha مع فصل خطوة تحليل Material YAML عن خطوة مطابقة TexEnv ومع أسباب فشل آمنة. إخفاقات Alpha السابقة لا تعني إصلاح النار.
- [تقرير التغطية](../../evidence/20261116_gt_all82_original_shader48_remaining_materials.json).

### تأكيد التسعة زائد الأربعة من المصدر — 16 تشرين الثاني

- [43764506277](https://github.com/alwansan/raf/actions/runs/43764506277) **SUCCESS**: شيدرات BlockPaint/DirtPile/Vegetation/GrassPlot/Skin_Amplify/Shimmer/SailPaint/Hair_Amplify/BillboardFade وParticle108/Particle20/Smoke34/Candle16 جميعها جمعت وفُحصت في Unity Android Vulkan وتثبتت على الـShader GUID الأصلي في نفس المصدر. من 786 مادة Custom، **540 non-Dummy (68.7%)** و**246 Dummy** موزعة على **47 هدفاً مستخدماً**. بنيت 0 حزمة لعبة، ولم تتغير 29213 ملف Material/Meta. [دليل أصلي](../../evidence/20261116_gt_thirteen_original_shader_same_export_acceptance.json).
- [43768013634](https://github.com/alwansan/raf/actions/runs/43768013634) **SUCCESS**: next30 أصل Shader48، 55 Vulkan1.1/HLSL verified، 4-Pass ShaderLab original property bindings، 62 entrypoints verified. [دليل المصدر](../../evidence/20261116_gt_next30_original_shader48_all55_vulkan_stage_proof.json).
- [43768744473](https://github.com/alwansan/raf/actions/runs/43768744473): Unity isolated real Android Vulkan ShaderBundle testing للـnext30، والنتيجة عند كتابة هذه الملاحظات مفتوحة. [43768958865](https://github.com/alwansan/raf/actions/runs/43768958865) يربط جرد مصادر Shader48 من الـ82 مالكاً مع **246** مادة بعد 13، وليس 333 بعد تسعة.
- [43767741576](https://github.com/alwansan/raf/actions/runs/43767741576) فشل باختبار Alpha real مع دليل محلي جديد: 9 exported external PPtr من عشرة type3/fileID 2800000، وواحد type0 internal nonzero. هذا مسار ربط، لا دليل Alpha pixels مفقودة. فحص متابعة [43767766873](https://github.com/alwansan/raf/actions/runs/43767766873). لا نعلن إصلاح fire/water المرئي.


### أحدث حالة موثقة – 16 نوفمبر 2026
- [43764506277](https://github.com/alwansan/raf/actions/runs/43764506277) SUCCESS: 13 Shader48 أصلياً مثبتاً على GUID الأصلي في نفس Unity export؛ 540/786 non-Dummy مقابل 246 Dummy على 47 shader targets، 0 broken، و29213 Material/meta/YAML untouched. لا لعبة APK/XAPK.
- [43768958865](https://github.com/alwansan/raf/actions/runs/43768958865) SUCCESS: 82 original SHA-authenticated owners، 165 Shader48، و243 مادة Dummy تطابق اسماً أصلياً فريداً مقابل 3 مواد متشابهة الاسم، وصفر غير معروف.
- [43768013634](https://github.com/alwansan/raf/actions/runs/43768013634) SUCCESS: next30 55/55 DXBC→Vulkan/HLSL؛ [43768744473](https://github.com/alwansan/raf/actions/runs/43768744473) SUCCESS Unity Android Vulkan 4 Pass و31 routes و0 errors؛ [43769218778](https://github.com/alwansan/raf/actions/runs/43769218778) SUCCESS serialized Vulkan bundle verified [8,13,8,2] Vertex/Fragment؛ [43769866165](https://github.com/alwansan/raf/actions/runs/43769866165) SUCCESS synthetic protected installer. هذه لا تعني إثبات تثبيت next30 في التصدير الأصلي بعد.
- [43767766873](https://github.com/alwansan/raf/actions/runs/43767766873) FAILED: مصدر Particle108 خمس Materials وعشرة TexEnv؛ تسعة type3 fileID 2800000 صحيحة وواحد local type0. لا Alpha pixels أو Adreno proof.
- اقرأ دائماً https://github.com/alwansan/raf/blob/feature/android-native-port/clients/GT/RESTORE_AR.md قبل الاستكمال. لا XAPK حتى إكمال الاستعادة.

### CI جديد بعد تحديث RESTORE_AR — 16 نوفمبر 2026
- بدأ [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176) في full ZIP2 same-export بعد التسعة وأربعة Particle لإعادة بناء وترجمة وتثبيت next30 Shader48 مع الحفاظ على GUID الأصلي والتحقق من 31 VS/FS Vulkan routes. يراجع 29213 Material/meta/YAML محمي، ويعيد حساب المواد الحقيقية. **العدد المستهدف فقط**: 570 non-Dummy / 216 Dummy / 46 shader references؛ **آخر قيمة مثبتة لا تزال** 540 non-Dummy / 246 Dummy / 47 shader references، إلى أن تنتهي CI بنجاح. لا APK/XAPK. يجب فحص نتائج run وتحديث clients/GT/RESTORE_AR.md و01/02/03 مجدداً فور ظهور دليل جديد.

### تقدم 23 مادة – 16 نوفمبر
- بدأ [43773953670](https://github.com/alwansan/raf/actions/runs/43773953670) فحص source-only الأصلي لاستعادة شيدر يربط 23 مادة Custom Dummy، فيه 4 Pass / 33 زوج VS/FS / 8 VS orphans / 58 برنامج D3D11 أصلي، مع تمييزه عن شيدر آخر له 23 مادة لكنه يحتوي 1156 variants ولا يجوز اختزاله. بوابة الجرد كل الـ82 owner من ZIP2 SHA. لم يثبت Unity أو GUID بعد، ولن ينشئ XAPK. افحص النتيجة عند العودة ثم حدّث RESTORE_AR.md أولاً والخطة/الاختبارات/الدليل. العدد المثبت يبقى 246 Dummy حتى قبول نفس التصدير في [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176).

### أحدث نتائج 16 نوفمبر — next23 original source PASSED، Unity Vulkan مفتوح
- [43774524669](https://github.com/alwansan/raf/actions/runs/43774524669) SUCCESS: شيدر 23 Material أصلي، 58/58 D3D11→Vulkan/HLSL، 33 VS/FS + 8 orphan VS، 66 routed stage compilations، 74 parameter records، 1192 CB offsets و552 Texture/Sampler mappings و236 varyings، 17 property بينها 3 Range وDefault واحد خارج bounds حفظ كما هو. فحص Source فقط، لا GUID.
- [43774787696](https://github.com/alwansan/raf/actions/runs/43774787696) بدأ private Unity Android Vulkan bundle للتحقق من 4 Pass و33 VS/FS routes بالـSMOL-V. لم تقبل نتيجته حتى الآن. بعد PASS يتوجب تثبيت original Shader48 عبر نفس source→export GUID في التصدير الأصلي وفحص مواد Dummy.
- [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176) next30 في full export لا يزال بلا نتيجة نهائية. آخر أرقام يقينية: **540/786 non-Dummy، 246 Dummy، 47 Shader targets**؛ لا XAPK. ملف المصدر الرئيسي الحي: clients/GT/RESTORE_AR.md؛ حدّثه في كل دفعة.

## تحديث التحقق الحي — 16 نوفمبر 2026 / GT

| مستوى الإثبات | الدليل | الخلاصة |
| --- | --- | --- |
| SOURCE | [43774524669](https://github.com/alwansan/raf/actions/runs/43774524669) | NEXT23: 58/58 original D3D11→Vulkan roundtrip، 4 Pass، 33 VS/FS [8,13,8,4]، 8 orphan VS |
| ISOLATED UNITY | [43774787696](https://github.com/alwansan/raf/actions/runs/43774787696) | SUCCESS Unity 2021.3.45f2 Android Vulkan bundle، 33 VS و33 FS متحقق منها؛ ليس تثبيت GUID |
| SAME-EXPORT GUID | [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176) | NEXT30 SUCCESS أصل source SHA→GUID و31 Vulkan route: 570/786 non-Dummy، 216 Dummy، 46 targets، 0 broken، 29213 YAML/meta unchanged |
| DEVICE VISUAL | لا قياس جديد | لا إثبات إزالة بياض المواد أو مربع النار أو استعادة Water/GPU بالكامل |

- artifact NEXT30: `gt-fourteen-next30-source-shader-full-export-audit-43773151176`، ID `14186801044`، digest zip `sha256:41f5ba7bbcd1accca6e04b60902749cffdecaf5ce9c1febe607d1abef173b8cd`. Commit التشغيل `988490597b63f6c404536b4b311c03d0f6d3f8dc`؛ 570/786 = **72.5% من Custom Material documents** فقط.
- فشل سابق [43773953670](https://github.com/alwansan/raf/actions/runs/43773953670) أُصلح باختبار المصدر [43774524669](https://github.com/alwansan/raf/actions/runs/43774524669). فشل FireAlpha الواقعي 43773481136 و43773517218 لم يُحل بنجاح الاختبار الصناعي 43773517246.
- **المتبقي** 216 مادة Dummy و46 Shader reference targets؛ NEXT23 يحتاج same-export install وأرقام post15 من فحص حي، لا من طرح 23. ماء Spectrum/Foam/Depth/FFT وKernel6 والظلال/الشفافية وAndroid device parity غير مقبولة بعد. لا لعبة XAPK.

## دفعة برمجة لم تُعتمد بصرياً — 16 نوفمبر 2026

- تأكدت نتيجة [43777739448](https://github.com/alwansan/raf/actions/runs/43777739448) **SUCCESS**؛ job `133007783009` نجح في فحص `py_compile` واختبارات `test_gt_install_next23_original_shader48.py` و`test_gt_install_next30_original_shader48.py`. هذا **دليل اختبارات صناعية فقط** وليس تثبيتاً على GUID في التصدير الكامل؛ آخر رقم فعلي **216 Dummy / 46 Shader targets**.


- بدء [43777739448](https://github.com/alwansan/raf/actions/runs/43777739448) للـunit static fail-closed next23 بعد إضافة workflow `raft-gt-next23-installer-static-gate.yml`، لا تحويله إلى ادعاء same-export.\n\n

- أُضيف [مثبت NEXT23](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/gt_install_next23_original_shader48.py): حارس 216/46 post14، 165 source Shader48 SHA، تمييز shader الـ23 الصحيح بالتوبولوجيا (شيدر آخر 23 مادة مختلف 1156 variants)، receipt Unity [8,13,8,4] VS/FS، ومطابقة source owner/PathID لنفس exporter ShaderGUID مع حفظ .meta. آخر Unity isolated ناجح 43774787696؛ اختبار التثبيت الحقيقي 43777283111 لم ينتهِ.
- أضيف جرد post15 بعد التثبيت، يرفض كل خروج عن المتوقع 1536 total/750 Builtin/786 Custom و193 Dummy/593 non-Dummy/45 targets و0 broken أو تغير أي ملف من 29213. **كلها assert أهداف وليست نتيجة مثبتة حتى SUCCESS**.
- كود [فاحص النار](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/gt_particle108_export_alpha_diagnostic.py) صار يتحقق direct Texture2D trace مقابل external material GUID **subset** فقط مع إبقاء local PPtr type0 خارج الصور المصدرة؛ إضافة [اختبارات](https://github.com/alwansan/raf/blob/feature/android-native-port/tests/test_gt_particle108_export_alpha_diagnostic.py). [43777415580](https://github.com/alwansan/raf/actions/runs/43777415580) SUCCESS للاختبار الاصطناعي؛ [43777415610](https://github.com/alwansan/raf/actions/runs/43777415610) real pending؛ Alpha pixel على الهاتف غير مثبت.
- وثيقة الدليل: [20261116_gt_next30_post14_next23_and_particle108_progress.json](../../evidence/20261116_gt_next30_post14_next23_and_particle108_progress.json).

## FireAlpha تصدير حقيقي نجح جزئياً — 16 نوفمبر

- [43777398215](https://github.com/alwansan/raf/actions/runs/43777398215) **SUCCESS** job `133006699574` على ZIP2/AssetRipper: `GT_PARTICLE108_TWO_EXTERNAL_ALPHA_IMAGES_ONE_LOCAL_TEXTURE_PPTR_PENDING`. `linked_exported_images_decoded=2` و`has_explicit_alpha=2` و`all_opaque=1` و`has_transparent_pixels=1` و`has_partially_transparent_pixels=1` و`fully_transparent_pixel_present=1`. `alphaIsTransparency=1` للاثنتين؛ `alphaSource` و`mipmapEnabled` غائبان؛ `original_source_texture_pixels_compared=false` و`android_device_fire_pixels_verified=false`. Artifact ID 14187007842 (digest `sha256:fef3c6dd93accdb736b89e4673281a8ccc5f80be7b45d1e7e6922c9e318f426e`).
- [43778269494](https://github.com/alwansan/raf/actions/runs/43778269494) **SUCCESS** لاختبار comparator `classify_original_local_texture_trace` الذي يميز تطابق/اختلاف/غياب local PPtr مقابل class28 original source trace دون اختلاق external importer. Real [43778269514](https://github.com/alwansan/raf/actions/runs/43778269514) لم يقبل بعد. تقرير FIRE لا يثبت shader blend أو نتيجة هاتف.
- NEXT23 ما يزال same-export غير مثبت، آخر Material census مؤكد 216 Dummy على 46 targets من 43773151176؛ G0-G6 مفتوحة.

## دليل إضافي مثبت: post14/source Shader48 top16 — 16 نوفمبر

- [43779089456](https://github.com/alwansan/raf/actions/runs/43779089456) **SUCCESS** job `133011977501`: تنزيل تقرير NEXT30 الحقيقي، اجتياز `GT_POST14_REAL_EXPORT_216_MATERIAL_46_GUID_BASELINE_ACCEPTED`، ثم فحص 82 owner SHA و165 Shader48 على 14 مصدر و16 هوية مفردة. عشرات حالات التوبولوجيا، بينها (Material docs,Passes,VS/FS routes,D3D11 unique programs): (23,4,1156,134)، (23,4,33,58)، (18,4,33,58)، (17,3,23,43)، (15,4,33,58)، (11,4,33,58). Artifact `gt-post14-original-216-Dummy-shader-topology-43779089456` ID `14187109374`, SHA256 ZIP `fb3a8383cfe88df192718ada0b3506b3f8bd923eb4c0bc0737eedb95eaf4203c`. **Source only: no DXBC translation, no Unity, no Shader GUID install, no GPU**.
- [43778988866](https://github.com/alwansan/raf/actions/runs/43778988866) FAILED أولاً بسبب `FileNotFoundError` عند القراءة الافتراضية لجذر Artifact؛ أصلحت القراءة باستخدام `rglob` unique file في `379bb8b`، [43779089456](https://github.com/alwansan/raf/actions/runs/43779089456) أثبت PASS بعدها. فشل wrapper لا دليل تلف Shader48 الأصلي.
- NEXT18 Source run [43779460803](https://github.com/alwansan/raf/actions/runs/43779460803) انطلق على source SHA مع `216/46` وتوبولوجيا `4/33/8/58` متوقعة، لا نجاح يضاف قبل run result. اسم المصدر/GUID/Programs لا تُرفع.
- Fire local type0 SHA-original top-mip classifier + exact same export PPtr helper في `gt_particle108_export_alpha_diagnostic.py`؛ static tests [43778717524](https://github.com/alwansan/raf/actions/runs/43778717524) SUCCESS، real [43778717548](https://github.com/alwansan/raf/actions/runs/43778717548) قيد التنفيذ. Base Fire evidence [43777398215](https://github.com/alwansan/raf/actions/runs/43777398215) success partial للاثنتين فقط، لا Android visual parity.
- Material coverage لم تتغير بعد هذه الفحوص: 570/786 non-Dummy (72.5% من Custom Material documents فقط)، 216 Dummy على 46 GUID targets؛ G0-G6 مفتوحة.

## دليل واقعي جديد + فشل Next18 محصور — 16 نوفمبر

- [43778717548](https://github.com/alwansan/raf/actions/runs/43778717548) **SUCCESS** ZIP2/AssetRipper؛ `same_export_original_local_PPtr_matches_Texture2D28_trace=true`, `original_local_Type0_Texture2D28_source_top_mip_alpha_decoded=true`; source RGB/alpha profile: `has_explicit_alpha=true`, `all_opaque=false`, `has_transparent_pixels=true`, `has_partially_transparent_pixels=true`, `fully_transparent_pixel_present=true`. `original_local_Type0_external_GUID_inferred=false`; `original_local_Type0_texture_has_exported_image_proof=false`; `original_local_Type0_original_and_exported_pixels_compared=false`; phone FireAlpha unverified. Artifact `14187855918` digest `sha256:34075724eda74d28f5c6a780e01958239907b8fe0dadeeda842b23e60f4d0198`.
- [43779460803](https://github.com/alwansan/raf/actions/runs/43779460803) **FAILED** عند تركيب original ShaderLab NEXT18، رغم 58/58 D3D11→Vulkan11/HLSL validated و66 source routed stages compile و33 VSFS/8 orphan VS؛ السبب حارس ثابت `3 Range/1 outside` من NEXT23 على Shader48 مختلف، وليس فشل D3D11. أصلحته في `84e79b0` مع `validate_authentic_source_ranges` و`allow_out_of_range_defaults` فقط لما يثبته المصدر، واختبار `36b12fa`. runs [43779759999](https://github.com/alwansan/raf/actions/runs/43779759999) و[43779784096](https://github.com/alwansan/raf/actions/runs/43779784096) لم يُقبل بعد إكمالها.
- post14 exact counted material 570/786 non-Dummy و216 Dummy/46 targets، 29213 meta/material/YAML unchanged، 0 broken. No next18 Unity bundle or GUID install or visual claim.

## GT — استمرار الاختبارات المستقلة 16 نوفمبر

- [43779759999](https://github.com/alwansan/raf/actions/runs/43779759999) **SUCCESS source** و[43779784096](https://github.com/alwansan/raf/actions/runs/43779784096) **SUCCESS source** بعد تحويل NEXT18 Range contract إلى أرقام أصلية: 15 properties، 7 Range/0 outside، 58 D3D11/66 stage compiles و33 paired VSFS، `private_original_18_material_ShaderLab_4pass_composed=true`. Artifact source-safe ID `14187499272`, SHA256 `d9d8f1277fa1859b5d418c6c45b10c665aef20f32078743465d18d406a2cec06`. لا Unity/GUID/device proof.
- [43780123319](https://github.com/alwansan/raf/actions/runs/43780123319) FAILED YAML validation (no jobs) بسبب `printf '%s\\n'` broken newline؛ أصلح [a8d7b001](https://github.com/alwansan/raf/commit/a8d7b0012e197756734bcfbd19b2446cdf512bf5)، Unity isolated [43780219002](https://github.com/alwansan/raf/actions/runs/43780219002) at real Android Vulkan compiler, no final proof yet.
- [43780491219](https://github.com/alwansan/raf/actions/runs/43780491219) next17 SOURCE SHA-original 17 Material/43 programs/23 keyword routes/3 Pass started, current source translation, no result adopted. NEXT23 full same-export still pending final.
- FireAlpha [43778717548](https://github.com/alwansan/raf/actions/runs/43778717548) real original local type0 PPtr same-export class28 exact matched + original top mip alpha decoded; no exported PNG/GUID or device pixel acceptance.
- Last accepted: 570/786 Custom non-Dummy (72.5% CUSTOM MATERIAL COVERAGE ONLY), 216 Dummy/46 Shader GUID targets, 0 broken, 29213 unchanged Material/meta/YAML.

## Next18 Unity serialized Vulkan full proof — 16 نوفمبر 2026

- [43780219002](https://github.com/alwansan/raf/actions/runs/43780219002) **SUCCESS** job 133015477047؛ `GT_ORIGINAL_921_UNITY_SAFE`: unityVersion 2021.3.45f2, 4 Pass, registeredRoutes 33, errors 0, androidVulkanOnly true, privateBundleCompiled true. `GT_ORIGINAL_921_BUNDLE_ROUTES`: compiled table true, vertex_and_fragment_entrypoints_verified true, `vertex_routes_by_pass=fragment_routes_by_pass=[8,13,8,4]`، source shader SHA256 `e7654374f3eacc6b0487d619487886ae20c3b21d4745d0d915e712dd5ac24cc1`. Artifact `gt-next18-original-unity-33route-safe-43780219002` ID 14188102481، archive SHA256 `0384868233bf970f63bef96861ec41cc12a705eb58a27dd662f9a83eb2b9c49b`. **ISOLATED UNITY** فقط.
- [43780491219](https://github.com/alwansan/raf/actions/runs/43780491219) FAILED: next17 workflow اختبر وترجم NEXT18 كخطأ plumbing (GT_NEXT_18 log output)، ولدى next17 source حارس موروث 58 عوضاً عن 43؛ أصلاح المصدر `bd9c59d` والworkflow `c855514`، [43780876983](https://github.com/alwansan/raf/actions/runs/43780876983) يتطلب نتيجة فعلية، ولا يوجد source17 accepted بعد.
- آخر same-export audit NEXT30 43773151176: 570 non-Dummy / 216 Dummy 46 targets، 29213 untouched، 0 broken. لا DEVICE proof أو XAPK.

## CI scope correction NEXT18/NEXT17/NEXT23 — 16 نوفمبر

- [43781139286](https://github.com/alwansan/raf/actions/runs/43781139286) **SUCCESS static** for `scripts/gt_install_next18_original_shader48.py`: 193/45 post15 fail-closed source gate and exact 33-route Unity receipt digest, change only exported Dummy .shader with .meta bytewise preserved; not run in full project, no post15 material audit.
- [43777150940](https://github.com/alwansan/raf/actions/runs/43777150940) FAILED at `test_source_quality_and_two_23_objects_must_be_topology_checked` because old snapshot source owner fixture had less than 165; actual pipeline's earlier model/next30 steps passed. [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) includes previously fixed fixture commit 263cda9 and is running; same-export next23 still UNVERIFIED.
- [43780876983](https://github.com/alwansan/raf/actions/runs/43780876983) FAILED unit test fixture false assumption 17 (data 23+17 actually one 17); fixed test 23+16 (no 17) commit adbbe8b9 and rerun [43781304391](https://github.com/alwansan/raf/actions/runs/43781304391). Source 17 not yet accepted.
- Material last accepted unchanged: 570 non-Dummy / 216 Dummy, 46 original GUID targets, 29213 SHA material/meta untouched; SOURCE vs UNITY vs SAME-EXPORT vs DEVICE remain distinct.

## Next17 post14 original source acceptance — 16 نوفمبر

- [43781304391](https://github.com/alwansan/raf/actions/runs/43781304391) **SUCCESS** job 133018876883: status `GT_SHA_ORIGINAL_REMAINING_17_MATERIAL_SHADER48_D3D11_PRIVATE_STAGES_TRANSLATED`, original 82 source owners SHA verified, 43 D3D11 unique roundtrip Vulkan 1.1, 3 ShaderLab Pass [8,13,2] VSFS routes / 8 orphan VS, 46 independent stage compile, original 15 properties/6 Range, 54 parameter records, 901 named CB offsets, 338 texture/sampler bindings, 176 varying records. Artifact 14188333139, ZIP SHA256 1a78b9b9b46d26a4b1014dcf58461f95a5f2ac297f8d6018ab6f25a75f3bd468. **No Unity, same-export install, Adreno pixels in this source-only run**.
- [43781774987](https://github.com/alwansan/raf/actions/runs/43781774987) FAILED before Unity compile: next17 workflow typo `custom==686`, violates post14 real 786/1536 custom count. Code fixed [01cb0801](https://github.com/alwansan/raf/commit/01cb0801ed7aaf0b127d9e1f5980dd30bdcd452f); isolated Unity [43781873039](https://github.com/alwansan/raf/actions/runs/43781873039) in progress and must decode both VSFS [8,13,2], zero Unity shader errors.
- Baseline same-export still only NEXT30 accepted 43773151176 570/786 non-Dummy, 216 Dummy/46 targets; NEXT18 and NEXT17 are not original export GUID installed. Water/Fire/FFT/device test G0–G6 open.

## CI acceptance — Next17 Unity and next15/11 Source — 16 نوفمبر

- NEXT17 [43782074242](https://github.com/alwansan/raf/actions/runs/43782074242) SUCCESS job 133021309218؛ Unity 2021.3.45f2 Android Vulkan `passCount=3`, `registeredRoutes=23`, `errors=0`, `privateBundleCompiled=true`; independent serialized SMOL-V source candidate SHA256 `c479018de19d5d26e6aac7dee341bdba585db439b22ad6ea6d58ca31a877907b`, `vertex_routes_by_pass=fragment_routes_by_pass=[8,13,2]`, table verified true. Artifact 14189140548 ZIP digest f9e7e45c103562f52c74f81e4597805796e248b4a1c4ae5f3612cd9f978ac95c. ISOLATED UNITY only, no original GUID.
- NEXT15 [43782323454](https://github.com/alwansan/raf/actions/runs/43782323454) SUCCESS SOURCE SHA 82 owners/unique 15-material Shader48, 58/58 original D3D11/HLSL/Vulkan, 33 paired VSFS [8,13,8,4], 8 orphan VS, 66 stage compiles, 23 original properties/12 Range, 74 params, 1607 CB offsets, 346 texture/sampler links, 260 varyings. Artifact 14188699030 SHA256 5fef654d8fc29829de9efe976f6a73d7cc3ece6f621cfb5d464db82daebb7624.
- NEXT11 [43782328731](https://github.com/alwansan/raf/actions/runs/43782328731) SUCCESS SOURCE SHA 82 owners/unique 11-material Shader48, 58/58 genuine DXBC→Vulkan/HLSL, 33 pairs [8,13,8,4], 66 stage compiles, 9 original properties/0 Range, 74 params, 828 CB offsets, 306 texture/sampler, 199 varyings. Artifact 14187964353 SHA256 9c891cecdac3d325fe0ed3e8d25f41ba95dba1a4c7a3d0889d2fd8631ceeb3d9.
- NEXT15/11 Unity tests [43782657334](https://github.com/alwansan/raf/actions/runs/43782657334) and [43782661831](https://github.com/alwansan/raf/actions/runs/43782661831) launched; no acceptance until serialized bundle proof. Official Material counts unchanged 570/786 custom non-Dummy, 216 Dummy/46, 29213 unchanged, no game pixels.

## GT — دليل قبول 4 SOURCE+UNITY و3 installer guards، 16 نوفمبر

- [43782657334](https://github.com/alwansan/raf/actions/runs/43782657334) **SUCCESS** NEXT15 job 133023141566: Unity 2021.3.45f2 Android Vulkan `privateBundleCompiled=true`, `passCount=4`, `registeredRoutes=33`, `errors=0`, serialized VS/FS `[8,13,8,4]`, candidate SHA256 `27064d720e10037a2697426081d6030d234018f42bb53a0e643d5a22435cd7b8`; Artifact ID 14189580629 archive SHA256 `7acc1741e4e4acd9e1c88491789136fd85f9b8c26bf61e2e822e62604b29cd57`.
- [43782661831](https://github.com/alwansan/raf/actions/runs/43782661831) **SUCCESS** NEXT11 job 133023155858: same Unity Android Vulkan 4Pass/33 serialized VS/FS routes and 0 errors, candidate SHA256 `5732a11c9f3125709396ba3b6324940411adacddcc7ba1a0953d7183b797ee0b`; Artifact ID 14189086879 zip SHA256 `3ff0c535bc8a36a731e4aa11e1f528db3009013ef1a828c0ef0ef8f4a4c5c1c3`. Source ORIGINAL D3D11 58/58 each in [43782323454](https://github.com/alwansan/raf/actions/runs/43782323454) and [43782328731](https://github.com/alwansan/raf/actions/runs/43782328731).
- [43784558673](https://github.com/alwansan/raf/actions/runs/43784558673) **SUCCESS** safety static-only, 9/9 tests for `gt_install_next17/15/11_original_shader48.py`; next17 expects [8,13,2] and future real census 175/44, next15/11 [8,13,8,4] and future real census 158/43 and 143/42 respectively. Those **must be read from actual same-instance AssetRipper after predecessor steps**, never substituted as proof. Code changes only exported dummy Shader48 bytes while preserving original .meta/GUID and saving backup.
- **NO same-export installs for NEXT18/17/15/11, no Android phone image tests, no XAPK**. Baseline actual [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176): 570 non-Dummy Custom, 216 Dummy/46 target, 0 broken and 29213 files protected. NEXT23 [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) still in progress.

## CI verified post15 native full export — 16 نوفمبر

- [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) **SUCCESS** full actual ZIP2 AssetRipper instance، `GT_NEXT23_SAME_EXPORT_ORIGINAL_GUID` source owner/PathID→Shader GUID exact and 33 Vulkan VSFS [8,13,8,4]. `GT_FIFTEEN_ORIGINAL_SHADER48_SAME_EXPORT_POSTINSTALL`: **193 Dummy + 593 non-Dummy Custom = 786**، 45 original Dummy shader targets، 0 broken، 750 builtin، 1536 total Material docs، 29,213 original Material/meta/YAML SHA untouched. Safe artifact ID 14190151552 SHA256 41f534719e2d63507e3ec06d489b964d5a0800908b0faaa072805e7d1ed830cf. Actual Custom Material coverage 593/786=75.45%, not device visuals.
- NEXT10p33 Unity [43785362318](https://github.com/alwansan/raf/actions/runs/43785362318) SUCCESS source original 58/58 D3D11, 4 passes/33 serialized Vulkan VSFS `[8,13,8,4]`, zero errors, candidate SHA 3ff8016d267fd7e2e5a9faf835e6b5fc3fe2d18f70fc9e567aad53c51c481bae, artifact 14190078538. NEXT10p31 Unity [43785367029](https://github.com/alwansan/raf/actions/runs/43785367029) SUCCESS source 55/55 D3D11, 4 passes/31 VSFS `[8,13,8,2]`, zero errors, candidate SHA efccbe88ce3545de5222b2857a421ed7fab170116491ee99ed340aae5e775691, artifact 14189184448. Neither original export GUID installed.
- [43785949219](https://github.com/alwansan/raf/actions/runs/43785949219) **SUCCESS** static-only original GUID installer safety, 6/6 tests for two *distinct* 10-Material Shader48. New real full export [43786161961](https://github.com/alwansan/raf/actions/runs/43786161961) launched with strict expected post16 175 Dummy/611 non-Dummy/44 GUID, **not yet accepted**.
- NEXT18/17/15/11 SOURCE+ISOLATED UNITY proven; original GUID installs pending. G0–G6、水 FFT/kernel6, original fire image and GPU Device pixels still open. No game XAPK.

## GT — Full export NEXT18 quality provenance fix and NEXT17 workflow launch, 16 نوفمبر

- **Genuine baseline** [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) **SUCCESS** post15 same export 593 non-Dummy / 193 Dummy (45 remaining original Shader GUID targets), all 29213 Material/meta/YAML byte SHA unchanged, 0 broken. 75.45% Custom Material coverage only.
- NEXT18 old full [43786161961](https://github.com/alwansan/raf/actions/runs/43786161961) is based on `cbca1efe...`, hardcodes incorrect translator quality `gt-fifteen...193`, but translator demands `gt-fourteen...216`; this may fail later at source step after expensive preflight. Fixed only translator input in workflow commit `75088aec...`; replacement [43787527334](https://github.com/alwansan/raf/actions/runs/43787527334) pending. The NEXT18 install stage retains actual post15 193/45 required; post16 `611/175/44` NOT VERIFIED.
- NEXT17 full [43787809110](https://github.com/alwansan/raf/actions/runs/43787809110) running on independent `0cfea848...`: original-next17 source authentic 43 D3D11 and 23 VSFS route from post14 216/46, Unity 2021 Vulkan serialized [8,13,2] and 0 errors, original exported GUID install only after real NEXT18 post16 (611/175/44), post17 expected 628/158/43. **NO post17 actual proof yet**. No game Player/Adreno pixel evidence in these workflows.

## GT 16 نوفمبر — verifiable 7+7 original Shader48 SOURCE

- [43788590820](https://github.com/alwansan/raf/actions/runs/43788590820) SUCCESS source NEXT7p33: 58 genuine original DXBC→HLSL→Vulkan1.1, 33 paired VSFS routes [8,13,8,4], 8 orphan VS, 4 passes, 66 independent HLSL compiles, 9 original properties/0 Range, 816 CB offsets, 364 source sampler/Texture bindings, 199 varying records; artifact 14190883438 SHA256 `046487eb0db5be19f44bfad10384e02b4f34fc9f504abb1320ae5fef70a9b516`. SOURCE only. Unity [43789192895](https://github.com/alwansan/raf/actions/runs/43789192895) no final result at update.
- [43788585885](https://github.com/alwansan/raf/actions/runs/43788585885) failed NEXT7p11 SOURCE composer at `compose_three_pass_recovered_original_shaderlab` because shared 921 composer allowlist missed real [4,5,2] routing; original 22/22 D3D11 were already valid. Introduced source-tag-constrained branch `verified_source_next_seven_pass_modes` (commit `180b5ee7c93a7e23d03107ac2692d8b361663667`) and regression tests for missing/swapped LightMode. [43789088799](https://github.com/alwansan/raf/actions/runs/43789088799) source reconstruction passed (private_original_7p11_material_ShaderLab_3pass_composed true; 22/22 entries), failed stale CI assert 31 vs 11 VSFS only, fixed `3f585052`.
- [43789264382](https://github.com/alwansan/raf/actions/runs/43789264382) **SUCCESS source NEXT7p11**: exact SHA-original 82 owners, 22/22 D3D11, 11 paired VSFS [4,5,2], 2 orphan VS, 3 passes, 22/22 stage compiles, 12 properties/4 Range, 337 CB offsets, 108 resource sampler bindings, 61 varying records. Artifact `14190954229` ZIP `abec389870df852cc4dea671884cf6044143690041dbfb6dbb935f82aa104033`. Isolated Unity [43789424745](https://github.com/alwansan/raf/actions/runs/43789424745) launched, must prove 3 passes/11 routes both VSFS and 0 shader errors. No DEVICE or SAME-EXPORT GUID proof for either 7-Material Shader48.
