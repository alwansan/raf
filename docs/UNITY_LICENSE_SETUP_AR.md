# إعداد ترخيص Unity لمشروع Raft Android

> الحالة بتاريخ 2026-10-30: استرجعنا مشروع Unity مبدئياً واختبرنا الروابط، لكن لم نفتح أو نبنِ المشروع بواسطة Unity Editor. فحص [GitHub Actions](https://github.com/alwansan/raf/actions/runs/41032390828) أثبت عدم توفر أسرار الترخيص المطلوبة. لا ترفع ملف الترخيص أو كلمة المرور داخل مستودع عام أو دردشة.

## روابط مباشرة

- [إنشاء حساب Unity / تسجيل الدخول](https://id.unity.com/)
- [تنزيل Unity Hub](https://unity.com/download)
- [إرشادات GameCI v4 الحالية للتفعيل](https://game.ci/docs/github/activation/)
- [إعدادات GitHub Actions Secrets للمستودع](https://github.com/alwansan/raf/settings/secrets/actions)
- [Workflow تجربة الاستيراد وبناء Android](https://github.com/alwansan/raf/actions/workflows/raft-unity-editor-android-import.yml)

## إذا عندك Unity Personal (المجاني)

1. تفتح Unity Hub على **Windows أو macOS أو Linux** وتسجّل الدخول بحساب Unity. **Unity Hub لا يعمل على هاتف Android مباشرة**. إذا ما عندك حاسوب، تحتاج وصولاً لحاسوب موثوق أو سطح مكتب بعيد لتفعيل الترخيص مرة واحدة.
2. من Unity Hub تروح إلى `Preferences > Licenses > Add` وتختار `Get a free personal license`. توثيق GameCI v4 يؤكد ضرورة إنشاء ملف `.ulf` حديث.
3. تستخرج ملف الترخيص `Unity_lic.ulf` من:
   - Windows: `C:\ProgramData\Unity\Unity_lic.ulf`
   - macOS: `/Library/Application Support/Unity/Unity_lic.ulf`
   - Linux: `~/.local/share/unity3d/Unity/Unity_lic.ulf`
4. تروح إلى [GitHub Actions secrets](https://github.com/alwansan/raf/settings/secrets/actions) وتختار `New repository secret` لكل واحد:
   - `UNITY_LICENSE`: **محتوى** ملف `.ulf` كاملاً.
   - `UNITY_EMAIL`: بريد حساب Unity.
   - `UNITY_PASSWORD`: كلمة مرور حساب Unity.
5. تفتح [الـWorkflow](https://github.com/alwansan/raf/actions/workflows/raft-unity-editor-android-import.yml)، تختار `Run workflow` ثم الفرع `feature/android-native-port`. لا تغيّر `main`.

## إذا عندك Unity Pro أو ترخيص تجاري مرقّم

حسب [GameCI v4](https://game.ci/docs/github/activation/)، تخلي `UNITY_SERIAL`, `UNITY_EMAIL`, `UNITY_PASSWORD` بدل `UNITY_LICENSE`. عدلت الـWorkflow حتى يقبل أيّاً من المسارين بعد فحص وجود الأسرار، بدون عرض قيمها بالسجل. لا تشترك بخطة مدفوعة فقط لهذا الاختبار قبل مراجعة أهليتك للترخيص المجاني.

## ملاحظات مهمة

- **لا تعتمد طريقة `.alf` القديمة لتفعيل Unity Personal**؛ توثيق Unity الحالي يقول إن التفعيل اليدوي غير مدعوم لهذا النوع، ويطلب Unity Hub. إرشادات GameCI v2/v3 حول `unity-request-activation-file` قديمة، وأداة GitHub المرتبطة بها مؤرشفة/غير مُصانة.
- إعداد أسرار GitHub وحده لا يشغّل الـWorkflow؛ بعد إضافة الأسرار شغّله يدوياً من صفحة Actions.
- المراحل السابقة تعمل بدون الترخيص: فحص الموارد، دمج السورس، اختبارات الـAndroid Offline Platform، وتجميع .NET التشخيصي.
- بعد تشغيل Unity Editor فعلياً سنعرف أخطاء التجميع الأصلية، المكتبات الناقصة، واحتياجات Android Build Support. **الـAPK غير موجود لحد الآن**.
- لا تنشر ملفات اللعبة الأصلية أو نسخة مشتقة للعامة بلا حقوق توزيع مناسبة.
