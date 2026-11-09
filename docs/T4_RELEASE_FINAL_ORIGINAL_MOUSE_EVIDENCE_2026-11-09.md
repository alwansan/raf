# T4 — استعادة أدلة الماوس النهائية بعد تحرير التقاط المؤشر

**جلسة:** `20261109T2042Z-T4-chat-release-final-window-q6n4`، `origin=chat`، 9 نوفمبر 2026  
**الخلل:** `INPUT-005`، قبول الهاتف غير مثبت؛ هذا إصلاح **Source-only**.

## الدليل من المصدر الأصلي

في `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs`، تكتب `ReleaseCapture()` سجل `physical_mouse_capture_released` **أولًا**، ثم:

- `physical_mouse_captured_action_callbacks_final` إذا زادت أحداث الفعل على آخر نقطة تسجيل.
- `physical_mouse_legacy_reader_evidence_final` إذا زادت نداءات قارئ Unity على آخر نقطة تسجيل.

بعد هذين السجلين فقط تُجري `epoch++` وتصفّر مخازن أحداث Android وعدادات قراءة Unity. لهذا تنتمي سجلات `_final` الحقيقية إلى **نفس جلسة التسجيل ونفس `epoch` السابقة على التحرير**، لكنها تظهر بعد حدث التحرير في ترتيب JSONL.

كان `scripts/t4_correlate_mouse_runtime_epochs.py` يتعامل مع `physical_mouse_capture_released` عبر `active=None` ويهمل الملخصات اللاحقة. نتيجة ذلك كانت اختبارات النقر السريع أو التمرير القصير التي لا يصدر ملخصها إلا وقت التحرير تفقد دليلاً أصليًا، مع أنها قد تكون قد وصلت إلى قارئ Unity.

## الإصلاح الآمن

أُضيفت نافذة نهائية محدودة `pending_final` لكل محاولة. عند سجل `released` يحتفظ المحلّل بمرجع المحاولة المنتهية **فقط** لاستقبال السجلين الأصليين ذوي لاحقة `_final`، وبالترتيب الذي تكتبه C# (أحداث Android النهائية أولًا ثم قارئ Unity النهائي إن وُجدا).

تُرفض الحالات التالية دون إسنادها للمحاولة السابقة: قارئ أو callback عادي بعد التحرير؛ طلب/إعادة محاولة جديد قبل السجل النهائي؛ جلسة `PersistentDiagnosticLog` أخرى؛ `epoch` مختلف؛ تكرار سجل نهائي؛ انعكاس ترتيب النهائيات؛ أو فاصل يتجاوز 8 سجلات غير مرتبطة. وأُضيف إبطال fail-closed للمحاولة نفسها إذا كان السجل النهائي داخل نافذتها مشوّه الرقم أو غير مطابق للمرحلة الزمنية؛ لا يمكن إصلاحه لاحقًا بسطر صحيح لرفع قبول زائف.

كل الأدلة المعتبرة تستمر في المرور على فحوص C# `True/False` والعدد `int32/long` والعدادات المتزايدة وقنوات LEFT/RIGHT/MIDDLE وV/H والأختام الزمنية `session/sequence` التي أضيفت في دورات T4 السابقة. **التطابق يعني تزامن الدليل فقط**؛ لا يعني الاستجابة الفعلية داخل اللعبة.

## إجراءات المصدر ونتائج GitHub Actions

1. [commit 20efd8020d](https://github.com/alwansan/raf/commit/20efd8020d68bca166a2a23a24e8d4f03163bc6d): حفظ فرصة نهائية مقيدة بجلسة/مرحلة التقاط أصلية.
2. [commit 5c43c3a20](https://github.com/alwansan/raf/commit/5c43c3a20b397fa6e9bfaabd7c5a96d067b492ab): **12 اختبارًا** لحالات ترتيب C# الحقيقي وللتداخل بين الجلسات أو المراحل وتكرار السجلات وتجاوز حد الأمان.
3. [CI42695937421](https://github.com/alwansan/raf/actions/runs/42695937421) **COMPLETED SUCCESS 69/69**، job 129427666265.
4. [commit 8e5db658a8](https://github.com/alwansan/raf/commit/8e5db658a8b597697a907eb39ea0834f15feae12): منع إحياء دليل نهائي بعد سطر مشوّه/epoch خاطئ.
5. [commit 4e7ac40839](https://github.com/alwansan/raf/commit/4e7ac40839328bc1e7688f41c0a645ca3a54bb46): **اختباران سلبيان إضافيان** لهذا السيناريو.
6. [CI42696168324](https://github.com/alwansan/raf/actions/runs/42696168324) **COMPLETED SUCCESS 71/71**، job 129428503951، النص النهائي: `Ran 71 tests in 0.029s; OK`.

هذه اختبارات Python للمدخلات المصطنعة الموافقة لبنية C#، **وليست بناء Unity أو لعبة Raft على Android**. لم يُعدل أي ملف مصدر Android/Unity أو مشاهد أو `.meta` أو `.rgd` أو OBB أو إعدادات اللعبة، ولم يصدر T4 أي Mini أو XAPK.

## أحدث دليل هاتف وحدوده

المجلد [CL/test/shared-20261109-233132-554663211](https://github.com/alwansan/CL/tree/main/test/shared-20261109-233132-554663211) مصدره `731d7a68bb3826b348d0314f694737b522e92976`، وهو رفع آخر لاختبارات المختبر الموحد (30 حالة). **T4-01 إلى T4-09 جميعها `NEEDS_INPUT`** وليست `PASS`. لا يوجد في هذا الرفع اختبار دخول لعبة كاملة وتحريك LEFT/RIGHT/MIDDLE أو عجلة V/H مع نتيجة فعلية داخل Raft.

## التسليم

أبقِ `INPUT-005 OPEN` و`Raft full-game NOT_READY 0/3`. عند توفر XAPK موقعة من T5 طبقًا لسياسة 5/5 منفصلة، اجمع ملفًا من عملية Raft واحدة يحوي `PersistentDiagnosticLog.session/sequence` و`epoch` وأحداث تحريك/ضغط Android وقارئ Unity، وجرّب النقر السريع ثم الإفلات، مع تشغيل الكاميرا والتاتش والكيبورد والعالم المحلي والحفظ `.rgd` والصوت وSettings. نفّذ:

```bash
python3 scripts/t4_correlate_mouse_runtime_epochs.py <single-process-original-Raft-log.jsonl>
```

قد يُثبت الإخراج تزامن Android callback وUnity getter؛ لكن `device_pass=false` و`unity_gameplay_verified=false` ثابتتان، ويجب إضافة دليل مستقل من المالك على فعل الزر في اللعبة.
