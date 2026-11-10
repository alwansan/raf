# GFX-MULTI-026 — دليل اختبار الموديلات الستة وقنوات GPU على الهاتف

**GFX-LAB | المصدر ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 | هذا APK مختبر مستقل، وليس Raft الكاملة**

## شرط التسليم

لا يعتبر رابط APK مقبولاً حتى يثبت GitHub Actions: `BuildPipeline.BuildPlayer = Succeeded`، وجود APK واحد حقيقي، `arm64-v8a/libunity.so` و`AndroidManifest.xml` و`classes.dex`، `apksigner verify`، و`aapt badging` للحزمة `com.alwansan.raft.graphicslab.channels`، ثم SHA256 وحفظ Artifact. بعد ذلك يُحدَّث هذا الدليل برابط التشغيل والتحقق.

## تجربة الهاتف

- نزّل ملف الـArtifact من Actions وافتح ZIP واستخرج `GfxLab-Multi-Six-Channel-Probe.apk` وثبّته. هذا اسم حزمة **جديد** يمكن وضعه إلى جانب اختبار الستة السابق `com.alwansan.raft.graphicslab.multi`، وليس إلى جانب ملفات اللعبة الكاملة بالضرورة. لا تحتاج OBB.
- افتح التطبيق أفقياً، وجرّب القائمة الجانبية M00–M05. M03 مهم لأنه يحتوي على مادتين، وM01/M04 نموذجان `skinned` لكن وضعية العرض الحالية OBJ ثابتة وليست Animation أو Rig أصلياً.
- لكل موديل التقط صورة في وضع `SOURCE_PBR_STANDARD_APPROX` ثم اضغط `COPY LOG`. أرسل JSON مع الصورة واذكر إذا حصل تكسّر، ألوان مفقودة، Alpha غريب، أو مادة اختفت. هذا الوضع يستخدم Unity Standard تقريبي.
- اختبر أزرار لوحة الصور على اليمين: `BASECOLOR` ثم `NORMAL` ثم `METALLIC`. داخل كل دور بدّل `RGB/R/G/B/A`؛ الصورة الناتجة هي **ناتج أخذ عينة GPU من شيدر فحص مستقل**، وليست Renderer Shader48 الأصلي.
- بدّل `SOURCE COLORSPACE` و`FORCE LINEAR` لقياس الاختلاف في أخذ عينات sRGB/Linear. لا تستنتج تلقائياً أن النسخة الأفتح/الأغمق أكثر أصالة. أصلاً BaseColor وMetallic مخزنتان sRGB في المصدر وNormal Linear، وقد تختلف معاني القنوات الدقيقة بحسب Shader48.
- في M03 جرب `SURFACE 1/2` و`SURFACE 2/2` مع BaseColor/Normal/Metallic، وصورة/LOG لكل مادة. إن ظهرت `NO SOURCE TEXTURE / PROBE UNSUPPORTED` فدوّن الدور والموديل والقناة.
- قيّم شيدر التشخيص، الرسوم، الموديلات، الاختيار، الكاميرا، حالات Copy Log، FPS إن توفر خارجياً، والانهيارات. لا تدّعِ أن Original Shader48 شُغّل بسبب ظهور ألوان أو قنوات صحيحة.

## القيم التي سنراجعها في COPY LOG

`experiment=GFX-MULTI-026`، `modelId`، `materialMode`، `diagnosticProbeStatus=DIAGNOSTIC_SHADER_NOT_SOURCE_SHADER48`، `diagnosticRole`، `diagnosticChannel`، `diagnosticSampling`، `diagnosticTextureAssigned`، `diagnosticShaderSupported`، `diagnosticMaterialSurface`، `deviceModel`، `gfxDevice`، `gfxApi`، `colorSpace`، `errors`، `firstError`. القيم `originalShaderRestored=false` و`originalAnimationRestored=false` و`coloredPixelsAutomaticallyVerified=false` يجب ألا تُرفع إلى true بغير دليل.

## حدود قبول الأدلة

- source links/PNG in runner + signed Unity APK = مرحلة `UNITY_IMPORT_COMPILE` فقط.
- ظهور قنوات GPU على الجهاز مع لقطات أصلية وJSON = `GPU_EXPERIMENT` للمختبر وحده، وليس `ANDROID_GAME_PIXELS`.
- تكافؤ شيدر اللعبة الأصلي `Shader48` (2 SubShaders/7 Passes، keywords/CB/sampler bindings/render state) وRig/Animation وPC↔Android pixel parity لم يثبت.
- `RENDER-002/WATER-001` لا يغلقان بهذه التجربة.
