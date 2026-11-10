# GFX-LAB — قرار نقل DX11 `noperspective` إلى GLES3 أو Vulkan (GFX-MULTI-042)

**الحالة:** مبني على اختبار فعلي على جهاز Adreno 730؛ صالح كمسار مرجعي تشخيصي **للاستيفاء فقط**، وليس استعادة Shader48 كاملاً.

## الدليل الموثّق من الهاتف

- GFX-MULTI-041 قدّم **أربعة** شيدرات اصطناعية جديدة تماماً، لا تتضمن Shader48 أو موارد Raft.
- سجل الهاتف الحقيقي: GLES3، 28 حدثاً، 14 snapshot، وأربع قراءات GPU وصور PNG بحجم 256×256. 0 أخطاء Unity، 0 تحذيرات، 0 رسائل مفقودة.
- `Flat` أعطى أزرق ثابتاً. `Linear` و`NoPerspective` كانا **متطابقين على مستوى صورة RGBA كاملة**، وليس ثلاث نقاط فقط.
- تحليل ثانٍ مستقل للصور كلها مع تصحيح ترتيب صفوف PNG (أعلى→أسفل) إلى إحداثيات OpenGL (أسفل→أعلى)، واستخدام مراكز البكسلات وإحداثيات المثلث الأصلية و`W=[0.55,1,2.7]`. داخل منطقة ذات وزن barycentric لكل رأس أكبر من 0.02: **20,212 بكسلاً**.
  - خطأ GPU Linear عن المرجع المنظوري الحسابي = **0.000981208** (متوسط `abs(RGB)`).
  - خطأ GPU AffineEmulated عن المرجع `affine` = **0.000983381**.
  - خطأ GPU AffineEmulated عن مرجع `perspective` غير الصحيح = **0.143924693**.
  - كل بكسلات `Flat` الداخلية البالغ عددها 20,212 زرقاء `(0,0,255)`.
- التقارير المجمّعة الآمنة:
  - `gfxlab/evidence/20261110_gfx040_owner_adreno_interpolation_safe.json`
  - `gfxlab/evidence/20261110_gfx042_owner_affine_fullframe_safe_counts.json`
