# GT — الخطة الحيّة لاستعادة رسوميات Raft Android

**تاريخ التحديث:** 12 نوفمبر 2026 — GT / Chat-21.  
**فرع الكتابة الوحيد:** `feature/android-native-port`؛ **مصدر القراءة فقط:** `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`. **ممنوع Git LFS**.  
**سجل البيانات المهيكلة المعتمد:** [RESTORATION_PLAN.json](RESTORATION_PLAN.json) — راجع وضع كل دفعة وأدلتها قبل تعديل الحالة.  
**رسالة استكمال الجلسات:** [RESTORE_AR.md](RESTORE_AR.md)؛ **حالة GT:** [state.json](state.json)؛ **الذاكرة:** [MEMORY.md](MEMORY.md).  

## ما المقصود بـ«مستعاد»؟

المراحل لا تتساوى ولا تُجمَع في نسبة واحدة:
1. **موثّق من المصدر:** هوية الأصل/ملف ZIP2 وحجمه وبصمته الأصلية مثبتة.
2. **مستعاد داخل Export:** بيانات الأصل أو ربط Texture/Material أو إعداد importer مثبت في AssetRipper Export نفسه مع التحقق من GUID.
3. **اختبار Unity:** استيراد/ترجمة/Compile في Unity 2021.3.45f2 لنطاق محدد، وقد ينجح حتى مع عيب بصري.
4. **موجود داخل الحزمة:** APK+OBB+XAPK موثّق SHA/توقيع وCRC من commit محدد. ليس إثبات عرض صحيح.
5. **مقبول على الهاتف:** مسار الرسم من Material→Shader/Pass→Textures→GPU ونتيجة الصور/اللوق مثبتة على الجهاز، من دون أعطال معروفة.

**تنبيه:** الوصول إلى `82/82` في الجرد أو إنتاج XAPK لا يعني استعادة `100%` من رسوميات Raft. لا توجد حالياً نسبة صادقة موحّدة لكل الرسوميات المعروضة. الأعداد التالية لأصول المصدر ومواضع استعمالها وليست كلها أشياء مرسومة مستقلة.

## المستعاد والموثّق إلى الآن

