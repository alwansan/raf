# بناء مختبر Android واحد للفريق T1–T5 — T5 فقط

**المرجع الحي:** apk-for-testing/UNIFIED_LAB_POLICY_AR.md وapk-for-testing/SHARED_BUILD_READINESS.md وapk-for-testing/TEST_CENTER.md. بناء اللعبة الكاملة XAPK له تصويت 5/5 مستقل لا يتغير.

1. لا تبن خمسة APKات ولا تختر اسم عامل واحد للتطبيق؛ الحزمة الوحيدة الجديدة com.alwansan.raft.lab.shared من apk-for-testing/unified/.
2. افحص live HEAD وCI وActions queued/in_progress وأقدم الحزم الموقّعة. يكفي **عامل واحد NEED_BUILD** بقرار حديث خلال 48 ساعة ودليل تغيير Java/driver فعلي يحتاج اختبار الهاتف، بعد مراجعة T5. لا يلزم إجماع الخمسة للميني. استخدم python3 scripts/check_shared_lab_votes.py --require-need قبل البناء.
3. إذا تغيّرت بيانات team-testpack.json فقط ويمكن استيرادها في APK الموجود، صدّر حزمة واحدة جديدة بدون إعادة APK. لا تكرر CI/بناء مكلف لتعديل توثيق أو صورة.
4. بناء حقيقي يحتاج تغيير الطلب المشترك الوحيد .github/raft-mini-lab-build-request.json في commit مستقل يغيّر هذا الملف فقط، برسالة تحتوي [raft-mini-lab]، مع requested_from_sha = SHA الأب المباشر الذي يحتوي كل التحسينات المنجزة. احسب SHA256 لملف apk-for-testing/unified/pack/team-testpack.json (لا تكتب SHA متوقع).
5. شكل الطلب: request_id فريد، target يساوي SHARED، requested_from_sha صحيح، pack_sha256 صحيح، reason يشرح السيناريو، publish false. اقرأ [المثال](BUILD_REQUEST_EXAMPLE.json) ولا تستعمل SHA الأصفار. لا تعدّل .github/raft-native-build-request.json الخاص بلعبة Raft.
6. workflow .github/workflows/raft-android-mini-lab.yml يتأكد من بيانات الطلب والـpack وتصويت العامل وتختبر Python، ثم يجمع APK واحداً عبر Gradle بدون Unity. لا تلغِ عمل الآخرين ولا تبدأ طلباً مكرراً أثناء تشغيل مشابه.
7. ناتج GitHub Actions هو ZIP يحتوي Raft-Team-Lab-debug.apk وteam-testpack.json وSHA256SUMS.txt — **ليس APK مباشر**. تحقق من APK bytes وapplicationId/versionCode وsha256 وشهادة التوقيع والأداء. التوقيع المؤقت للـdebug في runner قد يختلف؛ يجب تجهيز stable dedicated signing key آمنة قبل اعتماد تحديثات تحتفظ بالنتائج. لا تنشر مفتاحاً خاصاً أو كلمات مروره في المستودع.
8. إن احتاج المالك رابط تحميل APK مباشر، لا تضعه في TEST_CENTER.md حتى تنشر APK فعلياً على Release/مصدر تنزيل مباشر وتتحقق من الرابط والـSHA. إن فشل رفع Releases HTTP403 احتفظ بـArtifact ZIP وصرح بأنه ZIP، ولا تخترع رابط APK.
9. حدّث حالة البناء والإصدار والمصدر وpack SHA والرابط والنتيجة في SHARED_BUILD_READINESS.md وTEST_CENTER.md، وواصل عملك المعتاد أثناء تشغيل البناء. لا تقرّب نتائج mini lab من READY اللعبة إلا بدليل دمج واختبار Raft.
