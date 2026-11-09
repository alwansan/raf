# دليل المالك — استعمال ملفات Download/logs في المختبر الموحد (T5)

**9 نوفمبر 2026 — مصدر جديد، لا تنطبق الأزرار التالية على APK 0.2.14 الأقدم حتى يصدر بناء جديد.**

## مكان الملفات كما زود به المالك

- Download/logs/Raft-Android-Test/com.alwansan.raft.androidtest.apk
- Download/logs/Raft-Android-Test/Android/obb/com.alwansan.raft.androidtest/main.91.com.alwansan.raft.androidtest.obb
- Download/logs/Raft-Android-Test/manifest.json
- Download/logs/team-testpack.json
- Download/logs/t2-water-render-testpack.json
- Download/logs/T3.json
- Download/logs/t4-mouse-testpack.json
- Download/logs/top.niunaijun.blackbox_logcat.txt

## تشغيل الفحص

1. افتح المختبر العربي الجديد واضغط **📂 اختيار مجلد Download/logs**، ثم اختر مجلد **logs** نفسه في منتقي ملفات Android واسمح بالقراءة. لا تحتاج Root أو Shizuku. إذا اخترت مجلد Raft-Android-Test فقط، لن يرى التطبيق ملفات الحزم الموجودة في جذر logs.
2. يعرض المختبر قائمة أدوار الملفات وأحجامها المتاحة؛ وجود ملف APK أو OBB لا يثبت توافق التوقيع أو تثبيت اللعبة أو تركيب OBB. ملف Android/obb هنا تحت Download/logs، وليس طلب صلاحية قراءة مجلد نظام لعبة أخرى.
3. إذا رفض Android 15 بعض ملفات/مجلدات Android/obb، اختر ملف APK أو OBB يدويًا من **T5-02**، ولا تعتبر رفض الوصول تلفًا في OBB. لا يقرأ الفحص OBB الكبير تلقائيًا.
4. اضغط **🔎 حساب SHA256 للملف** أمام APK أو OBB المقصود. انتظر اكتمال bytes وsha256. حالة EVIDENCE_READY تعني وجود دليل قراءة الملف المحدد فقط، لا PASS ولا سلامة OBB. لإثبات التطابق يجب الحصول على بصمة مرجعية مستقلة لنفس إصدار 91، وليس مقارنة عشوائية بإصدار 89.
5. **📄 مراجعة واستيراد team-testpack.json** يقبل فقط schema v2 وحزمة الفريق الموحدة، ويرفض تلقائيًا أي حزمة محلية أقدم من اختبارات APK المضمّنة. لا تستورد T3.json أو t2-water-render-testpack.json أو t4-mouse-testpack.json القديمة باعتبارها drivers جديدة. لا يمكن تشغيل Shader من JSON خارجي.
6. **📑 تلخيص تحذيرات السجل** يقرأ بحد أقصى أول 4 MiB من BlackBox ويعرض عدادات كلمات تحذير فقط، دون نسخ سطور السجل أو معلومات شخصية. العدادات لا تعني أن برنامج اللعبة شغّل الحدث ولا تحدد النطاق الزمني بدقة.
7. اختبارات T1-01..05 وT2-01..04 داخل المختبر آلية ومستقلة عن ملفات اللعبة. T3-01..06 تحتاج مراجعة صورة مختبر GPU، وT4-01..09 تحتاج ماوسًا حقيقيًا، وT5-03..06 تحتاج أدلة لعب/ملاحظة واقعية. لا تجعل وجود ملف أو صورة دليلاً على النجاح وحده.
8. بعد التجربة اضغط **📤 تصدير السجلات والنتائج**؛ ارفع أحداث JSONL وsummary JSON وصور T3 عند الحاجة إلى https://github.com/alwansan/CL/tree/main/test. لا ترفع APK/OBB أو BlackBox الخام إلى مستودع عام.

## الأدلة الهندسية

- مسار الملفات المحلي مقدَّم من المالك ولم يتوفر لبيئة GitHub Actions لقراءة خاماته؛ لا يوجد إثبات SHA/توافق إصدار91 قبل اختبار الهاتف.
- فحص مصدر Java/Android: https://github.com/alwansan/raf/actions/runs/42690234266
- البناء الجديد يجب أن يمر حراسة .github/raft-mini-lab-build-request.json وأن يتحقق T5 من APK نفسه قبل وضع رابط مباشر.
- لا يتم تغيير تصويت XAPK اللعبة الكاملة أو شروط قبول Unity/الماء.
