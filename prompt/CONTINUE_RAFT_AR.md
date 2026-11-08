<!-- T5_SHARED_SAF_CI42512390472 -->
> **آخر نقطة استعادة T5 (8 نوفمبر 2026، 18:56 UTC):** مختبر Android الواحد T1–T5 الأول [CI42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) نجح، Artifact ZIP ID `13628828717` يحتوي APK بحجم 78806 بايت وSHA256 `cee2df1b3bb2a1a3c8e9ab757f520040d36c5bf16d711587f7e2bc537f917472`، توقيع Debug غير مستقر ولم يتم فحص الهاتف. بعده عالج T5 فاحص SAF في المصدر [6f2cf77](https://github.com/alwansan/raf/commit/6f2cf77ece6609ee3155750a729aef259a743cef) لاستعمال StreamSha256 محدد بـ16GiB وحماية قراءات صفرية/تشغيل مكرر وفحص الصور والـpack؛ [CI42512390472](https://github.com/alwansan/raf/actions/runs/42512390472) **SUCCESS** (4 Python + 16 JDK + Android Java compile). **الإصلاح أحدث من APK السابق وغير موجود بداخله، ولم يُنتج APK ثانياً.** اقرأ [جلسة T5](coordination/clients/T5/sessions/20261108T1852Z-T5-chat-unified-saf-stream-k6p2.md) و[TEST_CENTER](../apk-for-testing/TEST_CENTER.md) و[SHARED_BUILD_READINESS](../apk-for-testing/SHARED_BUILD_READINESS.md)؛ mini r2 T5 NO_BUILD مع انتظار نتيجة هاتف، ولا تمس تصويت XAPK 5/5 أو NOT_READY 0/3.

<!-- T3_PRIVATE_4WAY_SHADER48_ROUTE_42308586115 -->
> **نقطة استكمال T3 — 6 نوفمبر 2026:** [CI42308586115](https://github.com/alwansan/raf/actions/runs/42308586115) **SUCCESS** على SHA `d38559b4`: 4 أزواج VS/FS أصلية Shader48 مرتبطة بجدول أسماء مفاتيح المصدر، ملف ShaderLab خاص مؤقت واحد بأربع حالات، **8/8** تجميع HLSL Vulkan1.1 glslang + spirv-val و9/9 فحوص اصطناعية. المصادر الخاصة تُحذف من runner ولا تنشر. **ليس شيدرًا مدمجًا أو مجرَّبًا في Unity/Android، ولا يثبت Material keyword binding أو شفاء الألوان/النار/الدخان/الماء.** RENDER-002 مفتوحة/NOT_READY، تصويت T3 «لا يحتاج» بلا طلب بناء. استعد جلسة [T3 التفصيلية](coordination/clients/T3/sessions/20261106T2252Z-T3-chat-keyword-routed-61e9.md) والسجل [work](coordination/work/RENDER-002/20261106T2252Z-T3-chat-keyword-routed-61e9.json) قبل متابعة ربط الكلمات الأصلية بالخامات أو Unity Editor، واحفظ تشغيل T5 الأصلي [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) دون إلغاء.

> **نتيجة هاتف جديدة، 5 نوفمبر 2026.** أكد المالك دخول العالم وحفظه والخروج ثم إعادة الدخول باستخدام Artifacts للتشغيل 42058825739. راجع [السجلات والصور وتوزيع العمل](../docs/DEVICE_FEEDBACK_42058825739_AR.md) قبل اختيار المهمة. أولوية الماء والألوان والمؤثرات مستمرة. الماوس الفعلي، الأزرار الثلاثة يميناً، Resolution الموجود، والتحقق من APK/OBB والأداء مطلوبة الآن.

<!-- T4_REAL_5NOV_WORLD_SAVE_LOADT_CI42153533612 -->
> **T4 LOCAL-005 — إثبات فعلي لدوال حفظ/تحميل Raft الأصلية (6 نوفمبر 2026):** نجح تشغيل [CI42153533612](https://github.com/alwansan/raf/actions/runs/42153533612) على المصدر `5c1d78117640b174d571a5a2a592b8388fb662ed`: **7/7 ملفات عالم حقيقية من CL ليوم 5 نوفمبر**، توافق نوع `RGD` المشتق مع وسيط الدالة الأصلية، تدقيق IL آمن، استدعاء `SaveAndLoad.Save` الأصلي وكتابة ملف مؤقت غير فارغ ثم `SaveAndLoad.Load<T>` الأصلي لناتج الحفظ ومطابقة نوع الجذر وحذف الناتج، جميعها 7/7. **36/36 اختبار حماية**، ورفض ملف متغير البصمة قبل التسلسل. التجربة .NET8 معزولة؛ لا تثبت حفظ التقدم في Unity/Android أو الخروج الكامل وإعادة فتح العالم على إصدار جديد. **LOCAL-005 مفتوحة**؛ لا تعديل لنظام حفظ اللعبة أو تشغيل Unity جديد. [سجل T4](coordination/clients/T4/sessions/20261106T0246Z-T4-chat-original-owner-save-roundtrip-j4q8.md) و[تسليم T5](coordination/discussions/LOCAL-005/20261106T0246Z-T4-chat-original-owner-save-roundtrip-j4q8-to-T5.md).

> **تحديث المالك، 5 نوفمبر 2026.** الدردشة العامة تبقى في مكانها (Stay in Chat). الدردشة والمهمة المجدولة تتشاركان هوية العامل وتكتبان في ملفات جلسات مستقلة. تتقدم كل دورة في نطاق مختلف عند وجود تداخل. [بروتوكول الدردشة والجدولة](coordination/T_TEAM/CHAT_AND_SCHEDULE_AR.md) هو المرجع الحالي عند تعارض تعليمات الذاكرة أو حالة الجلسة أدناه. أذن المالك باستخدام REA والأدوات المفيدة وتجارب GitHub Actions وفق سياسة الفريق.

> **توجيه المالك الأحدث — 5 نوفمبر2026: فريق T1–T5 فقط.** أوقف المالك جميع عملاءB والسابقين. يرثT كل الإصلاحات والأدلة والمهام، وحجوزات السابقين غير ملزمة حتى لو بقيstate قديم يقولactive. لا تمحُ ذاكرتهم ولا تعِد تفعيلهم أو تلغِActions فعلية. ابدأ من [فريقT](coordination/T_TEAM/README.md) و[البرومبت](coordination/T_TEAM/PROMPT_AR.md). السجل القانوني للمشكلات والموارد يبقى فيB_TEAM لحفظ الروابط، ويستخدمهT دون تصفير. الأولوية للماء/FFT والشيدرات والألوان والخامات والعالم المحلي؛ الصوت وSettings محفوظان والتاتش/layout مؤجلان. حواجزSteam منB50 موجودة فيالمصدر ولم تثبتبعدعلىهاتفأحدث؛ لا تكررإصلاحاًموجوداً. لفريقT التجارب اللازمة بما فيهاUnityوالرسوميات وفق التنسيق والأصالة والموارد؛ لا ادعاءREADYمنCIولاdummyأوfakeflags. ما يتعارض أدناه تاريخي، والتوجيه الكامل فيT_TEAM.

> **توجيه المالك الأحدث — فريق B01–B50 / 2026-11-04:** العملاء السابقون متوقفون بحسب المالك؛ حافظ على إصلاحاتهم وأدلتهم، وتجاوز حجوزاتهم القديمة دون انتظارهم. المرجع الحالي [فريق B](coordination/B_TEAM/README.md). الأسماء معروفة في الجلسات ولا تُغيّر. الأولوية للماء/FFT والشيدرات والألوان والخامات ودخول العالم المحلي؛ الصوت وSettings يعملان بحسب تجربة المالك، والتاتش/الأزرار/layout مؤجلة بلا تطوير الآن. المصدر ZIP2 مثبت، والأرشيف الخاص متاح لكن يلزم تحقق payload: metadata الحالية تختلف عن manifest. لفريق B إذن التجارب اللازمة بما فيها Unity/رسوميات وفق التنسيق والميزانية والأصالة؛ حدود CPU-only التاريخية ليست قيداً على هذا الفريق. الاختبارات/النسخ التشخيصية لا تعني READY ولا تبرر dummy أوfake flags. راجع أحدث السجلات: Steam StoreStats يفشل داخل SaveGame بعد WorldHasBeenLoaded فيAPK86. لا تغيّر جداول ولا تُفعّل العملاء السابقين ولا تلغِjobs. ما يلي من تعليمات متعارضة تاريخي؛ تفاصيل التوجيه الحي في ملفات B_TEAM.

> **آخر نتيجة W1:** [41748891281](https://github.com/alwansan/raf/actions/runs/41748891281) SUCCESS: تحقق165شيدرًا للعبة و60شيدرًا قياسيًا وحُلّت روابط1544خامة أصلية ضمن16ملفًا، دون مراجع معلّقة. الشيدران المتكرران بالاسم مختلفان ببياناتهما وبرامجهما وكل منهما مستخدم؛ لا تدمجهما. [التسليم الحالي](../docs/W1_ORIGINAL_SHADER_OBJECT_LINKS_2026-11-04.md). التالي تتبع هوية الأصل إلىGUIDالتصدير في العملية نفسها لشرح1544→1536، وليس تخمينGUIDمن الاسم. تحقق41745967644 نجح نهائيًا. Native41741108965 فشل؛ لاXAPKجديد، NOT_READY0/3، ولا طلب بناء مماثل.

> **آخر نتيجة W1:** البناء41741108965 فشل قبلUnity ولم ينتجXAPK. [تسليم التشخيص والتحقق](../docs/W1_NATIVE_FAILURE_AND_ENGINE_REFERENCE_PROOF_2026-11-04.md): نجح41745779746 في مطابقة750مرجعًا داخليًا مع11معرفًا من25شيدرًا أصليًا؛ اختباراتW1المحلية52ناجحة. تأكد نجاح41745967644 نهائيًا بعد تثبيت بصمة قاعدة196شيدرًا؛ لا تكرر البناء نفسه. ما زالت هوية الشيدر المخصص المكرر وربط الأصول والماء مفتوحة، NOT_READY0/3.

> **استأنف من محاولة البناء الفعلية:** [41741108965](https://github.com/alwansan/raf/actions/runs/41741108965)، المصدر الثابت `2cb893434d7c819f085d52b34fad1e6568db4ae8`، FAILED قبل Unity؛ لم ينتج APK/OBB/XAPK. افحص النتيجة والأدلة أولاً ولا تكرر الطلب.

> **Latest explicit owner request, 2026-11-04:** Attempt one full project/XAPK build using the existing native workflow after W1 ZIP2 scene-provider and Material-reference diagnostics. This is an experimental attempt, not READY (0/3). Read [W1 attempt handoff](../docs/W1_OWNER_FULL_BUILD_ATTEMPT_2026-11-04.md), refresh its Actions run, retain both strict builtin/water gates, and repair actual failures without repeating an identical build. No schedule changes.


> **Owner update 2026-11-04:** Prefer original game data from `zip2/Raft`, pinned15964ea8f246b6e076ce26b60931ee2e1a9a2385. Read `docs/ZIP2_SOURCE_PROVIDER.md` before acquisition. Reassemble split files and verify size/SHA; avoid new LFS pulls. Keep current Raft tree and existing fingerprints until consumers are migrated. Focus on water/shaders/colors/materials and original-data restoration. This updates source acquisition, not this role's build permissions.



**Owner role replacement, 3 November 2026:** Task6ae930dd1c248191ab637a5268342007 was renamed and enabled as «Raft — عميل الإصلاح والتجارب». It now performs source/resource repairs and CPU-only experiments using coordination records; its previous readiness/build coordinator role is superseded. It does not initiate Unity/native delivery. Other tasks unchanged; do not recreate a coordinator automatically.
أريدك أن تستكمل **الإصلاح والتطوير الهندسي الفعلي** لمشروع Raft v1.1.01 من Windows إلى Android Native، من أحدث حالة مؤكدة، وليس الاكتفاء بخطة أو تقرير.

المستودع: https://github.com/alwansan/raf

الفرع الوحيد المسموح تعديله: `feature/android-native-port`. ممنوع تعديل/دمج/حذف `main` أو `zip` أو `Unity-Editor`، ومستودع `alwansan/CL` للقراءة فقط.

ابدأ بقراءة هذه الملفات من الفرع مباشرة وبالكامل:

1. https://github.com/alwansan/raf/blob/feature/android-native-port/docs/CURRENT_OWNER_REQUIREMENTS.md
2. https://github.com/alwansan/raf/blob/feature/android-native-port/AGENTS.md
3. https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/STATUS.md

ثم اقرأ أحدث ملف تسليم وروابط الأدلة والتقارير والكود والاختبارات التي يشير إليها STATUS.md. راجع HEAD وActions والإصدار المنشور واللوغات الجديدة مباشرة؛ لا تعتمد على حالات IN_PROGRESS القديمة أو تعدّ سجلات APK قديم تجربة لإصلاح لم يُنشر.

**تصحيح اللمس المعتمد: كلك أيسر، وليس كلك أيمن.** النقرة القصيرة مرة واحدة؛ بعد ضغط مستمر500ms يصبح زر الماوس الأيسر مضغوطاً حتى الإفلات، مع السحب والإلغاء الآمن. مسار الإدخال `MouseButton.Left`/`KeyCode.Mouse0`، مع الحفاظ على UGUI والكونترولر الافتراضي والأجهزة الخارجية ومنع ازدواج النقر. أي وصف قديم RIGHT/Mouse1 متجاوز.

**تنسيق البناء حسب الجاهزية:** اقرأ وحدّث `docs/APK_BUILD_READINESS.md`. مهمة **Raft — جاهزية وبناء اللعبة** الجديدة تراجع العوائق المستمرة، وعندما تُحل عوائق المصدر والموارد وتصبح الخطوة التالية تجربة المستخدم، تشغّل مسار APK+OBB+XAPK الحالي وتصلح مشاكل البناء والتغليف، مع حفظ واستعادة المخرجات الموقعة وتجنب تكرار بناء مكافئ. مهمتا الاستعادة تتابعان إصلاحات المصدر وLFS واختبارات Python/C# وتجارب DXBC/SPIR-V/HLSL. لا تبدأ بناءً لمجرد نجاح دفعة جزئية، ولا تشترط إثبات الهاتف لإنتاج النسخة التي يحتاجها اختبار الهاتف. نجاح الترجمة أو التجميع لا يثبت تشغيل الماء أو العالم أو الصوت أو اللمس فعلياً.

واصل من أعلى عائق مثبت، خصوصاً UltimateWater/FFT والشيدرات والخامات المفقودة، وFMOD والعالم المحلي والحفظ والاتجاه والأداء. لا تزوّر النوى أو نجاح تحميل العالم، وحافظ على `.meta`/GUIDs وصيغة `.rgd` والمحتوى الكامل. لا تطلب مني PC أو تراخيص وأدوات سبق توفيرها، وتجاهل الجلسة1.txt وtext.txt ولا تنتظر إعادة رفعهما.

اترك مهمتي الاستعادة ومهمة الجاهزية والبناء كما هي؛ لا تنشئ نسخاً جديدة. افحص العمل المتزامن قبل كل كتابة واستخدم expected SHA دون force. **حدّث `prompt/STATUS.md` والتسليم بعد كل تقدم مهم وقبل إنهاء الجلسة، وحدّث هذه الرسالة عند تغير التوجيهات دون أن أطلب نقل الجلسة مجدداً.**


**توجيه إلزامي جديد (2026-11-03):** واصل التطوير الحقيقي ولا تعلن ولا توثق READY_FOR_BUILD قبل إغلاق كل عائق مثبت وإتمام **ثلاث مراجعات كاملة ومستقلة** لنفس candidate SHA الثابت. في كل مرة راجع مباشرة HEAD/Actions، الموارد والبصمات وLFS، أصالة شيدرات UltimateWater/FFT والخامات، FMOD، العالم المحلي والحفظ .rgd، اللمس الأيسر Mouse0 والـXbox، Settings والاتجاه والأداء، ثم اختبارات CI والتوقيع وتسليم APK+OBB+XAPK واستعادة المخرجات الموقعة. وثّق أدلة كل مراجعة، وأعد العد إلى 0/3 إن تغيّر مصدر النسخة. لا تخلط قبول الهاتف اللاحق بعوائق ما قبل البناء. إلى حين اكتمال الشروط: NOT_READY. لا تنشئ أو تعدّل المهام الثلاث الحالية.

Continue.


للعمل المتوازي اقرأ prompt/coordination/README.md وسجل هويتك وذاكرتك وخطتك قبل التنفيذ؛ البرومبت الموحد والاستعادة موجودان في المجلد نفسه.
