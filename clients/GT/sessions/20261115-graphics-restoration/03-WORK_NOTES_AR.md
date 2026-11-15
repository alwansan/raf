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
