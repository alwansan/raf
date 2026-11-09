# T5 → T1–T4 | تسليم APK مختبر موحّد واحد بمدخل ملفات المالك (R5)

session_id=20261109T2002Z-T5-chat-owner-local-logs-6d27; origin=chat
build_source_parent=731d7a68bb3826b348d0314f694737b522e92976; build_request=97014d9b7b579480af37ae254de89080ce29f78f

المالك وضع ملفات اختبار داخل Android Download/logs/ وليس في CL: APK لعبة Raft وmain.91...obb وmanifest.json وteam-testpack.json وT3.json وt2-water-render-testpack.json وt4-mouse-testpack.json وBlackBox logcat. هذه الملفات غير متاحة لنا من GitHub/Actions، يلزم اختيارها في تطبيق الهاتف عبر SAF بإذن المالك.

## التنفيذ المثبت

- مصدر حاوية T5 يحتوي ACTION_OPEN_DOCUMENT_TREE + persisted read grant + scoped recursive listing حتى 500 إدخال/عمق8؛ العرض بالعربية. لا قراءة OBB تلقائية، ولا مسار مطلق أو صلاحية تخزين عامة.
- زر SHA256 صريح للـAPK/OBB المكتشف يستخدم StreamSha256 الموجود، يسجل selected_file/bytes/full SHA ولا يرقّي EVIDENCE_READY إلى PASS؛ manifest يعرض حقولًا محافظة غير معتمدة.
- إمكانية استيراد ملف team-testpack محلي متوافق وغير أقدم؛ الحزم القديمة T2/T3/T4 تُعرض كملفات بيانات غير تنفيذية، ولا تُفسّر shader أو تضيف driver.
- سجل BlackBox الخاص بالمالك يُفحص عند الضغط فقط حتى 4MiB، وتُعرض عدادات كلمات دون طباعة النص أو paths/PIDs/أسرار؛ هذه ليست LogRaft مؤكدًا ولا صحة GPU.
- Source CI42690234266 SUCCESS (actual SDK35 compile + JVM controls). R5 requested with CAS head lease commit97014d9; build CI42691609924 SUCCESS. APK package com.alwansan.raft.lab.shared, 0.2.17-shared v17, 110042 bytes, SHA256 272d4ce9a199c5876b179926c9f27ed0d7a8c4db34b2a3993de2c44a94e323cf; v2 DEBUG cert 1ce4e4c53eb8a48a1d0639dadba8bf70eae556911214b10babb20b08e283f20d. Artifact ZIP13707257362 expires 2026-11-23T20:18:56Z. Not direct GitHub Release.
- Existing T1-05 GLES local512 compiled class present, total 30 cases retained. Testpack unchanged sha256 9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6. T5 is NO_BUILD, full game Raft readiness remains NOT_READY.

## المطلوب من زملاء الفريق عند توفر نتيجة الهاتف

- T1: اقرأ T1-05 actual GPU checked_floats/first_mismatch from fresh CL/test؛ الفحص الاصطناعي لا يثبت Raft original FFT.
- T2: تعامل مع t2-water-render-testpack.json القديم بوصفه بيانات فقط؛ 4 فحوص GLES المدمجة موجودة، أما shader Raft الأصلي فيحتاج driver/Unity مخصص ودليل فعلي.
- T3: T3.json لا يضيف driver؛ شاشات الألوان T3-01..06 والتقاط PixelCopy تحتاج صورة هاتف ومراجعة، وليس اسم ملف داخل logs.
- T4: t4-mouse-testpack.json لا يمنح تحكمًا في الماوس؛ افتح فحوص captured/uncaptured داخل APK بماوس حقيقي، ثم راجع فرقها عن اللعبة.
- T5: قارن SHA256 للـmain.91/APK ببصمات signed delivery **لنفس الإصدار 91** فقط؛ لا تصنّف mismatch مع v89 فسادًا. احتفظ بـCL خام للقراءة فقط. أدلة owner تحت https://github.com/alwansan/CL/tree/main/test.

دليل المالك: apk-for-testing/OWNER_LOCAL_LOGS_GUIDE_AR.md، مركز التنزيل: apk-for-testing/TEST_CENTER.md.
