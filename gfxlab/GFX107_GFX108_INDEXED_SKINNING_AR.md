# GFX-LAB — نتيجة الاستعادة المصدرية لهياكل العظام GFX107–GFX108

**التاريخ:** 11 نوفمبر 2026  
**الفرع:** `experiment/android-graphics-rootcause`  
**مصدر اللعبة:** ZIP2 عند Commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

## ماذا تحقق فعليًا؟

| التجربة | التشغيل المؤكد | النتيجة | الاختبارات |
|---|---|---|---:|
| GFX106 — عظام المصدر/Transform | [42950536938](https://github.com/alwansan/raf/actions/runs/42950536938) | SUCCESS | 10 |
| GFX107 — مقارنة `bone.world × bindpose` | [42951739739](https://github.com/alwansan/raf/actions/runs/42951739739) | SUCCESS | 12 |
| GFX108 — Linear Blend Skinning المفهرس CPU | [42953322197](https://github.com/alwansan/raf/actions/runs/42953322197) | SUCCESS | 18 |

**GFX106:** عثرنا على 213/213 عظمة أصلية ذات Transform وبالعدد المطابق من bindposes. ترتبط 100 عظمة M01 و100 عظمة M04 و8 عظام M02 بالكامل بـRootBone المختار؛ أما M00 وM05 فعظامهما موجودة، لكن بعضها خارج سلالة RootBone المحدد.

**GFX107:** نجح حساب المصفوفات لجميع العظام الأصلية الـ213. قارنا حاصل `bone.world × bindpose` مع ناتج العظمة الأولى للـMesh نفسه عند سماحية `1e-4`. تطابقت 161/213؛ في M01 وM04 توجد 26 عظمة مختلفة من أصل100 بكل منهما. هذه علامة على اختلاف وضعية المصدر عن وضعية الربط الممكنة، ولا تثبت تلف Mesh أو Rig.

**GFX108:** استخدمنا `UnityPy.helpers.MeshHelper.MeshHandler.process()` لفك المواضع والأوزان والفهارس الأصلية بنفس ترتيب الرؤوس من `VertexData`، **دون OBJ welding أو قلب محور X الخاص بالمُصدّر**. الحساب الرياضي `Σ(weight_i × (boneWorld_i × bindPose_i) × originalVertex)` نجح لكل الرؤوس الأصلية الـ14,033 في خمسة موديلات Skinned. لا يوجد رأس عُوِّض ببيانات افتراضية.

| الموديل | العظام | الرؤوس الأصلية التي حُسبت | عرض مؤثرات العظام في المصدر | رؤوس تختلف عن مرجع العظمة الأولى، سماحية 1e-4 |
|---|---:|---:|---:|---:|
| M00 | 3 | 375 | 2 | 0 |
| M01 | 100 | 5,095 | 4 | 695 |
| M02 | 8 | 1,666 | 4 | 0 |
| M03 | 0 | غير Skinned | — | — |
| M04 | 100 | 2,445 | 4 | 679 |
| M05 | 2 | 4,452 | 2 | 0 |
| **المجموع** | **213** | **14,033** | 2 أو 4 | **1,374** |

تم التحقق من صيغة مؤثرين لكل رأس في M00 وM05 عبر التقرير الآمن الذي سجل فقط اتساع قنوات الوزن والفهرس؛ ثم صُفّرت الخانتان الإضافيتان (وزن صفر)، فلا تُصنع مساهمة عظمة غير موجودة. صيغة أربعة مؤثرات بقيت في M01/M02/M04. يرفض الكود أي طول غير مثبت أو اختلاف طول الأوزان والفهارس.

## الفرق بين «الحساب» و«الاستعادة الكاملة»

- **المثبت:** وجود source bone links، وصلاحية المصفوفات، وإمكانية حساب وضعية CPU الحالية على جميع الرؤوس المفهرسة دون فقد أو دمج.
- **غير المثبت:** أن هذه الوضعية هي Bind Pose الأصلية أو الوضعية نفسها من مشهد PC، وأن Animator/Animation Clips أو GPU Skinning أو Shader48 الحقيقي يشتغل في Android.
- **غير المثبت:** تطابق مساحة RenderTarget والمصفوفات بين DirectX وGLSL، أو مواد Shader48 وNormal/Texture/CB وحالات الرسم أو لقطات PC↔Adreno.

الأولوية التالية هي إنشاء **اختبار GPU لهياكل مصدرية أصلية على Android** مع تسجيل نفس النموذج ووضعية العظام/الكاميرا/المصفوفات وربط GPU بقيم CPU، ثم استكمال باقي بوابات Shader48. لا تدمج الإصلاح في الفرع المنتج T1–T5 قبل دليل هاتف موثوق. لن ننتقل للماء أو النار في مختبر GFX-LAB حتى تنتهي هذه المرحلة.

**العلامات الصحيحة:** `originalShaderRestored=false`، `originalAnimationRestored=false`، `original_rig_restored=false`، `phase_closed=false`.

## الأدلة والمصادر

- `gfxlab/evidence/20261111_gfx106_original_rig_hierarchy_safe.json`
- `gfxlab/evidence/20261111_gfx107_original_bindpose_cpu_safe.json`
- `gfxlab/evidence/20261111_gfx108_original_indexed_cpu_skin_safe.json`
- **الوصفة المستخدمة:** `gfxlab/tools/gfx107_source_bindpose_math.py`، `gfxlab/tools/gfx108_indexed_skinning_cpu.py`، `gfxlab/tools/gfx108_original_indexed_skin_cpu.py`.
- خرج CI العام لا يحتوي بيانات العظام أو المصفوفات أو Mesh الأصلية أو PPtrs أو صور المالك؛ سُجّل نجاح تنظيف ملفات المصدر الخاصة في التشغيل النهائي.
