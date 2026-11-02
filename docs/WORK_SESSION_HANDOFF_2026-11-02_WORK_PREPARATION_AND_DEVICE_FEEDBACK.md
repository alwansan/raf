# تسليم جلسة Work — Raft Android Native — 2026-11-02
## 1. تعليمات المالك الجديدة: الفهم والاستعداد أولاً
هذا ملف انتقال لجلسة Work جديدة. المطلوب في بداية الجلسة الجديدة قراءة المشروع وتاريخه والتسليمات والكود والاختبارات وفهمها والاستعداد، ثم إخبار المالك بإيجاز بأنك مستعد لسماع مشاكل تجربته. **المالك لم يقدّم في هذا التسليم وصف نتائج تجربته الجديدة أو مراجعة التطبيق. لا تختلق نتائج ولا تفترض أن التجربة نجحت أو فشلت، ولا تطلب منه اختبار APK أو رفع شيء الآن.** سيشرح لاحقاً المشاكل والتفاصيل ويرفع اللوغ. مساره المعتاد هو مستودع CL أدناه؛ افحصه لمعرفة المتاح فعلياً وميّز القديم من الجديد، ولا تساوِ وجود سجل قديم بتقرير جديد عن النسخة المنشورة. بعد أن يؤكد المالك مشاكله، اربطها بنسخة APK والسجلات المناسبة ثم استكمل التطوير الفعلي وفق التفويض السابق.
طلب التحضير هذا لا يغيّر تعليمات المهمة المجدولة ولا يلغي تفويض التطوير القائم. لم تُعدّل المهمة المجدولة بهذا التسليم. لا تبدأ في جلسة التحضير دورة بناء ثقيلة أو تغييرات وظيفية جديدة قبل إتاحة المجال للمالك لشرح المشاكل؛ يمكنك القراءة والتحقق والتحضير دون تعطيل العمل القائم.

## 2. المستودع والقيود الثابتة
- Repository: https://github.com/alwansan/raf
- الفرع الوحيد المسموح تعديله: feature/android-native-port.
- ممنوع تعديل أو دمج أو حذف main أو zip أو Unity-Editor. فروع lograf وclog تخص تطبيقات التسجيل، وليست فرع اللعبة؛ لا تغيّرها ضمن هذه المهمة.
- جهاز التجربة POCO F5 Pro، ولا يوجد PC لدى المالك. Unity وكل بناء Android عبر GitHub Actions؛ لا تطلب تثبيت Unity على كمبيوتره. Termux ممكن فقط إذا احتاج فعلاً خطوات هاتف.
- Unity 2021.3.45f2، ubuntu-24.04، Android ARM64 IL2CPP. الترخيص وFMOD الرسمي ومفتاحه الخاص والتوقيع متاحون ومختبرون؛ لا تطلب إعادة إعدادها أو نشر قيمها.
- حافظ على .meta وGUIDs والمشاهد والـprefabs والأصول والأنظمة الأصلية وصيغة الحفظ .rgd. لا تنشر السورس المفكك أو المشروع المستعاد أو الأصول الخام أو الأسرار.
- المالك يفضّل اكتمال المحتوى على الحجم، ويوافق على APK كبير وOBB وXAPK وأجزاء نقل متعددة. لا تختزل اللعبة أو تقلّل الصور بلا دليل تقني. APK/OBB المجمّعان المصرح بهما يجوز نشرهما وفق بوابات المشروع؛ الحظر التاريخي العام على APK/OBB النشر تجاوزته تعليماته الأحدث.
- التفويض الهندسي السابق يسمح بالإصلاح والاختبار والرفع في الفرع المحدد دون موافقة لكل خطوة. احترم طلب التحضير الجديد في افتتاح الجلسة، ثم استأنف عندما يشرح المالك مشاكله.

