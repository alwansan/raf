> **تحديث المالك، 5 نوفمبر 2026.** الدردشة العامة تبقى في مكانها (Stay in Chat). الدردشة والمهمة المجدولة تتشاركان هوية العامل وتكتبان في ملفات جلسات مستقلة. تتقدم كل دورة في نطاق مختلف عند وجود تداخل. [بروتوكول الدردشة والجدولة](CHAT_AND_SCHEDULE_AR.md) هو المرجع الحالي عند تعارض تعليمات الذاكرة أو حالة الجلسة أدناه. أذن المالك باستخدام REA والأدوات المفيدة وتجارب GitHub Actions وفق سياسة الفريق.

> توجيه5نوفمبر2026: هذه السياسة لفريقT1–T5 الحالي. مصدرZIP2 وبصماته والسجل التاريخي محفوظة. راجع المراجعة الجديدة قبل تنفيذ أمر.

# المصادر وActions والاعتماد
## ZIP2
الأصل المثبت alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385، ملف RAFT_FILE_MANIFEST.tsv وREADME_ZIP2.txt وrestore_raft.sh. اقرأ docs/ZIP2_SOURCE_PROVIDER.md.366ملفاً و7789295609بايت و22ملفاً مقسماً؛ أعد التجميع مرتباً في staging منفصل، ثم تحقق size/SHA قبل الاستعمال. لا تمرر مجلد part-XXXXX كملف أصلي. احتفظ بـRaft الحالي ومراجع GUID والبصمات، وتجنب LFS جديداً.
## raf-archive الخاص
https://github.com/alwansan/raf-archive/releases/tag/Raft-zip2-reconstructed
تحقق metadata حياً: private=true، Release id433949448،370assets، immutable=false عند المراجعة. اسم tag ليس ضمان عدم التغير؛ سجل asset id/digest/bytes ووقت التحقق وmanifest source. أسماء المسارات في وصف الإصدار تستخدم __ بدل /. لا تطبق mapping تخمينياً إذا اختلفت الأسماء/URL encoding.
**حالة التحقق الآن SOURCE_ARCHIVE_VALIDATION_REQUIRED**: مقارنة أسماء366ملفاً بالmanifest المثبت وجدت365اسماً مطابقاً حرفياً، وكل365حجمها أكبر من الأصل، و0تطابق size/digest، واسم unity default resources غير مطابق حرفياً. مثال DLL:3211991 مقابل3211776 (+215)، sharedassets0.assets:115978319 مقابل115978112 (+207). Content-Type يذكر multipart/form-data. هذه قرائن metadata على غلاف نقل/رفع غير مطابق، لا إثبات تشخيص محتوى أو تلف الأصل. لم تُنزّل جميع الأصول للتحقق البايتي ولم يُتحقق من payload خاص من خلال binary API في هذه المراجعة.
لا تغيّر الأصلي ولاتقبل حجمًا جديداً ولا تحدث pin لإسكات الفرق. افحص ملفاً صغيراً في بيئة مصرح بها: GitHub asset SHA يثبت transport فقط؛ يجب أن يساوي payload الأصلي manifest. إذا ثبت multipart، فصل غلافه في staging بparser صحيح وحدود صريحة ثم تحقق SHA/size الأصلي؛ لا قص عشوائي للبايتات. سجل fixture غير خاص واختبار رفض/قبول. عند تعذر التحقق استخدم ZIP2 المثبت واستمر. لا تطلب من المالك رفع اللعبة مرة أخرى.
## TOKEN
المالك أتاح credential في GitHub Environment عبر رابط settings/environments/26287164011/edit وذكر TOKEN. لم تُقرأ قيمة ولا إعداداته في هذه المراجعة. قد يكون TOKEN اسم environment أوsecret؛ لا تخترع اسماً أوتدعيصلاحيته.
Environment secrets متاحة فقط للjobs التي تشير لاسم البيئة الصحيح وبعد قواعد الحماية، وليست متاحة تلقائياً لكل جلسة أو مستودع آخر. استعمل secret reference في env للخطوة المحتاجة، لا تطبع القيمة ولا تضعها في checkout URL/args أو source/logs/artifacts أو memory. استخدم GITHUB_TOKEN حيث يكفي؛ يظل الوصول إلى raf-archive حسب الصلاحيات الفعلية. secrets لا تنتقل إلى workflow في مستودع آخر تلقائياً. لا تسأل المالك عن القيمة في المحادثة، ولا تحاول كشفها عبر job. لا تفترض أن token يمنح تجاوز API limits أو build quotas.
## حدود GitHub Actions — تحقق4نوفمبر2026
وفق الوثائق الرسمية: standard GitHub-hosted runners في public repositories مجانية، مع حدود التشغيل/التزامن وسياسات GitHub؛ larger runners ليست مجانية لمجرد public. Private repositories لها compute included شهري حسب خطة المالك، والتجاوز قد يُحاسَب أو يتوقف عند الميزانية. storage/cache لها حساب وحدود منفصلة. token لا يغيّر هذه القواعد. خطة المالك والاستهلاك الفعلي والمتبقي غير مقروءة هنا؛ لا تكتب unlimited ولا تدفع رسومًا مفترضة.
مراجع: https://docs.github.com/en/actions/concepts/billing-and-usage ، https://docs.github.com/en/billing/concepts/product-billing/github-actions ، https://docs.github.com/en/billing/reference/product-usage-included .
افحص النتيجة الفعلية للjob ورسالة billing/authorization؛403/404ليسا إثبات نفاد حصة. عند رفض لحصة/ميزانية لا تكرر بلا تغيير ولا تغيّر خطة الحساب؛ سجّل السبب وانتقل لتجربة محلية أو runner مصرح آخر.
## قواعد تجارب الفريق
اسم workflow raft-tn-<experiment>.yml، name ظاهر Tn + issue + سؤال. session/experiment id في reports/artifact/paths. concurrency لا تتصادم مع غيره وcancel-in-progress:false؛إذا كانت GPU/Unity/قرص مشتركة استعمل mutex المورد المشترك بجانب هوية التجربة. timeout وميزانية واضحة. لا full auto-on-every-push؛ paths محددة أو dispatch صريح، لا cron متكرر لكل عميل. ثبت versions/SHA، تحقق disk أولاً، cache حسبhash لا اسم branch، ونظف temporary/credentials قبل artifact.
اختبارات المصدر الخاص تبقىprivate؛ تقارير raf العام لا تتضمن raw/game/decompiled/shader/bytecode، أو traces تحويها ضمن stack/compiler snippets. لا تغيّر بيانات Release الأصلي أو privacy أوbranchمحمي. هذا النظام يسمح تجارب لازمة لا ينشئ build جديداً بمجرد تجهيز الملفات.

