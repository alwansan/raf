# GFX102 — اختبار تصحيح NoPerspective على Adreno 730

**GFX-LAB · 11 نوفمبر 2026 · تجربة تشخيصية مستقلة فقط**

المستودع: [alwansan/raf](https://github.com/alwansan/raf/tree/experiment/android-graphics-rootcause)

## سبب الاختبار الجديد
حللت في هذه الدورة ملفين من المالك:
- ZIP SHA256: `8b788636517fc672416ccd76d5a32baea9da627fa8c7b2a261c04ba81556af6c`.
- ZIP SHA256: `350a42d8494918c16e07e3c73dde1ef9622f8bc2cec813c930b9290115d512c4`.

ملفات ZIP سليمة، والتجربتان متطابقتان في `summary.json` و`events.jsonl` (17 حدثًا لكل واحدة). جهاز المالك Adreno 730 أعلن فعلاً امتداد `GL_NV_shader_noperspective_interpolation` ضمن 104 امتدادات على GLES 3.2/GLSL ES 3.20. نُفّذت قراءات GPU الثلاثة `Smooth` و`Flat` و`AffineEmulated` بنجاح. فشل كل من Vertex وFragment ضمن native `#version 300 es` برسالة `'noperspective' : Reserved word.` دون أي `glGetError` عند التجميع. هذه **مشكلة تجميع برنامج GLSL 300 تحت شرط امتداد معلن**؛ لا تثبت فشل عتاد Adreno ولا تقنعنا بأن اللعبة قد استعيدت.

دليل Khronos الرسمي للامتداد: https://registry.khronos.org/OpenGL/extensions/NV/NV_shader_noperspective_interpolation.txt

شاهد سابق على معالجة خاصة Qualcomm باستخدام GLSL ES 3.20 في Skia:
https://skia.googlesource.com/skia.git/+/d782fd600e2c44d09e751588189a54f1d3612484/src/gpu/ganesh/gl/GrGLCaps.cpp

## ما الذي يختبره APK GFX102؟
- حزمة منفصلة: `com.alwansan.gfx102`، لا تزيل GFX101.
- برامج GPU اصطناعية `Smooth` و`Flat` و`AffineEmulated` مع المقارنة الرياضية CPU.
- برامج `NativeNoPerspectiveES300`، `NativeNoPerspectiveES310` و`NativeNoPerspectiveES320`، في كل واحد `#extension GL_NV_shader_noperspective_interpolation : require` لكل من Vertex/Fragment.
- كل محاولة لها سجل تجميع/ربط منفصل ومعرف إصدار GLSL. أي نجاح تجميع لا يكفي؛ يجب مقاربة اللون غير المنظوري الصحيح في `glReadPixels`.
- جميع الحالات التي نجحت في الرسم تحفظ PNG وSHA256 وقراءات نقاط GPU مع المتوسط الرياضي. يتيح التطبيق `EXPORT ALL LOGS ZIP` أيضًا عند تعثر الحفظ التلقائي.

## البناء والتجربة

**لا يعتبر APK جاهزًا لمجرد وجود الكود؛ تحقق أولاً من نجاح GitHub Actions وتوقيع الحزمة.**

رابط Workflow الجديد:

https://github.com/alwansan/raf/actions/workflows/gfxlab-multi102-qualifier-version-matrix-apk.yml

إذا كانت النتيجة `SUCCESS` وفيها Artifact باسم `GFX102-GLES-Native-Qualifier-Probe-APK` يحوي APK و`gfx102-safe-delivery.json`، يمكن تنزيل APK الموقّع والتحقق من اسم الحزمة وبصمة SHA256 المكتوبة في الملف، ثم تثبيته على POCO F5 Pro.

1. افتح GFX102؛ لا يحتاج OBB أو اتصال إنترنت ولا أصل لعبة Raft.
2. اتركه في الواجهة حتى ينهي الاختبارات ويظهر مسار حفظ السجل.
3. إذا لم تُحفظ السجلات تلقائيًا، اضغط `EXPORT ALL LOGS ZIP`.
4. أرسل ملف `GFX102-ALL-TEST-LOGS-*.zip` الناتج من `/storage/emulated/0/Download/Games/cl/test/g/`.

## التدقيق وقرار النتيجة
يشغّل المختبر أداة `python3 -m gfxlab.tools.gfx102_owner_zip_audit <file.zip>`، وتتحقق من CRC الداخلي للصور وملفات ZIP وبصمات SHA ومن حالة المحاولات الثلاث.

- `NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE`: تم إثبات الاستيفاء غير المنظوري الأصلي **لهذا المثلث الاصطناعي على GPU فقط**.
- `NATIVE_EXTENSION_ADVERTISED_BUT_ALL_GLSL_VERSIONS_FAILED`: حتى 3.20 رُفض. سنحتاج توثيق خطأ 320 والتحول لمسار Vulkan أو محاكاة GLES المحددة.
- `NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH`: تم تجميع برنامج لكن يخرج استيفاء Smooth، فلا تعتمد النتيجة على أنه أصلية.
- `CONTROL_FAILURE_OR_INCONCLUSIVE`: أحد الضوابط فشل؛ لا يصح إصدار حكم على native.

**المرحلة الأولى ليست مكتملة**، حتى مع نجاح GFX102: يجب إثبات Shader48 الحقيقي وMaterial/CB/Normal وRig والمرجع البكسلي PC↔الهاتف.

`originalShaderRestored=false`، `originalAnimationRestored=false`، `phase_closed=false`.