## 3. ترتيب القراءة والمصدر المرجعي
ابدأ بهذا الملف كاملاً، ثم AGENTS.md، ثم اقرأ بالترتيب:
1. docs/WORK_SESSION_HANDOFF_2026-11-02_WORKFLOW_ISOLATION.md **حتى نهايته**؛ الأقسام الأولى تحتوي حالات IN_PROGRESS تاريخية، والأقسام الأخيرة تسجل النجاح المنشور والإصلاحات الأحدث.
2. docs/NATIVE_WORKFLOW_OPERATIONS.md.
3. docs/WORK_SESSION_HANDOFF_2026-11-02_COMPLETE_DELIVERY.md وdocs/ANDROID_INSTALL_AR.md.
4. docs/WORK_SESSION_HANDOFF_2026-11-02_STANDALONE_APK.md كتاريخ لحدود standalone، وليس لإلغاء تفضيل split/fidelity اللاحق.
5. docs/WORK_SESSION_HANDOFF_2026-11-01_LOGRAFT_GPU_OOM.md.
6. docs/WORK_SESSION_HANDOFF_2026-11-01_FULL_GRAPHICS_RECOVERY.md.
7. docs/WORK_SESSION_HANDOFF_2026-11-01_DEVICE_RENDER_INPUT_PERFORMANCE.md.
8. docs/WORK_SESSION_HANDOFF_2026-11-01_FMOD_ANDROID.md.
9. docs/WORK_SESSION_HANDOFF.md من بدايته إلى نهايته؛ ثم التقارير المرتبطة: MESH_RECOVERY_FINDINGS، UNITY_COMPILER_DEPENDENCIES، VERIFIED_FINDINGS، RECONSTRUCTION_STATUS، PORTING_ROADMAP، FMOD_ANDROID_INTEGRATION، NETWORK_COMPATIBILITY.
راجع الملفات الفعلية والكود والاختبارات المشار إليها، لا تكتفِ بعناوين الوثائق. أحدث دليل حي هو HEAD/Actions/Release؛ لا تكرر خطأ قديم تم إصلاحه باعتباره العائق الحالي. بعض بدايات AGENTS.md ما زالت تقول إن41419971187 جارٍ؛ هذه حالة تاريخية متجاوزة، لا وصفاً للحاضر.

## 4. حالة مؤكدة عند إعداد التسليم
HEAD قبل هذا الالتزام الوثائقي:
77ab61f5b441e2c194608e6cca30bd1e1dbca971
رسالة الالتزام: docs(raft): record successful APK OBB XAPK release and touch CI regression fix.
أعد جلب HEAD عند وصولك؛ المهمة المجدولة قد تتقدم بعده.

آخر بناء Unity كامل مؤكّد:
https://github.com/alwansan/raf/actions/runs/41448086401
- COMPLETED SUCCESS، آخر تحديث16:43:07UTC =19:43:07بتوقيت بغداد يوم2026-11-02.
- مصدره الثابت9462f8edd8cdb5becbccb96521f2876ef9924410، وليس HEAD الأحدث.
- native-request-gate125286118813، license125286258718، reconstruct125286312079، publish125404166486، delivery-result125409960846: كلهاSUCCESS.
- Unity/IL2CPP، استعادة40مشهد، المصدر/SDK، البيانات الأصلية/FMОD، توقيع APK، التغليف، الاحتفاظ، النشر والتحقق من ملفات Release: نجحت. recovery artifact خُطي لأنه لم يحدث فشل تغليف؛ هذا متوقع وليس نقصاً.
- هذا دليل بناء وتسليم، **ليس تحققاً من الرسوم أو الصوت أو إنشاء العالم أو اللمس أو الحفظ أو تركيب OBB على الهاتف**.

الإصدار الموجود فعلياً:
https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1
هو إصدار اللعبة المقصود. إصدارات lograf-* تخص أداة اللوغ حتى لو ظهرت أحدث في قائمة Releases العامة.

