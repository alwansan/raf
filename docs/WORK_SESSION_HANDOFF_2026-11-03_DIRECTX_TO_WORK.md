# Raft Android Native — تسليم Work الجديد — 3 نوفمبر 2026

**اقرأ هذا الملف كاملاً أولاً في جلسة Work الجديدة.** هذا تسليم متابعة تطوير فعلي، وليس مجرد خطة. بعده اقرأ الروابط بالترتيب في آخر الملف. اعتمد أحدث HEAD وActions لأن بعض المستندات الأقدم تسجل عمليات كانت جارية ثم اكتملت. المالك قدم فعلاً صوراً وتفاصيل تجربة ولوغات جديدة يوم 2 نوفمبر؛ تعليمات جلسة التحضير القديمة بالانتظار حتى يشرح المشاكل أصبحت تاريخية.

## 1. حدود العمل الملزمة

- المستودع: https://github.com/alwansan/raf
- **الفرع الوحيد المسموح تعديله**: `feature/android-native-port`. ممنوع تعديل/دمج/حذف `main` و`zip` و`Unity-Editor`. مستودع https://github.com/alwansan/CL للقراءة فقط، وفروع تسجيل اللوغ مستقلة.
- **أحدث تعليمات المالك: «لا تشغل بناء حتى اخبرك لذالك اكمل الاصلاحات».** لا تشغيل أو طلب أو dispatch لبناء Unity Editor أو Android APK/OBB/XAPK أو نشر Release أو تجربة Unity ثقيلة، حتى يرفع المالك الحظر صراحة. لا تعدّل `.github/raft-native-build-request.json` ولا `.github/raft-native-experiment-request.json`.
- **«لاتعدل المهمة المجدولة».** لا تغيير إعداداتها ولا تشغيلها/تعطيلها ولا إنشاء نسخة. تحقّق من تغييرات الوكيل المجدول على نفس الفرع قبل كل كتابة لتجنب التضارب. اختبارات Python/C# الخفيفة والتجارب المستقلة CPU-only / no Unity / no LFS مسموحة.
- لا يوجد PC لدى المالك. Unity 2021.3.45f2، Android ARM64 IL2CPP، GitHub Actions، هاتف POCO F5 Pro. اعتماديات Unity/FMОD 2.02.15 والمفاتيح والتوقيع سبق إعدادها والتحقق منها؛ لا تطلب إعادة الإعداد أو الملفات المتوفرة.
- حافظ على المشاهد والمحتوى الكامل وملفات `.meta` وGUIDs وأصول اللعبة وصيغة الحفظ `.rgd`، ولا تزوّر نتائج العالم أو الشيدرات أو الصوت. لا تنشر المشروع المعاد بناؤه أو مصادر خاصة أو ملفات مفككة أو أسرار، ولا تخلط نجاح CI مع تجربة الهاتف. المستخدم يفضل اكتمال المحتوى على تقليص حجم APK.

## 2. آخر حالة مؤكدة في GitHub

