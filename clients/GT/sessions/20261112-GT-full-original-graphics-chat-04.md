# GT — دورة 04: استعادة موارد Raft الرسومية الحقيقية ودمج مسار ZIP2 في البناء

- **session_id:** `GT-20261112-CHAT-04-full-original-graphics`
- **origin:** `chat`
- **agent / branch writable:** `GT` / `feature/android-native-port`
- **immutable source:** `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- **write policy:** جميع الموارد من ZIP2، لا `git lfs pull/fetch/checkout` ولا إعادة كتابة `zip2`، لا إلغاء أعمال T1–T5 ولا تشغيل APK كامل دون بواباتهم
- **baseline from immediately preceding GT checkpoint:** `c9db87e742577461a315da9d5e0b5685c5fab969`; live branch advanced during this session, see actual run commit SHAs below
- **scope:** تحويل الجرد المرجعي إلى إعادة بناء بايتات الرسوميات الأصلية كاملة داخل مدخل AssetRipper، ثم وصل المدخل بمسار native الحقيقي وتدقيقه
- **evidence:** [20261112_full_zip2_graphics_restoration.json](../evidence/20261112_full_zip2_graphics_restoration.json)

## عمل هندسي منفّذ داخل المشروع

1. **أداة إدخال أصل حقيقي:** `scripts/gt_zip2_export_resources.py` تستعيد ملفات ZIP2 المسجلة، وتجمع part-00000… بالترتيب وتطابق SHA256 والحجم الكامل قبل ظهور الملف، وتملأ مسار `Raft_Data` المؤقت الذي يقرأه AssetRipper. تسمح بإعادة استعمال ملفات أصلية موثقة وتتجنب تجاوز الملفات المتغيرة أو `.meta`. ملفات اختبار `tests/test_gt_zip2_export_resources.py` تمارس corrupt split، الرفض المبكر والـGUID/ملفات الباقين.
2. **المصدر المصغّر والمرئي الفعلي:** [43122665358](https://github.com/alwansan/raf/actions/runs/43122665358) أعاد 5 ملفات (656,558,804 bytes)، مثبتاً 398 StreamingTexture extents؛ [43123035437](https://github.com/alwansan/raf/actions/runs/43123035437) أعاد ملفي `sharedassets0.assets` و`.resS` (1,895,109,248 bytes) وثبت 1,116 Texture extents و557 Mesh extents.
3. **الاستعادة الكاملة لأولويات رسوميات اللعبة:** [43124662931 — PASS](https://github.com/alwansan/raf/actions/runs/43124662931) أعاد فعلاً **134 ملفاً أصلياً** (82 Unity Serialized owners + 48 stream files + 2 engine builtins + original globalgamemanagers وboot.config)، **7,532,909,297 بايت** بصمات وحجوم صحيحة مباشرة في مدخل AssetRipper المؤقت. أتم قراءة 4,050 Texture2D، منها 3,948 مع stream extents صالحة تغطي 5,932,309,293 بايت من البيانات الأصلية، و102 inline/empty أصلية. فحص متطلبات Mesh stream و9 ComputeShader و165 Shader في المصدر. [Artifact 13902706287](https://github.com/alwansan/raf/actions/runs/43124662931/artifacts/13902706287) يحوي ملخصاً آمناً فقط، **لا بيانات اللعبة**.
4. **تعديل الإنتاج الرئيسي (حقيقي في YAML):** `.github/workflows/raft-unity-editor-android-import.yml` أصبح يعدّ الموارد الأصلية الـ134 ويفحصها مرتين عبر ZIP2 فقط في `$RUNNER_TEMP/input/Raft_Data` قبل AssetRipper. فحص texture، Shader، Compute، وMesh source يعود إلى البيانات المستعادة لا مؤشرات LFS. استرجاع بيانات Mesh ranges يقرأ verified local files لا GitHub LFS. تُحفظ `.meta/GUID` الأصلية في exporter دون تغيير في هذه الخطوة؛ التماثل النهائي مع `ExportedProject` لم يثبت بعد.
5. **مصدر الصوت من ZIP2 أيضاً دون LFS:** بناء `MasterBank.bank` (101,600,960 بايت؛ SHA256 `10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339`) تحقق فعلياً في [43125353255 — PASS](https://github.com/alwansan/raf/actions/runs/43125353255). native StreamingAssets يجلبه بصورة مستقلة من ZIP2 ثم يمرر `--verified-external-master-bank` إلى أداة T5 الحالية التي تتحقق مرة أخرى من المصدر. لا LFS ولا اختبار سماع الصوت على الهاتف بعد.
6. **بوابة إنتاج لا تحتاج XAPK:** [43125034578 — PASS](https://github.com/alwansan/raf/actions/runs/43125034578) اختبرت شروط أخذ 134 أصلاً وحفظ مسار بناء Raft الرسمي دون Git LFS، بعد تصحيح duplicate sparse checkout YAML والتكيّف مع التحقق المنفصل لمورد الصوت.
7. **اختبار AssetRipper الكامل مستقل عن APK:** `.github/workflows/raft-gt-original-export-smoke.yml` يستخدم أداة AssetRipper نفسها و`RaftExportLineage` نفسها، يحاول توليد مشروع تصدير كامل من 134 مصدراً أصلياً وmanaged assemblies ويجري تحقق .meta/Material texture على الناتج؛ [43125542125](https://github.com/alwansan/raf/actions/runs/43125542125) كان يعمل وقت تسجيل بداية هذه الدورة. **لا تنسب له نجاح تصدير أو مطابقة GUID حتى يظهر الدليل.**

## الحدود وإدارة التعارضات

- **المثبت الآن:** أصول المصدر واكتمال استعادة `7.533 GB` المطلوبة للرسوميات إلى مدخل importer حقيقي ووجود مصدر الصوت الأصلي بصورة مستقلة؛ الأدوات متصلة بملف workflow native.
- **غير مثبت بعد:** نجاح AssetRipper في تحويل كل الـ134 إلى `ExportedProject`، نفس-المثيل `GUID/.meta`، صحة Shader Pass وCompute kernels على Adreno، شاشة هاتف أو FPS، وبناء XAPK من SHA جديد.
- لم ترفع الحمولات الأصلية إلى git commits أو artifacts. `zip2` و`main` untouched. لم يبدأ GT عملية XAPK native رسمية أو يصوت نيابة عن T1–T5.
- ملفات Source managed `Raft_Data/Managed/*.dll` يجهزها مسار T5 الأصلي منفصلة؛ أصل `MasterBank.bank` والـAudio الأصلي كذلك منفصل. العدد 134 **لا يساوي كل 366 ملفاً لنسخة PC**.

## نتيجة فعلية لاحقة: AssetRipper real export PASS (لا APK)

اكتمل [43125542125](https://github.com/alwansan/raf/actions/runs/43125542125) بتشغيل AssetRipper الحقيقي على **134 ملفاً أصلياً** استعيدت من ZIP2 + 151 Managed providers أصلية محددة الهوية، وتم إثبات `RAFT_SCRIPT_IMPORT_FIDELITY`: `decompiled_script_export=true`, `export_completed=true`, `mono_structure_layout_mismatch_lines=0`, `unknown_backend_fallback=false`. الناتج الفعلي يحوي **40 مشهداً `.unity`، 1,536 ملف `.mat`، 4,003 صورة Texture، 8,372 ملف `.asset` و18,368 ملف `.meta`**. [Artifact 13902689523](https://github.com/alwansan/raf/actions/runs/43125542125/artifacts/13902689523) آمن، ولا يحوي بنية المشروع الأصلية أو private export trace.

**قيد حاسم:** خطوة `verify_exported_material_texture_links` أعادت exit 2، لكن `continue-on-error` جعل نتيجة workflow الكلية `success`؛ **لا تعنِ النتيجة الخضراء أن كل Texture GUID صحيح**. تم تعديل workflow ليحفظ error_code الآمن في [إعادة التشغيل 43126735391](https://github.com/alwansan/raf/actions/runs/43126735391) قبل إرجاع exit، لنعرف أول عائق. وأُضيف خيار `RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE=1` إلى كود الـExporter الخاص بنا لتمكين private exact source Texture→Export GUID trace في اختبار GT المقبل، مع إبقاء إنتاج T5 المعتاد على Material/Shader فقط عند عدم تفعيل الخيار.

## ما يلي

1. افحص Job/Artifact للـExporter المستقل `43125542125` وشخّص أصل الخطأ إن فشل، ثم أصلحه وكرر اختبار المسار المحدود. احفظ نتيجة وsha.
2. إذا نجح exporter، استعمل same-instance trace مع `scripts/b05_verify_material_texenv_bindings.py` و`scripts/verify_exported_material_texture_links.py` وقارن .meta/GUID بلا تخمين أسماء. أصلح Material/Texture أو Mesh أولاً حيث فشل التصدير، ثم انتقل لShader/Pass حقيقي في فئة مرئية.
3. افحص مع T5 حزمة تجريبية ضمن TRIAL_BUILD_POLICY قبل أي Native APK، وسجّل معرّف المرشح والاختبارات بوضوح. لا تعط نسبة completion بلا دليل هاتف.