| الملف المنطقي | الحجم بالبايت | SHA256 المنشور |
| --- | ---: | --- |
| Raft-Android-Test.apk | 672642221 | da62f996e6ee089a856ac6b812b5497c165dc3c827999e1fdc1cfdbacf1b4d56 |
| main.80.com.alwansan.raft.androidtest.obb | 2301297690 | 6a22a2be3818a9d84753a1e0031fe21acc405eccc983ec7034125e29697dc15c |
| Raft-Android-Test.xapk | 2973941163 | 5123820620e754dcfb2f5da98c566f89698e59cae57e8121c9cc4f2ea5605d5a |

الـAPK ملف مباشر، وكل من OBB وXAPK منشور في3أجزاء نقل؛ كل جزء من الأولين1073741824بايت، ثالث OBB153814042، وثالث XAPK826457515. توجد11ملفات Release فعلية مع delivery.json وSHA256SUMS وINSTALL_AR.md وreassemble.py. الأرقام/الهاشات أعلاه من بيانات Release، ولم يُعَد تنزيل جميع الجيجابايتات في جلسة التحضير.
APK+OBB أوXAPK بديلان. الأجزاء ليست ملفات OBB مستقلة؛ أعد تركيب الملف الأصلي والتحقق من حجمه وSHA256 حسب الإرشادات. APK وحده لا يكفي مع companion_required=true. رقم نسخة هذا الإصدار80 والحزمةcom.alwansan.raft.androidtest.
لا تدّعِ أن XAPK يثبت تلقائياً دون مثبت متوافق أو أن Android15 ركب OBB. لا تُسمِّ ZIP عادياً APKS؛ APKS الحقيقي يخرج من bundletool/AAB إذا توفّر سبب ومصدر صالح.

## 5. ما حدث بالبناء، ولماذا الإصلاح موثوق
- 41400935501: standalone قديم فشل بسبب ملف Unity/Gradle بحجم2750611860 يتجاوز Java array؛ ليس دليلاً على فشل split ولا GPU الهاتف.
- 41403797736: أُلغي قبل أي job، بعد ثانية من دخول41414168826 إلى مجموعة انتظار مشتركة؛ الدليل يطابق استبدال pending آلياً. starter/actor ليس إثباتاً لهوية من ألغى يدوياً.
- 41419971187/source1eaa2465: Unity وAPK وFMOD والتوقيع نجحت، ثم فشل التغليف PermissionError: [Errno13] Permission denied: 'builds/delivery'؛ لم يُنشر APK. ليس فشل ترخيص أو CSharp أو إلغاء. سبب ملكية حاوية Unity استنتاج معقول؛ ملكية/وضع المجلد القديم لم تُقَس مباشرة، لكن منع الكتابة مؤكد.
- تشخيص مستقل41447497169 نجح واستخرج الخطأ من سجل خاص دون Unity/LFS. أول محاولة41447389494 احتاجت --allow-escape-sequences لأن gh يرفض ANSI افتراضياً حتى مع تحويل المخرجات لملف.
- إصلاح2114bfc5: التغليف في RUNNER_TEMP/raft-android-delivery، والـartifact من runner.temp. لا chmod/chown شامل ولا حذف/تصغير محتوى. احتفاظ استرجاع دقيق للـAPK+OBB المراجَعين فقط إذا فشلت خطوة التغليف، مع بقاء النشر وفحص التسليم فاشلين عند غياب التسليم الصحيح.
- CI41447887741/job125285448012:13اختبار تغليف ناجح، منها تنفيذ bash الحقيقي مع builds غير قابل للكتابة تحت مستخدم غيرroot؛ المسار القديم يعيد PermissionError والجديد ينجح ويحفظ بايتات APK/OBB. محلياًroot تخطّى هذا السيناريو فقط، لذا اعتمد نتيجة Actions غير المتخطاة.
- preflight41447887756 نجح. ثم طُلب بناء واحد41448086401، ونجح فعلياً شاملاً النشر. لا تعِد بناءه لمجرد قراءة اللوغ أو التحضير.

