# بروتوكول التعاون والاستئناف (GFX-LAB)

## مستقل عن فريق T
لا نغيّر بروتوكول T1–T5 ولا ملفاتهم. نستفيد من الأدلة المثبتة لديهم مع ذكر أصحابها وروابطها، ولا نأخذ ملكية ملفاتهم أو مهامهم. فرعنا مشتق من main المصغّر، ولذلك ليس فيه Raft project أو سكربتات feature تلقائياً.

## دورة العمل
- في البداية: تحقق من HEAD وفرع الأصل وسجلات CI الحديثة والنسخة التي اختبرها المالك. اقرأ الذاكرة والجلسات والتحذيرات في ROOT_CAUSE_REVIEW_AR.md؛ حدّد اسم تجربة لا يتكرر.
- خزّن `experiments/<session_id>.json` فيه: `session_id,origin,issue_id,question,hypothesis,reference_refs,control,planned_tests,resource_key,status`. لا تحفظ بيانات مصدر خاصة أو لقطات أصلية حساسة.
- ثم `memory/sessions/<session_id>.md` ويسجّل `resumed_from,base_sha,source_ref,commands,run_urls,outcome,evidence_level,negative_controls,limitations,next_step`.
- `memory/STATE.json` فهرس قابل للتحديث؛ لا يتغلب على جلسات أو CI أحدث. `memory/MEMORY.md` ملخص قرارات ثابتة ومعلومات قابلة للاستعادة. إن اختلف الدليل مع الذاكرة، صدّق الدليل الأحدث المثبت وحدّث الملخص.
- إن تعذر مورد أو تغير SHA، توقف عن ادعاء الإثبات، واختر تجربة بديلة صغيرة. أنشطة CI طويلة: سجّل رابطها ولا تفترض نجاحها.

## سلم قبول لا يقبل الاختصار
1. إثبات أصل الملف SHA + النوع/الهوية (ORIGINAL_SOURCE).
2. إثبات التصدير **بنفس عملية AssetRipper** وربط GUID/مادة/برنامج (SAME_EXPORT).
3. Unity 2021 يستورد ويترجم البديل الصحيح، والـPass والـkeywords والـCB والـsampler صحيحون (UNITY_IMPORT_COMPILE).
4. مخرجات مرشح GPU مطابقة لمرجع أصل مثبت لنفس المدخلات (GPU_EXPERIMENT).
5. راصد البكسلات من **Raft Android الحقيقي** مع تعريف نسخة/OBB والمشهد/الإعدادات (ANDROID_GAME_PIXELS).
6. قبول المالك على الهاتف (OWNER_ACCEPTANCE).

لا تخلط successful shader compile مع shader correctness، أو mini GLES screenshot مع Raft، أو `Dummy` مع shader مستعاد، أو عدد material docs مع عدد rendered pixels.

## السلامة والتسليم
- تجارب source-only افتراضياً؛ ابدأ بالأقل كلفة والأكثر قابلية للفصل بين الفرضيات.
- لا تغيّر بيانات PC أو APK الحالية، ولا تنسخ المصدر المفكك العام، ولا تسجّل مسارات خاصة/أرقام GUID/قنوات shader الخاصة علناً.
- حافظ على البيانات الموقعة والمراجع SHA، وابعد التشخيص الجديد عن تشغيلات T الحية.
- عند ثبوت إصلاح، سلّمه كتقرير مع حدوده للعامل المالك قبل نقل patch إلى feature. الاختبار المستقل لا يرفع readiness.
