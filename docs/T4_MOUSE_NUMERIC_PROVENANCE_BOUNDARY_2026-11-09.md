# T4 — تصحيح صيغة `System.Boolean.ToString` وحدود الأرقام في سجل الماوس الأصلي

**التاريخ:** 9 نوفمبر 2026، 20:27 UTC  
**العامل/الجلسة:** T4 / `20261109T2024Z-T4-chat-numeric-provenance-f7v2` / `origin=chat`  
**المشكلة:** INPUT-005 مفتوحة. هذا فحص مصدر وسجل **لا** يعني نجاح الماوس على الهاتف ولا يستلزم بناء Raft XAPK.

## أصل المشكلة الثابت في مصدر اللعبة

في `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs`، داخل `LogLegacyReaderEvidence`، تُدمج قيمتا C# المنطقيتان `requested` و`nativeCaptured` بنص السجل مباشرة:

```text
"; captureRequested=" + requested + "; captureObserved=" + nativeCaptured +
```

تُنتج `System.Boolean.ToString()` قيَم `True`/`False` (بحرف أول كبير). لكن لاحقة البرنامج النصية المقصودة كقيمة حرفية في المصدر نفسه:

```text
"; countersAreGetterCallsNotClicks=true; unityGameplayVerified=false"
```

تستخدم الحروف الصغيرة. الفاحص القديم `scripts/t4_correlate_mouse_runtime_epochs.py` كان يقرأ `true|false` فقط في جميع الحقول، وبالتالي يرفض السجل الحقيقي حتى لو وُجدت جلسة `PersistentDiagnosticLog` صحيحة و`epoch` و`callbacks` و`Unity Legacy getter` متطابقة. الاختبارات السابقة استخدمت كلها تقريبًا الصيغة الصغيرة المصنعة، لذا مرّت دون التقاط تعارض المصدر.

كذلك، كانت صيغة `epoch=(\d+)(?!\d)` تسمح خطأً بقراءة `epoch=12junk` كـ12، ويمكن أن يؤدي تحويل حقل طويل جدًا من آلاف الأرقام إلى استثناء `ValueError` بدل وسم السجل بأنه غير صالح. المصدر الأصلي يملك `epoch` وعدادات callback ضمن `int32`، بينما عدادات مجموع getter ضمن `long`، وعدّادات قنوات `Report()` الإحدى عشرة ضمن `int32`.

## ما تغيّر

في `scripts/t4_correlate_mouse_runtime_epochs.py`، commit `6f3df6bf68921ca2a80106192724b7dbb94bb3a0`:

1. `parse_bool` يقبل فقط صيغ المصدر الحقيقية `True/False` أو النصوص الحرفية `true/false` مع حدود حقل صريحة؛ ويرفض `TRUE` أو `true9` أو `Truejunk` والحقول المكررة.
2. `epoch` أصبح حقل ASCII bounded `0..2147483647` بأقصى عشرة أرقام وحد نهاية حقل حقيقي؛ تُرفض المفاتيح المكررة أو الأرقام الملحقة بالحروف.
3. `parse_counter` يقبل ASCII decimal بحد 19 رقمًا وقيمة لا تتجاوز `long.MaxValue=9223372036854775807`؛ الاستدلال على الأرقام الهائلة أو المكررة يفشل كدليل دون محاولة تحويل عدد أطول من ذلك.
4. عدادات `PhysicalMouseActionEvidence` لا تتجاوز `int.MaxValue`. تُفحص سجلات `PhysicalMouseLegacyReaderEvidence.Report()` ذات الإحدى عشرة قناة كـ`int32`، وتُرفض التوابع الرقمية المشوهة بدل قبولها ضمن channel-level proof.
5. يحافظ المحلّل على مفاتيح النتائج القديمة والقيود الثابتة `device_pass=false`، `unity_gameplay_verified=false`؛ لا يعدل مدخلات Android أو Unity أو ملف نتائج المالك.

## الإثبات القابل لإعادة الإنتاج

- مصدر الإصلاح: [commit 6f3df6bf](https://github.com/alwansan/raf/commit/6f3df6bf68921ca2a80106192724b7dbb94bb3a0).
- اختبارات جديدة: commit `29cba2a3344df64094c9409a3117f167d5b1717d`: **15 اختبارًا** تشمل JSONL مطابقًا للمصدر C#، و`False` الحقيقي، وكلمات `TRUE/true9`، وعلامات `epoch` المكررة والمشوّهة، وحدود `int32/long`، وأرقامًا من 5500 خانة في الحقول وقنوات `Report`. الاختبار الإيجابي يتحقق من وجود `LEFT` press-mask مع `down0` fallback في الجلسة نفسها، دون الادعاء بأن اللعبة استجابت.
- [CI42692994798](https://github.com/alwansan/raf/actions/runs/42692994798) **SUCCESS 42/42** لاختبارات ما قبل الإضافة على مصدر التصحيح.
- [CI42693129361](https://github.com/alwansan/raf/actions/runs/42693129361) **COMPLETED SUCCESS 57/57** على commit `29cba2a3344df64094c9409a3117f167d5b1717d`، job `129417825568`؛ سجل الاختبار: `Ran 57 tests in 0.033s; OK`. هذه اختبارات Python source-only؛ لا يوجد APK أو سجل لعب جديد.
- أحدث `CL/test/shared-20261109-225506-552476830`: نسخة المختبر الواحد `0.2.14-shared`، عدد 30 حالة، `T4-01..09` كلها `NEEDS_INPUT`. هذا السجل ليس إثباتًا للماوس الملتقط داخل Raft، ولم يتغير نتيجة إصلاح الفاحص.

## المدى والحدود وخطوة التسليم

هذا الإصلاح يعالج **رفض دليل C# الصحيح وفشل التحليل مع أرقام غير صالحة**. لا يعالج زرًا لا يصل إلى Unity، ولا يعني أن وراثة 20 موضعًا أصليًا من ZIP2 أصبحت تعمل على الهاتف. حتى وجود ارتباط صالح بين `session+epoch+pressMask/down0` لا يثبت السببية أو استجابة اللعبة أو اتجاه عجلة التمرير الأفقي. الإخراج يبقى `device_pass=false`.

في التجربة المقبلة بعد توافر **XAPK موقعة ومطابقة للمصدر**، يجب جمع JSONL فعلي من عملية Raft واحدة، مع الحفاظ على `session/sequence` دون تكرار `startup`، ثم إجراء LEFT/RIGHT/MIDDLE + V/H wheel والربط بكود Unity واللعب الحقيقي، وحفظ العالم `.rgd` والكاميرا/التركيز/الكيبورد/الصوت/Settings.

**لا** يُطلق T4 بناء XAPK أو Mini استنادًا إلى هذا الإصلاح، ولا يغيّر تصويت 5/5 للعبة كاملة أو بوابات `NOT_READY 0/3`، ولم يلمس الأصول الخاصة أو ملفات بقية العاملين.
