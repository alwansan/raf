<!-- OWNER_T5_ARABIC_PORTRAIT_20261108 -->

<!-- T5_SHARED_R4_T1_05_20261109 -->
## ✅ أحدث إصدار المختبر الموحّد — T1-05 FFT-like local512 (9 نوفمبر 2026)
- **بُنيت نسخة واحدة بنجاح:** [GitHub Actions #42686652150](https://github.com/alwansan/raf/actions/runs/42686652150) SUCCESS، طلب [raft-mini-lab] في [commit 3185e449](https://github.com/alwansan/raf/commit/3185e449dcefd27ab77b527f9d3b85d71104f497). التطبيق عربي عمودي، package `com.alwansan.raft.lab.shared`، versionCode=14، versionName=0.2.14-shared، يحتوي **30 حالة** بما فيها T1-05 الجديدة؛ ليس Raft game XAPK.
- **Artifact ZIP** من صفحة التشغيل، ID `13705307079`، SHA256 `067c150204468dea9daf49f7a06b908a0c2833f272435dae6a12cc182a637626`، ينتهي **23 نوفمبر 2026 19:48 UTC**. يحتوي APK وpack وSHA256SUMS، **ليس رابط APK مباشرًا عامًا على Release**. وفر T5 نسخة APK مستخرجة مستقلة للمالك في دردشته.
- **الـAPK المستخرج والمتحقق منه:** 99,622 bytes، SHA256 `e145a50b8b2be0a9f3a37493fe5f0f243b65644b844706cf82192c91d4ea6c52`، موقع v2 بشهادة Debug SHA256 `a60c8608f3c79a40a074e191f1696700dd6bbe160cb9343b971091b114709927`. توقيعه مختلف عن v0.2.13 السابق: **صدّر نتائج القديم ثم أزل APK المختبر فقط وثبّت الجديد**، ولا تمس اللعبة الأصلية. حزمة JSON revision2/30 حالة SHA256 `9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6` مطابقة بايتياً للأصل داخل APK ولا تحتاج استيرادًا.
- **اختبار الهاتف المطلوب:** افتح المختبر واضغط «تشغيل T1 تلقائيًا»، تحقق من حالة T1-05، ثم صدّر `events*.jsonl` و`summary*.json` وارفع الجلسة إلى [CL/test](https://github.com/alwansan/CL/tree/main/test). لا يلزم screenshot لـT1-05 لأن نتيجته الرقمية من GPU SSBO readback. [دليل T1-05 بالعربي](workers/T1/T1_05_OWNER_GUIDE_AR.md).
- **الحدود:** CI/build SUCCESS وليست نتيجة Android15 GPU PASS؛ التجربة synthetic GLES3.1، لا تثبت إصلاح Raft FFT الأصلي/ShaderLab أو جودة صور اللعبة. ليس هناك طلب full XAPK، والتصويت 5/5 وجاهزية 0/3 مستقلان.

> **توجيه المالك الجديد — واجهة عمودية وعربية:** طلب المالك تحويل **تطبيق المختبر T1–T5 فقط** من Landscape إلى Portrait وتعريب أزرار واجهته و**عناوين وتعليمات ونتائج التوقع** لكل الـ29 حالة. لا يغيّر ذلك وضع عرض لعبة Raft الكاملة (أفقي). تغييرات المصدر: `apk-for-testing/unified/app/src/main/AndroidManifest.xml` و`UnifiedLabActivity.java` وقاموس `ArabicLabStrings.java`، مع بقاء `team-testpack.json` ومعرفاته الأصلية دون تعديل. **هذه التغييرات لا تظهر في APK السابق 0.2.9**؛ لا توصف بأنها موجودة في التطبيق على هاتف المالك إلا بعد بناء وفحص APK جديد. تعليمات الفريق في [البلاغ المشترك](../prompt/coordination/T_TEAM/OWNER_ARABIC_PORTRAIT_CL_UPLOADS_20261108.md).

> **مصدر نتائج الهاتف الأساسي:** المالك يرفع ملفات الاختبارات في [CL/test](https://github.com/alwansan/CL/tree/main/test). اقرأ أحدث `shared-*` وملفات العملاء (وبالأخص `shared-20261108-223228-464718661`) قبل أي تشخيص. ذلك مجلد أدلة **مختلف عن** `CL/raft log`. ثبت T4 ملف mouse كبير في أحدث رفع، وبقي `T5-02..06` بحاجة لإدخال فعلي؛ `T5-01 PASS`. لا تنشر ملفات اللعبة الخاصة إلى CL/test.

# Raft — ONE TEAM LAB APK / T1–T5

<!-- T5_SURFACE_SCREENSHOT_FIX_20261108 -->
## ✅ أحدث مختبر T1–T5 — تصحيح السكرين شوت الأسود (8 نوفمبر 2026، 20:20 UTC)

**جديد:** [GitHub Actions #42519487402](https://github.com/alwansan/raf/actions/runs/42519487402) **COMPLETED SUCCESS**؛ نسخة مشتركة واحدة عربية عمودية، إصدار `0.2.13-shared`، package `com.alwansan.raft.lab.shared`. Artifact ZIP رقم `13632379139` (ينتهي **22 نوفمبر 2026، الساعة 20:20 UTC**) يحتوي APK و`team-testpack.json` و`SHA256SUMS.txt`. **ZIP GitHub ليس رابط APK مباشر على Releases**. تم استخراج APK وفحص SHA وتوفيره للمالك في محادثة T5، دون نشره كـRelease عام.

- **APK الفعلي:** 93,910 بايت، SHA256 `6a41002cee345c48413ef56b0820211fb4ae73292229ec33ce830e82897194a7`, versionCode `13`, v2 Debug cert SHA256 `1b47e47c4e4a170a8b6a7f31c9718c8bd9be4a20a77b72a08edf65b3e754e3e6`. شهادة إصدار `0.2.10` السابق مختلفة `7e3a8c74414403e1ebded585b2e1da918de8d797a394cf154ea5f56c527836b9`: **صدّر سجلاتك أولاً، احذف تطبيق المختبر القديم، وثبّت APK الجديد**. تغيير شهادة Debug يمنع تثبيته فوق القديم، وقد يؤدي الحذف إلى زوال نتائج التطبيق المحفوظة داخله.
- **التصوير:** اكتشف المالك بالصور أن `T3-01` الآلية من v0.2.10 حفظت حيز GLES **أسود** مع حالة `EVIDENCE_READY`، بينما تصوير هاتفه يُظهر ثلاثة أعمدة أحمر/أخضر/أزرق. [تقرير مقارنة الدليلين](unified/SCREENSHOT_FIDELITY_OWNER_REPORT_20261108_AR.md)؛ الإصلاح يطلب `PixelCopy` من **GLSurfaceView نفسها**، يطابق ألوان الصورة بقراءة GPU الحقيقية، ويُعيد المحاولة عند السواد، ويُدمج Surface الصحيحة في صورة نافذة كاملة بدلاً من قص الارتفاع على 900 بكسل. إذا فشل يكتب `NEEDS_SCREENSHOT` ويطلب صورة فعلية من المالك ولا يعلن نجاحًا.
- **اختبار فعلي ناقص:** [CI42519126545](https://github.com/alwansan/raf/actions/runs/42519126545) **SUCCESS** لاختبارات السياسة الفعلية/تجميع Android؛ نجاح المصدر **لا يثبت إصلاح تصوير الهاتف** قبل تجربة v0.2.13 على نفس الجهاز.
- **للتجربة:** افتح الإصدار العربي واضغط **«تشغيل T3 تلقائيًا»** أو **«إعادة الاختبارات التلقائية بالقوة»**؛ افتح PNG الجديدة لصور `T3-01..06` وتأكد أن حيز اللون غير أسود، وارفع ملفات PNG و`events*.jsonl` و`summary*.json` إلى [CL/test](https://github.com/alwansan/CL/tree/main/test). يمكنك رفع لقطة نظام Android لنفس T3-01 للمقارنة؛ لا تعتبر `EVIDENCE_READY` نجاحًا بصريًا تلقائيًا.
- **بدون تغيير حزمة الاختبارات:** 29 حالة بنفس JSON sha256 `6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f`. الوضع العمودي وتعريب الواجهة مستمران؛ اللعبة الكاملة Unity/XAPK لم تُبن، **NOT_READY 0/3**.
- سجل الطلب النهائي مثبت على parent source SHA `e7a6248b0d0c14b9772bd52f3bbdc5cf22fa9b9a`، request [15d146f](https://github.com/alwansan/raf/commit/15d146f441554818b59fbd0eb917474c01cefd3a). طلبان أقدم فشلا بسبب **تغيّر parent SHA أثناء عمل العملاء** قبل وصولهما للتجميع؛ لم يُنتجا APK، ونجح الثالث مع مقارنة رأس الفرع قبل تحديثه.



<!-- T5_ARABIC_PORTRAIT_CI42517104924_VERIFIED -->
## ✅ نسخة المختبر العربية العمودية الجديدة — 8 نوفمبر 2026، 19:52 UTC

**أحدث Mini APK واحد T1–T5:** [GitHub Actions run #42517104924](https://github.com/alwansan/raf/actions/runs/42517104924) **COMPLETED SUCCESS**. Artifact ZIP ID `13631588625` (ينتهي **22 نوفمبر 2026، 19:52 UTC**) يحوي APK فعليًا وحزمة JSON و`SHA256SUMS.txt`. **هذا ZIP Artifact وليس رابط APK مباشر من GitHub Releases**؛ تم استخراج الـAPK والتحقق من الهاش وتسليمه للمالك كملف مباشر في محادثة T5، دون نشره في Releases.

- **Raft-Team-Lab-debug.apk:** حجم `90,058` بايت، SHA256 `0f469cc650182370b570d96c8e92e3f9c686f6b4417ae10e22d3c35b0084fd42`, package `com.alwansan.raft.lab.shared`, version `0.2.10-shared`, versionCode `10`.
- **AndroidManifest الفعلي داخل APK:** أربع Activities كلّها `screenOrientation=portrait`، عنوان التطبيق `مختبر اختبارات رافت`، Android target 35. الواجهة الرئيسية عربية RTL، وعناوين/خطوات/نتائج متوقعة لكل الاختبارات الـ**29** بالعربية عبر `ArabicLabStrings.java`.
- **نفس الحزمة بلا تعديل:** `team-testpack.json` SHA256 `6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f`. المصادقة في التطبيق تعالج نفس الـ29 IDs؛ لا يُعلن نجاح أي اختبارات يدوية دون المستخدم.
- **تحذير تحديث مهم:** توقيع Android Debug لهذا الإصدار SHA256 `7e3a8c74414403e1ebded585b2e1da918de8d797a394cf154ea5f56c527836b9` **يختلف** عن توقيع الإصدار الأول `cd2b1f9875dce958ef4ac5f6a08737174d60870df6562afb5636b7fe377cc259`. **صدّر نتائج 0.2.9 أولًا** ثم احذف تطبيق المختبر القديم وأعد تثبيت APK العربي؛ لا تضمن تحديثًا فوقه أو استمرار تفضيلات التطبيق المحلية. لا تحذف ملفات CL/test المرفوعة.
- **طريقة الاستخدام:** بعد التثبيت اختر «▶ تشغيل الاختبارات التلقائية لكل الفريق»، ثم قسم «طلبات تحتاج تدخلك» للاختبارات T4/T5 اليدوية. اختبار T5-02 يفتح منتقي SAF؛ والبقية تتطلب تجربة أو دليلًا. صدّر السجلات وارفعها إلى **[CL/test](https://github.com/alwansan/CL/tree/main/test)**. اقرأ [دليل T5 العربي](unified/T5_OWNER_TEST_GUIDE_AR.md). لم تُختبر هذه النسخة على Android 15 فعلياً بعد.
- **الأدلة:** source-only Arabic/portrait [CI42516899166](https://github.com/alwansan/raf/actions/runs/42516899166) و[CI42516908881](https://github.com/alwansan/raf/actions/runs/42516908881) SUCCESS؛ full shared mini [CI42517104924](https://github.com/alwansan/raf/actions/runs/42517104924) SUCCESS. Embedded source parent `93e32950c521d9890ce845eb8213cd6704cd7f98`, build request commit `c5100411c50ec3b663fa9262eb68c49c95180f3e`. **هذه ليست لعبة Raft الكاملة** ولا تغييرًا على تصويت XAPK 5/5 أو NOT_READY 0/3.



**8 نوفمبر 2026 — نظام جديد:** تطبيق Android واحد وحزمة `team-testpack.json` واحدة لجميع T1–T5؛ لا حاجة لتحميل خمسة APKات. [تعليمات التعاون](UNIFIED_LAB_POLICY_AR.md) · [جاهزية بناء المختبر فقط](SHARED_BUILD_READINESS.md) · [مصدر التطبيق الواحد](unified/README.md) · [برومبت الاستعادة المحسن](../prompt/coordination/T_TEAM/RESTORE_SHARED_LAB_AR.md).

## روابط المستخدم

| الملف | رابط مباشر | الحالة |
|---|---|---|
| **Raft Team Lab.apk** — تطبيق واحد لجميع العملاء | **بُني بنجاح، لكن لم يُنشر أصل APK مباشر على GitHub Release**؛ APK موجود داخل Artifact ZIP بعد استخراجه. | CI_BUILT / NO_PUBLIC_DIRECT_APK |
| **Raft Team Lab artifact ZIP** — يحوي APK الفعلي وJSON وSHA256SUMS | [GitHub Actions #42509945996 — Download artifact ZIP](https://github.com/alwansan/raf/actions/runs/42509945996)؛ Artifact ID `13628828717`، **ليس رابط APK مباشر** | SUCCESS — ينتهي 2026-11-22 18:26 UTC |
| **team-testpack.json** — حزمة واحدة، 29 اختباراً | [تنزيل مباشر لملف JSON](https://raw.githubusercontent.com/alwansan/raf/feature/android-native-port/apk-for-testing/unified/pack/team-testpack.json) | SOURCE_READY — يحتاج APK يدعم schema v2 |
| **صور ونتائج الاختبارات** | `/storage/emulated/0/Download/Games/cl/test/shared-<session>/` بواسطة MediaStore | ينتجها التطبيق عند التشغيل/التصدير |
| **الأدلة والتطبيقات القديمة** | [سجل الإصدارات الخمسة السابقة](LEGACY_INDIVIDUAL_APKS.md) | HISTORICAL ONLY، لا تختبر الخمسة الآن |

**رابط APK المباشر** يجب أن يكون رابط أصل APK حقيقي منشور، مثلاً أصل Release بعد فحص فتحه ومحتواه، لا صفحة `actions/runs` أو ملف ZIP Artifact موصوف خطأ كـAPK مباشر. إذا تعذر Release، اذكر رابط ZIP بوضوح كحل مؤقت، ولا تخترع الرابط.

> **تحديث T5 للمصدر بعد بناء APK (8 نوفمبر 2026، 18:56 UTC):** نجح [CI42512390472](https://github.com/alwansan/raf/actions/runs/42512390472) في إصلاح مسار SHA256 الموحّد لاختيار APK/OBB عبر SAF مع حدود 16GiB وحماية تكرار القراءة الصفرية والاحتفاظ بالنتائج. **هذا التغيير (commit 6f2cf77) ليس داخل APK المبني في CI42509945996**؛ نتيجة CI الجديدة تجميع Java وفحوص مصدر فقط، وليست APK ثانياً أو إثبات هاتف. لا يلزم تنزيل تطبيق آخر الآن؛ أي إصدار أحدث يجب أن يخضع لقرار Mini جديد وفحص توقيع/Artifact مستقل.

## فحص T5 الفعلي — 8 نوفمبر 2026، 18:26 UTC

- Unified build request commit [3555baf](https://github.com/alwansan/raf/commit/3555bafae757bb0523e00e171582530ab4193b32), embedded source parent SHA `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8`. [Actions run #42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) **SUCCESS**: Python validation, 20/20 pure-Java evidence-policy assertions, Gradle `:app:assembleDebug` and upload-artifact completed.
- Artifact `13628828717` ZIP SHA256 `f98d32f6a78e49ba319e250234cca5ed3eb48853a760c4ec6c78950227648fa6`; expires **2026-11-22T18:26:36Z**. Extract `Raft-Team-Lab-debug.apk` (78,806 bytes, SHA256 `cee2df1b3bb2a1a3c8e9ab757f520040d36c5bf16d711587f7e2bc537f917472`), plus `team-testpack.json` (9,384 bytes, SHA256 `6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f`) and `SHA256SUMS.txt`. ZIP contained exactly these three files; the APK embedded the same JSON SHA256.
- AndroidManifest binary decoded locally: package `com.alwansan.raft.lab.shared`, versionCode **9**, versionName `0.2.9-shared`, target platform Android 15/compile SDK 35, main Activity exported. Actual APK signing block **v2** present; certificate DER SHA256 `cd2b1f9875dce958ef4ac5f6a08737174d60870df6562afb5636b7fe377cc259`; issuer **Android Debug**, not established as stable across future builds. ZIP CRC and member hashes passed; no device installation or functional GPU/input/screenshot/SAF test yet.
- **Limitations:** no publicly hosted APK Release asset yet, so no verified public direct APK URL. The actual Android APK is available to owner by extracting the Actions Artifact ZIP (or via this conversation's file attachment); do not mistake ZIP for APK. Package is experimental and does not prove Raft Unity shader, water, mouse or graphics fixes. Full-game XAPK 5/5 vote and 0/3 release-ready gates are unchanged.

> **للمالك الذي استخدم Auto All ولم يعرف تشغيل T5:** راجع [خطوات T5 على الهاتف، وأدلة CL/test الموجودة](unified/T5_OWNER_TEST_GUIDE_AR.md). 29 اختباراً تعمل من pack المضمن بلا استيراد؛ AUTO T5 ينفذ T5-01 فقط، بينما T5-02..06 تحتاج فتح سطر الطلب في **IN-APP REQUESTS** قرب أسفل شاشة التطبيق. لا تضع PASS بلا ملاحظة. سجلات CL/test لليوم تثبت 9 PASS + 6 EVIDENCE_READY + 14 NEEDS_INPUT، وليس تعطّل التشغيل التلقائي. إصلاح T5-02 للـOBB الضخم `6f2cf77` أحدث من أول APK.

## العملاء الخمسة في واجهة التطبيق الموحد

| العامل | اختبارات موجودة في الحزمة الموحّدة | نوع الإثبات |
|---|---|---|
| **T1** | T1-01..04 — GLES3.1، Compute، SSBO، negative compiler | GPU auto/الحصول على نتيجة أصلية للاختبارات الاصطناعية |
| **T2** | T2-01..04 — GLES3، FBO multi-pass، two negative controls | GPU auto/لا يثبت Raft Foam الأصلي |
| **T3** | T3-01..06 — الألوان، vertex، alpha/sRGB، shader negative | عرض GLES فعلي + PixelCopy لصورة نافذة التطبيق، ثم مراجعة بصرية |
| **T4** | T4-01..09 — Left/Right/Middle/Scroll/capture/keyboard | يحتاج ماوس فعلي؛ طلب داخل التطبيق حتى يؤكده المالك |
| **T5** | T5-01..06 — package identity/SAF full SHA/OBB/perf/controls | الهوية آلية؛ الاختبارات التي تحتاج ملفاً أو لعبة تظل manual |

## تجربة واحدة بدلاً من خمسة

افتح التطبيق الواحد، اختر **AUTO ALL** لتشغيل كل ما يمكن قياسه فعلياً، أو **AUTO T1..T5** لاختبارات عامل واحد. ليس كل اختبار يقبل التنفيذ الصامت؛ الحالات التي تحتاج ضغط ماوس أو فتح ملف أو حكم بصري تظهر في **قائمة طلبات داخل التطبيق**. اختر الطلب لتشغيله/إرفاق صورته، ثم **NEXT** و**FINISH**؛ لا تُزال الحالة حتى تحفظ نتائجها الحقيقية ودليل الصورة المطلوب.

تعاد الحالة عند تغيّر محتوى الحالة أو مصدر برنامجها، أو فقدان الصورة المطلوبة؛ غير المتغيّرة لا تعاد لمجرد تغير إصدار APK. تسجّل البيانات في JSONL وملف summary وصور الحالة في مجلد الجلسة. **لقطات الشاشة التلقائية تخص نافذة مختبرنا فقط**، وليس لعبة Raft خارج التطبيق.

## أين يضع العمال آخر حالة؟

- كل عامل يعدل **صفه وحده** في [جاهزية المختبر المشترك](SHARED_BUILD_READINESS.md)، ويقدم التغييرات/الحالات عبر ملفات العمل والجلسات.
- **T5 وحده** يصدر طلب بناء واحد إذا كان هناك **NEED_BUILD واحد على الأقل** بدليل حقيقي ويتطلب تغيير native driver، بعد التحقق من الحالات الخمس والجولة وActions وملف الحزمة.
- حزمة JSON فقط جديدة؟ حدّث الرابط/الحزمة الواحدة دون بناء جديد إذا كان driver موجوداً في APK السابق.
- تصويت اللعبة الكاملة XAPK الأصلي **مستمر دون تغيير** في [ملف 5/5](../prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md).
