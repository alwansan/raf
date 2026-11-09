# دليل تجربة Shears — مختبر ألوان Raft GFX-LAB v0.2

**هذا دليل للاختبار بعد نجاح ملف APK الموقّع في GFX-SHEARS-005، ولا يعتبر الاختبار قد نجح على الهاتف قبل صور المالك.**

التطبيق مستقل عن لعبة Raft الأصلية وعن مختبر GFX الأبيض السابق؛ الحزمة المتوقعة: com.alwansan.raft.graphicslab.shears، منظر أفقي 3D مع نموذج Shears الأصلي 375 vertex/420 triangles.

## أربع حالات داخل التطبيق
كل ضغطة على **NEXT MATERIAL** تنقل للحالة التالية، وبعد الحالة الرابعة تعود للأولى:
1. LIT_WHITE: الشكل الأصلي + مادة Standard بيضاء، للمقارنة مع APK الأبيض السابق.
2. UNLIT_WHITE: لون أبيض دون استجابة ضوئية، لفصل مشاكل الإضاءة عن الهندسة.
3. SOURCE_ALBEDO_STANDARD_DIAGNOSTIC: صورة الـAlbedo الأصلية + tint محفوظ في المصدر على شيدر Unity Standard، **ليس Shader Raft الأصلي**. هذه الحالة الأفضل لمقارنة زرقة المعدن وبني المقبض مع صورة اللعبة.
4. SOURCE_TEXTURE_PBR_STANDARD_APPROX: يضيف Normal وMetallic الأصليتين إلى Standard. قد يختلف اللمعان/الشفافية عن Raft PC لأن original Shader48 يحتوي 2 SubShaders و7 Passes، ولم يُستعد بعد.

## ماذا ترسل؟
- لقطة واحدة لكل وضعية، ويفضّل نفس زاوية الكاميرا عبر RESET VIEW؛ يمكنك تدوير المقص بإصبعك أو SPIN للتأكد من العمق.
- في وضع ALBEDO انسخ **COPY LOG** وأرسل JSON كاملاً، ثم في وضع PBR انسخ JSON آخر. تأكد من fields sourceTextureChainVerified=true، originalShaderRestored=false، gpu API، errors.
- هل ظهرت الشفرات زرقاء؟ هل لون المقبض/الهيكل بني؟ هل الوجه المقابل للمقص طبيعي؟ هل PBR حسّن أو أفسد الضوء مقارنة بـALBEDO؟
- إذا ظهر خطأ أو شاشة سوداء، أرسل لقطة واترك وضع الاختبار واسم APK ولا تمس اللعبة الأصلية.

**تفسير النتائج:** عودة اللون تعني أن source texture stream وUV وUnity texture binding نجحت على الجهاز. لا تثبت استعادة شيدر Raft الأصلي أو النار/الماء/الظلال الكاملة. الاختبار الصحيح التالي بعد هذا هو المصدر الأصلي للـ7 Passes وShader variant/keywords والسامبلر والـDXT5nm.
