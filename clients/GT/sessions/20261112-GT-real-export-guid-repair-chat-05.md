# GT / chat / 2026-11-12 — دورة 05: تشخيص وإصلاح ربط Material/Texture بعد التصدير الحقيقي

- **agent** GT — **session_id** `GT-20261112-CHAT-05-texture-source-export-diagnostics`
- **origin** `chat`
- **branch الوحيد المسموح للكتابة** `feature/android-native-port`
- **source الوحيدة لمحتوى Raft الأصلي** `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385` (لا git LFS، لا fallback)
- **resumed_from** `20261112-GT-full-original-graphics-chat-04.md`، latest checked branch HEAD `b2a1c736741405a98b4d158316cc887d0a41d09e`
- **scope** عزل أسباب فشل `reference_target_not_verified_texture` و`INCONCLUSIVE_BEFORE_AGGREGATE_REPORT` على أصل تصدير AssetRipper الحقيقي؛ لا كتابة في .meta/GUID، لا تشغيل XAPK أو تغيير تصويت T5
- **أعمال الفريق** T1/T2/T3/T4/T5 مستقلة؛ استعمال CI مستقل GT فقط، ولا إلغاء workflows أخرى
- **experiment key** `gt-zip2-15964e-asset-ripper-036098a-texenv-134-originals-1556-materials`

## بداية مثبتة من Actions (قبل تغييرات الدورة)

