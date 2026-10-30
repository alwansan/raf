# Raft — Unity Editor in GitHub Actions (Android-only control)

هذا الفرع للتحكم بـ **Unity Editor على GitHub Actions من هاتف Android**، بدون تعديل الفروع `main` أو `zip` أو `feature/android-native-port`.

**ليس مشروع Unity الجاهز للتشغيل**: الفرع `feature/android-native-port` يحتوي ملفات اللعبة الأصلية وأدوات إعادة البناء. الـ workflow هنا يسحب الفرع ذاك بشكل مؤقت داخل runner، ويُعيد تكوين Unity project، ثم يحاول فتحه وترجمته داخل Unity Editor 2021.3.45f2.

## روابط سريعة

- [Workflow وسجلات تشغيل Unity](https://github.com/alwansan/raf/actions/workflows/raft-unity-editor-cloud.yml)
- [Secrets](https://github.com/alwansan/raf/settings/secrets/actions)
- [Variables](https://github.com/alwansan/raf/settings/variables/actions)
- [تعليمات تفعيل Unity Personal الحديثة — GameCI](https://game.ci/docs/github/activation/)
- [Unity Account](https://id.unity.com/)
- [Unity Hub](https://unity.com/download)

## 1) إعداد الترخيص — مرة واحدة

إذا عندك Unity Personal مجاني: تفعيل الملف `.ulf` يتم عبر Unity Hub على **Windows أو macOS أو Linux**. هاتف Android وحده لا يشغّل Unity Hub، و**GitHub Actions لا يحل مشكلة أول تسجيل وتفعيل ترخيص Personal بشكل سحري**. تگدر تستخدم كمبيوتر موثوق مؤقتاً، أو كمبيوتر سحابي بسطح مكتب تدخله من الموبايل، لإنشاء الملف بطريقة رسمية.

افتح Unity Hub وسجّل دخولك بحساب Unity، بعدها `Preferences > Licenses > Add > Get a free personal license` ثم استخرج `Unity_lic.ulf`:
- Windows: `C:\ProgramData\Unity\Unity_lic.ulf`
- Linux: `~/.local/share/unity3d/Unity/Unity_lic.ulf`
- macOS: `/Library/Application Support/Unity/Unity_lic.ulf`

**لا تستخدم طريقة `.alf` اليدوية القديمة لتفعيل Personal**؛ الإجراء لم يعد مدعوماً رسمياً، وأداة `game-ci/unity-request-activation-file@v2` مهجورة.

من [GitHub Secrets](https://github.com/alwansan/raf/settings/secrets/actions) اختر `New repository secret` وأنشئ:
- `UNITY_LICENSE`: النص الكامل لملف `Unity_lic.ulf` (وليس اسم الملف).
- `UNITY_EMAIL`: إيميل حساب Unity.
- `UNITY_PASSWORD`: كلمة المرور لحساب Unity.

**بديل Unity Pro**: استعمل `UNITY_SERIAL` بدل `UNITY_LICENSE` مع نفس `UNITY_EMAIL` و`UNITY_PASSWORD` (فقط إذا كنت تملك Serial فعلياً).

لا تضع أي سر داخل `README`، GitHub Variables، كود workflow، Artifacts، رسائل ChatGPT، أو لقطات شاشة.

## 2) اختبار Unity Editor بدون تحميل Raft

من [GitHub Actions Variables](https://github.com/alwansan/raf/settings/variables/actions) اختر `New repository variable`:
- **Name**: `RAFT_UNITY_MODE`
- **Value**: `smoke`

هذا يجعل الـ workflow يسحب Unity Editor 2021.3.45f2 مع Android Build Support بواسطة GameCI v4 ويفتح مشروع Unity صغير موجود في هذا الفرع. يتأكد من نجاح فتح المحرر وتجميع C# وتحديد Android كهدف. **لا ينزّل ملفات Raft الأصلية ولا أي LFS**.

### تشغيل الاختبار من الهاتف

ملفات الـ workflow غير موجودة في `main` عن قصد؛ لذلك زر `Run workflow` قد لا يظهر. حسب [وثائق GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)، `workflow_dispatch` يحتاج وجود الـ workflow في الفرع الافتراضي. البديل المضمون هنا هو **push** إلى `Unity-Editor`:

1. افتح [README في فرع Unity-Editor](https://github.com/alwansan/raf/blob/Unity-Editor/README.md).
2. اضغط علامة القلم `Edit` (قد تحتاج اختيار `Desktop site` في Chrome).
3. غيّر سطر حالة/تجربة بسيط أسفل الملف، ثم `Commit changes` **مباشرة إلى `Unity-Editor`**.
4. افتح [Actions runs](https://github.com/alwansan/raf/actions/workflows/raft-unity-editor-cloud.yml) وانظر job المسمّى `smoke`. وجود كلمة `UNITY_EDITOR_CLOUD_SMOKE_OK` في السجل ونجاح المهمة يعني أن تجربة المحرر المصغّرة نجحت.

**تغيير Secrets أو Variables وحده لا يشغّل workflow تلقائياً؛ يلزم push جديد.**

## 3) استيراد مشروع Raft الحقيقي (لاحقاً)

بعد نجاح `smoke`، غيّر نفس variable:
- `RAFT_UNITY_MODE` = `raft`

ثم كرر تعديل README ودفع commit إلى `Unity-Editor`.

سيجلب الـ workflow الإصدار الأحدث من `feature/android-native-port` في بيئة مؤقتة، ويشغّل اختبارات overlay، وينزّل **ثلاثة LFS objects فقط** (`resources.assets`, `sharedassets0.assets`, `sharedassets36.assets`, حوالي 322 MiB)، ويتحقق من SHA256، ثم يعيد إنشاء المشروع بـ AssetRipper + ILSpy، ويحاول Unity Editor import + Android build.

قبل التنزيل فحص مساحة القرص، ولن يسحب بقية Git LFS البالغ حجمها عدة GiB. **تحميل LFS يمكن أن يؤثر على حدود الاستخدام والفوترة**؛ لذلك لا تختَر `raft` إلا بعد قبول كلفة/حدود الشبكة في GitHub، وتأكد من `Settings > Billing and licensing`.

النتيجة قد تكون أخطاء استيراد/ترجمة أو عدم توفر مساحة. **نجاح إنشاء 40 مشهد وربط GUID لا يعني لعبة قابلة للتشغيل**. لا يُنشر APK أو assets من اللعبة من هذه workflow. إذا نجح البناء، يلزم استكمال تحويل الإدخال والرسوميات والشبكة وAndroid.

## 4) إيقاف تجارب Unity

غيّر `RAFT_UNITY_MODE` إلى `off` أو احذف المتغير. بعدها أي push سيشغل فقط فحصاً خفيفاً، ولن يبدأ Unity أو تنزيل Raft LFS.

## 5) ما الذي لا يستطيع GitHub Actions فعله؟

- يفتح **Unity Editor في headless/batch mode** للتجميع والاختبار، وليس نافذة محرر تفاعلية على شاشة هاتفك.
- لا يستبدل الحصول على ترخيص Unity صحيح أو حقوق نشر ملفات اللعبة الأصلية.
- Unity Personal قد يحتاج في البداية جهازاً بواجهة سطح مكتب، ويمكن أن يكون هذا الجهاز *سحابياً ومتحكَّماً به من هاتفك* بدل امتلاك PC.
- لا يضمن APK يعمل؛ أولاً يجب اجتياز import/compile ثم معالجة مشاكل Android.
- لا يخزن كلمات المرور أو ملف الترخيص في مستودع عام.

### سجل التحفيز (غيّر هذا السطر فقط لتشغيل تجربة جديدة)
- البداية: إعداد منفصل بتاريخ 2026-10-30؛ الوضع الافتراضي `off`.
