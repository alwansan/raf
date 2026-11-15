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
