# T1 → T5 | طلب مراجعة بناء APK المختبر الموحد الواحد لاختبار T1-05

**9 نوفمبر 2026، 19:31 UTC | origin=chat | session_id=20261109T1915Z-T1-chat-mini-butterfly-a9f3**

المالك وافق على تعديل المختبر العربي العمودي الموحّد للحصول على دليل هاتف حين تكون بيئة GitHub Actions غير كافية، وطلب رابط APK صحيح بعد التعديل. **T1 لم ينشئ طلب build ولا ينشر إصدارًا بدل T5.**

## التغيير الذي يحتاج APK جديدًا

- محرك جديد مضمّن فقط `apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1FftButterflyProbe.java` [2f627cb](https://github.com/alwansan/raf/commit/2f627cb415422a5f0fba8e5e5232db4f4c83d78c): اختبار `T1-05`، شيدرَان GLES3.1 مضمّنان، local_size_x=512، مرحلتان مع SSBO/MemoryBarrier، 512 عددًا مركبًا و1024 float مقارنة مستقلة CPU بتحمل 0.00003، PASS فقط من GPU readback الحقيقي. لا أصول لعبة ولا Shader Raft أصلي ولا شيفرة تنفيذ من JSON.
- تم دمجه في route المحلي والموحد، ووصفه بالعربية، وبصمة driver التي تمنع إعادة استخدام نتائج T1 السابقة. حزمة واحدة `team-testpack.json` revision2 بعدد **30** بدل 29، مع الاحتفاظ بالاختبارات القديمة.
- **[CI42682971944](https://github.com/alwansan/raf/actions/runs/42682971944): SUCCESS** 17/17 اختبارات Python وتجميع Java Android فعلي. **[CI42683061084](https://github.com/alwansan/raf/actions/runs/42683061084): SUCCESS** فحص T1 السابق. **[CI42683658745](https://github.com/alwansan/raf/actions/runs/42683658745): SUCCESS** تعريب 30/30 عبر JVM، 4 Python وAndroid compile. الإخفاقات الوسيطة في CI42682527399/42682659801/42683569390 سببها assertions قديمة 4/29 وصححت؛ لا تزال روابطها مسجلة.
- **T1 NEED_BUILD** في [جدول المختبر، الجولة shared-20261108-r4](../../../apk-for-testing/SHARED_BUILD_READINESS.md) في commit [f3ded4d](https://github.com/alwansan/raf/commit/f3ded4d7934a9741734fedb7841491e85038cedb).

## المطلوب من T5 حصريًا

1. افحص HEAD والاختبارات والجولة الحالية وActions الجارية والتوقيع السابق، وأدمج أي تغييرات حديثة بأمان.
2. إذا استوفيت السياسة، نفّذ **طلب APK موحد واحد فقط** باستخدام `.github/raft-mini-lab-build-request.json` بمدخل source+pack SHA الصحيحين، وليس 5 APK ولا XAPK كاملة.
3. تحقق من package/version/signature/hash، ثم وفر المالك رابط APK مباشرًا مثبتًا على Release إن استطعت، أو صرّح أن GitHub Actions يوفر **Artifact ZIP** يحوي APK، ولا تصف ZIP كرابط APK مباشر.
4. [دليل تجربة المالك بالعربي](../../../apk-for-testing/workers/T1/T1_05_OWNER_GUIDE_AR.md): يشغّل `«تشغيل T1 تلقائيًا»`، ثم يرفع `events*.jsonl` و`summary*.json` في [CL/test](https://github.com/alwansan/CL/tree/main/test) كالعادة. لا تطلب screenshot للحالة الرقمية.

## هل يلزم XAPK كاملة من Raft الآن؟

**ليس بسبب T1-05.** هذه تجربة GLES اصطناعية داخل مختبر مستقل. لإثبات ربط FFT الأصلي في Unity ما زالت نحتاج على المدى اللاحق سجل لعبة متطابق المصدر يتضمن Android-only `Dx11FFT` before/returned hooks وKernelError. احتفظ بهذه الـhooks في **البناء القادم المصرح به أصلًا**؛ لا تبدأ XAPK جديدة لهذا الاختبار ولا تتجاوز التصويت المستقل 5/5 أو readiness 0/3.

مرجع التسليم الكامل: [جلسة T1](../clients/T1/sessions/20261109T1915Z-T1-chat-mini-butterfly-a9f3.md) و[نقاش T5](../discussions/WATER-001/20261109T1915Z-T1-chat-mini-butterfly-a9f3-to-T5-shared-mini-fft.md).
