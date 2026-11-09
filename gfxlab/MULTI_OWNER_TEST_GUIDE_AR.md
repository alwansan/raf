# GFX-MULTI-003 — دليل تجربة ستة مجسمات على هاتف Android

**الحزمة المستقلة (إذا أثبت GitHub Actions نجاح بناء APK والتوقيع):** `com.alwansan.raft.graphicslab.multi`. لا تحذف مختبر المقص `com.alwansan.raft.graphicslab.shears` أو لعبة Raft الكاملة. Unity 2021.3.45f2، IL2CPP ARM64، OpenGLES3، Linear.

## واجهة التطبيق
- القائمة الجانبية تحتوي **M00–M05**: **M00 Shears** (المقص الذي قبلته بصرياً)، M01 source person/100 bones **static bind pose only**، M02 large_prop، M03 large_mesh، M04 tool، M05 multi_material. هذه تسميات فئات مُثبتة من الـGameObject/Mesh في المصدر وليست تأكيداً لأسماء العناصر داخل اللعبة؛ تحديد M01 بأنه لاعب كامل يتطلب مشهداً/ريغاً موثقاً.
- زر `NEXT MATERIAL` يبدّل بالتتابع: `WHITE_LIT`، `WHITE_UNLIT`، `SOURCE_ALBEDO_STANDARD`، `SOURCE_PBR_STANDARD_APPROX`.
- التدوير بإصبع، التقريب بإصبعين، `RESET VIEW` لإعادة الزاوية، `SPIN` للدوران، `SHOW HELPERS` لإظهار قاعدة العرض (مخفية افتراضياً). الصور الأصلية ليست منشورة منفردة، بل موجودة داخل APK المختبر فقط.
- `COPY LOG` ينسخ JSON للموديل والوضع المختار واسم GPU/API وعداد أخطاء Unity.
- **كل موديل من المصدر الأصلي ومربوط بصور أصلية. الشيدرات المعروضة Unity Standard diagnostic وليست بالضرورة Raft Shader48 الأصلي أو جميع Passes والـkeywords.** `originalShaderRestored=false` و`originalAnimationRestored=false` متوقعان، وليس فشل جهاز.

## اختبار بصري سريع (يتكرر للموديلات الستة)
1. افتح M00 في وضع `SOURCE_PBR_STANDARD_APPROX`، وتأكد أنه نفس المقص الملون v0.2 حتى نصادق عدم وجود تراجع.
2. بدّل M01–M05، وفحص كل مجسم من جميع الزوايا؛ هل هو مجسم كامل أم جزء من شخصية/منشأة؟ هل تظهر أوجه مفقودة أو حواف مقلوبة أو خامات في موضع خاطئ؟
3. قارن `SOURCE_ALBEDO_STANDARD` مع `SOURCE_PBR_STANDARD_APPROX`. لو ظهرت ألوان صحيحة في Albedo وخلل في PBR، فهذا يرجّح ربط Normal/Metallic/Shader fallback وليس فقد الألوان.
4. خصّص اهتماماً لـM01 (Skinned source but static OBJ pose) وM05 (2 مواد و6 صور). لا نستنتج صحة حركة العظام من ثبات مجسم فقط.
5. في كل موديل اضغط COPY LOG وأرسل JSON وصورة من `SOURCE_PBR_STANDARD_APPROX`؛ وإذا وجدت مشكلة أرسل لقطة Albedo من نفس الزاوية. يفضّل 6 صور + 6 سجلات صغيرة.

## حقول التقرير المرتقبة
`modelId`, `category`, `originalGeometryKind`, `materialMode`, `deviceModel`, `gfxApi`, `colorSpace`, `sourceGeometryVerified`, `sourceTextureChainVerified`, `originalShaderRestored`, `originalAnimationRestored`, `availableModels`, `sourceBones`, `sourceMaterials`, `sourceTextures`, `vertices`, `triangles`, `errors`, `firstError`.

## مسار قرار العيوب
- أبيض في كل الأوضاع: تحقق من مرجع model/Renderer وUnity material، وليس اتهام Adreno مباشرة.
- ألوان Albedo صحيحة لكن PBR خاطئة: افصل normal-map packing (DXT5nm), MetallicGlossMap channels, Linear/sRGB وsampler/UV. لا تغير المادّة الأصلية عشوائياً.
- قطعة من نموذج أو وضعية غير طبيعية مع M01: هذا متوقع ممكن من OBJ ثابت؛ استعادة 100 bone وbindpose/Animator مسار مستقل.
- مواد متعددة ناقصة عند M05: فحص submesh→Material slot الأصلي وترتيب Unity importer؛ بوابة Unity build توقفنا إذا اختلف العدد.
- 0 errors في JSON مع صورة جميلة لا يعني تكافؤ shader كامل. قبول هذا المختبر هو **source texture path on-device** فقط.

## الوثائق التقنية
- مصدر 5 إضافية: [GFX-MULTI-001](https://github.com/alwansan/raf/actions/runs/42711514279).
- استخراج الستة والمواد/الصور: [GFX-MULTI-002](https://github.com/alwansan/raf/actions/runs/42712118731).
- بناء Unity وتوقيع APK: [GFX-MULTI-003](https://github.com/alwansan/raf/actions/runs/42712833407).
- رسالة الاستعادة: [RESTORE_AR.md](../prompt/graphics-lab/RESTORE_AR.md).
