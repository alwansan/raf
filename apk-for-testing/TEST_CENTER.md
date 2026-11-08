# Raft — ONE TEAM LAB APK / T1–T5

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

## فحص T5 الفعلي — 8 نوفمبر 2026، 18:26 UTC

- Unified build request commit [3555baf](https://github.com/alwansan/raf/commit/3555bafae757bb0523e00e171582530ab4193b32), embedded source parent SHA `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8`. [Actions run #42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) **SUCCESS**: Python validation, 20/20 pure-Java evidence-policy assertions, Gradle `:app:assembleDebug` and upload-artifact completed.
- Artifact `13628828717` ZIP SHA256 `f98d32f6a78e49ba319e250234cca5ed3eb48853a760c4ec6c78950227648fa6`; expires **2026-11-22T18:26:36Z**. Extract `Raft-Team-Lab-debug.apk` (78,806 bytes, SHA256 `cee2df1b3bb2a1a3c8e9ab757f520040d36c5bf16d711587f7e2bc537f917472`), plus `team-testpack.json` (9,384 bytes, SHA256 `6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f`) and `SHA256SUMS.txt`. ZIP contained exactly these three files; the APK embedded the same JSON SHA256.
- AndroidManifest binary decoded locally: package `com.alwansan.raft.lab.shared`, versionCode **9**, versionName `0.2.9-shared`, target platform Android 15/compile SDK 35, main Activity exported. Actual APK signing block **v2** present; certificate DER SHA256 `cd2b1f9875dce958ef4ac5f6a08737174d60870df6562afb5636b7fe377cc259`; issuer **Android Debug**, not established as stable across future builds. ZIP CRC and member hashes passed; no device installation or functional GPU/input/screenshot/SAF test yet.
- **Limitations:** no publicly hosted APK Release asset yet, so no verified public direct APK URL. The actual Android APK is available to owner by extracting the Actions Artifact ZIP (or via this conversation's file attachment); do not mistake ZIP for APK. Package is experimental and does not prove Raft Unity shader, water, mouse or graphics fixes. Full-game XAPK 5/5 vote and 0/3 release-ready gates are unchanged.

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
