# T4 — مصادقة هوية جلسة سجل Unity الفعلي عند ربط أحداث الماوس

**التاريخ:** 2026-11-09 19:15 UTC  
**العامل:** T4؛ `origin=chat`؛ `session_id=20261109T1912Z-T4-chat-logger-session-guard-n5r7`  
**نطاق التغيير:** `INPUT-005`، فاحص مصدر فقط؛ لا تعديل للعبة أو UI أو APK.

## أصل المشكلة في كود اللعبة

قرأت `android-port/Runtime/Platform/PersistentDiagnosticLog.cs` الأصلي في الفرع؛ التسجيل الفعلي ليس مجرد نص باسم العملية، بل أسطر JSONL تتضمن بالضبط `utc, session, sequence, thread, area, operation, detail`. يولّد `session` عند إنشاء logger جديد، وقد يتغيّر داخل عملية Unity الواحدة بعد دورة تهيئة/إغلاق المسجّل. يتزايد `sequence` بانتظام داخل الجلسة، ويمكن تكرار صفوف `startup-*.jsonl` إن جُمعت مع `raft-*.jsonl`. وفي الوقت نفسه يتكرّر `epoch` بين تشغيلات اللعبة؛ لذا لا يكفي التشابه العددي لجمع حدث Android captured مع قارئ Unity Legacy من سياق آخر.

## إصلاح فاحص T4

حدّثت `scripts/t4_correlate_mouse_runtime_epochs.py` دون تعديل `AndroidPhysicalMouseCapture.cs`:
- يفحص JSONL الحقيقي في `area=input`، ويميز `session` و`sequence` الصحيحتين عن النصوص القديمة غير المنسوبة؛ لا يدمجهما في إثبات واحد.
- يغلق محاولة الالتقاط عندما ينتقل السياق إلى جلسة logger أخرى، حتى لو اتفقت قيمة epoch.
- يرفض تكرار أو تراجع sequence ضمن جلسة logger؛ وتصبح **كل محاولات هذه الجلسة غير مؤهلة** للإثبات، بما فيها مؤشرات قد تكون سبقت إعادة قراءة `startup`.
- يحتفظ بسلوك source-only السابق: حواجز `captureRequested=true` و`captureObserved=true`، ومقارنة callbacks/getters ضمن epoch وطلب واحد، ورفض عدم اتساق العدادات، ولا ينتج `device_pass=true` قط.
- يضيف نتائج رقمية مجمّعة `logger_sessions_scanned`, `poisoned_logger_sessions`, `provenance_scope_mismatches`, `matched_jsonl_scoped_attempts`, `matched_unattributed_legacy_attempts`. **لا يطبع مُعرّفات session الحساسة أو مسارات ملفات المالك.**

تم إنشاء **ثمانية اختبارات جديدة** فوق 16 السابقة، تتضمن جلسة logger واحدة صحيحة، جلسة أخرى تعيد نفس epoch ولا يجوز جمعها، سجلين صحيحين مستقلين، إعادة صفوف startup بsequence أصغر، قيمة sequence من نوع bool، خلط سجل أصيل بنص غير منسوب، تمويه `area=unity`، وسطور JSONL فعلية. كل المدخلات اختبارية ولا تتضمن سجلات خاصة أو أصول اللعبة.

## الإثبات

- المصدر: `a8e475613ccc2e438fb4c71e7c76aab04aac4149`.
- الاختبارات: `abf1ede6bbea3b9073c9ab20b826be46dd486c93`.
- CI المبدئي للمصدر وحده: [42681390984](https://github.com/alwansan/raf/actions/runs/42681390984) SUCCESS.
- **CI النهائي [42681491521](https://github.com/alwansan/raf/actions/runs/42681491521) SUCCESS**، job `129376929867`، السجل يؤكد **Ran 24 tests in 0.006s, OK**. من ضمنها 8 حالات provenance الجديدة، ولا يوجد بناء Unity ثقيل.

## ما لم يثبت

هذا فاحص logs ولا يقرأ APK أو الهاتف ولا يضمن عدم تزوير JSONL خارجياً. وجود قارئ Unity وcallback في نفس `session+epoch` لا يعني أنهما ضغطة ماوس واحدة أو أن Raft استجاب لها فعليًا. `device_pass=false` و`unity_gameplay_verified=false` دائمًا. أحدث أدلة المالك `CL/test` ما زالت تعرض مدخلات T4 uncaptured من 8 نوفمبر؛ لا توجد تجربة game حديثة مثبتة لـLEFT/RIGHT/MIDDLE وV/H Scroll في XAPK يضم إصلاحات T4.

## مساعدة الفريق دون تداخل

فحصت CI الخاص بـT5: الفشل الأول `42680558991` سببه اختلاف `shared-` في معرّف session؛ أصلحه T5 نفسه بالفعل وأصبح `42680745095` SUCCESS. وفحصت CI الخاص بـT2: `42680680366` متوقف عند سجل T3 تاريخي يفتقر `id/event_id`؛ T2 وثّق وطلب من T3 تصحيحه في `prompt/coordination/discussions/COORD-001/20261109T1911Z-T2-chat-T3-event-identity-n6q8.md`، ولذلك لم أعدّل سجل T3 أو مسار T2.

## استكمال العمل

عندما يصدر XAPK أصيل من T5 يتضمن مصادر T4، يستخرج سجل JSONL **لعملية واحدة** ويُشغّل:

```bash
python3 scripts/t4_correlate_mouse_runtime_epochs.py /path/to/one-raft-log.jsonl
```

لا تجمع startup وraft الدائريين بنسخ أسطر مكررة؛ سيمنع التسلسل ذلك من إعطاء مطابقة وهمية. قارن حالة `capturedCallbackEvents` مع `positiveFallback` لقارئ Legacy والنتيجة الفعلية داخل Raft، وراقب الكاميرا وFocus/ESC والتاتش وفتح العالم وحفظ `.rgd` والصوت. لا تبن APK بسبب هذا الفاحص وحده.

**INPUT-005 OPEN؛ اللعبة الكاملة NOT_READY 0/3.**