## تقدم موروث لا تعِد تنفيذه بلا سبب
أضاف B03 scripts/b03_verify_archive_payload.py لاستخلاص raw أوmultipart أحادي فيstaging والتحقق منbytes/SHA الأصلي مع16اختباراً اصطناعياً. لم يثبت تقريره تنزيلpayload خاص حي. اقرأ docs/B03_ARCHIVE_PAYLOAD_VERIFICATION_2026-11-04.md قبل تطوير بديل. عند مراجعةmetadata5نوفمبر بقيRelease433949448/370asset وحجمAssembly-CSharp.dll=3211991؛ لا تطابق الحجم الأصلي3211776. استخدمZIP2 إن لم تتوفر صلاحية binary intake؛ لا تعطل مساراتP0 ولا تطلب رفعاللعبة ثانية.

## REA في تجارب الفريق
المصدر الرسمي https://github.com/morluto/rea. راجع الوثائق ومتطلبات البيئة للأداة والإضافة المختارة. ثبت إصدار rea-agents أو commit محدداً. ابدأ بتحليل صغير في Actions إذا كانت الإضافة تعمل بلا واجهة تفاعلية في runner المعني. استعمل أداة أخرى إن كان محرك REA المطلوب يحتاج بيئة غير متاحة. سجّل الأوامر والنسخة ونطاق الإثبات في سجل التجربة.
