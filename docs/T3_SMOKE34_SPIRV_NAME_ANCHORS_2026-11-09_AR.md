# T3 — فحص أسماء متغيرات الدخان الأصلي بعد SPIR-V وHLSL
2026-11-09، العامل T3، المشكلة RENDER-002 (OPEN/NOT_READY 0/3).

## خلاصة مثبتة
[CI42689814110](https://github.com/alwansan/raf/actions/runs/42689814110) SUCCESS من مصدر ZIP2 الأصلي ذي commit ثابت `15964ea8f246b6e076ce26b60931ee2e1a9a2385`، 6 مشاهد SHA و4 owners SHA، 17 اختبارات مصدر-حر جديدة +7 سابقات، 4/4 SPIR-V أصلي و4/4 دائري و2/2 توافق VS/FS، و4/4 تطابق resource shapes.

قارنا عبر `spirv-cross --reflect` أسماء المتغيرات **داخل الذاكرة المؤقتة** للتحويل المصدق نفسه، مع التحقق من تطابق بيانات انعكاس Location+Type الآمنة. النتيجة:
- مدخلات المراحل: 13 اسمًا في المصدر، 13 اسمًا في الدائري، **صفر تطابق اسم+نوع**، و13 اسمًا مصدر-فقط مقابل 13 مشتق-فقط.
- مخرجات المراحل: 9 في المصدر، 9 في الدائري، **صفر تطابق اسم+نوع**، و9 أسماء مصدر-فقط مقابل 9 مشتق-فقط.
- ليست هناك أسماء ناقصة؛ لكنها متغيرة بالكامل، لذلك لا يمكن اعتماد الاسم الذي ولده المترجم لإثبات mapping صحيح لـLocation.
- كما ثبت سابقًا [CI42687834153](https://github.com/alwansan/raf/actions/runs/42687834153): التغيّر في بعض مواقع الإدخال والإخراج مرشح إعادة ترقيم مع محافظة أنواع البيانات، **وليس إثباتًا دلاليًا**. نتائج VS/FS داخل كل نسخة متوافقة بنيويًا، وهذا لا يثبت أن متغيرات الدخان الأصلية احتفظت بمعانيها.

## تجربة ونتائج / حدود
أضيف gate إلى `scripts/t3_original_smoke34_spirv_translation.py` مع allowlist numeric و`scripts/t3_spirv_interface_name_drift.py` موروثة؛ اختبارات حماية من injection وduplicate/unsafe/missing/mismatched raw reflection. [CI42689581763](https://github.com/alwansan/raf/actions/runs/42689581763) فشل في بيانات اختبارات اصطناعية غير متزامنة (لا Original Shader)، ثم أصلحناها [837022d](https://github.com/alwansan/raf/commit/837022d50bdaa22abcf7537775fe33e4ed137114) وتحققنا على المصدر الأصلي. Artifact آمن [13706885671](https://github.com/alwansan/raf/actions/runs/42689814110/artifacts/13706885671)، expires 16 نوفمبر 20:07 UTC. لا أسماء/ShaderLab/PathIDs/GUID/برامج منشورة.

**القادم:** انتقل إلى بيانات DXBC الأصلية الفعلية (signature semantic/index/register/mask) وربط VS/FS أولًا، ثم قارِن مخارج مترجم SPIR-V بحدود مضبوطة. لا تخترع map من الاسم المولّد أو نوع vec4 مكرر، ولا تنشئ إصلاح لعبة/ShaderLab أو APK قبل إثبات المعنى وربط الPass. لا توجد صورة هاتف تثبت إصلاح الدخان بعد. حافظ على باقي عمل الفريق.