| المجال | الدليل المنجز | المتبقي لإعلان الاستعادة الرسومية |
|---|---|---|
| **مصدر ZIP2** | **134 ملفاً** أصلياً بحجم **7,532,909,297 بايت** (82 حاوية Unity مسلسلة، 48 stream و40 مشهداً). تم SHA-authentication دون LFS وصدّر AssetRipper مشروعاً فعلياً. | إثبات الرسم لكل عائلة مورد على GPU، لا الاكتفاء بنجاح استخراجها |
| **Mesh والمشاهد** | **4,708 Mesh** أصلية؛ **40/40 مشهداً** موجوداً في export، وUnity نجح في بناء نسخة Android قديمة موقعة. | رسم Submesh وUV وNormal/Tangent والـSkinning لجميع الحالات المؤثرة، والتأكد من عدم ظهور الطوف أبيض |
| **Texture2D** | **4,050 Texture2D**، منها **3,948** ذات stream خارجي موثق و**102** inline/empty؛ **4,151** ربطاً داخلياً و**416/416** ربطاً خارجياً متطابقاً مع الأصل. | صحة Sampling والألوان/الـmips على Android في كل المواد |
| **Texture2DArray** | **9 مصفوفات/52 طبقة**، **50** طبقة BC3 ذات بيانات أصلية و**2** فارغتان أصلاً؛ أُصلحت 9 importer grids بالـexport المؤقت، وحُفظت GUID و**28** رابط Material؛ **50/50** pixel-parity للـtop mip في المصدر/Export. | كافة الـmips، استيراد/أخذ عينات Adreno وعرض المصفوفات داخل المشاهد |
| **مواد Material** | المصدر **1,556**؛ ملفات Export **1,536** منها **750** تعتمد Builtin؛ نجحت restorers في تحويل **16 مستند Material** مخصصاً من Dummy إلى غير Dummy. | **770 مستند Material مخصصاً لا يزال يرتبط بشيدر Dummy**؛ هذا عدد مستندات مواد وليس 770 شيدراً مختلفاً |
| **Unity Builtins/الـvendors** | أدوات دقيقة لأصول Unity 2021.3.45f2 (198 Shader من الأرشيف الرسمي) وTMP/PostFX/Volumetric وDepth Copy في pipeline، مع حراس للحفاظ على Meta/GUID. | تحقيق Pass/variant/مخرجات PostFX والظلال على هاتف Android، لا الاكتفاء بـsource restorer |
| **Shader48 للجسيمات** | Shader أصلي ذو **108 مواضع ParticleSystemRenderer**؛ أربعة أزواج VS/FS وثمانية برامج مترجمة ونجاح ShaderBundle تجريبي داخل Unity Android Vulkan باستخدام Sampler تقريبي. | المطابقة الأصلية للـsampler والـkeywords والـMaterial/GUID واختبار البكسلات على الهاتف؛ **ليس مدمجاً كشيدر أصلي مكتمل** |
| **الماء/Compute** | **165 Shader objects** و**9 ComputeShader objects** موثقة في المصدر؛ توجد أدوات للتحقق من Spectrum/Foam/FFT. | **42,229** أخطاء Pass و**7,263** خطأ kernel index 6 بسجل الهاتف، والهوية الحقيقية للـkernel6 لم تثبت |
| **حزمة Android** | استرداد حزمة قديمة موقّعة: APK **672,892,355 B** + OBB **2,320,414,462 B** وXAPK من [43246196803](https://github.com/alwansan/raf/actions/runs/43246196803). | البناء الكامل الحديث [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) لا يزال في Unity Editor عند آخر فحص؛ لم تُقبل الألوان/الماء/النار/الأداء على الهاتف |

**أدلة مصدر مهمّة:** [الجرد الكامل](https://github.com/alwansan/raf/actions/runs/43114648901) · [AssetRipper الحقيقي](https://github.com/alwansan/raf/actions/runs/43125542125) · [بوابة المصدر 9/28/416/50](https://github.com/alwansan/raf/actions/runs/43207734641) · [Shader48 التقريبي في Unity](https://github.com/alwansan/raf/actions/runs/43236578305).

## ما تبقّى والأولويات الحالية

| الرمز | الأولوية | الحالة | المهمة التالية / معيار قبولها |
|---|---|---|---|
| **M1** | P0 | **جارٍ** | راقب بناء [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) ولا تكرره وهو جارٍ. إذا فشل اقرأ **أول خطوة فاشلة** ثم أصلحها؛ نجاحه = APK/OBB/XAPK موقّعة حديثة وبصماتها صحيحة، وليس إصلاح الصورة |
| **M2** | P1 | **معطّل بنقص برنامج أصلي** | عالج `UltimateWater/Spectrum/Water Spectrum` (يتطلب 6 Pass على الأقل في log baseline) و`UltimateWater/Foam/Global` (2 Pass على الأقل): إثبات Shader GUID/Material/RenderTexture وربط HLSL الأصلي ثم Unity Android import وPass count وإعادة اختبار الجهاز |
| **M3** | P1 | **معطّل بنقص هوية kernel** | اربط kernel رقم 6 بكائن ComputeShader SHA-original وترتيب kernels ومكان Dispatch؛ لا تفترض أنه FFT اعتماداً على الرقم وحده. أعد بناء برنامج حقيقي وقارن النتائج على Vulkan ثم Adreno |
| **M4** | P1 | **لم يكتمل** | رتّب الشيدرات الأصلية حسب عدد استعمالات Renderer في المشاهد، وأصلح على دفعات من ضمن **770 Material Dummy**؛ فحص Guid→Pass→Keyword→Sampler→Texture، ثم المقارنة على الهاتف (ألوان الطوف، النار، الظلال) |
| **M5** | P2 | **قيد التشخيص** | عالج Cursor RGBA32 وOBB GUID وMissing MonoScript من مواقع الأصل، ثم أثبت استقرار frame time وسلامة الواجهة وعالم Offline |
| **M0** | P0 | **مكتمل لهذا النطاق فقط** | توثيق جرد المصدر ونقطة baseline واستقبال CL وتجربة بوابة اللوق. لا يعني استكمال الاستعادة الرسومية |

### فشل الهاتف الذي يحكم القبول

السجل `CL@cffd3f7be2d0c47649da9b28eae17c36d031f0e8` بتاريخ 12 نوفمبر لجلسة `LogRaft-20261112-183147-926` أثبت:
- **42,229** Water Shader invalid passes: **19,191 Spectrum** و**23,038 Foam/Global**.
- **7,263** Kernel index 6؛ لا يثبت السجل وحده جهة استخدام الـCompute.
- **4,668** تحذير Cursor RGBA32، **2** OBB GUID load failures و**1** MonoScript مفقود.
- اللقطات تظهر **الطوف أبيض تقريباً** مع بقاء بعض الأشياء ملونة؛ سجلت لقطة HUD هبوطاً إلى **0.29 FPS**. لا يُنسب سبب اللون أو الإطارات إلى كود معين من هذه اللقطات وحدها.

[الدليل الثابت](evidence/20261112_cl_device_graphics_failure_receipt.json) · [الاختبار المصدرّي الناجح بكشف الفشل](https://github.com/alwansan/raf/actions/runs/43263197989). أداة `scripts/gt_device_graphics_acceptance.py --strict` **ترفض** هذا السجل، وهذا التصرف صحيح. يجب أن ينجح الاختبار على *جلسة جديدة* فقط بعد زوال الأخطاء ومراجعة الصور.

## طريقة التقدّم من أي محادثة جديدة

1. افتح [رسالة الاستعادة](RESTORE_AR.md)، ثم [الخطة JSON](RESTORATION_PLAN.json)، [state.json](state.json)، [SUMMARY_AR.md](SUMMARY_AR.md) وآخر ملف `sessions/`. تحقّق من Git HEAD وActions قبل أي تعديل.
2. اختر هدفاً واحداً من M1→M5، وحافظ على مصدر ZIP2 SHA والبصمات الأصلية؛ استخدم runner مؤقتاً و`lfs: false`.
3. نفّذ اختباراً صغيراً أولاً (synthetic negative controls، ثم source-real/Unity/phone حسب التقدم)، سجّل Run ID وSHA وما **لم** يثبت.
4. حدّث خلية/حقل `Pxx` في JSON والحالة وملخص المالك، ثم [RESTORE_AR.md](RESTORE_AR.md) و[MEMORY.md](MEMORY.md) وملف الجلسة. لا تعلن «مستعاد» دون مستوى الدليل المناسب.
5. لا توقف البناء القديم ولا تضع **SUCCESS** في علامة `device_verified` لمجرد أن Unity أنتج APK أو أن مختبراً مستقلاً نجح. لا تحفظ شيفرات الشيدر الأصلية أو GUID الخاص داخل نتائج عامة.

**الحدّ الحالي:** الاستعادة نجحت في *توثيق المصدر واستعادة أجزاء Export والـvendor وبعض النماذج التجريبية*؛ **استعادة رسوميات اللعبة الكاملة لم تكتمل**. النجاح النهائي مشروط بتصحيح الماء والشيدرات والمواد والنار والظلال وحصول مقارنة هاتف موثوقة.
