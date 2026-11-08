<!-- T5_R2_ARABIC_PORTRAIT -->
> **تحديث 8 نوفمبر 2026:** الإصدار التجريبي المشترك الجديد `0.2.10-shared` بواجهة عربية RTL، أربعة Activities عمودية Portrait، و29 وصف/خطوات/توقع بالعربية عبر `ArabicLabStrings.java` **دون تغيير ملف JSON أو معرّفات الاختبارات**. [CI42517104924](https://github.com/alwansan/raf/actions/runs/42517104924) SUCCESS، artifact ZIP ID `13631588625`، APK 90,058 bytes SHA256 `0f469cc650182370b570d96c8e92e3f9c686f6b4417ae10e22d3c35b0084fd42`; لا توجد نسخة GitHub Release APK مباشرة مؤكدة، ولا تحقق على الهاتف بعد. **شهادة Debug جديدة مختلفة عن 0.2.9**، لذا يجب تصدير نتائج القديم وحذفه قبل تثبيت الجديد. توجيه المالك لجميع العمال في [OWNER_ARABIC_PORTRAIT_CL_UPLOADS_20261108](../../../prompt/coordination/T_TEAM/OWNER_ARABIC_PORTRAIT_CL_UPLOADS_20261108.md)، ورفع اختبارات الهاتف إلى https://github.com/alwansan/CL/tree/main/test.

# APK موحّد واحد للفريق الخماسي
تطبيق `com.alwansan.raft.lab.shared` يحتوي على T1 GLES Compute، T2 GLES FBO، T3 GLES مواد/ألوان، واختبارات إدخال T4 وT5/SAF، **ولا يحتوي لعبة Raft أو كامل assets**.

الملفات الأصلية القديمة تحت `apk-for-testing/host/` و`apk-for-testing/workers/T3/gles-lab/` تُستخدم كـsourceSets من غير نسخ محتواها أو محو عمل العملاء. واجهة البداية الجديدة `UnifiedLabActivity` فقط. CMake/Unity/IL2CPP ليس مطلوباً.

الاختبارات الموحدة data-only `pack/team-testpack.json` مضمنة افتراضياً. بعد ذلك يمكن تحديث JSON موحد عبر SAF بدون APK جديد فقط عندما تكون drivers موجودة في APK.

زر Auto All وAuto Tn يشغل فقط الحالات التي تمتلك driver فعلياً ويمكن قياسها. حالات ماوس مادي أو حكم بصري لا يجوز إعلان PASS تلقائي لها؛ تظهر في قائمة المتابعة، مع شاشة خطوة تالية/إنهاء وإرفاق screenshot. صور تطبيقنا يمكن محاولة التقاطها عبر PixelCopy؛ التطبيقات الأخرى تحتاج مشاركة المستخدم.

البناء: `gradle -p apk-for-testing/unified :app:assembleDebug -PsourceSha=<HEAD_SHA>`. **أُكّد بناء Gradle APK واحد بنجاح** في [CI42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) على parent SHA `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8`؛ artifact ZIP ID `13628828717` يحوي APK وJSON، وليس رابط APK مباشر. شهادة Debug غير مثبتة عبر تحديثات، ولم يُتحقق من التثبيت/الاختبارات على الهاتف؛ اقرأ TEST_CENTER.md. النسخ القديمة الخمس تاريخية للاحتفاظ بالأدلة فقط.