- [43128711194](https://github.com/alwansan/raf/actions/runs/43128711194) مكتمل `success` على مستوى workflow وAssetRipper نفسه، لكن B46 فشل بـ**`reference_target_not_verified_texture`**؛ `continue-on-error` أخفى الرفض عن status النهائي. 
- `GT_REAL_ALL_82_TEXENV_FIDELITY` = `INCONCLUSIVE_BEFORE_AGGREGATE_REPORT` لأن full 82-owner source→export comparator خرج قبل حفظ aggregate. **ليس نجاحاً** ولا دليل تلف موارد؛ السبب التشخيصي لم يكن منشوراً.
- فحص B05 محدود `sharedassets6.assets` **exit=0** و40 scene/1536 .mat/4003 image/18368 .meta بقيت مصدرة بالفعل، مع استعادة 134 مصدراً الأصلي 7,532,909,297 bytes.
- Raw exported shader audit قبل vendor restorers يثبت **786 Material docs Dummy، 140 Shader files Dummy**؛ لا يدل على آخر صورة بعد restorers.

## تغييرات هندسية لهذه الدورة

1. `scripts/gt_diagnose_export_texture_targets.py` يفحص **كل** مراجع texture المصدرة ويفصل حسب category: missing_guid، wrong imported image fileID، importer mismatch، missing serialized subobject، unsupported type، أو targets سليمة. لا يُخرج names/GUIDs/file content، لا يغير assets. `tests/test_gt_diagnose_export_texture_targets.py` ترفض GUID مكرر وتفصل كل نوع failure، [CI 43130925504 PASS](https://github.com/alwansan/raf/actions/runs/43130925504).
2. `scripts/gt_full_original_export_texenvs.py` صار يرصد مرحلة الفشل `original_authentication` أو `private_same_instance_trace` أو `exported_material_yaml` أو `source_export_pointer_join` ويصدر فقط `reason_code` من قائمة محددة، مع `unclassified_<Exception>` لغيرها. لا تتسرب أسماء أو IDs من errors. اختبارات `tests/test_gt_full_original_export_texenvs.py` عُدّلت؛ CI [43130925504 PASS](https://github.com/alwansan/raf/actions/runs/43130925504).
3. GT export workflow عُدّل لتشغيل `gt_diagnose_export_texture_targets` على **ExportedProject الحقيقي** وحفظ category report وfull 82-owner reason report؛ real CI [43130965693](https://github.com/alwansan/raf/actions/runs/43130965693) بدأ، عند آخر تفقد كان في ZIP2 checkout. انتظر نتيجة المصدر الحية (لا استنتاج مسبق) ثم استعمل الفئات ذات الفشل الموثق للإصلاح بدقة.

## ما لم يتحقق

- سبب `reference_target_not_verified_texture` النهائي (fileID/importer/class) = unknown حتى انتهاء classifier real run.
- full 82 source→export comparison = inconclusive قبل نشر diagnostic stage؛ لا تخمّن تلف material أو GUID.
- 786 Raw Dummy ليس حالة post-restorer، ولا Android GPU/FFT/Water proof، ولا XAPK جديد في GT.

## next action

افحص jobs/logs/artifact لـ[43130965693](https://github.com/alwansan/raf/actions/runs/43130965693) واستخرج من `GT_ACTUAL_EXPORTED_TEXTURE_TARGETS` التجميعات ومن `GT_REAL_ALL_82_TEXENV_FIDELITY` phase+code. ابنِ إصلاحاً مبنياً على سبب حقيقي، مع synthetic negative controls وCI actual جديد؛ ثم استعد official vendor TMP/PostFX/Volumetric على GT isolated exported project وطبق T3 post-restorer raw-vs-restored، وحدث الملفات الدائمة.

## نتائج مؤكدة من هذه الدورة — مصدر المشكلة لا مجرد تشخيص عام

- **[43130965693 SUCCESS](https://github.com/alwansan/raf/actions/runs/43130965693):** تصدير AssetRipper الحقيقي نجح على 134 ملفات ZIP2؛ أداة GT الجديدة أثبتت أن مشكلة B46 الوحيدة في فئة استيراد الصور هي **28 مرجع imported-image بـfileID لا يساوي 2800000**؛ 4,525 مرجع صورة صحيحة، 5,649 null أصلية في Export، 14 builtin، **صفر GUID مفقود، صفر wrong TextureImporter، صفر serialized-texture-subobject missing، صفر unsupported file type**. تقرير محمي [Artifact 13904844489](https://github.com/alwansan/raf/actions/runs/43130965693/artifacts/13904844489).
- في نفس التشغيل فحص الـ82 original owners المحدد سابقاً رجع **`failed_phase=source_export_pointer_join` و`reason_code=Unverified traced original Material`**. تفسيره الموثق: Same-instance AssetRipper trace يشمل أيضاً original Unity engine built-in Material خارج قائمة 82 حاوية Raft الموثّقة؛ لا يجوز تسجيل تلك المواد كمفقودة من اللعبة. عُدّلت `scripts/gt_full_original_export_texenvs.py` لتمرير `selected_owners=set(OWNERS)` مع إبقاء التحقق من **كل** original 82 owners ومنع collisions، والسجل يصنف engine خارج النطاق بأعداد فقط. صححت tests حتى تفرق بين `selected_texture_targets_proven` و`all_texture_targets_proven` ولم تختلق إثبات كامل لمحرك Unity. Synthetic controls [43132895106 PASS](https://github.com/alwansan/raf/actions/runs/43132895106) و[43132895114 PASS](https://github.com/alwansan/raf/actions/runs/43132895114).
- **فرضية المصدر للـ28**: قد تكون روابط Cubemap بصيغة 8900000 لا Texture2D 2800000؛ **لم تثبت بعد**. أداة `scripts/gt_diagnose_texture_export_lineage.py` تقارن كل nonstandard PPtr داخل مواد Unity مع ClassID الأصل (89 لـCubemap)، pointer من **نفس مثيل AssetRipper**، `TextureImporter.textureShape` الحقيقي؛ لا تُقبل أي حالة بلا 3 قيود من المصدر. الاختبارات الاصطناعية نجحت [43132895114](https://github.com/alwansan/raf/actions/runs/43132895114)؛ التشغيل الفعلي [43132978685](https://github.com/alwansan/raf/actions/runs/43132978685) مخصص لإثبات الفرضية أو رفضها. لا يغير أي GUID أو .meta حتى تأتي النتيجة.
- **shader restoration**: [43131923736](https://github.com/alwansan/raf/actions/runs/43131923736) نفّذ TMP ثم PostFX shaders ثم PostFX histogram compute ثم Volumetric جميعها في GT ExportedProject المعزول، لكن برنامج الحماية الأول أخفق لأنه اعتبر أي `.meta` جديد يشير إلى تغيير `.meta` الأصلي؛ النتيجة `ORIGINAL_EXPORTED_META_MUTATED` لا تثبت فساد الـ18,368 ملفات الأصلية. جرى إصلاح `scripts/gt_test_vendor_shader_restoration.py` ليفحص **bytes لكل .meta الأصلية مع السماح بإضافة .meta رسمية جديدة** ويحسب removed/changed/added منفصلة؛ فحوص negative/synthetic مرت بعد إصلاح خطأ newline في fixture. إعادة التشغيل الحقيقية بتلك السياسة ما زالت مطلوبة قبل نشر postrestore dummy material counts.
- Full native XAPK لم يطلبه GT، وT1–T5 مستمرون بالعمل في نطاقاتهم. **لا تغير تصويت أو CI native الكامل** بسبب نجاح مخبر GT فقط.

