# Raft Android Native — تسليم Work الجديد — 3 نوفمبر 2026

**اقرأ هذا الملف كاملاً أولاً في جلسة Work الجديدة.** هذا تسليم متابعة تطوير فعلي، وليس مجرد خطة. بعده اقرأ الروابط بالترتيب في آخر الملف. اعتمد أحدث HEAD وActions لأن بعض المستندات الأقدم تسجل عمليات كانت جارية ثم اكتملت. المالك قدم فعلاً صوراً وتفاصيل تجربة ولوغات جديدة يوم 2 نوفمبر؛ تعليمات جلسة التحضير القديمة بالانتظار حتى يشرح المشاكل أصبحت تاريخية.

## 1. حدود العمل الملزمة

- المستودع: https://github.com/alwansan/raf
- **الفرع الوحيد المسموح تعديله**: `feature/android-native-port`. ممنوع تعديل/دمج/حذف `main` و`zip` و`Unity-Editor`. مستودع https://github.com/alwansan/CL للقراءة فقط، وفروع تسجيل اللوغ مستقلة.
- **أحدث تعليمات المالك: «لا تشغل بناء حتى اخبرك لذالك اكمل الاصلاحات».** لا تشغيل أو طلب أو dispatch لبناء Unity Editor أو Android APK/OBB/XAPK أو نشر Release أو تجربة Unity ثقيلة، حتى يرفع المالك الحظر صراحة. لا تعدّل `.github/raft-native-build-request.json` ولا `.github/raft-native-experiment-request.json`.
- **«لاتعدل المهمة المجدولة».** لا تغيير إعداداتها ولا تشغيلها/تعطيلها ولا إنشاء نسخة. تحقّق من تغييرات الوكيل المجدول على نفس الفرع قبل كل كتابة لتجنب التضارب. اختبارات Python/C# الخفيفة والتجارب المستقلة CPU-only / no Unity / no LFS مسموحة.
- لا يوجد PC لدى المالك. Unity 2021.3.45f2، Android ARM64 IL2CPP، GitHub Actions، هاتف POCO F5 Pro. اعتماديات Unity/FMОD 2.02.15 والمفاتيح والتوقيع سبق إعدادها والتحقق منها؛ لا تطلب إعادة الإعداد أو الملفات المتوفرة.
- حافظ على المشاهد والمحتوى الكامل وملفات `.meta` وGUIDs وأصول اللعبة وصيغة الحفظ `.rgd`، ولا تزوّر نتائج العالم أو الشيدرات أو الصوت. لا تنشر المشروع المعاد بناؤه أو مصادر خاصة أو ملفات مفككة أو أسرار، ولا تخلط نجاح CI مع تجربة الهاتف. المستخدم يفضل اكتمال المحتوى على تقليص حجم APK.

## 2. آخر حالة مؤكدة في GitHub