## 6. الفرق بين النسخة المنشورة وHEAD الحالي
النسخة المنشورة9462f8e تضم إصلاح التغليف وإصلاحات اللمس التي كانت قبل طلبها. لا تضم تلقائياً الالتزامات التالية:
- 9f7380da: ترشيح Debug.Log المعلوماتي غيرRAFT وغيرwarning/error قبل AndroidRuntimeLog.UnityMessage لتخفيف كتابة القرص/التدوير. يحتفظ بالأخطاء والتحذيرات ومراحلRAFT. دليل ترتيب مصدر، وليس قياس تحسنFPS. platform41450883944 وoriginal41450883692 SUCCESS.
- 971c5169: ResetLayout يلغي التقاط الأصابع قبل حذف مواضع PlayerPrefs وإعادة الافتراضيات، كي لا تعيد حركة متأخرة حفظ موضع قديم. platform41474913719 وoriginal41474913844 SUCCESS.
- 06c1970: منع نقرة اختيار دون سحب من SavePosition؛ كانت تحفظ anchors دون anchoredPosition الأصلي فتجعل الزر يقفز عند استعادة التخطيط. original41478533706 SUCCESS. platform41478533664 فشل في assertion قديم يطالب بحفظ غير مشروط، لا في Unity/CSharp.
- 384c8cd: تصحيح assertion لاختبار اللمس ليتوافق مع شرط dragged الجديد، دون إزالة إصلاح الإنتاج. أحدث platform41489467418 COMPLETED SUCCESS. HEAD77ab61f5 وثّق هذه النتيجة.
قبل أي ادعاء عن تجربة المالك، عيّن source/versionCode/SHA للـAPK المثبّت. لا تنسب ملاحظة على80إلى تغييرات لم تدخل APK80، ولا تفترض أن المالك ثبّت80أصلاً قبل أن يتضح ذلك.

## 7. الاستعادة واللعب: المؤكد وما لم يكتمل
هذا إعادة بناء لمشروع Windows Mono، وليس مشروع Editor أصلياً جاهزاً. استُخدم AssetRipper وUnityPy وILSpyCmd 11.2.0.10050 مع CSharp9_0؛ احفظ أسماء الأنواع والحقول وGUIDs. نجاح net8 المعزول لا يساوي Unity/IL2CPP.
- استُعيدت 40 مشهداً وروابط MonoScript/SDK، والمصدر الحقيقي بدل stubs، والمخازن الخارجية للمجسمات؛ عولجت تصادمات حالة الأحرف وasmdef وUGUI/TMP/InputSystem و21 DLL أصلية.
- تغطية 17 كائن LFS أصلي/~6.85 GB، و4050 Texture2D و3948 external extents مثبتة تاريخياً. اكتمال البايتات لا يثبت استعادة مصدر الشيدرات.
- جرد المصدر شمل نحو 165 شيدر D3D11 مجمّعاً و9 compute. تصدير AssetRipper أعطى Dummy140 برنامجا أحادي pass دون ملفات compute الأصلية. استرجاع الأرشيف لا يعيد HLSL الأصلي تلقائياً.
- استُعيدت مصادر TMP 3.0.6 الرسمية وUnity PostFX v1 مع GUIDs الأصلية حيث تنطبق. Ultimate Water والبرامج الخاصة ما زالت تحتاج استعادة أو إعادة بناء وتحققاً.
- المالك لا يملك حزمة Ultimate Water الأصلية ولا PC. ابحث في الملفات الأصلية والأرشيفات والمصادر المصرح بها قبل طلب اعتماد. عند تعذره بعد الأدوات وActions، اكتب الاسم والإصدار والرابط الرسمي والمحاولات وخطوات الهاتف الدقيقة في docs/USER_ACTIONS_REQUIRED.md، وضعه جانباً واستمر في أعمال مستقلة. لا تكرر الطلب كل ساعة.
- أصلح FFT temporary RenderTexture lifetimes باستخدام finally عند استثناء SetTexture/Dispatch؛ اختبارات CPU doubles لا تثبت زوال تسرب GPU على الهاتف.
- استبعاد Windows Party من Android solo له حدود واضحة، مع الحفاظ على المسار المحلي وRPC والهوية دون Steam. LAN يستضيفه الهاتف لاحقاً، وليس استبدالاً صامتاً لكل الشبكات.
- استعادة Conditional(UNITY_ANDROID) لاستدعاء Save الأصلي ومواضع التخزين تحافظ على .rgd. صدور الاستدعاء في harness لا يثبت roundtrip لحفظ عالم حقيقي.
- FMOD 2.02.15: تحميل Java System.loadLibrary بالترتيب fmod ثم fmodstudio، وJava FMOD.init، وJNI مع original providers. إصلاح Resources/FMODStudioSettings يحتاج 15 asset+meta أصلية وPlatforms/DefaultPlatform حقيقية. فُحصت 3 مكتبات ARM64 وJava DEX و36 ملف StreamingAssets أصلي وبنوك غير مضغوطة. سماع الصوت ونجاح RuntimeManager على الهاتف ما زالا بند تحقق.
- DXVK وVKD3D-Proton وFEX ليست إصلاحاً جاهزاً لـAPK ARM64 Unity؛ افحص الجدوى المعمارية قبل أي دمج.

