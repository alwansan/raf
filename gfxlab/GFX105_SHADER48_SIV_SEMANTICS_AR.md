# GFX105 — نتيجة تحويل NoPerspective النظامي لـShader48 الأصلي

**الدور:** GFX-LAB · **الفرع الوحيد المسموح بالكتابة:** `experiment/android-graphics-rootcause`  
**المصدر:** ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` · **التاريخ:** 11 نوفمبر 2026

## لماذا هذا الاختبار؟
أثبت هاتف POCO F5 Pro / Adreno 730 في GFX102 أن GLSL ES 310 و320 يشغّلان `noperspective` فعلًا في مثلث تشخيصي، بينما ES300 يرفض الكلمة. لكن لا يجوز افتراض أن كل `linear_noperspective` في DXBC الأصلي يخص varying عادي. لذلك فحص GFX103 ثم GFX104 ثم GFX105 المصادر الأصلية لجميع الأزواج الـ524 المرتبطة بـShader48.

## النتيجة المثبتة من GitHub Actions

| التحقق | تشغيل Actions المكتمل | النتيجة | اختبارات Python |
|---|---|---|---:|
| GFX103 — نوع مدخلات DXBC | [42945815709](https://github.com/alwansan/raf/actions/runs/42945815709) | SUCCESS | 17 |
| GFX104 — ترجمة DXBC إلى SPIR-V وGLSL ES310 | [42946470013](https://github.com/alwansan/raf/actions/runs/42946470013) | SUCCESS | 14 |
| GFX105 — هوية POSITION / FragCoord عبر المراحل | [42949456992](https://github.com/alwansan/raf/actions/runs/42949456992) | SUCCESS | 18 |

**الشاهد الرسمي:** SHA المصدر ثابت، وكل تشغيل قرأ ZIP2 داخل CI، أنتج تقرير عدديًا آمنًا فقط، ثم نفّذ خطوة حذف البيانات الخاصة بنجاح. فشل GFX105 الأول [42949270886](https://github.com/alwansan/raf/actions/runs/42949270886) بسبب تشدد غير صحيح في parser تجاه تعليمة DXBC ذات كلمة واحدة، وأُصلح وأُضيف اختبار رجوع قبل اعتماد التشغيل النهائي.

## النتائج الدقيقة

- 524 زوجًا أصليًا مطابقًا من Shader48 عبر 7 Passes.
- 472 برنامج Fragment مميزًا ضمن هذه الأزواج.
- **0** تصريحات `NoPerspective` في المداخل العادية `DCL_INPUT_PS`.
- **16** تصريحًا `linear_noperspective` في المداخل النظامية `DCL_INPUT_PS_SIV`، وكلها نظام `POSITION` (`D3D10_SB_NAME_POSITION=1`).
- تحققت صلاحية SPIR-V للحالات الـ16، وكانت المدخلات النظامية `BuiltIn FragCoord=15` في جميعها.
- تصدير GLSL ES310 نجح في الحالات الـ16، وكل ملف منها يشير إلى `gl_FragCoord`.
- صفر حالات نظامية ذات اسم آخر، وصفر فشل في تقرير GFX105 النهائي.

**التفسير المعتمد:** تحققنا على مستوى بنية التعليمات ومعرّفات الدلالة أن المدخلات الأصلية `SV_POSITION` تُعامل كمدخل نظامي `FragCoord`، لا كـ`noperspective varying` اعتيادي يربط Vertex وFragment. لهذا لا يجوز إعادة كتابة كل شيدرات Shader48 أو إجبارها على استعمال `GL_NV_shader_noperspective_interpolation` دون ضرورة أثبتها المصدر.

## ما الذي لم يثبت؟
هذه النتائج ليست إثباتًا لتطابق القيم الرقمية لكل fragment. ما زال يلزم فحص فروق إحداثيات نافذة DirectX مقابل GLES، واتجاه Y، وعمق Z، وW، وحالات RenderState، والـMaterial والسامبلرات وConstantBuffer، والـrig والأنيميشن، ومرجع البكسلات PC↔Android. البوابات الأخيرة تبقى مفتوحة.

**العلامات الملزمة:** `originalShaderRestored=false`، `originalAnimationRestored=false`، `pcAdrenoPixelParityVerified=false`، `phase_closed=false`.

## التنفيذ القادم
أولوية العمل هي الانتقال من تعداد تعليمات الاستيفاء إلى تحقيق GPU لـShader48 الأصلي: مطابقة Material→sampler/CB، وفك Normal حسب المصدر، وبناء Mesh/Rig مفهرس مع skin weights/bindposes، ثم مرجع لقطة PC بنفس ظروف الهاتف. لا تحتاج هذه النتيجة إلى إعادة اختبار GFX102 أو تغيير جميع إصدارات GLSL إلى 320.

المراجع الفنية:
- [DirectX Tokenized Program Format — Microsoft](https://github.com/microsoft/DirectX-Headers/blob/main/include/directx/D3D12TokenizedProgramFormat.hpp)
- [SPIR-V BuiltIn enum — Khronos SPIRV-Headers](https://github.com/KhronosGroup/SPIRV-Headers/blob/main/include/spirv/unified1/spirv.hpp)
