# Graphics Root-Cause Lab — حدود العمل

هذه التعليمات تخص **فقط** الفرع `experiment/android-graphics-rootcause`. أنشئه المالك من `main@9b89f62772c2c61f6269fd2249f8560af1522892` بتاريخ 2026-11-09. **لا تُسقط تعليمات فرع الفريق عليه بصورة آلية**.

- الكتابة في هذا الفرع فقط. لا تعدّل `main` أو `feature/android-native-port` أو `zip`/`zip2` أو `Unity-Editor` أو مستودع CL؛ الفريق T1–T5 يعمل بالتوازي.
- هذا الفرع **مختبر مستقل خفيف**، وليس نسخة كاملة من اللعبة. لا تستورد أصول Raft أو صور/شيفرات مفككة أو مراجع GUID خاصة أو DXBC/HLSL/SPIR-V خاصة إلى GitHub العام. بيانات الأصل تُقرأ عند الضرورة في runner خاص مع SHA مثبت وتُحذف، ويُنشر تجميع آمن فقط.
- المصادر: [فرع الفريق](https://github.com/alwansan/raf/tree/feature/android-native-port)، [سجلات الهاتف](https://github.com/alwansan/CL/tree/main/raft%20log)، [اختبارات الهاتف](https://github.com/alwansan/CL/tree/main/test). لا تعتبر دليل المصدر أو CI الصناعي دليل بكسلات Android.
- قبل أي تجربة اقرأ `prompt/graphics-lab/RESTORE_AR.md` و`memory/MEMORY.md` و`memory/STATE.json` وأحدث `memory/sessions/` و`docs/ROOT_CAUSE_REVIEW_AR.md`؛ تحقق من HEAD والتشغيلات الحية قبل كتابة جديدة.
- ابدأ كل دورة `session_id` مستقلاً، `origin=chat` افتراضياً، واكتب نطاقاً مفصولاً ومصدر/تشغيل/baseline ومخرجات متوقعة في `experiments/` قبل التنفيذ. التحديثات أثناء الجلسة في ملفها فقط، والملخص/STATE في النهاية؛ لا تستبدل جلسة أخرى.
- كل نتيجة لها مرحلة دليل واضحة: `ORIGINAL_SOURCE`، `SAME_EXPORT`، `UNITY_IMPORT_COMPILE`، `GPU_EXPERIMENT`، `ANDROID_GAME_PIXELS`، `OWNER_ACCEPTANCE`. لا ترقي درجة دون إثبات مستقل. التمييز بين عدد `Material` وعدد `Renderer slot` وعدد البكسلات واجب.
- لا تضف شيدر Dummy بوصفه إصلاحاً؛ لا تزود عدد Pass شكلياً، ولا تضبط flags نجاح مزيفة. لا تدمج أي تصحيح في فرع الفريق إلا بتوافقه مع المصدر الأصلي وبالاتفاق مع العامل المالك للنطاق.
- منع APK/OBB/XAPK جديد بمجرد نجاح محاكاة أو ترجمة. إن احتجنا اختبار Android لاحقاً، راجع مركز mini lab الموحد لدى T5، وحافظ على شروط بناء اللعبة الحقيقية وتصويتها المستقل.
- اختبارات CI في هذا الفرع، إذا لزمت، مصدرية/خفيفة، `cancel-in-progress: false` واسم تجربة فريد؛ لا تطلق عمل Unity ثقيل أو تعيد بناء اللعبة دون مبرر موثق وتنسيق.
- حفظ الصوت/Settings/دخول العالم المثبت في نسخة 89؛ لا تخلط تشخيص الرسوم مع تراجع وظائف أخرى.
