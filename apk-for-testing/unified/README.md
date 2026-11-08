# APK موحّد واحد للفريق الخماسي
تطبيق `com.alwansan.raft.lab.shared` يحتوي على T1 GLES Compute، T2 GLES FBO، T3 GLES مواد/ألوان، واختبارات إدخال T4 وT5/SAF، **ولا يحتوي لعبة Raft أو كامل assets**.

الملفات الأصلية القديمة تحت `apk-for-testing/host/` و`apk-for-testing/workers/T3/gles-lab/` تُستخدم كـsourceSets من غير نسخ محتواها أو محو عمل العملاء. واجهة البداية الجديدة `UnifiedLabActivity` فقط. CMake/Unity/IL2CPP ليس مطلوباً.

الاختبارات الموحدة data-only `pack/team-testpack.json` مضمنة افتراضياً. بعد ذلك يمكن تحديث JSON موحد عبر SAF بدون APK جديد فقط عندما تكون drivers موجودة في APK.

زر Auto All وAuto Tn يشغل فقط الحالات التي تمتلك driver فعلياً ويمكن قياسها. حالات ماوس مادي أو حكم بصري لا يجوز إعلان PASS تلقائي لها؛ تظهر في قائمة المتابعة، مع شاشة خطوة تالية/إنهاء وإرفاق screenshot. صور تطبيقنا يمكن محاولة التقاطها عبر PixelCopy؛ التطبيقات الأخرى تحتاج مشاركة المستخدم.

البناء: `gradle -p apk-for-testing/unified :app:assembleDebug -PsourceSha=<HEAD_SHA>`. **لم يتم تأكيد بناء/تثبيت هذه النسخة بعد**؛ اقرأ CI والرابط الحقيقي في TEST_CENTER.md. النسخ القديمة الخمس تاريخية للاحتفاظ بالأدلة فقط.
