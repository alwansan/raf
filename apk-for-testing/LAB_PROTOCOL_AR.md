<!-- OWNER_SHARED_MINI_LAB_20261108 -->
> **تم استبدال تعليمات إنشاء mini APK منفصل لكل عامل بتوجيه المالك الأحدث:** [البروتوكول المعتمد الموحد](UNIFIED_LAB_POLICY_AR.md) و[برومبت الاستعادة](../prompt/coordination/T_TEAM/RESTORE_SHARED_LAB_AR.md). الأجزاء أدناه تاريخية لأدلة وقيود Android/ملفات LogRaft فقط؛ لا تستعملها لتوجيه العمال إلى خمسة APK أو خمسة packs. التصويت الخاص بـXAPK الكامل يبقى دون تغيير.

# نظام APK الاختبارات المصغرة — فريق T1–T5
**توجيه المالك 8 نوفمبر 2026 — مستقل عن XAPK الكامل.**
يقرأه كل عميل في بدايات chat/scheduled والاستعادة. الهدف صنع اختبار Android صغير سريع، لا اللعبة كاملة، لقياس فرضية تستلزم هاتف المالك. لا يلغي تصويت الخمسة الموجود في prompt/coordination/T_TEAM/TRIAL_BUILD_POLICY_AR.md ولا يغير شروط 3/3 للجاهزية النهائية.

## قواعد العمل
- T1: FFT/Compute/GPU. T2: Foam/Spectrum/Blur وShaderLab. T3: ألوان/خامات/mesh/نار وإضاءة/particles. T4: ماوس فعلي (Left/Right/Middle/Scroll) وPointer Capture والعالم والحفظ. T5: host مشترك وCI وتكامل حزم وتوزيع وأداء. لكل عامل صلاحية إنشاء مختبر باسمه؛ لا يحتاج أصوات 5/5.
- قبل إنشاء مختبر جديد: افحص التجارب الحية والعمل الجاري وGitHub Actions؛ إذا أمكن حسم الفرضية بـCPU/Unity/CI أو باستيراد testpack إلى تطبيق موجود فلا تصنع APK جديداً. إذا استلزم جهازاً، أنشئ أصغر APK فعلي واختبارات مرقمة 2–10، إيجابية وسلبية، مع baseline واضح.
- **لا تخلط بين أنواع الإثبات:** اختبار OpenGL/Vulkan أصلي صغير لا يثبت استعادة ShaderLab/Unity ولا لعبة Raft الكاملة. لا تستخدم dummy أو أعلام نجاح وهمية ولا تتجاوز الأصالة/GUIDs والحفظ.
- سجّل: worker/lab ID، app package وversionCode، immutable source SHA، case IDs، expected/observed، PASS/FAIL/UNEXPECTED، طابع UTC، الجهاز/API/ABI/GPU driver، lifecycle والـinput callbacks (action/source/buttonState/actionButton/axis)، أخطاء Shader/GL/Vulkan/Unity، الاستثناءات والـstack، FPS مع نطاق القياس، وSHA256 للملفات. لا تدعي التقاط Logcat لألعاب أخرى دون أداة منفصلة وصلاحيات حقيقية.
- تبقى الملفات والـlogs أثناء العمل في app-private persistent storage، ثم تُصدر تلقائياً أو بزر Export إلى **`/storage/emulated/0/Download/Games/cl/test/<worker>-<lab>-<session>/`**. على Android 10+ استخدم MediaStore.Downloads/RELATIVE_PATH لإنشاء الملفات التي يملكها التطبيق؛ وعلى Android 11+ لا يمكن اختيار جذر Download كله بـACTION_OPEN_DOCUMENT_TREE. استخدم ACTION_OPEN_DOCUMENT أو مجلداً فرعياً يسمح به المنتقي، وACTION_CREATE_DOCUMENT كبديل. لا تعتمد على READ/WRITE_EXTERNAL_STORAGE أو MANAGE_EXTERNAL_STORAGE أو روت كي تعمل الطريقة على Android 15. مرجع: https://developer.android.com/training/data-storage/shared/documents-files .
- يوفر المختبر زر اختيار ملف أو مجلد للاستيراد عبر SAF: testpack.json declarative data-only، وملفات PNG/mesh/parameters بمسارات نسبية آمنة، SHA256 وحجم محدود. **لا تسمح بتنفيذ dex/so/script أو code من حزمة مستوردة**. شيدرات/Render/Compute حقيقية تُدمج في APK mini lab أثناء البناء، لا من textpack غير موثوق أو PC DXBC غير مدعوم.
- يمكن بناء مختبر Tn مستقل (native GLES/Vulkan أو Unity صغير إذا لا بد)، بعنصر لعبة أصلي واحد مرخّص ومحدود فقط مع مواد/خامات لازمة، لا ZIP2 الكامل؛ لا تنشر raw proprietary game assets/decompiled shaders/أسرار في repo أو Releases العامة. سجّل حدود التجربة.
- تطبيق LogRaft في branch lograf يمكن تشغيله بصورة مستقلة لالتقاط ما يسمح به Shizuku/Android. لا تخلط سجله مع logs المختبر ولا تفترض أن استيراده يعطيه امتيازات إضافية.
- **كل عامل يحدّث صفه وحده** في TEST_CENTER.md عند ظهور APK/ملف حقيقي قابل للتنزيل؛ وضع NOT_PREPARED/SOURCE_READY/BUILDING/READY_TO_TEST/DEVICE_PASS/DEVICE_FAIL/MIXED. أدرج رابط download ثابتاً صحيحاً بعد التحقق منه، أو صفحة Actions Artifact + وقت انتهاء صلاحيتها، وSHA256/size/package/version/commit وطرق الاختبار والصور والـlogs. لا تنشئ روابط متوقعة ولا تطلب اختباراً قبل وجود الملف.
- ابق في الدردشة نفسها واحفظ origin/session_id/sha/work_id وتجربتك في clients/Tn/sessions وMEMORY.md عندما تعمل، مع expected SHA وعدم الكتابة فوق ملف عامل آخر. لا توقف عملاً مفيداً بانتظار المستخدم؛ ساعد بقية الفريق عند تعذر التقدم. لا تدّع استمرار التنفيذ بين الدورات.
- لا تلمس .github/raft-native-build-request.json أو workflow لعبة Unity الكامل لإنتاج مختبر مستقل. استخدم workflow اختبار محدوداً منفصلاً وcancel-in-progress:false، ولا تزاحم موارد Unity/GPU الثقيلة. **المختبر لا يدخل تصويت 5/5 للعبة؛ XAPK الكامل يبقى بتصويت الخمسة فقط.**

