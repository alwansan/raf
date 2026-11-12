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
| **الماء/Compute** | **165 Shader objects** و**9 ComputeShader objects** موثقة في المصدر؛ توجد أدوات للتحقق من Spectrum/Foam/FFT. | أصل Spectrum مُثبت بـ**7 Passes** و**28 برنامج VS/FS حسب variants** (7×2×2)، وأصل Foam Global بـ**2 Passes**؛ على الهاتف **42,229** أخطاء Pass و**7,263** خطأ kernel index 6، وهوية هذا kernel لم تثبت |
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

### تدقيق الفرق بين المصدر الأصلي ورسالة Pass من الهاتف

- كائن `UltimateWater/Spectrum/Water Spectrum` الأصلي يحمل **7 Passes** تحت SubShader واحد، وبرنامجين (VS/FS) لكل نسختين من كل Pass = **28 مرجع stage**؛ وثقته [B09 الأصلي](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/b09_spectrum_topology_contract.py) مع [CI 41920232173 SUCCESS](https://github.com/alwansan/raf/actions/runs/41920232173).
- كائن `UltimateWater/Foam/Global` الأصلي يحمل **2 Passes** وأربعة برامج VS/FS أصلية؛ برامج Foam الحقيقية وCB0 والـSamplers تحتاج ربطاً وتجميع Unity Android قبل الدمج.
- `verify_water_render_contract.py` يطلب `Spectrum >= 6` لأن السجل القديم طلب Pass #5. **هذا حد أدنى لتفسير log فقط**؛ استعادة شيدر Spectrum الصحيحة تحتاج **7 Passes مع Pass states والـkeywords الأصلية**، ولا يجوز ملء العدد بـPass فارغة.
- [CI 43268872421 SUCCESS](https://github.com/alwansan/raf/actions/runs/43268872421) يختبر هذا الفرق في [بوابة الخطة](../../scripts/gt_restoration_plan_check.py)، ولا يثبت أن البرنامج الأصلي صار داخل APK.

### تجربة GT الجديدة داخل Unity Editor (اختبار قراءة فقط)

أُضيف [GTOriginalWaterPassImportProbe.cs](../../android-port/Editor/GTOriginalWaterPassImportProbe.cs) ويُستدعى من `AndroidNativeBuild.ValidateSdkBindings` قبل بناء Android التالي. يفحص كائني Spectrum وFoam المسمّيين في Assets، ويُبلغ عن عدد الـPasses المستوردة وعن وجود `//DummyShaderTextExporter` وتكرار اسم shader وأخطاء المسار. يحفظ الفرق بين **Spectrum الأصلي 7** والحد الأدنى المسجّل **6**، وFoam الأصلي **2**. لا يطبع GUID أو HLSL أو مسارات الأصل، **ولا يعدّل أي ملف shader أو .meta أو Material**. أدلة Unity على الهاتف ما زالت غير متاحة؛ الفحص التشخيصي وحده لا يُصلح الشيدر ولا يضمن أصالة محتواه.

**[43269999662 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43269999662):** 5 اختبارات مصدرية + تجميع وتشغيل C# بواسطة .NET مع محاكيات Unity API، والتحقق من Shader Spectrum ناقص بPass واحد وFoam بPassين ومنع path traversal. **هذا ليس تشغيل Unity Editor الأصلي ولا اختبار Adreno.** في البناء الحديث التالي، ابحث في سجل Unity عن `GT_WATER_IMPORTED_PASS_DIAGNOSTIC` ثم اربط الناتج بالـGUID والـMaterial وبرنامج المصدر قبل تعديل حالة `unity_verified`.

## دفعة GT الجديدة — Spectrum الأصلي: مصدر → حالات الرسم → ShaderLab خاص (Chat-22)

استخدمت المصدر الأصلي `ZIP2@15964ea8` من دون LFS، وأصلحت تعارض مكان ملف `sharedassets0.assets` بين موفّر ZIP2 وأداة B09، بعد التحقق من **115,978,112 بايت وSHA الأصلي**. **المصدر الأصلي لم يتغير**.

| التحقق | مثبت | حدّ الإثبات |
|---|---|---|
| Spectrum Shader topology | **7 Passes أصلية** و**14 زوج VS/FS** | استعادة هويات المصدر، لا استيراد Android |
| Vulkan 1.1 | **28/28 stage variants** تم تجميعها فعلياً، و**13** برنامجاً مميزاً أُعيدت ترجمته | نجاح glslang/spirv-val فقط |
| حالات الرسم | **7/7** حالات Render State مختلفة، ببيانات أصلية | SHA-verified private source state، لا Pixels |
| خصائص Spectrum | **6**: خامتان Texture و3 Float وVector واحد | القيم/الأسماء باقية في scratch الخاص، ليست منشورة |
| ShaderLab | **مرشحان خاصّان، كل واحد 7 Passes**؛ المجموع 14 Pass structural envelopes | **ليسا شيدراً واحداً ذا Keyword routing أصلي**؛ لا GUID/Material parity |
| أداة Unity 2021 | تجربة **isolated variant0** على Android Vulkan أُطلقت في [43275506146](https://github.com/alwansan/raf/actions/runs/43275506146) | لا تعتبر Unity نجاحاً قبل انتهاء التجربة وفحص `ProbeResults` |
| اللعبة الأصلية على الهاتف | **غير مكتمل** | ألوان الماء والـSamplers والـCB0 والـRT والـShader/Material GUID لم تُثبت |

الاختبارات المثبتة: [43273276394 — ترجمة البرامج 28/28](https://github.com/alwansan/raf/actions/runs/43273276394) · [43273958426 — حالات الرسم الأصلية](https://github.com/alwansan/raf/actions/runs/43273958426) · [43274729958 — مرشحا ShaderLab الخاصان](https://github.com/alwansan/raf/actions/runs/43274729958). كلها **SUCCESS في نطاقها فقط**.

**الخطوة القادمة:** افحص [تجربة Unity 43275506146](https://github.com/alwansan/raf/actions/runs/43275506146). إذا فشلت في استيراد shader أو بناء AssetBundle، استخرج فئة الخطأ الآمنة وصحّح ربط sampler/cbuffer من الأصل؛ لا تصنع سامبلر أو pass وهمياً. بعد نجاح Unity بشكل منفصل، أثبت variant1 ثم Keyword routing الحقيقي وربط GUID والمادة وRT الأصلي، ثم جرّب رسم الماء على الهاتف. لا تدمج المرشحين الاثنين في اللعبة بوصفهما شيدراً أصلياً مكتملًا.

### نتيجة تجربة Unity 2021 الفعلية — عطل CBuffer في Spectrum (Chat-22)

[43275506146 — FAILURE](https://github.com/alwansan/raf/actions/runs/43275506146): **استورد Unity فعلياً Shader Spectrum خاصاً بـ7 Passes** وبنى Android Vulkan AssetBundle حجمه **6,095 بايت**، لكن الفاحص سجّل **خطأَي Shader**، لذلك لا يجوز اعتبار الاختبار ناجحاً. كشف Unity GLSL linker اتحاد نفس اسم Uniform CBuffer بين Vertex وFragment بأحجام مختلفة (`vec4[4]` أمام `vec4[5]` أو `vec4[7]`)؛ ليست مشكلة نقص Passes في هذا المرشح، وليست دليلاً على أن البرنامج الأصلي معطوب.

أضفت إصلاحاً تشخيصياً محدوداً هو `scripts/gt_spectrum_private_stage_buffer_isolation.py`: يفصل أسماء رموز CBuffer المؤقتة بحسب Stage على **نسخة ShaderLab الخاصة** فقط، مع إعادة مطابقة بايتية عكسية بعد إزالة البادئات والتأكد من عدم تغيير annotations من نوع `register(...)`. لا يغيّر مصدر ZIP2 أو Shader/.meta/GUID أو ربط Material الأصلي. [43276622833](https://github.com/alwansan/raf/actions/runs/43276622833) توقف على بيانات الاختبار الصناعي بسبب أحرف `\\n` حرفية لا أسطر فعلية. أصلحت المثال في commit `8e46f03a`؛ و[التجربة الجديدة 43277618651](https://github.com/alwansan/raf/actions/runs/43277618651) دخلت Unity 2021 Android Vulkan، **وما تزال نتيجة تجميع الشيدر غير مثبتة عند آخر تحقق**؛ يجب فحصها وSafeResult.

**الأولوية بعد الإصلاح:** التحقق من ترجمة برنامج Unity دون أخطاء؛ ثم اختبار variant1 وربط كِلا مسارَي Keyword الأصلية في شيدر واحد، ثم مصادر Sampler وCB0 وMaterial/RT/GUID، ثم XAPK حديث وتجربة هاتف. لا تخلط نجاح Bundle مع Pixel equivalence.

### GT / Chat-23 — نجاح Shader Spectrum منفصلين وفحص التوحيد

بعد معالجة `cb4_struct` داخل نسخة اختبار خاصة، [43286126572 SUCCESS](https://github.com/alwansan/raf/actions/runs/43286126572) اجتاز **كلا العملين**: Unity 2021 Android Vulkan والتدقيق المستقل النهائي للسجل. لكل مرشح 7 Passes مستوردة؛ Variant0 Bundle **12080B** وVariant1 **12409B**؛ مجموع أخطاء GLSL linker وInternal Variant وShader import/compile **صفر**. هذه **نجاحات فعليّة لتجميع البرامج الخاصة المعزولة فقط**، لا نسخة Raft الأصلية.

[43286701677 SUCCESS](https://github.com/alwansan/raf/actions/runs/43286701677) أثبت من نفس ZIP2 الأصلية توافق Keyword **index4** والـ14 زوجاً/28 stages في 7 Passes، وركّب ShaderLab خاصاً واحداً يحتوي 7 برنامج Pass و2 فرع مصدر أصلي لكل واحد (مع عزل Uniform Blocks القابل للعكس). **لا يثبت Scope flags ولا Runtime اختيار Material**. [43288288144](https://github.com/alwansan/raf/actions/runs/43288288144) يختبر المشروع الموحد في Unity 2021 Android Vulkan مع تسجيل 2 ShaderVariantCollection candidates، وبعدها فحص Console نهائي مستقل. يلزم نجاح الثلاث مهام قبل اعتباره "Provisional Unity Compilation"، ويبقى Material/GUID/RT/CB0/Adreno غير مثبت.

### GT / Chat-23 — منع False Green من ShaderUtil في Spectrum Variant1

حالة المصدر ما زالت **7 Passes أصلية، 14 VS/FS pairs، 28/28 مراحل Vulkan، 7 حالات رسم، 6 Properties**. [Unity2021 CI 43279249696](https://github.com/alwansan/raf/actions/runs/43279249696) أثبت استيراد وتجميع **Variant0 الخاص** (7Pass، 0 خطأ Shader، Bundle 12079 B). **لا GUID/Material/Adreno**.

[43282759870](https://github.com/alwansan/raf/actions/runs/43282759870) أعاد `SUCCESS` لمرشح Variant1، ومع ذلك سجل Unity أظهر **12 GLSL link errors** و**12 internal variant creation failures** حول `cb4_struct` المتعارض بين VS وFragment، بينما `ShaderUtil.GetShaderMessages` أبلغ صفر خطأ. **هذا فشل مثبت ولا يجوز إدراجه كنجاح.** مُخرَج Bundle 12418B لا يُثبت سلامة البرامج.

أضفت `scripts/gt_spectrum_private_stage_buffer_isolation.py` بإصلاح **اختياري قابل للعكس** لأسماء `cbN_struct`/`cbN` داخل ShaderLab الخاص فقط، دون تعديل `register(bN)` أو أصول Raft؛ وفحصاً جديداً `scripts/gt_spectrum_ci_console_gate.py` يرفض أي أخطاء Link أو Import أو إنشاء internal variant من سجل GitHub Actions النهائي. **[43285251243](https://github.com/alwansan/raf/actions/runs/43285251243)** هو التشغيل الجديد؛ **يجب اجتياز مهمتي `original-private-spectrum-pairs` و`strict-final-unity-console` معاً**. النجاح الظاهري للمهمة الأولى وحدها لم يعد كافياً، ولا يعني أصالة Material أو GPU Pixels.

الخطوة القادمة: حل فشل `cb4_struct` إن بقي، ثم اختبار مصدر Keyword index4 في شيدر واحد، وربط مادة اللعبة/RT/CB0/GUID واختبار الهاتف. [جلسة Chat-23](sessions/20261112-GT-spectrum-variant1-console-gate-chat-23.md).

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