- آخر HEAD **قبل التزام ملف التسليم هذا**: `7cb5a8455d2550d6a472abf6ed309dc88e05e210`، تحديث التوثيق بعد نجاح تحويل DXBC الأصلي. إعادة القراءة واجبة عند بداية Work؛ الالتزام الجديد سيرفع HEAD.
- **آخر بناء Unity أصلي منشور**: https://github.com/alwansan/raf/actions/runs/41448086401 — `COMPLETED SUCCESS` بتاريخ 2026-11-02، مصدره الثابت `9462f8edd8cdb5becbccb96521f2876ef9924410`، وليس HEAD الحالي.
- إصدار اللعبة: https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1 . APK versionCode80 باسم `Raft-Android-Test.apk` حجمه 672642221 بايت، SHA256 `da62f996e6ee089a856ac6b812b5497c165dc3c827999e1fdc1cfdbacf1b4d56`. OBB بحجمه الكامل 2301297690 بايت، SHA256 `6a22a2be3818a9d84753a1e0031fe21acc405eccc983ec7034125e29697dc15c`، منشور في 3 أجزاء. XAPK بحجمه الكامل 2973941163 بايت في 3 أجزاء. توجد 11 ملفات إصدار تشمل تعليمات التثبيت/التجميع والبصمات. ملف APK وحده لا يكفي بدون OBB. هذا **نجاح بناء وتسليم فقط، لا دليل تشغيل العالم/الرسوم/الصوت/اللمس على الهاتف**؛ والإصلاحات الأحدث غير موجودة في APK80.
- أحدث تجارب مصدر مؤكدة: DXBC/HLSL https://github.com/alwansan/raf/actions/runs/41527047341 SUCCESS؛ مصدر العالم https://github.com/alwansan/raf/actions/runs/41526652528 SUCCESS؛ ماسح ComputeShader https://github.com/alwansan/raf/actions/runs/41525570605 SUCCESS؛ تجربة HLSL اصطناعية https://github.com/alwansan/raf/actions/runs/41525025301 SUCCESS. الأخطاء القديمة في محاولات DXBC كانت تبعيات بناء أدوات (submodule وspirv-cross)، وتم إصلاحها قبل نجاح التشغيل الأخير. لا Unity ولا APK جديد في هذه التجارب.
- قبل التعديل: راجع HEAD ومجموعات workflow وقائمة pending/running وأحدث per-file SHA، ثم ارفع commit إلى الفرع المحدد فقط. احترم queue:max وcancel-in-progress:false. لا تعدّ الاستكمال الخلفي مضموناً من جلسة عادية.

## 3. ملاحظات الجهاز الأصلية التي سلّمها المالك

- فتح Settings يسبب تمدد/تغير حجم الشاشة والأبعاد، بينما بداية اللعبة تظهر طبيعية؛ الاتجاه يجب أن يكون أفقياً من أول تشغيل وحتى العودة من الخلفية.
- معظم المواد والألوان بيضاء/خاطئة، مربعات مؤثرات موحّدة اللون، ماء ورغوة وشيدرات مفقودة. `UltimateWater.Internal.Dx11FFT.ComputeFFT` يرمي `Invalid kernelIndex` للفهارس 2 و6 في مورد مصدّر يحوي صفر kernels. أخطاء تمريرات `Water Spectrum` و`Foam/Global` و`Blur` و`Depth Copy` و`VolumetricLight`.
- إنشاء العالم يقف عند `INITIALIZING ASSETS` ثم `HAVING ISSUES CONNECTING / TRYING TO CONNECT TO HOST`. لا تزيّف اكتمال الاتصال؛ حافظ على إعدادات العالم وRPC والفيزياء الأصلية. `PersonController.GroundControll` يرمي NullReference، ويرتبط زمنياً باعتراضات FMOD المبكرة.
- أخطاء الصوت: `EventNotFoundException` و`VCANotFoundException vca:/master`. موجودة في نسخة قديمة؛ إصلاحات محمّل OBB واستثناءات FMOD أحدث ولم تختبر على الهاتف.
- اللمس/التحكم لم يكن يستجيب، وأضيف overlay Xbox وإدارة pointer وUGUI، لكن لا تُعتبر استجابة gameplay مثبتة.
- لواحق سابقة تشير إلى GPU-memory OOM على الهاتف: 5363928kB مقابل threshold 1572864kB. افرق بين OOM الهاتف وexit137 في CI. لا تقدّر FPS أو PSS دون قياس.
- أرشيفات اللوغ المستلمة: `LogRaft-1793639905225.zip` (~5.79M سطر)، `LogRaft-1793640117875.zip` (~1.35M)، `LogRaft-1793642162566.zip` (~1.39M)، `LogRaft-1793642351692.zip` (~2.03M). سجلات JSONL في https://github.com/alwansan/CL/tree/main/raft%20log ، وصور `img`، ومجلدا `lf` و`logfox`. سجل الجهاز المستخدم للإصلاحات: `raft log/انتاج مسار /5/com.alwansan.raft.androidtest/files/raft-logs/raft-20261102T175617666-7f4e1846-0000.jsonl`. لا تنسب سجل APK قديم إلى إصلاح جديد.

