# تفاصيل العمل للجلسة الجديدة

## أماكن الملفات

- المشروع هو المستودع `alwansan/raf` وفرع العمل `feature/android-native-port`.
- طابق `HEAD` مع الفرع البعيد قبل بدء العمل. اللقطة المرجعية للتصدير الكامل هي `8ca634490a4bf13d920e92c1654686ace52cf2be`. دفعة التسليم اللاحقة تضيف BillboardFade وأدلة الاستعادة. استعمل `git status --short` و`git diff origin/feature/android-native-port` قبل أي مزامنة.
- حزمة المصدر الأصلية المثبتة ZIP2 عند `15964ea8f246b6e076ce26b60931ee2e1a9a2385` والمصدر المرحلي ضمن `work/zip2` و`work/gt-921-original`. راجع `RAFT_FILE_MANIFEST.tsv` وبصمات الأحجام وSHA واستعمل بيانات المصدر للقراءة فقط.
- اللوقات والصور في [alwansan/CL](https://github.com/alwansan/CL). النسخة المحلية المعروفة `work/particles-cl` عند `3c26bb5d0f4de2cbffd42197dae9ae1372721659`. الصور القديمة أظهرت المجسمات موجودة وبيضاء ومؤثر النار بمربع أسود. راجع أي لوقات أحدث قبل اعتماد استنتاج جديد.
- نواتج ShaderLab المولّدة وملفات Unity التجريبية تبقى خاصة وتُعاد من المصدر المثبت. استعمل [دليل BillboardFade المجمّع](../../evidence/20261115_gt_billboard_source.json) وتقارير CI؛ جلسة جديدة لا تعتمد على توفر ملفات scratch محلية.

## المسار الفني

- لربط النص والـGUID استعمل نفس export instance من AssetRipper المثبت. ثبّت الشيدر فوق ملفه المصدّر وحافظ على .meta والـMaterial PPtrs. مسار المجسمات يبدأ بـ`scripts/gt_original_921_all_variants.py --shader PROFILE`، ثم `scripts/gt_original_921_shaderlab.py` مع `--engine-keywords --verify-entrypoints` وملف المسارات الخاص. بعد Unity تحقق بـ`scripts/gt_verify_921_shader_bundle.py` ثم ثبّت بـ`scripts/gt_install_recovered_model_shader.py`.
- لا تفترض أن جدول fragment المنفصل لازم يكون موجوداً. بعض حزم Unity Vulkan تخزن وحدات المسارين معاً. فحصنا يفك SMOL-V ويفحص execution models ووجود كل تركيبة، ثم يربط تقرير التحقق ببصمة ملف ShaderLab.
- Unity 2021.3.45f2. ترتيب حقول CBuffer تصاعدياً حسب packoffset أصلح خطأ overlap. احتفظ بمعالجة حشو الـstruct وبحالة ShadowCaster التي لا تستقبل مدخلات fragment في DirtPile. مسارات instancing تستعمل pragma Unity ومادة اختبار مفعّل فيها instancing؛ قراءة إعداد Keep All داخلياً سبق أن أسقطت الفحص.
- BillboardFade يستخدم ForwardBase وForwardAdd مع [4,5] مسارات. التوليد اجتاز الفحص المحلي، وبقي فحص الحزمة في Unity والتثبيت بمسار إنتاج أندرويد. ابدأ بمتابعة تشغيل `[Billboard probe]` ثم قارِن النتيجة بتقرير المصدر.
- التصدير الكامل بلا APK في `.github/workflows/raft-gt-original-export-smoke.yml`. فحص الشيدر المعزول في `.github/workflows/raft-gt-original-921-all-variants.yml` مع اختيار shader وcompile_unity، وفحص ParticleShader في `.github/workflows/raft-gt-particle20-source-bound-unity.yml`. GitHub Actions قد يلغي الفحص المعلّق السابق عند الاشتراك في نفس concurrency group؛ افحص حالة job والخطوات قبل تكرار التشغيل.
- مسار الإنتاج `.github/workflows/raft-unity-editor-android-import.yml` يقوم بالاستعادة ثم التثبيت. ملف `.github/raft-native-build-request.json` بوابة طلب الحزمة. لا تعدّله خلال مرحلة الاستعادة. بعد الاستعادة، إذا بدأ بناء XAPK لا تنتظر البناء الطويل؛ سلّم رقم التشغيل للمالك.
- لحساب تغطية البقية، خذ `gt-raw-export-program-quality.json` من تشغيل 43651736236. اربط `dummy_shader_material_counts_by_name_digest` بحساب SHA256 لاسم ShaderLab الأصلي كما هو UTF-8، بما فيه المسافة الأولى في ` BlockPaint`. الاسم المكرر قد يخفي أكثر من GUID، فاستعمل lineage من المصدر للتثبيت. أعد الجرد بعد التثبيت؛ لا تطرح أعداداً من الجرد الخام وتعتبرها نتيجة تشغيل.
- افصل في تقاريرك بين المصدر، التصدير، ترجمة Unity، إثبات وحدة GPU داخل الحزمة، التثبيت في إعادة البناء، وإخراج البكسل على الجهاز. لحد التسليم ما عدنا إثبات بصري بأن كل المجسمات تلوّنت أو أن مربع النار اختفى من اللعبة.
- اشتغل بالتوازي على ملفات مستقلة عند الحاجة. المالك طلب أكثر من أيجنت لتسريع العمل. حدّث أدلة الاستعادة عند الدمج، مع SHA وrun ID ونطاق الإثبات.

## استكمال مثبت 15 تشرين الثاني 2026 — بعد رسالة التسليم

- فحص ShaderLab المعزول لـBillboardFade **نجح** في التشغيل [43723487222](https://github.com/alwansan/raf/actions/runs/43723487222): Unity 2021.3.45f2 Android Vulkan، تمريرتان ForwardBase وForwardAdd، مسارات `[4,5]` لكل من VS/FS، 9 تركيبات، `compiler errors=0`، والبصمة `74094b12475c554e88ef0424101f133902ce3db6cdb92854c35c2837fa984ce1`. مصدر القياس: [الدليل العددي](../../evidence/20261115_gt_billboard_unity_bundle.json).
- دمجت خطوات BillboardFade خلف Hair_Amplify في `.github/workflows/raft-unity-editor-android-import.yml` بترتيب الاستعادة، Unity Vulkan، فحص الـSMOL-V ومسارات `[4,5]`، ثم `gt_install_recovered_model_shader --shader billboard`. فحص المثبّت يحفظ ملف `.meta` وGUID ويُرفض عند نقص الـreceipt. التغيير [d2d00b9](https://github.com/alwansan/raf/commit/d2d00b9810de1724248f95601d8f91a86e757654).
- أضيف اختبار اصطناعي لحماية ForwardAdd وGUID في `tests/test_gt_install_recovered_model_shader.py`. رُبط بفحص المصدر غير المنتج للحزمة وأُطلق كتشغيل [43759121385](https://github.com/alwansan/raf/actions/runs/43759121385)؛ لا تُعد النتيجة مكتملة حتى تحقق خاتمته.
- أصبح `t3_audit_exported_material_programs` في مسار الإنتاج يستخدم `--rank-dummy-targets` بعد خطوات التثبيت لتحديد التالي حسب عدد المواد وبصمة الاسم؛ **لم ينفذ بعد على التصدير الكامل الجديد**. جرد `43651736236` الخام 786، والجرد القديم بعد Vendor فقط 770. لا تستنتج منهما العدد بعد جميع الشيدرات الحالية.
- أحدث CL معلوم `3c26bb5d0f4de2cbffd42197dae9ae1372721659` بتاريخ 13 نوفمبر. لا يزال تكافؤ الألوان/الماء/شفافية النار والقراءة المرئية للجهاز مفتوحاً. لا XAPK قبل إنهاء الاستعادات.
- الإجراءات التالية: افحص 43759121385 وأصلح أي فشل؛ شغّل/أضف مسار فحص صادر كامل **بلا APK** ينفذ كل مثبتات الإنتاج ويخرج الجرد الحقيقي بعد التثبيت، ثم عالج أعلى بصمات الشيدرات المتبقية بالدليل. تجنب التشغيل الكامل الذي يحزم XAPK. عند أي فحص طويل أعطِ رقم التشغيل مباشرة.

### تشغيل الدمج الكامل الجديد (بدون APK)

- SHA تنفيذ الفحص `f7fcd808e08ba4d3bcccd033b4694fa59bfa8ba7`، رقم [43759856414](https://github.com/alwansan/raf/actions/runs/43759856414). ملف التشغيل `.github/workflows/raft-gt-original-export-smoke.yml` يعمل على ZIP2 المثبت. أُضيفت 9 حلقات استعادة/Unity/تحقق/تثبيت كخطوات منفصلة لشيدرات: BlockPaint وDirtPile وVegetation وGrassPlot وSkin_Amplify وShimmer وSailPaint وHair_Amplify وBillboardFade؛ كل واحدة تعزل مخرجاتها الخاصة وتحذف مصدر الشيدر الخاص بعد فحص الحزمة.
- الدليل النهائي عند اكتمال الاختبار: Artifact باسم `gt-nine-shader-full-export-audit-<run_id>` وفيه `gt-nine-shader-postrestore-quality.json` و`gt-nine-shader-postrestore-summary-safe.json`. افحص ثبات GUID والمستندات المحمية، ثم استعمل `postrestoration_remaining_dummy_by_name_digest` لتحديد الأعلى استخداماً بين الشيدرات المتبقية؛ لا تفترض نجاح خطوات لم تنتهِ. أرشيفات المراحل الأخرى ترفع أرقام التحقق فقط، لا كود الشيدر الأصلي.
- ربطت الفحص الجديد بأصوات التنفيذ الأصلية على نفس الفرع؛ لا تحرر ملف `.github/raft-native-build-request.json` ولا تطلق أي بناء منتج للعبة، فالتوجيه يمنع XAPK قبل انتهاء الاستعادة. إذا تعطّل الفحص بعد خطوة معيّنة، طابق اسم المرحلة مع باقة المصدر أو المترجم أو المثبّت، ثم أصلح على الفرع نفسه وأعد الفحص.

### إضافة فحص شفافية خامات المؤثرات — 16 تشرين الثاني

- دالة `gt_particle108_export_alpha_diagnostic.py` تعتمد على `t3_original_particle_material_texenv.run` + `t3_original_particle_texture_targets.run` للتحقق من سلسلة Particle108 الأصلية (3 Texture2D، 5 مواد، 10 روابط) ثم `verify_export_lineage.identity/pointer` وملف Trace من **نفس تصدير Unity** لتحديد GUID الخاص بكل Texture2D. تقرأ Pixel alpha histogram من PNG/TGA/غيرها إذا دعم Pillow الملف، وتحسب غير المعتم والشفاف جزئياً ومعلمات TextureImporter كأرقام، ولا تنشر أسماء أو GUID أو صور.
- نجحت الاختبارات الصناعية في [43762000860](https://github.com/alwansan/raf/actions/runs/43762000860)؛ لم تُفحص موارد اللعبة الحقيقية بهذه الأداة بعد. عند توفر تصدير كامل، شغّل `python3 -m scripts.gt_particle108_export_alpha_diagnostic --original "$RUNNER_TEMP/gt-input" --manifest .gt-zip2/RAFT_FILE_MANIFEST.tsv --project "$RUNNER_TEMP/gt-project/ExportedProject" --trace "$RUNNER_TEMP/gt-private-export-lineage.json" --out "$RUNNER_TEMP/gt-particle108-export-alpha-safe.json"` في عملية لا ترفع ملفات الخامات الأصلية. لا يستنتج نجاح تقرير Alpha تطابق تظليل Vulkan وقت التشغيل أو سبب المربع الأسود.
- تشغيل الـ9 شيدرات [43759856414](https://github.com/alwansan/raf/actions/runs/43759856414) ما زال مطلوباً لإخراج `gt-nine-shader-postrestore-summary-safe.json` والجرد الحقيقي بعد التثبيت. لا تستخدم بيانات 786/770 القديمة للاستنتاج. أبقِ XAPK متوقفاً.

- أُطلق فحص مستقل للـ3 Texture2D الحقيقية (Particle108) مع مصدر ZIP2 وAssetRipper من [43762318768](https://github.com/alwansan/raf/actions/runs/43762318768). فحص الاختبار الصناعي السابق `43762000860` ناجح، أما هذا التشغيل الحقيقي ففي تقدم. Artifact عند النجاح باسم `gt-particle108-real-export-alpha-43762318768` وفيه **أعداد alpha/importer فقط**؛ إذا فشل راجع step `Check source-selected three Particle108 Texture2D exported alpha images and importer settings`. لا تنسب سبب مربع النار الأسود إلى textures إلا إذا تحقق اختلاف Alpha بين المصدر والتصدير، وبعدها ينبغي التحقق من blending والشيدر وقت التشغيل.

### دفعة إضافية: قياس 13 شيدر أصلي بدون حزمة لعبة

- التقرير التساعي [43759856414](https://github.com/alwansan/raf/actions/runs/43759856414) أثبت 453 مادة Custom مستعادة و333 Dummy متبقية، موزعة على 51 شيدر GUID مستخدم. ملفات Material وMeta محمية وعددها 29213 لم تتغير.
- فحص ترتيب المصدر [43763883804](https://github.com/alwansan/raf/actions/runs/43763883804) طابق 8 أسماء Shader48 حقيقية مع 101 مادة Dummy من 333؛ بقيت 232 خارج مطابقة الأسماء بمصادر الستة مشاهد. لا تخلط الاسم مع دليل GUID.
- توسع workflow التصدير الكامل بإعادة استخدام خطوات استعادة وتثبيت Particle108 وParticle20 وSmoke34 وCandle16 الأصليين على نفس export instance، بعد الشيدرات التسعة. فحص انتهاء الدفعة يثبت SHA لملفات المواد والـmeta، ويقيس Material Dummy بعد 13 شيدراً. التشغيل [43764506277](https://github.com/alwansan/raf/actions/runs/43764506277)، Artifact المنتظر gt-thirteen-source-shader-full-export-audit-43764506277. لا XAPK.
- الفحص الثاني لخامات النار [43763158214](https://github.com/alwansan/raf/actions/runs/43763158214) عزل ValueError إلى join_same_export_Texture2D28_GUID. كود الثالث [43764070678](https://github.com/alwansan/raf/actions/runs/43764070678) يميز الأسباب الآمنة مع عدادات trace أصلية من دون أسماء أو GUID.
- عند نجاح 13، أعد ترتيب Dummy الأصلي غير المستعاد من التقرير، وراجع اختلاف الصور والألوان وشفافية النار والماء، مع الأولوية لإثبات المصدر والحفاظ على روابط المواد. لا XAPK قبل اكتمال جميع موارد الاستعادة.

### أداة فرز جميع مصادر Shader48 بعد 13 شيدراً

- أنشأت scripts/gt_rank_full_export_dummy_shader_sources.py لتحديد كل Shader48 أصلي غير مستعاد من الـ82 مالكاً المثبتين في ZIP2. ترتبط هوية Shader48 بمسار المصدر/PathID في private exporter trace ثم GUID أصلي في ShaderImporter وMaterial.m_Shader الحقيقي، لا بالمطابقة الاسمية وحدها؛ ترفض انقلاب الاسم واختلاف SHA، ولا تنشر الأسماء/GUIDs/PathIDs.
- نجحت اختبارات source-free في [43765453006](https://github.com/alwansan/raf/actions/runs/43765453006). يمكن تشغيل الأداة على التصدير الكامل عندما تتوفر مخرجات 13 شيدراً المقبولة: python3 -m scripts.gt_rank_full_export_dummy_shader_sources --original "$RUNNER_TEMP/gt-input" --manifest .gt-zip2/RAFT_FILE_MANIFEST.tsv --project "$RUNNER_TEMP/gt-project/ExportedProject" --trace "$RUNNER_TEMP/gt-private-export-lineage.json" --out "$RUNNER_TEMP/gt-exact-source-shader-priority-safe.json". التقرير يخرج أعداداً وأوزاناً مجهولة فقط. لم يجرِ تطبيقه على المشروع الحقيقي حتى الآن، ولا يُعتمد العدد قبل نتيجة الـCI الفعلية.
- إصلاح Particle108 الجديد يحاول مسار Material21/TexEnv المستند إلى نفس المصدر ونفس export instance بعد إثبات خطأ direct Class28 pointer. الإصلاح يحتاج اختباراً حقيقياً، ونجحت الاختبارات الاصطناعية الإضافية في 43764952233. لا تغيّر GUID الخاص بالصور أو Material أثناء ذلك.

### الاستكمال بعد إثبات جميع أصول Shader48 — 16 تشرين الثاني

- [43766412259](https://github.com/alwansan/raf/actions/runs/43766412259) قام بجرد 165 كائن Shader48 موثقاً عبر 82 مالكاً من ZIP2؛ 330 مادة Dummy تطابق أسماء أصلية فريدة، وثلاثة مواد تختلط بين ثلاثة مصادر Shader48 بالاسم نفسه. صفر أسماء مفقودة؛ يستلزم إثبات export GUID ومحتوى برنامج GPU قبل الاستعادة النهائية.
- [43766959343](https://github.com/alwansan/raf/actions/runs/43766959343) بدأ فحص توبولوجيا 12 شيدر Dummy من D3D11 الأصلية. البرنامج: scripts/gt_probe_remaining_original_shader_dxbc_topology.py. ينشر أعداد Pass/Variant فقط، من دون DXBC أو أسماء أو GUID.
- فحص Alpha [43766815679](https://github.com/alwansan/raf/actions/runs/43766815679) يميز فشل قراءة Material YAML عن فشل join original Material TexEnv إلى exported Texture2D، ويصدر رمز فشل ثابت وآمن. الفحوص السابقة حددت المصدر وليس فقدان البكسلات.
- خذ نتيجة [43764506277](https://github.com/alwansan/raf/actions/runs/43764506277) بعد 13 شيدراً، عدل عدد Dummy الفعلي، ثم استعد شيدرات المصدر التالية بأثر المواد الأعلى. لا XAPK قبل استكمال جميع الموارد.

### إجراءات وخطوات الاستئناف — بعد قبول 13 Shader48

- تأكد نهائياً 43764506277 SUCCESS من ملف gt-thirteen-shader-postrestore-summary-safe.json: 540/786 Custom real ShaderLab (68.7%)، 246 Dummy و47 referenced Shader GUID، 0 broken، unchanged files 29213. استعمل 246 في كل تقارير الأولوية الجديدة، وأبقِ 333 مرجعاً لمرحلة تسعة شيدرات فقط.
- استخرج اختبار 43768013634 SUCCESS من private original shader script: شيدر 30 مادة له 4 Pass [8,13,8,2] و55 genuine D3D11 stages valid Vulkan11/HLSL؛ stage_parameter_records 70، CB reflected offsets 1007، textures/samplers 364، varying 232، composed ShaderLab 62 entrypoints glslang verified. التالي Unity 2021 Android Vulkan private bundle في 43768744473، ملف Editor: android-port/Experiments/GT/Editor/Next30ShaderValidation.cs. فلا تعتبر استعادة الهدف موثقة على GUID قبل Unity bundle وfull export.
- شغّلت 43768958865 لتحديث الـ82 source Shader48 census مع 246 remaining Dummy بعد تثبيت 13. هذا workflow يستدعي post13 artifact من 43764506277 ويستعمل expected_dummy_materials=246 وexpected_dummy_shaders=47.
- علة Particle108: 43767741576 أثبت 9 من 10 exporter Material TexEnv references type3 fileID2800000 وخامة عاشرة local type0. إن كانت بعض صور النار خارجية وصورة مخصصة embedded، يجب تتبعها إلى serialized Unity YAML/Asset importer المحلي، لا نسخ GUID اعتباطياً. فحص 43767766873 نسخة متأخرة ونتيجته لم تثبت.
- احفظ original shader source HLSL/SPIR-V وzip2 owner bytes داخل Actions temp فقط ولا تنشرها؛ اطبع safe counts وsafe reason codes. لا APK/OBB/XAPK.
