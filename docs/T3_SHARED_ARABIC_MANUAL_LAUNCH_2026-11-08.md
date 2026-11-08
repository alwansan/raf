# T3 — فتح اختبارات الرسوميات بالضغط + شاشة عربية عمودية

**تاريخ العمل:** 2026-11-08. **العميل:** T3، الجلسة `20261108T1940Z-T3-chat-arabic-manual-visual-v4c8`، `origin=chat`. **المسار:** RENDER-002؛ مختبر APK موحد واحد `com.alwansan.raft.lab.shared`. **لا يمس** اللعبة الأصلية أو AssetRipper/Unity shader sources.

## عطل حقيقي أثبته المستخدم والمصدر

أبلغ المالك أن الضغط على أي اختبار T3 لا يفتح شاشة أو رسماً؛ قبل الإصلاح كان `UnifiedLabActivity.openPending()` يعرض نص الاختبار فقط، وكان `launchManualCase()` الخاص بـ`t3_visual` يعرض رسالة تقول استخدم AUTO T3 بدلاً من فتح نشاط الرسم. حزمة البيانات T3 v1 القديمة تختلف عن الحزمة المشتركة v2، لكن حتى مع v2 كان نقر الاختبار يفتقر إلى مسار فتح حقيقي. **هذا فشل UX/runtime integration مؤكّد على مستوى المصدر؛ لم نثبت بعد سلوك هاتف الإصدار الجديد**.

## الإصلاح المدمج

1. تمت إضافة `T3_VISUAL_PREVIEW=406` ومسار `launchT3VisualCase` في التطبيق الموحد؛ الضغط على أي اختبار T3 من القائمة أو زر «تنفيذ الاختبار الذي اخترته» يفتح `T3LabActivity` بنفس رقم الحالة `T3-01..06` ومعرف جلسة التطبيق. كما يظهر الآن قسم جديد بستة أزرار «▶ فتح T3-XX» دائماً، حتى لو كانت الحالة محفوظة، فلا يُشترط العثور عليها ضمن الطلبات المعلّقة.
2. تمت إضافة نمط المعاينة `manual_case_id` إلى نشاط T3. بدلاً من `runSharedAutoT3()` ولقطة تعود بسرعة، يختار الاختبار الصحيح ويُبقي GLES الرسم والتعليق بالعربية أمام المستخدم حتى يضغط «📷 التقاط صورة هذا الاختبار والعودة إلى النتائج»؛ يمكن الرجوع بدون حفظ نتيجة. لقطة الشاشة تمر عبر حارس الإطار/البكسلات السابق و`PixelCopy` وMediaStore PNG/SHA.
3. في مسار نتيجة `T3_VISUAL_PREVIEW`، يتحقق التطبيق الموحد من رقم الحالة والنتيجة الفعلية، ويتأكد أن URI الصورة قابل للقراءة قبل حفظ `EVIDENCE_READY`. الفشل الحقيقي `FAIL` أو الحاجة للصورة `NEEDS_SCREENSHOT` تحفظ كما هي؛ إلغاء الصفحة يحافظ على النتيجة القديمة. **لا يوجد PASS تلقائي لمجرد التقاط صورة**؛ على المالك مشاهدة الصورة وكتابة ملاحظة ثم اختيار النجاح أو الفشل بنفسه.
4. عُرّبت عناوين وتوجيهات الحالات الست وشاشة T3 الداخلية وأزرار المشاهدة/التصدير. بالتزامن نفّذ T5 الواجهة العامة العربية، `ArabicLabStrings` لتوجيهات كامل الاختبارات، وتغيير `AndroidManifest.xml` إلى `screenOrientation=portrait`. احتفظ T3 بذلك؛ لم يلمس Manifest، ولم يستبدل ترجمة T5 أو بيانات `team-testpack.json`.
5. زادت فحوص المصدر `tests/test_t3_shared_visual_frame.py` إلى **10 اختبارات** تشمل مسار النقر، فتح النشاط، عدم حفظ نجاح مزيف، العربية، الوضع العمودي، زر الالتقاط اليدوي، والتحقق من رقم الحالة وURI الصورة. في فحص مباشر مستقل لمصدر GitHub: **18/18 invariants PASS**؛ هذا **ليس تشغيل Python/Gradle CI أو هاتف**.

## المراجع
- [T3 Arabic visual preview](https://github.com/alwansan/raf/commit/389b0779d6ad106503b3566c0aa0e1d129903421) — activity/T3.
- [T3 host child result routing](https://github.com/alwansan/raf/commit/7a03a2773b0c5953a85453632e5cc6a43a94d9ec) — إضافة أضيق مسار مخصص لتجربة T3 في host المشترك، دون تعديل منطق SAF/T5/driver T1/T2/T4.
- [T3 six explicit open buttons](https://github.com/alwansan/raf/commit/bef7f88ff98797f7aa0532e64cb4cc7a01922b44).
- [Regression tests](https://github.com/alwansan/raf/commit/55d8908f1a4ccb814b67063f743f03d433842f14) و[visible buttons assertion](https://github.com/alwansan/raf/commit/5e387f086d64a13db84df0daa6aa80449b30ade1).
- Shared source-only compile workflow: `.github/workflows/raft-t3-shared-png-source-gate.yml` (يُشغّل فحوص `test_t3_shared_visual_frame.py` و`:app:compileDebugJavaWithJavac` بدون assembleDebug؛ نتيجة تشغيله الحالي **غير مثبتة**).
- [T3 shared r2 build readiness](../apk-for-testing/SHARED_BUILD_READINESS.md): صوت T3 **NEED_BUILD** بسبب تعذر فتح اختبار فعلي على جهاز المالك؛ T5 **وحده** يقرر ويصدر APK موحداً واحداً بعد مراجعة الفرع والنتائج. لا تغير أصوات الآخرين ولا أطلب build لعبة Raft الكاملة.

## تجربة المالك **بعد بناء T5 ورفعه APK جديداً**
افتح «مختبر رافت الموحد» بالطول، واضغط «▶ فتح T3-01 — الألوان الأساسية». تظهر شاشة الرسم بثلاثة أعمدة أحمر/أخضر/أزرق وتعليمات عربية؛ بعد المشاهدة اضغط «📷 التقاط صورة هذا الاختبار والعودة إلى النتائج». إن رجعت بنتيجة `EVIDENCE_READY` اكتب ما رأيته في الملاحظة واضغط «نجاح حسب مشاهدتي» أو «فشل حسب مشاهدتي». كرر للاختبارات T3-02..06. يمكن استعمال «تشغيل T3 تلقائيًا»، لكن المعاينة اليدوية أجود عند التشخيص البصري.

**أدلة نحتاجها:** `summary-*.json` و`events-*.jsonl` وملفات `T3-01..06-*.png` داخل `Download/Games/cl/test/shared-<session>/` + حالات النجاح/الفشل المرصودة. لا تستخدم APK 0.2.9 السابق لاختبار مسار النقر الجديد؛ فهو سابق لهذا الإصلاح.

**باقي الحدود:** لم يُتحقق من Android portrait UI-device أو PixelCopy/MediaStore على POCO، ولم يثبت شيء عن تلوين لعبة Raft/النار/الماء/شيدر Particle108 الأصلي. تظل RENDER-002 وWATER-001 مفتوحتين؛ جاهزية XAPK الأصلي منفصلة وNOT_READY 0/3.
