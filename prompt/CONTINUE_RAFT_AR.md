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