## 8. اللمس والشاشة والأداء والتسجيل
- الاتجاه أفقي من الإطلاق حتى لو الهاتف عمودي، ومع الاستئناف. افحص SafeArea/notch/aspect/scaling وتخطيط جميع الصفحات والقوائم، لا زرّاً واحداً.
- New Input System 1.7.0 موجود. افحص PlayerInput/actions/controls وUI EventSystem قبل الاستبدال. حافظ على الماوس والكيبورد اللذين عملا سابقاً، والكونترولر والأجهزة الخارجية.
- توجد overlay اختيارية بأزرار وjoystick وتخصيص الموضع والحجم والشفافية والربط والحفظ/reset. راجع AndroidTouchGamepadOverlay وAndroidTouchLayoutHandle وAndroidTestDiagnostics، والبرامج verify_touch_binding_lifecycle.py وverify_touch_drag_capture.py، واختبارات test_android_touch_gamepad_policy.py.
- الإصلاحات السابقة تشمل منع تسجيل OnScreenControl مرتين عند تغيير controlPath، والبناء inactive قبل التسجيل، وSafeArea أول ظهور، والتقاط pointerId مستقل، ومنع السحب/الحفظ بأصبع أجنبي وتكرار الحفظ، وإلغاء capture عند تبديل المحرر أو disable أو reset. مرور harness أو ظهور أزرار ليس دليلاً على استجابة gameplay؛ طابق vendor 1.7 والربط الحقيقي.
- الأولوية: Singleplayer كامل، إنشاء/تحميل العالم والفيزياء والحقيبة وcrafting/building/survival، والحفظ الأصلي .rgd والصوت واللمس والأداء؛ ثم LAN. تجارب APK تدعم الاستعادة ولا تستبدلها.
- CPU/GPU/RAM/RSS/PSS/FPS/frame times/percentiles: اكتب unavailable لما لا يتاح، لا صفراً. ميّز GPU/load العام عن per-app GPU. تحقّق من GPU/API/driver الفعليين، لا اسم المعالج فقط.
- سجل تاريخي أثبت AdrenoVK 0615.95 وVulkan 1.1 request لهذه العملية؛ GLES لعملية أخرى لا يثبت API اللعبة. GPU model والعدادات يحتاجان قياساً من اللعبة.
- دليل LF تاريخي من MIUI Scout: 5363928 kB GPU memory مقابل threshold1572864 وقتل عملية اللعبة. CI exit137 واقعة مختلفة؛ OOM المضيف كان اشتباهاً حتى يثبت kernel/cgroup. لا تنسب السجل القديم إلى تجربة APK80 التي لم تُقدّم بعد.
- مسار اللعبة Application.persistentDataPath/raft-logs، والمتوقع /storage/emulated/0/Android/data/com.alwansan.raft.androidtest/files/raft-logs.
- startup محفوظ منفصلاً 4×256 KiB؛ JSONL bounded queue/rotation وتجميع الأخطاء مع أول stack/count/times، ومراحل FMOD/lifecycle/scenes/lowMemory/frames وعمليات أصلية محددة. لا تسجل passwords أو serialized game payload.
- حل world OOM وتسرب RenderTextures وshader passes وcompute kernels يحتاج أدلة مصدر وقياسات؛ لا تفترض أن إضافة دعم Snapdragon تكفي.