- آخر HEAD **قبل التزام ملف التسليم هذا**: `7cb5a8455d2550d6a472abf6ed309dc88e05e210`، تحديث التوثيق بعد نجاح تحويل DXBC الأصلي. إعادة القراءة واجبة عند بداية Work؛ الالتزام الجديد سيرفع HEAD.
- **آخر بناء Unity أصلي منشور**: https://github.com/alwansan/raf/actions/runs/41448086401 — `COMPLETED SUCCESS` بتاريخ 2026-11-02، مصدره الثابت `9462f8edd8cdb5becbccb96521f2876ef9924410`، وليس HEAD الحالي.
- إصدار اللعبة: https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1 . APK versionCode80 باسم `Raft-Android-Test.apk` حجمه 672642221 بايت، SHA256 `da62f996e6ee089a856ac6b812b5497c165dc3c827999e1fdc1cfdbacf1b4d56`. OBB بحجمه الكامل 2301297690 بايت، SHA256 `6a22a2be3818a9d84753a1e0031fe21acc405eccc983ec7034125e29697dc15c`، منشور في 3 أجزاء. XAPK بحجمه الكامل 2973941163 بايت في 3 أجزاء. توجد 11 ملفات إصدار تشمل تعليمات التثبيت/التجميع والبصمات. ملف APK وحده لا يكفي بدون OBB. هذا **نجاح بناء وتسليم فقط، لا دليل تشغيل العالم/الرسوم/الصوت/اللمس على الهاتف**؛ والإصلاحات الأحدث غير موجودة في APK80.
- أحدث تجارب مصدر مؤكدة: DXBC/HLSL https://github.com/alwansan/raf/actions/runs/41527047341 SUCCESS؛ مصدر العالم https://github.com/alwansan/raf/actions/runs/41526652528 SUCCESS؛ ماسح ComputeShader https://github.com/alwansan/raf/actions/runs/41525570605 SUCCESS؛ تجربة HLSL اصطناعية https://github.com/alwansan/raf/actions/runs/41525025301 SUCCESS. الأخطاء القديمة في محاولات DXBC كانت تبعيات بناء أدوات (submodule وspirv-cross)، وتم إصلاحها قبل نجاح التشغيل الأخير. لا Unity ولا APK جديد في هذه التجارب.
- قبل التعديل: راجع HEAD ومجموعات workflow وقائمة pending/running وأحدث per-file SHA، ثم ارفع commit إلى الفرع المحدد فقط. احترم queue:max وcancel-in-progress:false. لا تعدّ الاستكمال الخلفي مضموناً من جلسة عادية.

## 3. ملاحظات الجهاز الأصلية التي سلّمها المالك

- فتح Settings يسبب تمدد/تغير حجم الشاشة والأبعاد، بينما بداية اللعبة تظهر طبيعية؛ الاتجاه يجب أن يكون أفقياً من أول تشغيل وحتى العودة من الخلفية.
- معظم المواد والألوان بيضاء/خاطئة، مربعات مؤثرات موحّدة اللون، ماء ورغوة وشيدرات مفقودة. `UltimateWater.Internal.Dx11FFT.ComputeFFT` يرمي `Invalid kernelIndex` للفهارس 2 و6 في مورد مصدّر يحوي صفر kernels. أخطاء تمريرات `Water Spectrum` و`Foam/Global` و`Blur` و`Depth Copy` و`VolumetricLight`.
- إنشاء العالم يقف عند `INITIALIZING ASSETS` ثم `HAVING ISSUES CONNECTING / TRYING TO CONNECT TO HOST`. لا تزيّف اكتمال الاتصال؛ حافظ على إعدادات العالم وRPC والفيزياء الأصلية. `PersonController.GroundControll` يرمي NullReference، ويرتبط زمنياً باعتراضات FMOD المبكرة.
- أخطاء الصوت: `EventNotFoundException` و`VCANotFoundException vca:/master`. موجودة في نسخة قديمة؛ إصلاحات محمّل OBB واستثناءات FMOD أحدث ولم تختبر على الهاتف.
- اللمس/التحكم لم يكن يستجيب، وأضيف overlay Xbox وإدارة pointer وUGUI، لكن لا تُعتبر استجابة gameplay مثبتة.
- لواحق سابقة تشير إلى GPU-memory OOM على الهاتف: 5363928kB مقابل threshold 1572864kB. افرق بين OOM الهاتف وexit137 في CI. لا تقدّر FPS أو PSS دون قياس.
- أرشيفات اللوغ المستلمة: `LogRaft-1793639905225.zip` (~5.79M سطر)، `LogRaft-1793640117875.zip` (~1.35M)، `LogRaft-1793642162566.zip` (~1.39M)، `LogRaft-1793642351692.zip` (~2.03M). سجلات JSONL في https://github.com/alwansan/CL/tree/main/raft%20log ، وصور `img`، ومجلدا `lf` و`logfox`. سجل الجهاز المستخدم للإصلاحات: `raft log/انتاج مسار /5/com.alwansan.raft.androidtest/files/raft-logs/raft-20261102T175617666-7f4e1846-0000.jsonl`. لا تنسب سجل APK قديم إلى إصلاح جديد.
