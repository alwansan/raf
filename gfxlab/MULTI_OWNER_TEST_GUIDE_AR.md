# GFX-MULTI-003 — دليل تجربة ستة مجسمات على هاتف Android

**الحزمة المستقلة (إذا أثبت GitHub Actions نجاح بناء APK والتوقيع):** `com.alwansan.raft.graphicslab.multi`. لا تحذف مختبر المقص `com.alwansan.raft.graphicslab.shears` أو لعبة Raft الكاملة. Unity 2021.3.45f2، IL2CPP ARM64، OpenGLES3، Linear.

## واجهة التطبيق
- القائمة الجانبية تحتوي **M00–M05**: **M00 Shears** (المقص الذي قبلته بصرياً)، M01 person/100 bones، M02 tool/skinned/8 bones، M03 multi_material/static بمادتين، M04 complex_skinned_unidentified/100 bones، M05 generic/skinned/2 bones. **جميع نماذج Skinned تُعرض كـOBJ ثابت بلا rig أو Animation**. هذه تسميات فئات مُثبتة من الـGameObject/Mesh في المصدر وليست تأكيداً لأسماء العناصر داخل اللعبة؛ تحديد M01 بأنه لاعب كامل يتطلب مشهداً/ريغاً موثقاً.
- زر `NEXT MATERIAL` يبدّل بالتتابع: `WHITE_LIT`، `WHITE_UNLIT`، `SOURCE_ALBEDO_STANDARD`، `SOURCE_PBR_STANDARD_APPROX`.
- التدوير بإصبع، التقريب بإصبعين، `RESET VIEW` لإعادة الزاوية، `SPIN` للدوران، `SHOW HELPERS` لإظهار قاعدة العرض (مخفية افتراضياً). الصور الأصلية ليست منشورة منفردة، بل موجودة داخل APK المختبر فقط.
- `COPY LOG` ينسخ JSON للموديل والوضع المختار واسم GPU/API وعداد أخطاء Unity.
- **كل موديل من المصدر الأصلي ومربوط بصور أصلية. الشيدرات المعروضة Unity Standard diagnostic وليست بالضرورة Raft Shader48 الأصلي أو جميع Passes والـkeywords.** `originalShaderRestored=false` و`originalAnimationRestored=false` متوقعان، وليس فشل جهاز.

## اختبار بصري سريع (يتكرر للموديلات الستة)
1. افتح M00 في وضع `SOURCE_PBR_STANDARD_APPROX`، وتأكد أنه نفس المقص الملون v0.2 حتى نصادق عدم وجود تراجع.
2. بدّل M01–M05، وفحص كل مجسم من جميع الزوايا؛ هل هو مجسم كامل أم جزء من شخصية/منشأة؟ هل تظهر أوجه مفقودة أو حواف مقلوبة أو خامات في موضع خاطئ؟
3. قارن `SOURCE_ALBEDO_STANDARD` مع `SOURCE_PBR_STANDARD_APPROX`. لو ظهرت ألوان صحيحة في Albedo وخلل في PBR، فهذا يرجّح ربط Normal/Metallic/Shader fallback وليس فقد الألوان.
4. خصّص اهتماماً لـM01 وM04 (مصدر Skinned فيه 100 عظمة، لكن العرض OBJ ثابت) وM03 (مادتان و6 صور أصلية). لا نستنتج صحة حركة العظام من ثبات مجسم فقط.
5. في كل موديل اضغط COPY LOG وأرسل JSON وصورة من `SOURCE_PBR_STANDARD_APPROX`؛ وإذا وجدت مشكلة أرسل لقطة Albedo من نفس الزاوية. يفضّل 6 صور + 6 سجلات صغيرة.

## حقول التقرير المرتقبة
`modelId`, `category`, `originalGeometryKind`, `materialMode`, `deviceModel`, `gfxApi`, `colorSpace`, `sourceGeometryVerified`, `sourceTextureChainVerified`, `originalShaderRestored`, `originalAnimationRestored`, `availableModels`, `sourceBones`, `sourceMaterials`, `sourceTextures`, `vertices`, `triangles`, `errors`, `firstError`.

## مسار قرار العيوب
- أبيض في كل الأوضاع: تحقق من مرجع model/Renderer وUnity material، وليس اتهام Adreno مباشرة.
- ألوان Albedo صحيحة لكن PBR خاطئة: افصل normal-map packing (DXT5nm), MetallicGlossMap channels, Linear/sRGB وsampler/UV. لا تغير المادّة الأصلية عشوائياً.
- قطعة من نموذج أو وضعية غير طبيعية مع M01: هذا متوقع ممكن من OBJ ثابت؛ استعادة 100 bone وbindpose/Animator مسار مستقل.
- مواد متعددة ناقصة عند M03: فحص submesh→Material slot الأصلي وترتيب Unity importer؛ بوابة Unity build توقفنا إذا اختلف العدد.
- 0 errors في JSON مع صورة جميلة لا يعني تكافؤ shader كامل. قبول هذا المختبر هو **source texture path on-device** فقط.

## الوثائق التقنية
- مصدر الاختيار القديم: [GFX-MULTI-001 القديم](https://github.com/alwansan/raf/actions/runs/42711514279). **الاختيار الجديد المعتمد بعد استبعاد 12 هندسة غير صالحة:** [GFX-MULTI-001 الجديد](https://github.com/alwansan/raf/actions/runs/42719663373).
- استخراج الستة للترتيب القديم فقط: [GFX-MULTI-002](https://github.com/alwansan/raf/actions/runs/42712118731). **الإعادة نجحت:** [GFX-MULTI-002 الجديد](https://github.com/alwansan/raf/actions/runs/42720399689) ستة Mesh/7 مواد/21 صورة.
- بناء Unity السابق [GFX-MULTI-003 الأول](https://github.com/alwansan/raf/actions/runs/42712833407) و[المحاولة الثالثة](https://github.com/alwansan/raf/actions/runs/42718266273) **فشلا قبل APK**. لا تثبّت نسخة الستة إلا بعد بناء جديد ناجح وتحقق التوقيع.
- رسالة الاستعادة: [RESTORE_AR.md](../prompt/graphics-lab/RESTORE_AR.md).

- تحليل المصدر الجديد [GFX-MULTI-004](https://github.com/alwansan/raf/actions/runs/42720400057): Shader48 واحد مشترك في 7 Material slots باثنين SubShaders و7 Passes، لكنه ليس Shader Android مستعادًا.