## 9. مكان اللوغ والتجربة التي لم تُقدّم
- https://github.com/alwansan/CL/tree/main/raft%20log
- https://github.com/alwansan/CL/tree/main/raft%20log/lf
- https://github.com/alwansan/CL/tree/main/raft%20log/logfox
- https://github.com/alwansan/CL/tree/main/raft%20log/img

CL للقراءة فقط ضمن هذه المهمة. مؤشرات المجلدات الحالية مطابقة للجرد التاريخي:
- img: 130a4a84d22db12651e16cb6d63954a17fd9dbec
- lf: 36b6390bbcf39f70230c600bb7f0fbe3c36ae0b0
- logfox: e5e21da43aa0f8a61847b58e7ae4d4e8541ac8ce

الجرد السابق 3 جلسات LF و15 صورة و4 ملفات logfox من2026-11-01. لا تعتبرها رفعاً جديداً عن تجربة APK80. قد توجد ملفات مرفوعة في ChatGPT أيضاً، لكنها لم تُقرأ في هذا التحضير ولم تُعتمد كتقرير جديد. أعط الأولوية لما يحدده المالك ومسار CL، ولا تدّعِ تحليل ملف لم تفتحه.
بعد القراءة أخبر المالك بأنك مستعد؛ لا تطلب مراجعة أو تجربة أو رفعاً فورياً. هو سيشرح المشاكل ويرفع اللوغ لاحقاً. بعدها طابق العرض والنسخة والتوقيت والسجل واختبر الفرضيات ثم أصلح السبب.

## 10. فصل workflows ومنع إلغاء أو هدر البناء
- Main: .github/workflows/raft-unity-editor-android-import.yml. Push على الفرع المحدد يراقب فقط .github/raft-native-build-request.json.
- الطلب JSON فيه request_id فريد وreason وrequested_from_sha من40حرفاً للـHEAD الأساسي. التزام الطلب يحتاج [raft-native-build] و[raft-device-test]. العلامات وحدها لم تعد تشغّل البناء. workflow_dispatch بنمط native ونشر true بديل.
- الاختبارات الخفيفة في raft-reconstruction-preflight.yml وraft-android-platform-tests.yml وraft-android-offline-integration-tests.yml والبوابات المختصة. لا تغيّر ملف طلب البناء لأعمال docs/tests.
- تجربة Unity ثقيلة خاصة لفرضية محددة: raft-unity-android-experiment.yml و.github/raft-native-experiment-request.json وعلامتا [raft-native-build] و[raft-native-experiment] دون [raft-device-test]. ليست للتحايل على فشل main أو تزاحم بناء نشط.
- cancel-in-progress:false مع queue:max ومجموعات مستقلة ومنفذ Editor مشترك لتسلسل الترخيص. لا تلغِ أو تكرر البناء. افحص كل queued/pending/in_progress حسب workflow PATH والفرع؛ لا تخلط lograf/clog باللعبة.
- نجاح main يتطلب Unity فعلياً وكل بوابات البيانات والتوقيع و40 مشهداً وحزماً كاملة، ثم Release مطابق الأسماء والأحجام وdelivery-result. غياب/تخطي build أو release فشل، وليس نجاحاً أخضر.
- LFS مسموح حسب الحاجة؛ المالك أذن بنحو10 GB، لكن لا full checkout افتراضي. سجّل السبب والحجم وSHA256 وافحص المساحة وتجنب التكرار.
- عند تعذر السجل الضخم استخدم diagnostics sidecar دون Unity/LFS؛ لا تنشر السجل أو الأصول الأصلية كاملة.
- قبل الرفع أعد فحص HEAD واستخدم expected SHA/lease؛ لا تكتب فوق عمل المهمة المجدولة. وثّق النتائج والاختبارات والروابط وحالات Missing/Restored/Compiled/CI-validated/Device-validated.
- إذا لم يبق إلا انتظار مهمة أطول من10دقائق، أعط الرابط والحالة وتوقف عن الانتظار. لا تدّعِ استمرار التنفيذ بين الدورات.

