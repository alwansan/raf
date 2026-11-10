# GFX-MULTI-041 — اختبار AffineEmulated وتفسير NoPerspective على Adreno

**العميل:** GFX-LAB | **الفرع الوحيد للكتابة:** `experiment/android-graphics-rootcause`  
**نوع الاختبار:** أربعة شيدرات تشخيصية أصلية من إنشاء المختبر، لا شيدرات Raft Shader48.

## النتيجة التي بدأت منها هذه التجربة

من ZIP المستخدم الفعلي لتجربة GFX-MULTI-040: فُحصت 22 لقطة حالة (snapshot) و44 حدثاً، 0 أخطاء و0 تحذيرات. كان `Flat` ثابتاً، بينما صورة `Linear` وصورة `NoPerspective` متطابقتين **بايتاً ببايت** بالرغم من وجود 3 عينات ملوّنة وقراءات GPU ناجحة. جميع دورات التشغيل الأربع داخل السجل أكدت `DIAGNOSTIC_INTERPOLATION_MISMATCH`.

الحساب الهندسي المستقل بنفس إحداثيات المثلث وقيم `W=[0.55,1.0,2.7]` أكد:
- خطأ Linear GPU عن الإسقاط المنظوري الصحيح = **0.0010914** بالمتوسط.
- خطأ Linear GPU عن النتيجة affine = **0.1629662**.
- الاختلاف الرياضي الحقيقي بين المنظوري وغير المنظوري = **0.1630194**.

إذن تبديل `noperspective` في شيدر HLSL لم يغيّر مخرجات خط Unity GLES3 التي اختُبرت. **هذا لا يعني أن معالج Adreno معطوب** ولا يثبت وجود أو غياب امتداد OpenGL ES بعينه.

## لماذا نفصل بين الهاردوير والتحويل؟

مواصفة GLSL ES 3.20 الرسمية توفر `smooth` و`flat` كمؤهلات interpolation أساسية. `noperspective` ليس من المؤهلات الأساسية فيها، ويمكن توفيره عبر ملحقات مثل `GL_NV_shader_noperspective_interpolation` إذا كان متاحاً ومدعوماً في التطبيق/السائق.

- مواصفة Khronos: https://registry.khronos.org/OpenGL/specs/es/3.2/GLSL_ES_Specification_3.20.html
- امتداد Khronos: https://registry.khronos.org/webgl/extensions/NV_shader_noperspective_interpolation/

**لا نقرر أن الامتداد غير موجود على الهاتف اعتماداً على التشابه البصري؛ هذه التجربة تختبر نتيجة Unity، لا تسجّل قائمة الامتدادات الأصلية.**

## ما الجديد في GFX-MULTI-041؟

التطبيق الجديد يحتوي أربعة شيدرات، بدلاً من ثلاثة:

| الوضع | الوظيفة |
|---|---|
| Linear | تدرج منظور قياسي (المسار المرجعي الأول) |
| Flat | لون واحد من رأس المثلث (اختبار `nointerpolation`) |
| NoPerspective | HLSL `noperspective` كما في التجربة السابقة |
| AffineEmulated | **بديل رياضي جديد** للاستيفاء غير المنظوري باستخدام `smooth` المتاح |

خوارزمية AffineEmulated: يكتب Vertex Shader متغيرين `color × clipW` و`clipW`. عند قراءة Fragment Shader لهما بعد الاستيفاء المنظوري القياسي، تُحسب النسبة:

`affine = interpolated(color × clipW) / interpolated(clipW)`

بذلك تُلغى أوزان `1/clipW` ويعود تدرج اللون حسب أوزان الشاشة العادية. البرنامج يقارن **الأربعة** و3 نقاط داخل المثلث بمرجع CPU رياضي منفصل، ويخزن القياسات والصور PNG.

هذا أسلوب محتمل ضمن نقل shader مستقبلاً إذا غاب دعم `noperspective` الأصلي، **لكن نجاحه لا يستعيد بقية Shader48** (الخامات، الإضاءة، CB، حالات Pass، Rig، أو Pixel PC).

## خطوات اختبار الهاتف

1. افتح رابط Artifact الخاص بالتشغيل الناجح `GFX-MULTI-041` من GitHub Actions، واستخرج `GfxLab-AffineReference-GPUProbe.apk`.
2. ثبّته كبرنامج مستقل بالحزمة `com.alwansan.raft.graphicslab.affinereference`. يبقى تطبيق GFX-MULTI-040 القديم كما هو ولا تحتاج إلى إزالته.
3. افتح التطبيق بالوضع الأفقي. سيجري الاختبار تلقائياً، ثم يعرض أربع معاينات، والحالة النهائية وأخطاء المقارنة الرياضية.
4. في الحالة `DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH`: ثبت أن NoPerspective بقي عملياً مثل Linear **داخل هذه الترجمة Unity → GLES**، بينما نجح AffineEmulated في مطابقة CPU. في الحالة `DIAGNOSTIC_NATIVE_NOPERSPECTIVE_MATCHES_AFFINE`: المخرج الأصلي طابق Affine.
5. اضغط **EXPORT ALL LOGS ZIP** مرة واحدة. سيصدر ملفاً يحوي كل الحالات، والأخطاء مع Stacks، و**أربع صور GPU PNG** إلى:

`/storage/emulated/0/Download/Games/cl/test/g/`

6. أرسل ZIP في هذه الدردشة لقراءته. لا حاجة لاستخدام Termux أو نسخ Logcat يدوياً.

## حدود النتائج

- `DIAGNOSTIC_EMULATED_AFFINE_CPU_MISMATCH`: الفرضية التطبيقية أو توليد الشيدر بحاجة فحص، ولا يعني خطأ قطعيّاً في GPU.
- `INCONCLUSIVE_SHADER_OR_READBACK`: تعذّرت قراءة أحد الشيدرات الأربع بصورة مكتملة؛ راجع ZIP.
- نجاح الاختبار على Adreno لا يساوي مقارنة Windows PC ولا يعني `originalShaderRestored=true`.
- لا يُنشر ZIP الخاص أو صورة المستخدم داخل GitHub؛ فقط تقارير آمنة بأرقام جامعة.
- ملف GFX-MULTI-040 السابق يظل مرجعاً لا يُستبدل؛ الجديد يحمل معرف حزمة منفصلاً.
- العائق الأصلي المستقل G8 ما زال: `Shader48 Material property → DX11 t/s/b register/CB offset` لم يثبت في مصدر Unity المخزن، ولا توجد RDEF/Debug في 1275 DXBC أصلية مرتبطة.

## الملفات الفنية

- `gfxlab/unity/Assets/Shaders/GfxLabInterpolationAffineEmulated.shader`
- `gfxlab/unity/Assets/Scripts/GfxAffineReferenceProbe.cs`
- `gfxlab/unity/Assets/Editor/GfxAffineReferenceAndroidBuilder.cs`
- `.github/workflows/gfxlab-multi041-affine-reference-gpu-apk.yml`
- `gfxlab/tools/affine_reference_owner_zip_audit.py`
- `gfxlab/evidence/20261110_gfx040_owner_adreno_interpolation_safe.json`
- `memory/sessions/20261110-GFX-chat-affine-rootcause-15.md`

**حالة الجاهزية الفعلية:** يتحدد رابط تنزيل النسخة وتوقيعها فقط بعد نجاح GitHub Actions، ونتيجة GPU الفعلية تحتاج تشغيل المستخدم على الهاتف.
