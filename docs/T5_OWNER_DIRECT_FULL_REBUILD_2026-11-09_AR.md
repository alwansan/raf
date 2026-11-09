# T5 — مراجعة آخر بناء Raft كامل وإطلاق النسخة التجريبية الحديثة (9 نوفمبر 2026)

**المالك أمر مباشرة ببناء اللعبة الكاملة؛ هذه حالة owner-direct واحدة، وليست تصويت 5/5 ولا جاهزية READY.** لا تُمس أصوات T1–T5 في trial-20261106-r1؛ الحالة الكاملة NOT_READY 0/3.

## سبب إخفاقات النسخ السابقة

- [42281310905](https://github.com/alwansan/raf/actions/runs/42281310905): فشل Unity Editor بعشرة أخطاء CS0234 حول AndroidPhysicalMouseCapture؛ إصلاح T4 [f554e8b6](https://github.com/alwansan/raf/commit/f554e8b6757e46aa037603ed592a04acc2bf7a61) وفحوص ABI قبل Unity عالجا السبب المصدرى.
- [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023): reconstruct نجح وأنشأ artifact موقّعًا وآخر للتسليم، لكن نشر GitHub Release فشل HTTP403: Resource not accessible by integration؛ لذلك delivery-result فشل. الـpublish job يطلب بالفعل contents:write ويقرأ RAFT_RELEASE_TOKEN الاختياري؛ إذا عاد 403 فصلاحية GitHub الفعّالة تحتاج إصلاح المالك/إعداد التوكن، وليس إلغاء بوابة التسليم.

## النسخة الجديدة

- إصلاحات T1–T5 المندمجة ومراحل الاستعادة المثبتة موجودة على الفرع feature/android-native-port حتى المصدر **f66277c0572065e6fde495a52468542851124281**. مراحل الاستعادة من ZIP2 تنفذ في الـworkflow، وليست وعدًا بأن كل ShaderLab/FFT أصلي استعيد.
- طلب بناء واحد مستقل [6316f457](https://github.com/alwansan/raf/commit/6316f457dd7587db47469ebd29ec0cbc849584dd) مع owner_direct_request=true وتوثيق **القيود الخمس الدقيقة للماء** دون اختلاق kernels.
- **[GitHub Actions 42696228231](https://github.com/alwansan/raf/actions/runs/42696228231)** ينتج عند النجاح APK+OBB+XAPK، Android ARM64 IL2CPP، Unity2021.3.45f2. Gate التفعيل والترخيص ناجح؛ reconstruct بدأ بالفعل ونفّذ استعادة بيانات الرسوميات الأصلية وتدقيق تسعة ComputeShaders. لم تُنتَج حزمة نهائية بعد وقت كتابة التقرير.
- T1 FFT source CI42695722354 SUCCESS بعد فشل اختبارات أقدم، T4 mouse CI42695755986 SUCCESS، offline adapter CI42695722198 SUCCESS. تغييرات ما بعد source SHA ليست ضمن هذه النسخة.

## دليل الهاتف وحدود الاستنتاج

- CL/test/shared-20261109-233132-554663211 يثبت **T1-05 mini GLES synthetic PASS** 1024 float وخطأ 2.384e-7، لكن original_raft_compute_executed=false؛ لا يعد نجاحاً لماء اللعبة.
- T5-02 في الجلسة نفسها يقيس SHA لملف مختار اسمه main.91...obb ويعطي EVIDENCE_READY فقط؛ ليس إثبات تركيب/فساد OBB على الهاتف. T3 الصور تتطلب مراجعة، T4 الماوس وتكامل Unity تحتاج تجربة اللعبة.

## الاستكمال

افحص التشغيل 42696228231؛ عند فشل reconstruct أصلح أول خطوة فعلية فقط. عند النجاح تحقق من APK package/version/signature، OBB SHA/size والـdelivery manifest/XAPK، ثم موقف النشر. عند HTTP403 حافظ على رابط Artifact ZIP بوصفه ZIP وليس Release مباشرًا؛ لا تطلق تشغيلًا ثقيلًا مكررًا بلا سبب.

جلسة الاستعادة: [T5 20261109T2045Z](../clients/T5/sessions/20261109T2045Z-T5-chat-native-owner-rerun-5f28.md).