- تحقق مستقل من أداة قراءة PNG ذات حدود صارمة وCRC وفك `RGBA8` عبر [GFX-MULTI-042 CI42825803381](https://github.com/alwansan/raf/actions/runs/42825803381)، **SUCCESS /272 اختبارات Python**. استخدم CI بيانات اصطناعية، ولم يُحمّل صور المستخدم الخاصة.
- ZIP المستخدم الأصلي بقي خاصاً في المحادثة، ولم تُنشر الصور أو سجلات الهاتف أو معلوماته الشخصية على GitHub.

## ماذا ثبت، وماذا لم يثبت؟

**ثبت عملياً في هذا المسار:**
1. `Linear` المنظوري يتفق مع مرجع CPU على كامل منطقة المثلث الداخلية.
2. محاولة HLSL `noperspective` داخل خط Unity 2021.3 / OpenGLES3 أعطت **نفس** نتيجة `Linear`؛ لم تحافظ على المطلوب في هذه الحالة.
3. بديل `AffineEmulated` باستخدام `(attribute * clipW)` و`clipW` كقنوات ذات interpolator منظوري قياسي، ثم القسمة في Fragment، أعطى اللون غير المنظوري المتوقع كمياً على Adreno.
4. `nointerpolation` / flat أدى لوناً ثابتاً في اختبارنا.

**لم يثبت:**
- وجود أو غياب `GL_NV_shader_noperspective_interpolation` على برنامج تشغيل الجهاز؛ لم تُسجّل لائحة امتدادات GL أو يُجرَ بناء raw-GL مباشر.
- أن Unity أسقط `noperspective` في مرحلة واحدة محددة (HLSL translation أو compiler أو runtime): الاستنتاج عن *المسار الكامل* وليس تحديد المتسبب.
- استيفاء متجهات UV في Shader48 الأصلي، أو `ddx/ddy`، أو إعدادات mip/LOD، أو `centroid/sample`، أو الأداء والإضاءة والقص والظلال والإزاحة. اختبارنا يستخدم `float3 RGB` داخل مثلث واحد فقط.
- الأصالة الحرفية لـ Shader48 أو روابط `Material properties → t/s/CB registers`. المصدر يحتوي 1,275 DXBC مرتبطة بدون `RDEF` أو Debug reflection؛ G7–G12 تبقى مفتوحة.

## مسار التنفيذ الموصى به عند النقل

### GLES3 — نسخة متوافقة باستخدام حساب بديل

مبدأ رياضي للاستيفاء الخطي حسب الشاشة، لصفة (a_i) لكل رأس:

```hlsl
// Vertex, template only — original shader not provided
float4 clipPos = ComputeClipPosition(input);
output.position = clipPos;
output.affineNumerator = authoredAttribute * clipPos.w;
output.affineDenominator = clipPos.w;

// Fragment (both inputs use ordinary perspective-correct interpolation)
float3 affineAttribute = input.affineNumerator / input.affineDenominator;
```

البرهان: الاستيفاء المنظوري لـ `a*w` يساوي `Σ λ_i a_i / Σ(λ_i/w_i)`، والاستيفاء المنظوري لـ `w` يساوي `1/Σ(λ_i/w_i)`، وقسمة الأول على الثاني تعيد `Σ λ_i a_i` (الاستيفاء غير المنظوري). يستخدم `λ_i` الأوزان حسب الشاشة.

**قيود لا يجوز إخفاؤها:** المعادلة تحتاج تحديد قيم `clipW` الفعلية والمحافظة عليها في مسار VS→PS، وتمثيل دقيق عند القص أو قرب `W=0`، وقد تضيف varying ثانياً وتكلفة قسمة. لا تُفعّل تعويض `epsilon` تخمينياً على أي مصدر لعبة قبل اختبار الحدود. `ddx/ddy` ومرشحات texture/mip والـMSAA يجب فحصها على GPU بشكل مستقل؛ لا نعدّ نجاح اللون وحده كافياً.

يمكن أيضاً إجراء تحقيق مباشر في الامتداد `GL_NV_shader_noperspective_interpolation` عبر قائمة امتدادات الجهاز والـshader المترجم، **لكن لا نفترض توفره**.

### Vulkan — الحفاظ على `NoPerspective` في SPIR-V

في Vulkan/SPIR-V، `OpDecorate … NoPerspective` هو توصيف رسمي للاستيفاء الخطي غير المنظوري على مدخلات ومخرجات المراحل. Microsoft DXC توثّق مطابقة HLSL `noperspective` إلى SPIR-V `NoPerspective`، و`nointerpolation` إلى `Flat`.

**المصادر الرسمية:**
- Khronos GLSL ES 3.20 §4.5: https://registry.khronos.org/OpenGL/specs/es/3.2/GLSL_ES_Specification_3.20.html
- Khronos SPIR-V `NoPerspective` Decoration (13): https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html
- Microsoft DXC mapping: https://github.com/microsoft/DirectXShaderCompiler/blob/main/docs/SPIR-V.rst

**بروتوكول الفحص القادم عند وجود مصدر مترجم أصيل:**
1. تحديد البرامج الأصلية DX11 المرتبطة بالـPass/keyword/tier؛ لا تستخدم أصناف GLES غير المرتبطة من جدول مصدر `D3D11`.
2. التحقق من وجود `NoPerspective` في **متغير Input/Output المقصود** ضمن SPIR-V؛ لا تخترع أصالة الاسم أو رقم السجل.
3. التأكد من صلاحية SPIR-V وواجهات VS/PS وسياق Vulkan الفعلي.
4. تشغيل ناتج أصلي على الهاتف ومقارنته بمرجع Windows PC وصور الاختبار قبل الحكم بالتطابق.
5. في حال فقدت مرحلة التحويل `NoPerspective`، يكون البديل `AffineEmulated` مرجعاً مستقلاً **مع تحقق جديد للشيدر المعني**، لا استبدالاً تلقائياً لكل shaders.

**ملاحظة مصدر:** DXC يترجم **مصدر HLSL** إلى SPIR-V عند توافره؛ وجود DXBC الأصلي وحده لا يعني إمكانية تمريره إلى DXC أو استنتاج أسماء مواد اللعبة.

## وضع المرحلة الأولى

دليل الاستيفاء التشخيصي قوي ومكتمل لهذه الحالة ذات الأربع شذرات، ولا يوجد سبب لإعادة هذه التجربة بلا مدخل جديد. الأولوية الفعلية الآن ليست إنشاء المزيد من نسخ عرض المثلث، بل استعادة مصدر أصيل أو دليل مستقل لربط Shader48 Material/CB وPassStates ثم قياس النتيجة في مشهد أصلي.

**الحالة: `originalShaderRestored=false`.**
