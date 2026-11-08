# Raft Mini Lab — Android Java lightweight host

**مصدر فقط، لا APK جاهز بعد.** مخصص لاختبارات الماوس الحقيقي والصور/الملفات وJSONL. لا يحتوي اللعبة أو أصول ZIP2 أو Unity أو Shizuku. يحتاج Gradle 8.10.2 / AGP 8.7.3 / JDK17 / SDK35.

استخدم workflow اليدوي `.github/workflows/raft-android-mini-lab.yml` مع worker=T1..T5. يخرج APK debug مستقلاً (package: `com.alwansan.raft.lab.t4` مثال) ولا يدخل مسار لعبة Raft الكامل. توقيع debug في runner قد يتغير عند إعادة البناء؛ لا تفترض تحديثاً سلساً فوق النسخة السابقة. لا تزل تطبيق Raft الحقيقي ولا تحفظ الأسرار في المختبر.

يدعم host: قائمة حالات importable JSON، PASS/FAIL/UNEXPECTED، Android pointer capture ON/OFF وتسجيل pressed/scroll/route، file/folder SAF، حفظ JSONL في app-private وتصديره بـMediaStore.Downloads إلى `Download/Games/cl/test/<worker>-<lab>-<session>/`. إن منع موفر الملفات اختيار مجلد Downloads فاستعمل **Pick testpack file**، ولا تطلب MANAGE_EXTERNAL_STORAGE. هذه **نسخة هيكلية تجريبية تحتاج compile/device validation**؛ حالات shaders/Unity/GLES Vulkan الأصلية ينفذها العامل في renderer مخصص مبني مع APK، وليس بنص من ملف خارجي.

**مهم على فرع feature:** workflow_dispatch قد لا يعمل قبل وجود workflow على default؛ استخدم [الطلب الخاص بالمختبر](../../BUILD_REQUEST_AR.md) بدل تعديل main أو مسار اللعبة. لا ترسل طلباً من أجل اختبار شكلي أو دون حاجة هاتف فعلية.
