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
