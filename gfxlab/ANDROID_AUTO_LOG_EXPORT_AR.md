# GFX-MULTI-031 — تسجيل اختبارات Android بالكامل وتصدير ZIP إلى Downloads
**GFX-LAB | 2026-11-10 | لا يعني استعادة Shader48 الأصلي**

## متطلبات الهاتف
الموقع المستهدف بالضبط:
`/storage/emulated/0/Download/Games/cl/test/g/`

التطبيق `GfxLab-Multi-Six-AutoLogs.apk` حزمته المستقلة `com.alwansan.raft.graphicslab.autologs`، ويعرض M00–M05 مع الموديلات والتكستشرات الأصلية من ZIP2، لكنه يستخدم Unity Standard/ChannelProbe التشخيصيين وليس Shader48 الأصلي. لا يلزم OBB.

## ما يسجَّل تلقائياً
- عند كل تغيير Model M00–M05 أو NEXT MATERIAL أو نوع BASECOLOR/NORMAL/METALLIC أو RGB/R/G/B/A أو SOURCE/FORCE_LINEAR أو SURFACE 1/2 وغيرها، يضاف سطر JSON جديد إلى `snapshots.jsonl` مع سبب التغيير والوقت/الفريم وجميع تفاصيل نموذج الاختبار (المادة، GPU/API، ColorSpace، إحصاءات الجهاز، حالة الشيدر والأخطاء)، ويضاف حدث إلى `events.jsonl`.
- كل رسائل Unity من Debug.Log/Warning/Error/Exception/Assert تُجمع بواسطة `Application.logMessageReceivedThreaded`، مع نص الرسالة والـstack trace الذي يوفره Unity. يتم تفريغ الطابور على الخيط الرئيسي، مع حفظ أخطاء الكتابة وحالات إسقاط الرسائل إذا زاد الضغط.
- Snapshot إضافي كل 15 ثانية، وعند توقف/خروج التطبيق. `summary.json` يتضمن عدد الرسائل والأخطاء والتحذيرات وفرق الإسقاط ورسائل فشل القرص. حتى عند إغلاق التطبيق تبقى الجلسات السابقة في `persistentDataPath/gfxlab/sessions/`.
- هذا **لا يسحب تلقائياً logcat العام أو سجلات GPU kernel** على أندرويد بلا صلاحيات، بل يسجّل ما يصل إلى Unity وما نسجله نحن من اختبارات. كاش الشيدرات الأصلي غير مُدرج، والأصول الأصلية لا تُصدَّر ضمن الـZIP.

## زر التصدير
اضغط `EXPORT ZIP` من الصف العلوي بعد إنهاء الاختبارات. لا تحتاج `COPY LOG`، وهو لا يزال اختيارياً. التطبيق ينشئ `GFXLAB-ALL-TEST-LOGS-<UTC>-<session>.zip` يضم الجلسة الحالية وكل الجلسات السابقة الموجودة في بيانات **هذه الحزمة الجديدة**، و`latest/multi-report.json` وREADME.

Android 10+ يستخدم `MediaStore.Downloads` عبر Java bridge مع `RELATIVE_PATH=Download/Games/cl/test/g/`، و`IS_PENDING` أثناء النقل، والتحقق من مكان الحفظ الفعلي وحجم الـZIP بعد كتابة الملف قبل إظهار `ZIP SAVED`. لا تُطلب صلاحية الوصول الشامل إلى الملفات.

**إذا فشل نقل الملف، لا يدّعي التطبيق أن الحفظ الخارجي نجح.** تظهر `EXPORT FAILED` ورسالة السبب، ويظل ملف ZIP مؤقت في مجلد بيانات التطبيق `persistentDataPath/gfxlab/exports/`. التقاط logcat النظام خارج قدرة هذا التطبيق بدون جسر تشخيص مخصص وصلاحية صريحة.

## تعليمات اختبار المالك
بعد بناء CI ناجح وتوقيع APK: افتح M00 ثم M03، غيّر المادة BASE/PBR، ثم القنوات Normal/Metallic، وحالة Linear، ثم SURFACE 2/2 عند M03. لا تضغط COPY LOG لكل حركة. اضغط EXPORT ZIP **مرة واحدة**؛ افتح مدير ملفات هاتفك على المسار أعلاه وارفع ZIP فقط. إذا فشل التصدير أرسل صورة الخطأ الظاهر بدلاً من نقل ملفات يدوياً، ويمكننا إصلاح المسار بحسب الرسالة.

## درجات الإثبات
- `SOURCEFREE_TESTS`: تحقق من تسجيل جميع الأزرار وفحص مسار MediaStore وأرشيف ZIP بالحماية. **لا يثبت قدرة MIUI على الحفظ.**
- `UNITY_BUILD`: Unity 2021.3.45f2 يبني APK موقّعاً على GitHub.
- `OWNER_MEDIASTORE_TEST`: لا يُعلن حتى يضغط المالك EXPORT ويتحقق الملف الحقيقي في Download/Games/cl/test/g وأنه يحتوي `events.jsonl` و`snapshots.jsonl`.
- `SHADER48_RESTORED`: يبقى FALSE. لا يغيّر نظام الـlogs موانع original property→DX11 register/CB، PassStates وPC↔GPU parity.

## مصادر تنفيذ التخزين
Android Documentation: <https://developer.android.com/training/data-storage/shared/media> (التطبيق يملك الملفات التي ينشئها في MediaStore بدون إذن تخزين عام)، وUnity Java source plugin API <https://docs.unity.cn/cn/2021.3/Manual/android-java-and-kotlin-plugins-create.html>.


## ملاحظة مهمة قبل تحديث APK في المستقبل
قد تستخدم نسخ GitHub Actions مفاتيح توقيع Debug مختلفة. إذا طلب Android إزالة إصدار قديم لإعادة تثبيت إصدار جديد من **نفس الحزمة**، صدّر ZIP أولاً لأن إزالة التطبيق قد تمحو ملفات `persistentDataPath` وجلساته السابقة. عالجنا هذه الدورة بحزمة مستقلة `com.alwansan.raft.graphicslab.autologs` كي لا نستبدل `com.alwansan.raft.graphicslab.channels` السابقة. مصدر الـZIP الخارجي في Download يبقى بعد حذف التطبيق عادةً، لكن تحقق من وجوده قبل إلغاء التثبيت.