## 11. المهمة المجدولة والبيئة
المهمة المعروفة Raft — استعادة وتطوير Android، ID6ae68c9d65608191878d7e0c0e40645e، كل ساعة عند الدقيقة10 بتوقيت Asia/Baghdad. إن لزم فحصها استعلم حالتها الحية؛ لا تنشئ نسخة متداخلة ولا تفترض حالتها دون قراءة.
طُلب Thinking 6 بدل Instant 6. الوثائق تتيح اختيار النموذج ومستوى التفكير من الواجهة، لكن موصل الأتمتة السابق لم يوفّر حقول قراءته أو تغييره والمتصفح لم يكن مسجلاً. **لم يثبت تغيير النموذج**؛ تعديل prompt لا يغيّر المحرك. لا تحذف المهمة أو تدّعِ تغييره دون دليل.
Scratch قد يزول؛ المصدر الدائم هو المستودع والالتزامات والتقارير. استخدم موصل GitHub، وعند الحاجة إلى git اجعل GIT_LFS_SKIP_SMUDGE=1 لتجنب تنزيل الجيجابايتات لمجرد القراءة. استخدم الأسرار المضبوطة دون طباعتها.

## 12. افتتاح الجلسة الجديدة
اقرأ وقارن الحالة الحية والملفات أولاً، ثم أخبر المالك بإيجاز بأنك مستعد، وميّز APK المنشور عن HEAD الأحدث. لا تُعد سرد التاريخ كله ولا تدّعِ اكتمال اللعبة. انتظر تفاصيل المشاكل التي قال إنه سيشرحها بعد التحضير، ثم استكمل عملياً من الأدلة. هذا الانتظار طلب خاص بافتتاح الجلسة، وليس إلغاءً للمهمة المجدولة أو للأعمال المستقلة المصرح بها.

## 13. رسالة جاهزة لافتتاح الجلسة

أريد أن نكمل مشروع Raft Android داخل هذه الجلسة الجديدة في Work، لكن ابدأ الآن بالفهم والاستعداد فقط.

المستودع: https://github.com/alwansan/raf
الفرع الوحيد المسموح تعديله: feature/android-native-port. ممنوع تعديل أو دمج أو حذف main أو zip أو Unity-Editor.

اقرأ ملف التسليم الجديد كاملاً:
https://github.com/alwansan/raf/blob/feature/android-native-port/docs/WORK_SESSION_HANDOFF_2026-11-02_WORK_PREPARATION_AND_DEVICE_FEEDBACK.md

ثم اقرأ AGENTS.md وجميع التسليمات والتاريخ والتقارير والكود والاختبارات المرتبطة وفق ترتيب الملف، وراجع HEAD وأحدث Actions والإصدار الفعلي. ميّز مصدر APK المنشور عن تغييرات HEAD اللاحقة، ولا تعتبر نجاح البناء إثباتاً لنجاح اللعب أو الصوت أو اللمس.

