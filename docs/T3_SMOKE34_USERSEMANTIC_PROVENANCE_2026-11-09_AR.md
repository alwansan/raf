# T3 — تحقق UserSemantic ومواضع SPIR-V الأصلية لشيدر الدخان

**التاريخ:** 9 نوفمبر 2026. **المسؤول:** T3. **RENDER-002: OPEN / NOT_READY 0/3.**

## الخلفية
التجربة الأصلية [CI42691211652](https://github.com/alwansan/raf/actions/runs/42691211652) أثبتت 7 روابط بين Semantic+Index لمخرجات Vertex ومدخلات Fragment من DXBC الأصلي. [CI42692895633](https://github.com/alwansan/raf/actions/runs/42692895633) أثبتت 28 قناة معلنة، منها 22 قناة مستخدمة بالقراءة و6 قنوات معلنة غير مستخدمة. أما [CI42689814110](https://github.com/alwansan/raf/actions/runs/42689814110) فلم تجد أي تطابق في أسماء متغيرات `spirv-cross` بين المصدر والدائري؛ الأسماء غير صالحة كدليل مراسلة دلالي.

## الفرضية وطريقة التحقق
قد يحمل SPIR-V زخارف `OpDecorateStringGOOGLE` ذات `HlslSemanticGOOGLE` (قيمتها 5635) المرتبطة مباشرة بمُدخلات مرحلة Fragment إذا أصدرها المترجم. هذه المعلومة تختلف عن `OpName`، وقد تكون مدخلًا موثقًا لتجربة ربط الدلالات. أما تشابه أرقام سجلات DXBC و`Location` SPIR-V فلا يمثل إثباتًا مستقلًا للمعنى.

أضفنا محللًا ثنائيًا محددًا وآمنًا `scripts/t3_smoke34_spirv_usersemantic_annotations.py` ومسبار `scripts/t3_original_smoke34_usersemantic_probe.py`، وربطناهما حصريًا بالشيدر الأصلي الحقيقي المرتبط بـ17 Smoke-name ParticleSystemRenderers/34 خانة Material وبزوجَي Fragment ذوي keyword مطابق، باستخدام ZIP2 الثابت SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`، 6 مشاهد و4 أصحاب Shader. كل البرامج والتواقيع والأسماء ومسارات الأصول الحقيقية داخل runner الخاص فقط.

مرجع صيغة الزخارف: [Khronos SPV_GOOGLE_hlsl_functionality1](https://github.khronos.org/SPIRV-Registry/extensions/GOOGLE/SPV_GOOGLE_hlsl_functionality1.html).

## نتيجة الأصل الفعلي
[GitHub Actions 42696526193](https://github.com/alwansan/raf/actions/runs/42696526193): **SUCCESS**، 57/57 فحصًا (12 opcode و8 مشغل و9 gate جدولة و21 مصدر DXBC و7 جرد Shader). جرت أيضًا إعادة توثيق ملفات SHA الأصلية وتحويل مرحلتي Fragment واستخراج SPIR-V والدائري فعليًا.

| القياس | SPIR-V الأصلي | HLSL roundtrip SPIR-V |
|---|---:|---:|
| متغيرات Fragment Input المعلنة (إجمالي الزوجين) | 7 | 7 |
| قنوات Fragment Input المعلنة | 28 | 28 |
| وجود امتداد SPV_GOOGLE_hlsl_functionality1 | 0 | 0 |
| متغيرات مرتبطة بزخرفة HlslSemantic صريحة | **0** | **0** |
| من أصل 7 دلالات DXBC، المعينة بزخارف صريحة | **0** | **0** |
| مواضع SPIR-V المتساوية **رقميًا** مع سجلات DXBC | **7/7** | **5/7** |
| تطابق العدد + عائلة النوع + عرض المتجه عند نفس الرقم | **7/7** | **5/7** |

**التفسير:** الترجمة المباشرة احتفظت بتساوي رقم السجل الأصلي ورقم `Location` لجميع مدخلات Fragment السبعة، وإعادة التحويل غيّرت توافق اثنين. لكن لا توجد زخارف `HlslSemantic` فعلية تربط أسماء Semantic الأصلية بمُتغيرات SPIR-V، ولا يجوز قبول توافق الأرقام كـprovenance، حتى إن تساوت جميع عائلات الأنواع والعروض.

## حدود النتيجة والتسليم
كان التشغيل الأول [CI42696430679](https://github.com/alwansan/raf/actions/runs/42696430679) قد فشل بسبب إعادة تشغيل اختبار اصطناعي على المجلد المؤقت ذاته؛ أصلحنا الـfixture فقط، ثم نجحت التجربة الأصلية. artifact الآمن [13710355183](https://github.com/alwansan/raf/actions/runs/42696526193/artifacts/13710355183) صالح حتى 16 نوفمبر 2026 20:49 UTC ويحتوي عدادات فقط.

لم يُثبت هذا الفحص خريطة `DXBC SemanticName+Index+Register/Mask → SPIR-V Location+Component` بالاعتماد على تدفق التعليمات، ولم يُستعد ShaderLab، ولم تُشغّل لقطة Unity أو هاتف Adreno، ولم يُثبَت سبب الدخان المربّع أو إصلاحه. لم يُعدّل أي مشروع لعبة/APK/OBB أو ملفات الآخرين. مسار الخطوة التالية: تحقق instruction-provenance من مترجم vkd3d أو أدوات تحليل DXBC/SPIR-V مستقلة قبل اعتماد ربط semantic→Location أو إدخاله إلى mini Unity lab.
