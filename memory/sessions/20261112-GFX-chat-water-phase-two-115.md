# GFX-LAB — بداية استعادة الماء

`session_id=20261112-GFX-chat-water-phase-two-115` · `origin=chat`

أغلقت معايرة المرحلة الأولى كما في GFX154. فتح المالك المرحلة الثانية للماء. قرأت نقطة الاستعادة وذاكرة المختبر وحالته وآخر جلسة والتسليم ودليل Adreno، وراجعت GT ومرجع native المثبت. النطاق والبراهين السابقة في [مسار الماء](../../gfxlab/WATER_PHASE_TWO_AR.md).

[تنفيذ GFX155](https://github.com/alwansan/raf/commit/fd89f9b82023d4b3f7ead31ed30656b145526ccf) يضع Unity 2021.3.45f2 Vulkan/ARM64 IL2CPP في مشروع مصغر. الأربع حالات تُقرأ من ComputeBuffer وتُصدر مع القيم الخام. محلياً مر مرجع القيم وفحص أربعة ضوابط سلبية: NaN، عينة قديمة، ملف ناقص، API مختلف. هذا فحص بيانات اصطناعية على CPU. [CI 43143685531](https://github.com/alwansan/raf/actions/runs/43143685531) أُطلق للتحقق من البناء والتوقيع. اختبار Adreno والماء الأصلي قيد الانتظار.

الاستئناف: تحقق من CI والأثر أولاً، ثم راجع ملف الهاتف الجديد عند توفره. ابدأ بعدها بإثبات أنواع الماء وربط حالة أصلية واحدة من ZIP2 بـSpectrum/FFT واستعلامات الارتفاع. الأدلة المقبولة للمرحلة الأولى تظل مرتبطة بنطاقها.

أول بناء GFX155 توقف عند غياب `JsonUtility` من المشروع المصغّر. أُضيفت وحدتا JSON وAndroid JNI في `6aee6516a896c0868deac2020820890aaeb95f55` وبدأ [بناء التصحيح 43144304221](https://github.com/alwansan/raf/actions/runs/43144304221).

GFX156 [43144448074](https://github.com/alwansan/raf/actions/runs/43144448074) نجح على Assembly-CSharp الأصلي المثبت في ZIP2: 3033 نوعاً مفحوصاً و228 نوعاً ضمن المرشح اللفظي و4/4 مراسي معروفة. [التقرير المجمّع](../../gfxlab/evidence/20261112_gfx156_water_managed_census_safe.json). هذه نتائج ترشيح أسماء داخل metadata. تحتاج مطابقة PPtr بين MonoScript ومكوّن المشهد أو prefab لتحديد الأنواع التي تستخدمها اللعبة فعلاً.

**البناء المصحح ناجح.** [APK داخل الأثر 13911257611](https://github.com/alwansan/raf/actions/runs/43144304221/artifacts/13911257611). Unity نجح والتوقيع v2 والحزمة ARM64 IL2CPP وCRC اجتازت الفحص. بعد التنزيل أُعيد التحقق من SHA256 وCRC محلياً. [دليل الحزمة](../../gfxlab/evidence/20261112_gfx155_water_apk_safe.json). ثبّت APK على POCO F5 Pro وافتحه مرة وأرسل ZIP من `/storage/emulated/0/Download/Games/cl/test/g/`. يظل قبول Adreno ونتيجة الماء الأصلي معلقين.
