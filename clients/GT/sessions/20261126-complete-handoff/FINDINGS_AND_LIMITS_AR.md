# النتائج والاكتشافات وحدودها

| المجال | الدليل المتاح | ما لا يثبته |
|---|---|---|
| جرد المواد | آخر SAME-EXPORT مقبول 43929698985:688/786 Custom non-Dummy،98Dummy/37GUID،29213 التزام Material/YAML/meta | ليست نسبة اكتمال اللعبة أو قبول بكسلات أو runtime keywords |
| دمج مسار Native | 6c071a414 أضاف 10 دفعات مع ترتيب post9/post13/post23 و 82owner أصلية جديدة و SHA ديناميكية لملفات Native | Native المعدل لم ينفذ هنا، وفجوة GT selectors في مرشحات الدفعات ما زالت قائمة |
| NEXT23b |44783011957/artifact14654640691:134/134 ترجمة و 2312routed stages و 2312entrypoints و 20085CB offsets و 7516varyings،19 خاصية و 4Pass | مصدر ShaderLab خاص، ليس قبول Unity/engine keywords/GUID/هاتف |
| FFT Utilities | الأصل 7Pass،7VSFS،12 برنامج،خاصيتان؛12roundtrips و 14entrypoints محلياً | Unity DXC44781701884 فشل؛ HLSLcc ليس مقبولاً داخل Unity بعد |
| تحكم FFT | SHA DXC f8575ebd855cff193c9fdb506b5f2b2d427d4c583eb9c5c7af0d6ff39c948b23؛ HLSLcc4d6e4815130daca16fdec13b4572f19c24c978e99787ba6f57658e4578759a69 | فقط إزالة 7pragmas use_dxc؛ لا تعديل عيّنات أو casts ولا دمج لعبة |
| Coordinate FFT |6 إحداثيات float4 في SPIR-V الأصلي المترجم،6float2 في roundtrip،صفر integer في كليهما | لا تبرير لتحويل int تخميني لحل خطأ DXC |
| النار | pointer أصلي SAME-EXPORT و Texture2D غير exportable يمكن تصنيفه دون اختلاق GUID | لا صورة ثالثة مصدرة مثبتة ولا مقارنة alpha GPU؛ ارتباط Particle108 بالنار الظاهرة نفسه غير مثبت بالكامل |
| الجهاز 20 نوفمبر | CL pinned8db59a4،968pass roots:484Foam و 484FFT Utilities؛0kernel roots؛ScudoOOM أثناء Adreno Vulkan renderpass | انعدام kernel errors في جلسة واحدة ليس إثبات compute كامل؛ سبب التخصيص أو ربط OOM بخطأ passes غير مثبت |
| تجربة Unity الاصطناعية |45760877767 نجاح 120 بكسلاً/5 حالات،llvmpipeLLVM15،maxerror0،ضوابط texture/tint/alpha | لا game pixels ولا Android ولا قبول مواد اللعبة |
| دفعات 3/4/5 | تاريخياً240 بكسلاً لكل دفعة 3/4،و 15 اختبار تعداد للدفعة 5 بحسب RESTORE المنشور | أرشيفاتها الأصلية غير متاحة هنا؛ لا إعادة تحقق جديدة ولا ادعاء نشرها |

## فجوة keywords الإنتاجية

الملف evidence/ten-group-runtime-keyword-audit.json يوثق كل مجموعة وسطر compose. الدالة compose تبني عند engine_keywords=False سلسلة multi_compile بأسماء GT_ORIGINAL_921_Pn_Vn. اختيار تلك الأسماء يولّد جميع برامج الترجمة، لكنه لا يربطها بالأسماء التي تضبطها اللعبة. غياب token الخاص يختار default route0. generic model installer مع counts_override يقبل engine_keywords_verified=False؛ وبقية مثبتي NEXT لا يشترطون دليلاً إيجابياً للكلمات الأصلية. لذلك لا يصح تحويل جرد non-Dummy إلى ادعاء مطابقة تشغيلية.

## مسودات منشورة للحفظ لا للاعتماد

NEXT23b workflow/C# probe و--next23b verifier يحاولون تسجيل engine routes الأصلية، ومقارنة SHA ومرحلتي Vulkan، ورفض GT-selector fallback. لم ينفذ هذا المسار حتى التسليم. يلزم مراجعة environment UNITY_LICENSE ومتاحية الأسرار قبل التشغيل؛ خلاف workflow FFT، مسودة NEXT23b الحالية لا تضبط job environment. فحص bundle الحالي يطابق الكلمات بتقاطع universe manifest ولا يرفض كل كلمة إضافية محتملة؛ كما يأتي ربط passType بالأصل من مسار composer، وليس إثبات مصدر مستقل من verifier. هذه حدود مراجعة يجب حسمها قبل اعتماد runtime parity.

FFT installer الجديد يتحقق من SHA owners و owner/PathID و trace class48 و GUID و meta وإيصالات source/Unity/bundle وربط المرشح، مع backup خارجي و commitments لكل ملفات المشروع و rollback. اجتياز اختباره الاصطناعي لا يعني أنه ركب على تصدير حقيقي؛ لا استدعاء له في workflow الإنتاجية الآن.

## اختبارات قديمة لا تُسوّى إلى أخضر

فحص 740 ملفاً منعزلاً تاريخياً أعطى 712pass و 28fail. واحد من الإخفاقات كان fixture تاريخية تقارن مجموعة شروط قديمة بـ FFT الجديد، وصُحح؛27 باقية أُعيد إنتاجها على الأساس f5115a4. السجلات وأسماء الفشل في tests/historical-results.json و historical-baseline-results.json. بعض الإخفاقات نقص modules/cryptography أو تعارض import وبعضها assertions قديمة؛ لا يعني ذلك أن suite كاملة خضراء. فشل discovery العام بسبب اسم اختبار مكرر بين scripts و tests محفوظ أيضاً.
