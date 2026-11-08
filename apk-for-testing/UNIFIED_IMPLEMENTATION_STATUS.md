# حالة تنفيذ المختبر المشترك — سجل هندسي لا دعوى نجاح
- **سياق:** آخر مراجعة 2026-11-08؛ خمسة APKات منفصلة ناجحة في CI مع رابط ZIP Artifact لكل منها. هذا ليس APK مشتركاً واحداً، ونجاح CI لا يعني نجاح Android device.
- **الهدف:** package ثابت، embedded team pack، Auto All وAuto Tn، نتائج ولقطات مع fingerprint، قائمة مهام تصوير داخل التطبيق، رابط APK مباشر موثوق وحزمة pack واحدة. [تعريفات](UNIFIED_LAB_POLICY_AR.md) و[تصويت المختبر](SHARED_BUILD_READINESS.md).
- **مهم:** حتى تثبت CI لنسخة التطبيق المشتركة، الحالة SOURCE_IN_PROGRESS وليست READY_TO_TEST؛ لا تطلب من المالك تنزيل تطبيق مشترك غير موجود. لا ترفع ملفات game raw إلى public artifact.
- **T1:** أصل مصدر compute موجود في `host/app/src/main/java/.../T1ComputeProbe.java`; واجبات GPU يجب إثباتها على GLES Adreno، ولا تُعتبر Unity FFT recovered.
- **T2:** `T2GpuActivity.java` اختبار GLES synthetic FBO؛ لا تثبت Foam original.
- **T3:** `workers/T3/gles-lab/.../T3LabActivity.java` synthetic color/alpha/sRGB baseline؛ يدمج لاحقاً ضمن APK مشترك. يظل فحص بصرياً بحاجة screenshot/review.
- **T4:** الأزرار physical left/right/middle/wheel لا تعمل داخل Raft رغم حركة الكاميرا؛ يحتاج callbacks فعلية وبناء مقارنة مع bridge.
- **T5:** package hash/OBB/SAF/UI والتسليم؛ لا يدعي إثبات OBB mounted أو game FPS من نسخة مختبر.
- **فشل شائع ينبغي منعه:** 5×APK مختلفة، ZIP Artifact يوصف direct APK، أصوات/نتائج قديمة، بناء heavy full game، انتحال screenshots أو PASS synthetic، إفلات stale refs عند overwrite ملف مشترك، missing screenshot after background crash.
- **تاريخ CL 8Nov:** 74,359 water invalid pass، 11,165 FFT invalid kernel و7,372 cursor format warnings من تلك الجلسة فقط؛ لا تثبت علتها المباشرة أو إصلاحها.

## فحص تجميع Java الموحّد — 8 نوفمبر 2026
- فشل الفحص المصدر الأول [CI42503889895](https://github.com/alwansan/raf/actions/runs/42503889895) بسبب `IOException` import مفقود في T3 PixelCopy، وتم إصلاحه في [88131a3](https://github.com/alwansan/raf/commit/88131a3732b86909b5060eaa2ce31eca27ec6594).
- **الفحص الثاني [CI42504045625](https://github.com/alwansan/raf/actions/runs/42504045625) COMPLETED SUCCESS**: اختبار manifest/ready + Gradle `:app:compileDebugJavaWithJavac` للمشروع الموحد. هذا **ليس assembleDebug APK**، ولم يُنتج ملف تنزيل APK جديداً، ولا يثبت أداء الهاتف أو الصور/الأزرار.
- بعد الفحص المصدر لا يزال T5 مطالباً بالمراجعة في SHARED_BUILD_READINESS.md (NEED_BUILD من عامل واحد مع دليل فعلي) ثم طلب بناء APK واحد على SHA محدد؛ لا تكرر خمس عمليات بناء.
