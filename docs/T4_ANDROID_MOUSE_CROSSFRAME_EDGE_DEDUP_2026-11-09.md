# T4 — إصلاح تكرار نقرة الماوس بين إطارَي Unity (2026-11-09)

**العامل T4؛ جلسة `20261109T0157Z-T4-chat-crossframe-click-e4p8`؛ الأصل chat؛ INPUT-005 OPEN.**

## الدليل والسبب
فُحص سجل مالك الهاتف الحقيقي القديم في `alwansan/CL@4680f5dc26127938e7696f932b2d9a80dc703937`:
`test/shared-20261108-223228-464718661/events-20261108-223341-464791801.jsonl` (Git blob `7c337320a1593ff8d9f9fd63e55ec30ed62cd202`).
بعد إزالة تكرار callbacks بين Activity/View هناك **13 ACTION_DOWN و13 ACTION_UP** بـ`actionButton=0`، تقابلها **13 ACTION_BUTTON_PRESS/RELEASE** بـ`actionButton=1` في نفس `eventTime` والـsource. هذه بيانات **Mini قديم uncaptured**؛ لا تثبت وصولها إلى Unity داخل Raft.

النسخة السابقة من `PhysicalMouseButtonWheelFrame` تدمج الحواف بأقنعة داخل إطار Unity الواحد فقط. إذا أخذت Unity عينة بين `DOWN` و`PRESS` يمكن أن تُسجل نقرة مكررة في إطار تالٍ. هذا **خطر مثبت بفحص المصدر وتجربة C# اصطناعية** وليس فشلاً ملاحظًا باللعبة.

## التعديل
- Commit `b5f9e60d991ff3d6d998e2f2b91e2e7ea1a30fcf`: `PhysicalMouseMotionSource.cs` يحتفظ بعلامات implicit/explicit للزر الأول لعمليات الضغط والإفلات؛ لا يمنع حافة ثانية إلا عندما **يتطابق توقيت الحدث الموجب + المصدر + deviceId غير السالب** داخل دورة capture نفسها. تتجاهل مطابقة التوقيت الناقص أو الجهاز المجهول لمنع إسقاط حدث غير موثوق؛ الحقائق الخاصة بالـheld وright/middle والتمرير باقية.
- `AndroidPhysicalMouseCapture.cs`: `MotionEvent.getEventTime()` و`getDeviceId()` يُنقلان مع callback غير MOVE إلى frame buffer الحالي. يظل `onCapturedPointer` يعيد false للزر والعجلة، ولا يُغيَّر مسار Mouse X/Y الخاص بالكاميرا.
- `Program.cs`: اختبارات تكرار DOWN/PRESS وUP/RELEASE إذا فاصلتهما Unity frames، والترتيب المعاكس، وهويتا جهازين مختلفتين، وReset عبر capture epoch، وحدث مجهول الهوية. لا يُنادى Unity API من Android event thread.
- `tests/test_t4_android_pointer_capture_policy.py`: توثيق اتصال callback الحقيقي بالـeventTime/deviceId. Commit `435665c85b32f67eb745ce9a0c25e0384dd4e8bd` أصلح اسم متغير MOTION في اختبار السياسة وحده بعد فشل المصدر الأول.

## التحقق
- [CI 42548460164](https://github.com/alwansan/raf/actions/runs/42548460164) FAIL بسبب مرجع `MOTION` غير المعرّف في اختبار Python فقط، قبل الوصول إلى C#.
- **[CI 42548512179](https://github.com/alwansan/raf/actions/runs/42548512179) SUCCESS** على `435665c85b32f67eb745ce9a0c25e0384dd4e8bd`: **66 اختبار Python (7+15+9+22+5+8)** و**139 فحص C#**، تحقق SHA الخاص بمكتبة `Assembly-CSharp.dll` الأصلية، تجميع مقابل `Unity 2021` Android وEditor managed ABI، تطبيق 20 موقع Legacy Input على 12 ملفًا في staging مؤقت دون نشر المصدر المفكك.

## حدود النتيجة
لا Unity Android player/IL2CPP build جديد، ولا XAPK مثبت على هاتف، ولا تجربة mouse capture حقيقية في اللعبة. `INPUT-005 OPEN` و`NOT_READY 0/3`. لا تعديل T5 Mini/حزمة الاختبارات، ولا بناء Mini مكرر، ولا تغيير في mouse-camera/touch/keyboard/audio/Settings/world `.rgd`.

**الخطوة التالية:** سجّل أحداث `T4-02` الحقيقية في المختبر المشترك مع `capture_request=ON` و`route=captured,captured=true`، وجرب LEFT/RIGHT/MIDDLE وWheel V/H. ثم اختبر نسخة لعبة موقعة مبنية على source commit الذي يحتوي الإصلاح، وقارن Android callback مع Legacy Input المستخدم فعليًا في Unity مع الحفاظ على الكاميرا والحفظ.
