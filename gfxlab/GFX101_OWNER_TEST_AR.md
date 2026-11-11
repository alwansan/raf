# GFX-MULTI-101 — دليل اختبار Adreno على الهاتف

**الحالة:** الملفات البرمجية موجودة على فرع `experiment/android-graphics-rootcause`. لا تنزّل APK إلا بعد ظهور `SUCCESS` وملف Artifact المؤكد في [GitHub Actions](https://github.com/alwansan/raf/actions/workflows/gfxlab-multi101-gles-native-interpolation-apk.yml). هذا المستند لا يزعم أن البناء اكتمل.

## ماذا يختبر؟
- التطبيق المستقل `com.alwansan.gfx101`، ولا يستبدل Raft أو GFX098، ولا يحتاج OBB أو إنترنت.
- يحاول إنشاء سياق GLES3 على الهاتف، ويسجل هوية المُعرّف ونسخة GLES وGLSL. يقرأ قائمة الامتدادات الفعلية من `GLES30.glGetStringi`، وينتقي `GL_NV_shader_noperspective_interpolation`.
- يشغّل GPU على مثلث مصطنع بثلاث قيم W مختلفة: `Smooth` (منظوري)، `Flat`، و`AffineEmulated` (محاكاة لا منظورية). يجرب `NativeNoPerspective` **فقط إذا أعلن تعريف الهاتف الامتداد الاختياري**.
- لكل حالة متاحة: لقطة GPU RGBA8 بحجم 256×256 وSHA256، وثلاث نقاط GPU مع حسابات رياضية CPU مستقلة. لن يعتبر المستشعر `NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE` نجاحًا دون نجاح الضوابط الثلاثة والامتداد والقراءات.

## الخطوات على POCO F5 Pro
1. بعد التأكد من نجاح CI، افتح Artifact الخاص به وحمّل `GFX101-GLES-Native-Qualifier-Probe.apk`، وثبت التطبيق باعتباره حزمة مستقلة.
2. افتح GFX101 واتركه في الواجهة إلى أن تظهر نتيجة الاختبار وعبارة حفظ السجلات. لا توجد شاشة ألعاب أو موديلات أصلية.
3. إذا تعثر الحفظ التلقائي، اضغط `EXPORT ALL LOGS ZIP`. يُستخدم Android MediaStore دون إذن تخزين شامل.
4. من المسار `/storage/emulated/0/Download/Games/cl/test/g/` أرسل فقط آخر ملف `GFX101-ALL-TEST-LOGS-*.zip`. لا حاجة إلى نسخ الأخطاء أو الصور يدويًا.

## تفسير النتائج
- `NATIVE_EXTENSION_NOT_ADVERTISED`: لم يعلن GLES عن امتداد NV؛ هذه **ليست** نتيجة فشل Adreno، ولا يمكن اختبار الاستيفاء الأصلي بهذه الواجهة.
- `NATIVE_EXTENSION_ADVERTISED_BUT_SHADER_COMPILE_OR_LINK_FAILED`: توجد إشارة امتداد، لكن لم ينجح برنامج GLSL؛ السجلات توضح السبب.
- `NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE`: الاختبار المصطنع الأصلي على الهاتف تطابق مع مرجع CPU. **لا يعني استعادة Shader48** أو مقارنة PC.
- `NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH`: النسخة المترجمة تتصرف كـSmooth رغم ادعاء الامتداد.
- `CONTROL_FAILURE_OR_INCONCLUSIVE`: لا يمكن الاستنتاج عن `NoPerspective` لأن اختبارًا مرجعيًا فشل.
- `NATIVE_GPU_UNEXPECTED_INTERPOLATION`: توجد نتائج فعلية غير مطابقة، تحتاج تحليلًا.

المفتاح دائماً: `originalShaderRestored=false`، `originalAnimationRestored=false`، `phase_closed=false`.

## بعد إرسال ZIP
تُراجع النتائج بالمدقّق الآمن `python3 -m gfxlab.tools.gfx101_owner_zip_audit /path/to/GFX101-ALL-TEST-LOGS-*.zip`. لا يرفع المدقّق الصور أو السجلات إلى المستودع. إذا لم يكن امتداد GLES متوفرًا، فالمسار التالي المقترح هو اختبار Vulkan SPIR-V `NoPerspective` منفصل، لا إعادة تسمية محاكاة GLES على أنها دعم أصلي.