## 4. مصدر اللعبة والمجالات المُصلحة/غير المؤكدة على الجهاز

- اللعبة الأصلية Raft v1.1.01 Windows Unity Mono وليست مشروع Unity Editor جاهزاً. استُعمل AssetRipper وUnityPy وILSpyCmd 11.2.0.10050 مع `-lv CSharp9_0` لإعادة المصدر. استُعيد نحو 40 مشهداً و64642 مرجع MonoScript GUID وروابط الأصل، مع إدارة stubs وhelper classes. النجاح في تجميع C# ضمن .NET10/8 لا يثبت Unity IL2CPP أو أداء هاتف.
- ملفات المصادر الأصلية على Git LFS تقارب 6.85GB/17 كائناً؛ تغطية 4050 Texture2D و3948 external extents موثقة بعد استعادة موارد المصدر. لكن هذه الاستعادة لا تعيد تلقائياً برامج شيدر DirectX الأصلية: تصدير AssetRipper احتوى نحو 140 shader، غالبيتها 0/1 pass، وتسعة ComputeShader مصدّرة بلا HLSL/Kernels.
- استُعيدت بشكل انتقائي برامج Unity built-in المطابقة 2021.3.45f2، وTMP 3.0.6، وPostFX v1، ومصدر volumetric أصلي/موثق مع pass مشتق لتوافق half-res. تُحفظ GUIDs و.meta والأصول الاحتياطية. Custom UltimateWater Spectrum/Foam/Depth/Compute ما زالت غير مكتملة. لا تستخدم fallback أبيض/أحادي pass أو kernel وهمياً.
- `scripts/probe_original_water_compute.py` يثبت من المصدر الأصلي أن `Dx11FFT` يستخدم **Dispatch مرتين، SetTexture ست مرات، 11 إشارة KernelIndex، و0 FindKernel**؛ `WavesRendererFFT` فيه 5 Blits و10 SetTexture. [CI 41521165451](https://github.com/alwansan/raf/actions/runs/41521165451) SUCCESS. لذلك فهارس النوى المحفوظة وترتيبها أهم من أسماء يمكن تخمينها.
- `scripts/verify_water_render_contract.py --strict` الآن **يفشل عن قصد** قبل Unity في أي بناء مُصرح به لاحقاً، طالما `authentic_water_kernel_identity_verified=false`. يتحقق من pass counts وCompute source وهوية المصدر؛ لا ترفع هذا العلم بلا إثبات. `scripts/audit_original_compute_metadata.py` يقرأ كائنات compute التسعة بعد استعادة LFS في البناء المسموح مستقبلاً، مع تقرير metadata فقط.
- `SoundManager.OnSceneEvent` في المصدر الأصلي أصبح محمياً على Android من `FMODUnity.EventNotFoundException` محصوراً في مشهد الصوت، دون تزوير علم تحميل العالم. `Raft_Network.WorldHasBeenLoaded` الأصلي يبث **scene event مرة واحدة قبل WorldHasBeenRecieved=true**؛ [41526652528](https://github.com/alwansan/raf/actions/runs/41526652528) original source probe/managed compile SUCCESS. استثناء FMOD غير معالَج قد يقطع readiness؛ لا يُثبت أنه السبب الوحيد.
- `PersonController.Start` الأصلي SHA256 `7889e538712b1dc992b6364248ed9c51a8b1dacc8ce2b5c19656e4d80105ce2e` فيه تعيينا `RuntimeManager.CreateInstance` قبل `settings` و`actionMove`. أضيف catch مقيّد للحادث الصوتي المفقود فقط لكي تكمل التهيئة. `GroundControll` يقرأ settings مرتين وactionMove مرة، لذلك احتمال أن خطأ FMOD يتركهما null معقول، لكنه لم يُثبت بعد بتتبع null الفعلي على الجهاز. [CI 41517241477](https://github.com/alwansan/raf/actions/runs/41517241477) SUCCESS.
- `AndroidFmodBankLocator.cs` و`AndroidFmodBootstrap.cs` يستكشفان OBB أصلياً من `getObbDir()` لأن Application.streamingAssetsPath قد يشير إلى APK حتى بوجود OBB؛ أزيلت عودة صامتة كانت تتخطى تحميل البنوك، وصارت هناك مراحل قراءة البنوك الخمسة وفحص master VCA وتسجيل نتائج FMOD. [41518727231](https://github.com/alwansan/raf/actions/runs/41518727231) و[41518726849](https://github.com/alwansan/raf/actions/runs/41518726849) SUCCESS اختبارات مصدر/ZIP، لا دليل سماع. `AudioSettingsBox.SettingStart` الأصلي SHA `97e9b951895671e47b98a8840eda474d60016e1c921477c57d8fa5316fb9bafc` فيه 6 `GetVCA` محمية بمسكات محددة للـAndroid؛ [41520433458](https://github.com/alwansan/raf/actions/runs/41520433458) SUCCESS. لا تخلق VCA وهمياً.
- `GraphicsSettingsBox.ApplyCurrentResolutionAndFullscreenMode` يعالج إعدادات عرض Windows على Android بنطاق ضيق للحفاظ على مساحة الشاشة الأفقية. `AndroidRightTouchPointer`, `RightTouchGesture`, `AndroidTouchUiPanel`, `AndroidTouchGamepadOverlay` تعمل على دمج Mouse1 والـUGUI والكونترولر Xbox الافتراضي (InputSystem 1.7) والتحكم بالشفافية والموضع والحجم وBind +/- والتقاط الأصابع والاستئناف. [41517380538](https://github.com/alwansan/raf/actions/runs/41517380538) و[41517381045](https://github.com/alwansan/raf/actions/runs/41517381045) SUCCESS في CI، **ليس إثبات touch gameplay على الجهاز**.
- الحفاظ على الحفظ الأصلي `.rgd` وتخزين Android مطلوب. بعض اختبارات offline identity وRPC نجحت، لكن إنشاء عالم وتشغيله وحفظه واسترجاعه على الهاتف لم ينجز كتجربة فعلية. اللوق الدائم في `Application.persistentDataPath/raft-logs`، بضوابط حجم/خصوصية وإشعارات وعلامات عمليات.

## 5. أحدث إنجاز محوري: فك DirectX الحقيقي عبر DXBC / SPIR-V / HLSL

اقرأ التقرير الكامل [DIRECTX_SHADER_TRANSLATION_EXPERIMENTS.md](DIRECTX_SHADER_TRANSLATION_EXPERIMENTS.md).

1. بحثت أدوات DXVK (Direct3D 8–11 إلى Vulkan)، VKD3D-Proton (D3D12 إلى Vulkan)، FEX (تشغيل x86/x64 فوق ARM64 Linux مع بيئة إضافية مثل Wine)، dxbc-spirv، glslang، SPIRV-Cross. **لا يوجد أي منها يستطيع بمجرد نسخه داخل APK إصلاح برامج Unity ComputeShader المفقودة**. الأدوات استُخدمت لفهم برامج DirectX الأصلية خارج Unity.
2. أول تجربة CPU مع HLSL مختلق لمختبرنا فقط: [41525025301](https://github.com/alwansan/raf/actions/runs/41525025301) SUCCESS. glslang HLSL→SPIR-V صالح Vulkan1.0، local group 8×8×1؛ Ubuntu vkd3d-compiler 1.2 لم يصنع DXBC من HLSL في تلك التجربة. لا تخلطها مع استعادة Raft.
3. **فحص بيانات Raft الحقيقية** [41525570605](https://github.com/alwansan/raf/actions/runs/41525570605) SUCCESS: جرد 80 ملف Unity أصلي من Git العادي دون LFS، ووجد داخل `Raft/Raft_Data/sharedassets29.assets` كائن `ComputeShader` أصلي `pathID=577`، raw object SHA256 `3c4307f852785a8564f90d68256cebfed575876e70c5c5fda8fd7da77d74cfff`. بداخله DXBC حقيقي **460 بايت** SHA256 `93880946974676dee3a7fa4d56246e7f0808874e1ec0327592acfa382950d099`، أقسام ISGN/OSGN/SHEX؛ stage هو **Compute Shader Model 5.0**. ملفات `resources.assets`، `sharedassets0.assets`، `sharedassets36.assets` ظلت LFS pointers؛ هذا **واحد من أصل تسعة** ولا دليل أنه نواة FFT الفاشلة.
4. جرى بناء مترجم `doitsujin/dxbc-spirv` من commit موثق `f528e1e821527e361f34829f78d1fbd5340e6f6a` مع spirv_headers submodule. [41526447256](https://github.com/alwansan/raf/actions/runs/41526447256) SUCCESS على **البرنامج الأصلي**: `vkd3d-compiler 1.2` أنتج SPIR-V 1.0 واحتفظ بمجموعة عمل **8×8×1** ونجح spirv-val Vulkan1.1 و1.3. dxbc-spirv أحدث أنتج SPIR-V 1.6 ونجح Vulkan1.3 ولم يجتز Vulkan1.1.
5. [41527047341](https://github.com/alwansan/raf/actions/runs/41527047341) SUCCESS: سلسلة البرنامج الأصلي `DXBC → VKD3D SPIR-V 1.0 → SPIRV-Cross HLSL مشتق خاص → glslang SPIR-V → spirv-val Vulkan1.1`، مع الحفاظ على workgroup 8×8×1. **هذا إثبات صحة تركيبية/ترجمية لبرنامج واحد، وليس إثبات مطابقة حسابية أو ربط موارد أو نجاح GPU أو استعادة نوى الماء الأصلية.** لم تُنشر بايتات DXBC أو الشيدر المفكك أو SPIR-V الناتج خارج مؤقتات CI.
6. ملفات الأدوات: `scripts/probe_directx_shader_bridge.py`, `scripts/probe_original_compute_containers.py`, `scripts/run_original_dxbc_translation_probe.py`, `scripts/run_shader_translation_lab.py`, `scripts/audit_original_compute_metadata.py`. Workflows منفصلة خفيفة: `raft-shader-translation-lab.yml`, `raft-original-dxbc-source-probe.yml`, `raft-real-dxbc-translation-probe.yml`. اختبارات المصدر في `tests/test_*.py`، جميعها بدون بناء اللعبة.
7. مؤلف UltimateWater الرسمي المعروف: https://github.com/Moonlit-Games/Ultimate-Water-System . المستودع عام لكنه ليس حزمة شيدرات كاملة، ولا نعلم الإصدار المطابق داخل Raft. لا تستبدل به شيدر مشابه أو حزمة غير متوافقة بلا تحقق من المصدر والـGUID والواجهات والفهارس. التطوير الجديد يجب أن يركز على كشف النوى الحقيقية في LFS ثم اختبار ترجمتها مع إثبات تطابق الموارد والسلوك.

## 6. خطوات عملية للجلسة الجديدة — لا تكتفِ بالتخطيط

**ابدأ بالقراءة وفحص الحالة الحية ثم بعمل هندسي حقيقي، بلا تكرار الأسئلة المحسومة.**

1. افحص HEAD وGitHub Actions وشجرة الفرع واللوغات القديمة/الجديدة، وتأكد من عدم وجود تغييرات متزامنة أو بناء Unity جارٍ. استخدم موصل GitHub وليس افتراضات من ذاكرة المحادثة. لا تغير ملف طلب native أو المهمة المجدولة.
2. الأولوية **استعادة نوى FFT UltimateWater الأصلية** من بيانات `resources.assets` و`sharedassets0.assets` و`sharedassets36.assets` في Git LFS، وليس برنامج `sharedassets29.assets` فقط. لا تخلط عدم قراءة ملف مع غياب المعلومة فيه. المالك يجيز استخدام LFS عند الحاجة، لكن تجنب تنزيل/تصدير كل ~6.85GB بلا سبب؛ افحص البصمات والأحجام والمساحة، وفضّل جرد metadata مبنياً على الملفات الضرورية فقط من دون Unity. الحظر الحالي هو على البناء Unity/APK والتجارب الثقيلة وليس على التحقيق التقني الآمن. لا تنشر كود الشيدر أو البايتات الأصلية.
3. طابق كل كائن `ComputeShader` مع المصدر ومسار GUID/fileID و`Dx11FFT` و`WavesRendererFFT` وأرقام kernel المحفوظة وترتيبها وموارد SetTexture/Dispatch؛ اعرف هل الأصلي DXBC أو DXIL أو بيانات رسومية ناقصة. **لا تعيّن kernel index 0 كبديل**. طبّق التجارب الخاصة الفعالة `DXBC -> VKD3D SPIR-V -> SPIRV-Cross HLSL` فقط على مصدر موثّق، مع اختبار Shader Model, reflection, workgroups وresource bindings والآثار الحسابية.
4. استعد الشيدرات متعددة التمريرات الأصلية للماء/الرغوة/العمق ومواد اللعبة باستخدام مصدر موثق والـGUID الصحيح؛ لا ترفع علم `authentic_water_kernel_identity_verified` إلا بعد إثبات هوية ومطابقة البرنامج. قبول spirv-val وحده غير كافٍ.
5. استكمل إصلاحات الصوت/العالم بشكل مصدر-موجه: تحميل بنوك FMOD من OBB الحقيقي، `vca:/master`، `PersonController.Start`، `SoundManager.OnSceneEvent`، وترتيب `Raft_Network.WorldHasBeenLoaded`. حافظ على RPC/الهوية/العالم والفيزياء والحفظ. اختبر بكود managed حقيقي ودوال أصلية مقتطعة مع اختبارات لا-Unity.
6. احتفظ بمشاكل واجهة Settings وأبعاد الشاشة والاتجاه الإجباري الأفقي واللمس UGUI/Xbox والذاكرة وGPU كعناصر مفتوحة حتى يتحقق الهاتف مستقبلاً. لا تعيد طلب اللوق الذي رفعه المالك بالفعل، ولا تساوِ نجاح CI بالصورة النهائية.
7. أجرِ تغييرات صغيرة موثقة فقط على الفرع المسموح؛ استخدم source/CI tests وراجع الفشل الأول ثم صححه. بعد كل مجموعة أعمال حدّث ملف التسليم ووثّق SHA/run links/حالة مصدر-اختبار-جهاز. إذا لم يبق إلا انتظار workflow طويل، أعط الرابط والحالة، ولا تدّعِ تشغيل أتمتة جديدة.
8. عند الحاجة الفعلية لاعتماد مدفوع أو نسخة خاصة لا يمكن استعادتها، دوّن اسم الحزمة والإصدار والرابط الرسمي والمحاولات في `docs/USER_ACTIONS_REQUIRED.md` وواصل المهام المستقلة؛ لا تطلب FMOD/Unity/AssetRipper/ILSpy مجدداً.

## 7. دليل المسارات والأساسيات

- **تعليمات مالك المشروع الملزمة:** `AGENTS.md`، وأول سطورها «NO FULL UNITY/APK BUILD».
- **سجل الجهاز مع الإصلاحات الأخيرة:** `docs/WORK_SESSION_HANDOFF_2026-11-02_DEVICE_FEEDBACK_ACTIVE.md` (اقرأ حتى آخر فقرة).
- **تقارير DirectX/SPIR-V الحالية:** `docs/DIRECTX_SHADER_TRANSLATION_EXPERIMENTS.md`.
- **ملف التسليم السابق الذي ضم تاريخ آخر APK:** `docs/WORK_SESSION_HANDOFF_2026-11-02_WORK_PREPARATION_AND_DEVICE_FEEDBACK.md`. تعليماته بالانتظار حتى يشرح المالك مشاكل تجربته متجاوزة لأنه شرحها بالفعل بعد ذلك؛ لا تعاملها باعتبارها الطلب الحالي.
- **فصل Actions والبناء:** `docs/WORK_SESSION_HANDOFF_2026-11-02_WORKFLOW_ISOLATION.md`، `docs/NATIVE_WORKFLOW_OPERATIONS.md`، `docs/WORK_SESSION_HANDOFF_2026-11-02_COMPLETE_DELIVERY.md` و`docs/ANDROID_INSTALL_AR.md`.
- **سجلات المصدر والتاريخ:** `docs/WORK_SESSION_HANDOFF.md` (اقرأ التاريخ كاملاً بما فيه أحدث checkpoint، لا تبدأ من حالات IN_PROGRESS القديمة)، `docs/WORK_SESSION_HANDOFF_2026-11-01_FMOD_ANDROID.md`، `docs/WORK_SESSION_HANDOFF_2026-11-01_DEVICE_RENDER_INPUT_PERFORMANCE.md`، `docs/WORK_SESSION_HANDOFF_2026-11-01_FULL_GRAPHICS_RECOVERY.md`، `docs/WORK_SESSION_HANDOFF_2026-11-01_LOGRAFT_GPU_OOM.md`.
- **تقارير إضافية:** `docs/RECONSTRUCTION_STATUS.md`، `docs/VERIFIED_FINDINGS.md`، `docs/MESH_RECOVERY_FINDINGS.md`، `docs/UNITY_COMPILER_DEPENDENCIES.md`، `docs/PORTING_ROADMAP.md`، `docs/FMOD_ANDROID_INTEGRATION.md`، `docs/NETWORK_COMPATIBILITY.md`، وملفات `scripts/` و`tests/` ذات الصلة.
- **المستودع واللوغات:** https://github.com/alwansan/raf/tree/feature/android-native-port وhttps://github.com/alwansan/CL/tree/main/raft%20log . لا تغير CL.
- **الاختبارات المسموحة:** `.github/workflows/raft-reconstruction-preflight.yml`، `raft-android-offline-integration-tests.yml`، اختبارات المنصة والخوادم الصوتية، وتجارب `raft-*dxbc*-probe.yml` و`raft-shader-translation-lab.yml` الخفيفة. تدفقات `raft-unity-editor-android-import.yml` و`raft-unity-android-experiment.yml` ثقيلة وممنوعة حالياً.
- **حدود GitHub:** GitHub Actions full build لا يُشغّل على commits `docs/` العادية؛ يحتاج الطلب الصريح والمفاتيح. لا تنشر نتائج التجارب التي تحتوي على DXBC أو HLSL تجاري؛ التقارير الهيكلية والبصمات فقط.

## 8. نص افتتاح جلسة Work الجديدة — انسخه كما هو

> أريدك أن تستكمل **التطوير الفعلي** لتحويل Raft v1.1.01 من Windows PC إلى Android Native APK، من أحدث دليل مؤكد، وليس إعداد خطة أو تكرار التاريخ فقط.
>
> **المستودع:** https://github.com/alwansan/raf
>
> **فرع العمل الوحيد:** `feature/android-native-port`؛ ممنوع تعديل أو دمج أو حذف `main` و`zip` و`Unity-Editor`، ومستودع `alwansan/CL` للقراءة فقط.
>
> اقرأ أولاً **ملف تسليم Work الجديد بالكامل**:
> https://github.com/alwansan/raf/blob/feature/android-native-port/docs/WORK_SESSION_HANDOFF_2026-11-03_DIRECTX_TO_WORK.md
>
> ثم اقرأ `AGENTS.md` وتقرير الجهاز `docs/WORK_SESSION_HANDOFF_2026-11-02_DEVICE_FEEDBACK_ACTIVE.md` وتقرير `docs/DIRECTX_SHADER_TRANSLATION_EXPERIMENTS.md`، والوثائق والتاريخ الكامل والاختبارات المرتبطة **بالترتيب داخل ملف التسليم**. راجع HEAD المباشر وآخر Actions وCL قبل أي تعديل. بعدها أكمل الهندسة فعلياً، خصوصاً **استعادة نوى UltimateWater FFT والشيدرات الحقيقية من ملفات LFS الأصلية**، وفحص نجاح DXBC → SPIR-V → HLSL على الكود الحقيقي، ثم إصلاح FMOD وتهيئة العالم واللمس والاتجاه والحفظ والأداء. لا تضف موارد وهمية ولا تنسب نجاح CI إلى الهاتف.
>
> **أمر المالك الحالي مستمر:** لا تشغّل أي بناء Unity Editor أو Android APK/OBB/XAPK أو Release، ولا تغيّر ملفي طلب البناء ولا المهمة المجدولة، **حتى أخبرك صراحةً بالسماح**. اختبارات Python/C# الخفيفة وأبحاث DirectX CPU-only مسموحة. لا تطلب مني PC أو مفاتيح Unity/FMОD أو إعادة رفع ملفات موجودة. نفّذ تغييرات مصدر واختبارات وتوثيقاً حقيقياً على الفرع المحدد؛ ميّز بين نجاح CI والتحقق الفعلي على الهاتف.
>
> **Continue.**

---

**Status:** Work transfer only. No Unity/native build, APK, release, scheduler change, branch merge, or device validation was performed while preparing this handoff.


## 9. Work continuation verified on 3 November — authenticated all nine original ComputeShaders

- New source-only SHA-pinned provenance verifier: `scripts/verify_targeted_lfs_compute_sources.py`; original inventory correlator: `scripts/probe_authenticated_water_compute_inventory.py`; six new synthetic regression tests and a narrowly scoped Git LFS CI workflow `.github/workflows/raft-original-water-lfs-compute-audit.yml`.
- Authenticated original Git LFS owners `resources.assets` (111533516 bytes), `sharedassets0.assets` (115978112), `sharedassets36.assets` (110149324) — **337660952 bytes total**. SHA256 checked pre/post LFS fetch; no other LFS downloaded, no project asset/meta/GUID written.
- Source commit: [cd4ab1e854a0daa2e5845a28e45125834b11cd0b](https://github.com/alwansan/raf/commit/cd4ab1e854a0daa2e5845a28e45125834b11cd0b). [CI 41533270315](https://github.com/alwansan/raf/actions/runs/41533270315), job125578639659: **COMPLETED SUCCESS**. All Python tests, three source LFS hashes, UnityPy metadata and object reconciliation passed. No Unity, APK, OBB, XAPK, release, GPU/device test or scheduled-task modification.
- Definitive structural result: **9/9** original ComputeShader objects; **42 valid DXBC bytecode containers**; kernel metadata slots 42 total. `resources.assets` pathIDs 905..911 have respective kernel counts 12,1,2,1,2,2,1; `sharedassets0.assets` pathID2456 has20; `sharedassets29.assets` pathID577 has1. `sharedassets36.assets` authenticated but contains no ComputeShader in this inventory.
- Dx11FFT original calls fixed kernel indices including 2 and6. Numerically plausible candidate owners (at least seven original kernels) are `resources.assets/pathID905` and `sharedassets0.assets/pathID2456`. **Not yet proven** to be actual water FFT owner, or to have matching resource bindings, program stages, kernel sequence or semantics. No fake FFT source, index clamp or pass changes. The strict water shader gate stays blocking.
- Detailed durable report: [docs/ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md](ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md). Next focus: identify the correct original source reference and exact kernel order, privately inspect DXBC model/workgroups/resource bindings of the two real candidates; then test authentic translation against expected Unity/Android contracts. Preserve build hold and the scheduled automation.