## شروط تسليم APK مختبر فعلي
1. كود مختبر قابل للبناء، CI/App build حقيقي وليس source-only، وملف APK موقّع للاختبار له SHA256.
2. UI تعرض هوية/نسخة التطبيق ورقم الاختبار وتعليمات خطوات واضحة، تسجيل input/graphics/asset/error والنتيجة والـtimestamp.
3. اختبار الاستيراد من ملف/مجلد عبر SAF، ومكان export الفعلي المذكور، مع فشل صريح لا ادعاء نجاح.
4. تحديث TEST_CENTER.md بروابط حقيقية وتجارب وخطوات وصور مطلوبة؛ تسجيل نتيجتها عند عودة المالك.
5. عدم اعتبار نجاح مختبر بمفرده علاجاً للعبة الكاملة حتى يُدمج ويُختبر على نسخة Raft حقيقية.

ملاحظات تجربة 8 نوفمبر في OWNER_FEEDBACK_2026-11-08_AR.md. صيغة بيانات الاختبار في TESTPACK_FORMAT.md.
## إطلاق Workflow من فرع غير افتراضي
اقرأ [BUILD_REQUEST_AR.md](BUILD_REQUEST_AR.md). الإطلاق الآمن يكون commit مستقل لتغيير `.github/raft-mini-lab-build-request.json` برسالة `[raft-mini-lab]` وبصمة HEAD الأب، لأن GitHub `workflow_dispatch` قد لا يظهر لـworkflow لم يُنشر في default branch. لا تنشئ request لمجرد إنشاء صفحات/تعريفات ولا تتجاوز فحص التداخل والـSHA.
