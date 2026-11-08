# كيف يطلق العامل بناء mini APK من الفرع feature/android-native-port

**لا تنسخ هذا المثال إلى طلب حي دون دليل.** يحتاج إنشاء/تحديث ملف واحد فقط `.github/raft-mini-lab-build-request.json`، وليس `.github/raft-native-build-request.json` الخاص باللعبة.

1. اجعل مصدر المختبر وtestpack جاهزين، وحدّث مستند العامل مع أسئلة الاختبار، ثم تحقق من نجاح اختبارات source المجدية. افحص أي workflow مختبر مماثل قيد التشغيل/queued أو Artifact موجود؛ لا تكرار بلا تغيير.
2. اقرأ **HEAD الحالي** قبل إنشاء الطلب واحفظه في `requested_from_sha` (40 lowercase SHA). نسق ملفات زملائك، واصنع commit مستقل يغير **فقط** `.github/raft-mini-lab-build-request.json`، بحيث يكون requested_from_sha هو الأب المباشر لذلك commit.
3. schema صريح من [المثال](BUILD_REQUEST_EXAMPLE.json): `request_id` فريد، `worker` واحد من T1..T5، `requested_from_sha` من HEAD قبل الطلب، `reason` سؤال اختبار جهاز محدد بين 15 و800 حرف. لا تستخدم صفر المثال الحقيقي.
4. **رسالة commit يجب أن تحتوي `[raft-mini-lab]`** حتى يجيز workflow طلب البناء من push. الـworkflow [raft-android-mini-lab.yml](../.github/workflows/raft-android-mini-lab.yml) لا يعمل من تعديل ملفات المصدر العادي أو التصويت، ولا يمس Unity أو طلب XAPK الكامل.
5. اطلع على run الحقيقي: source tests ثم Gradle/JDK17/AndroidSDK35 وبناء `app-debug.apk` منفصل باسم تطبيق العامل. إن نجح، ثبت link Artifact الفعلي (والصلاحية 7 أيام) والـSHA256 والـpackage/version في صفك في [TEST_CENTER.md](TEST_CENTER.md). لا تقل READY قبل ذلك.
6. انتبه: `workflow_dispatch` لا يعمل مباشرة إذا workflow موجود فقط على فرع غير افتراضي؛ **push request المحدد أعلاه هو مسار التشغيل المعتمد حالياً**. لا تعدل `main`. لا تنشئ أكثر من request أو تعدّله أثناء job جارٍ. لا تستخدم `GITHUB_TOKEN` لتنفيذ self-trigger دون فهم سياسة GitHub.
7. إذا أردت تجربة renderer خاصة تحتاج Unity/GL/Vulkan، استخدم workflow مستقل ومحدود واسم APK ونطاق وsource SHA وتوقيع مناسب، واحفظ جميع الملفات والـlinks في صفحة العامل. لا ترفع أصول ZIP2 الخام أو أسراراً.
8. إذا تعذر التوقيع الدائم، debug APK قد يحتاج uninstall لتطبيق المختبر السابق فقط بسبب تغير شهادة debug؛ لا تمس تطبيق Raft أو حفظه.

هذه آلية بناء للمختبر الصغير **اختيارية عند حاجة الإثبات**، ولا تعني أن اللعبة جاهزة أو أن إجماع 5/5 تحقق.