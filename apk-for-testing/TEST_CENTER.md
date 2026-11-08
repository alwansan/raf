# Raft — مركز APK الاختبارات الصغيرة T1–T5

[تعليمات المختبرات](LAB_PROTOCOL_AR.md) | [نتائج المالك 8 نوفمبر](OWNER_FEEDBACK_2026-11-08_AR.md) | [صيغة testpack](TESTPACK_FORMAT.md) | [تصويت الـXAPK الكامل المستقل](../prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md)

**المسار المطلوب للـlogs:** `/storage/emulated/0/Download/Games/cl/test/<worker>-<lab>-<session>/` باستخدام MediaStore على Android 15.

| العامل | التخصص | حالة المختبر | تحميل APK حقيقي | حزمة ملفات/اختبارات | تعليمات |
|---|---|---|---|---|---|
| T1 | FFT / GPU / compute | NOT_PREPARED | — | — | [T1](workers/T1/README.md) |
| T2 | Foam / Spectrum / Blur | NOT_PREPARED | — | — | [T2](workers/T2/README.md) |
| T3 | colors / materials / fire / lighting | NOT_PREPARED | — | — | [T3](workers/T3/README.md) |
| T4 | mouse left/right/middle/scroll/capture | SOURCE_READY (host فقط؛ لا APK) | — | [مثال 9 اختبارات](examples/t4-mouse-testpack.json) | [T4](workers/T4/README.md) |
| T5 | host / delivery / OBB / telemetry | SOURCE_READY (host فقط؛ لا APK) | — | — | [T5](workers/T5/README.md) |

**الصفوف أعلاه ليست روابط تنزيل متخيلة.** عندما يصدر العامل APK فعلياً يغيّر صفه وحده إلى READY_TO_TEST ويثبت link وversionCode وSHA256 والـsource SHA وCI وموعد انتهاء Artifact إن وجد. يجب أن تكون الملفات متاحة ومجربة بنيوياً قبل مطالبة المالك باختبار جديد. يُحفظ سجل الإصدارات السابقة بصفحة العامل.

**طريقة الاختبار:** افتح رابط APK عند READY_TO_TEST، ثبت التطبيق المختبر فقط دون حذف Raft، اختر CASE01..، جرّب baseline/test، سجّل PASS/FAIL/UNEXPECTED والملاحظات، استخدم اختيار ملف أو مجلد لحزم بيانات جديدة، اضغط Export Logs وشارك ملفات المجلد المحدد وصوراً عند الحاجة. تجميع LogRaft اختياري منفصل. لا تخلط بيانات اختبار المختبر مع نتائج اللعبة الكاملة.