تفاصيل تجربتي الجديدة ومشاكلها لم أقدّمها لك بعد. لا تفترض نتائج، ولا تطلب مني اختباراً أو رفع ملفات الآن. افهم المشروع واستوعبه أولاً وأخبرني عندما تصبح مستعداً؛ بعدها سأشرح لك المشاكل وأرفع اللوغ. مسار اللوغ المعتاد:
https://github.com/alwansan/CL/tree/main/raft%20log
افحص الموجود وميّز السجلات القديمة من الجديدة، ولا تنسب القديمة إلى النسخة الحالية بلا دليل.

لا تبدأ تعديلات وظيفية أو بناء Unity جديداً لمجرد التحضير، ولا تلغِ عملاً جارياً أو تغيّر المهمة المجدولة. بعد أن أشرح المشاكل، نكمل التحليل والإصلاح الفعلي وفق التفويض والقيود الموثقة.

## 14. دورة التطوير المجدولة 2026-11-02 21:15 بغداد — Android touch pause/resume

- Refreshed actual branch HEAD `4c19008876afce371f17dd311375fbd01670fce4` before source changes. Verified native [41448086401](https://github.com/alwansan/raf/actions/runs/41448086401) COMPLETED SUCCESS from older `9462f8e`; release [android-early-test-41448086401-1](https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1) still has 11 actual delivery assets including APK and OBB/XAPK transport parts. No new native requested. CL/raft log `lf`, `img`, `logfox` directory hashes remain `36b6390b`, `130a4a84`, `e5e21da4`: no new APK80 phone session verified.
- Source inspection: optional `AndroidTouchGamepadOverlay` had no `OnApplicationPause` lifecycle handling. Android may pause before pointer-up reaches an active `OnScreenStick`/`OnScreenButton`; Unity Input System documentation confirms that disabling all on-screen controls unregisters their simulated device. This is a **source-level risk**, NOT a measured or reported phone regression. Official reference: https://docs.unity.cn/Packages/com.unity.inputsystem%401.2/manual/OnScreen.html ; Android lifecycle: https://docs.unity3d.com/es/2018.4/ScriptReference/MonoBehaviour.OnApplicationPause.html .
- Commit [e00794eb](https://github.com/alwansan/raf/commit/e00794eb57677b2d15e620e6c8fd44e3775afba8) changes only `android-port/Runtime/Platform/AndroidTouchGamepadOverlay.cs` and `tests/test_android_touch_gamepad_policy.py`. On pause, deactivate the optional control canvas (releasing the virtual Gamepad and edit-pointer captures) without losing the user's visibility choice; on resume, reactivate only after the original InputSystemUIInputModule is active, retry safely in Update if the module is temporarily unavailable. Explicit hide/host disable clears the suspended flag. No new EventSystem, original game actions, scenes, GUIDs, FMOD, assets, or .rgd changed.
- [Android platform CI 41498709791](https://github.com/alwansan/raf/actions/runs/41498709791) COMPLETED SUCCESS, including the new source-policy regression and existing executable binding/drag harnesses. [Original offline integration 41498709603](https://github.com/alwansan/raf/actions/runs/41498709603) subsequently COMPLETED SUCCESS (18:16:06 UTC), including adapted original gameplay compilation and offline integration. Both cheap workflows are green. This is **CI/source validation**, not Unity compile of the new source, Android Activity pause/resume, virtual Gamepad pairing, or gameplay validation.
- Next: inspect actual APK80 device feedback only when supplied, matching source/versionCode; the new pause fix is not present in APK80. Continue independent original gameplay/save/render restoration. Request ONE new full native delivery only when a meaningful set of changes and all cheap gates justify it; never duplicate a running build. No owner action required now.
